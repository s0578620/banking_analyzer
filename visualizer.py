# visualizer.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import os

# === Settings ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, "output", "processed")

# === Load CSVs ===
@st.cache_data
def load_data(bank_type, year):
    filename = f"{bank_type.lower()}_{year}_mapped_20250422.csv"
    filepath = os.path.join(DATA_FOLDER, filename)
    if not os.path.exists(filepath):
        return pd.DataFrame()
    df = pd.read_csv(filepath, parse_dates=["Datum"])
    df["Monat"] = df["Datum"].dt.to_period("M").astype(str)
    return df

# === Sidebar ===
st.sidebar.title("🔧 Mega-Visualizer Einstellungen")

bank_types = st.sidebar.multiselect(
    "Kontotyp(en) auswählen:",
    ("volksbank", "mastercard"),
    default=("volksbank", "mastercard")
)

available_years = ["2022","2023", "2024", "2025"]
selected_years = st.sidebar.multiselect(
    "Jahre auswählen (für Vergleich):",
    options=available_years,
    default=available_years
)

st.sidebar.title("📈 Zusätzliche Visualisierungen")
cashflow_banktyp_enabled = st.sidebar.checkbox("Cashflow nach Banktyp anzeigen", value=True)
netto_saldo_enabled = st.sidebar.checkbox("Netto-Saldo Entwicklung anzeigen", value=True)
kumuliertes_vermoegen_enabled = st.sidebar.checkbox("Kumuliertes Vermögen anzeigen", value=True)

# === Daten laden ===
all_dfs = []
for bank_type in bank_types:
    for year in selected_years:
        df_temp = load_data(bank_type, year)
        if not df_temp.empty:
            df_temp["Jahr"] = year
            df_temp["Banktyp"] = bank_type
            all_dfs.append(df_temp)

if not all_dfs:
    st.error("❌ Keine Daten für die ausgewählten Jahre und Banktypen gefunden.")
    st.stop()

df = pd.concat(all_dfs, ignore_index=True)

# === Filter Settings ===
available_categories = sorted(df["Kategorie"].dropna().unique())
selected_categories = st.sidebar.multiselect(
    "Kategorien filtern:",
    available_categories,
    default=available_categories
)

min_betrag = float(df["Betrag"].min())
max_betrag = float(df["Betrag"].max())
betrag_range = st.sidebar.slider(
    "Betragsbereich (€):",
    min_value=min_betrag,
    max_value=max_betrag,
    value=(min_betrag, max_betrag)
)

min_date = df["Datum"].min()
max_date = df["Datum"].max()
date_range = st.sidebar.date_input(
    "Zeitraum filtern:",
    (min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

top_n = st.sidebar.slider("Top N Anbieter (nach Betrag):", 3, 20, 10)

# === Daten filtern ===
filtered_df = df[
    (df["Kategorie"].isin(selected_categories)) &
    (df["Betrag"] >= betrag_range[0]) &
    (df["Betrag"] <= betrag_range[1]) &
    (df["Datum"] >= pd.to_datetime(date_range[0])) &
    (df["Datum"] <= pd.to_datetime(date_range[1]))
]

# === Hauptseite ===
st.title(f"📊 Mega-FinanzÜbersicht: {', '.join(bank_types)} ({', '.join(selected_years)})")

# === 1. Monatlicher Cashflow Verlauf ===
st.subheader("1. Monatlicher Cashflow Verlauf")
fig, ax = plt.subplots()
for (banktyp, jahr), group in filtered_df.groupby(["Banktyp", "Jahr"]):
    monthly_sum = group.groupby(group["Datum"].dt.month)["Betrag"].sum()
    monthly_sum = monthly_sum.reindex(range(1, 13), fill_value=0)
    label = f"{banktyp.capitalize()} {jahr}"
    monthly_sum.plot(kind="line", marker="o", ax=ax, label=label)

ax.set_ylabel("Saldo (€)")
ax.set_xlabel("Monat")
ax.set_xticks(range(1, 13))
ax.set_xticklabels(["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"])
ax.legend(title="Banktyp / Jahr")
ax.grid(True)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,} €"))
st.pyplot(fig)

# === 4. Heatmap ===
st.subheader("4. Heatmap: Ausgaben pro Wochentag und Monat")
filtered_df["Wochentag"] = filtered_df["Datum"].dt.day_name()
filtered_df["Monat_Year"] = filtered_df["Datum"].dt.to_period("M").astype(str)
pivot_table = filtered_df.pivot_table(
    index="Wochentag",
    columns="Monat_Year",
    values="Betrag",
    aggfunc="sum",
    fill_value=0
)
ordered_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
pivot_table = pivot_table.reindex(ordered_days)
fig4, ax4 = plt.subplots(figsize=(12, 6))
sns.heatmap(
    pivot_table.applymap(lambda x: int(x)),
    annot=True,
    fmt="d",
    cmap="RdYlGn",
    linewidths=0.5,
    ax=ax4,
    center=0,
    cbar_kws={'label': 'Saldo (€)'}
)
ax4.set_title("Heatmap: Ausgaben pro Wochentag und Monat")
ax4.set_ylabel("Wochentag")
ax4.set_xlabel("Monat")
st.pyplot(fig4)

# === 5. Cashflow pro Banktyp ===
if cashflow_banktyp_enabled:
    st.subheader("5. Monatlicher Cashflow (gestapelt nach Banktyp)")
    monthly = filtered_df.groupby(["Monat", "Banktyp"])["Betrag"].sum().unstack(fill_value=0)
    fig5, ax5 = plt.subplots(figsize=(12, 6))
    monthly.plot(kind="bar", stacked=True, ax=ax5)
    ax5.set_ylabel("Saldo (€)")
    ax5.set_xlabel("Monat")
    ax5.set_xticklabels(monthly.index, rotation=45, ha="right")
    ax5.legend(title="Banktyp")
    ax5.grid(True)
    st.pyplot(fig5)

# === 6. Netto-Saldo Entwicklung ===
if netto_saldo_enabled:
    st.subheader("6. Monatlicher Netto-Saldo (Einnahmen - Ausgaben)")
    netto = filtered_df.groupby(filtered_df["Datum"].dt.to_period("M"))["Betrag"].sum()
    netto.index = netto.index.astype(str)
    fig6, ax6 = plt.subplots(figsize=(12, 4))
    netto.plot(kind="bar", color="skyblue", ax=ax6)
    ax6.set_ylabel("Netto-Saldo (€)")
    ax6.set_xlabel("Monat")
    ax6.axhline(0, color='black', lw=1)
    st.pyplot(fig6)

# === 7. Kumuliertes Vermögen ===
if kumuliertes_vermoegen_enabled:
    st.subheader("7. Kumuliertes Vermögen im Zeitverlauf")
    kumuliert = filtered_df.sort_values("Datum").set_index("Datum")["Betrag"].cumsum()
    fig7, ax7 = plt.subplots(figsize=(12, 4))
    kumuliert.plot(ax=ax7)
    ax7.set_ylabel("Kumuliertes Vermögen (€)")
    ax7.set_xlabel("Datum")
    ax7.grid(True)
    st.pyplot(fig7)

# === 5. Gesamtstatistik: Ausgaben pro Jahr & Provider ===

# Checkbox steuern
if st.sidebar.checkbox("Gesamtstatistik (Summe pro Provider & Jahr) anzeigen", value=True):
    st.subheader("5. Gesamtstatistik: Ausgaben pro Jahr & Provider")

    # Aggregieren
    provider_stats = (
        filtered_df.groupby(["Provider", "Jahr"])["Betrag"]
        .sum()
        .unstack(fill_value=0)
    )

    # Tabelle anzeigen
    st.dataframe(provider_stats.style.format("{:,.2f} €"))

    # Gesamtzeile hinzufügen (optional, falls gewünscht)
    provider_stats.loc["Gesamt"] = provider_stats.sum()

    # Balkendiagramm
    fig5, ax5 = plt.subplots(figsize=(12, 6))
    provider_stats.drop("Gesamt", errors="ignore").plot(kind="bar", stacked=True, ax=ax5)
    ax5.set_ylabel("Summe Betrag (€)")
    ax5.set_xlabel("Provider")
    ax5.set_title("Summe der Ausgaben pro Jahr und Provider")
    ax5.legend(title="Jahr")
    ax5.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,} €"))
    ax5.set_xticklabels(ax5.get_xticklabels(), rotation=45, ha="right")
    st.pyplot(fig5)


# === Footer ===
st.caption("🔍 Tipp: Aktiviere oder deaktiviere Plots je nach Analysebedarf!")
