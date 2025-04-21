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

# === Load all available CSVs ===
@st.cache_data
def load_data(bank_type, year):
    filename = f"{bank_type.lower()}_{year}_mapped_20250422.csv"  # adjust if date changes
    filepath = os.path.join(DATA_FOLDER, filename)
    if not os.path.exists(filepath):
        st.error(f"CSV für {bank_type} {year} nicht gefunden!")
        return pd.DataFrame()
    df = pd.read_csv(filepath, parse_dates=["Datum"])
    df["Monat"] = df["Datum"].dt.to_period("M").astype(str)
    return df

# === Sidebar ===
st.sidebar.title("🔧 Einstellungen")

# Typ Auswahl
bank_type = st.sidebar.selectbox(
    "Kontotyp auswählen:",
    ("volksbank", "mastercard")
)

# Jahr Auswahl
year = st.sidebar.selectbox(
    "Jahr auswählen:",
    ("2024", "2025")
)

# Lade CSV
df = load_data(bank_type, year)

if df.empty:
    st.stop()

# Kategorie Filter
available_categories = sorted(df["Kategorie"].dropna().unique())
selected_categories = st.sidebar.multiselect(
    "Kategorien filtern:",
    available_categories,
    default=available_categories
)

# Betrag Filter
min_betrag = float(df["Betrag"].min())
max_betrag = float(df["Betrag"].max())
betrag_range = st.sidebar.slider(
    "Betragsbereich (€):",
    min_value=min_betrag,
    max_value=max_betrag,
    value=(min_betrag, max_betrag),
)

# Datumsbereich Filter
min_date = df["Datum"].min()
max_date = df["Datum"].max()
date_range = st.sidebar.date_input(
    "Zeitraum filtern:",
    (min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# Top N Anbieter
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
st.title(f"📊 Finanz-Übersicht {bank_type.capitalize()} {year}")

# === 1. Monatlicher Cashflow Verlauf ===
st.subheader("1. Monatlicher Cashflow Verlauf")
monthly_sum = filtered_df.groupby("Monat")["Betrag"].sum()
fig, ax = plt.subplots()
monthly_sum.plot(kind="line", marker="o", ax=ax)
ax.set_ylabel("Saldo (€)")
ax.set_xlabel("Monat")
ax.grid(True)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,} €"))
st.pyplot(fig)

# === 2. Top Anbieter ===
st.subheader("2. Top Anbieter (nach Betrag)")
top_providers = (
    filtered_df.groupby("Provider")["Betrag"]
    .sum()
    .abs()
    .sort_values(ascending=False)
    .head(top_n)
)
fig2, ax2 = plt.subplots()
top_providers.plot(kind="bar", ax=ax2)
ax2.set_ylabel("Betrag (€)")
ax2.set_xlabel("Anbieter")
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha="right")
ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,} €"))

# Werte über Balken schreiben
for p in ax2.patches:
    ax2.annotate(
        f"{int(p.get_height()):,} €",
        (p.get_x() + p.get_width() / 2., p.get_height()),
        ha='center', va='bottom',
        fontsize=8, rotation=0
    )
st.pyplot(fig2)

# === 3. Einnahmen vs Ausgaben ===
st.subheader("3. Einnahmen vs Ausgaben")

einnahmen = filtered_df[filtered_df["Betrag"] > 0]["Betrag"].sum()
ausgaben = -filtered_df[filtered_df["Betrag"] < 0]["Betrag"].sum()

def pie_label(pct, allvals):
    absolute = int(pct/100.*sum(allvals))
    return f"{pct:.1f}%\n({absolute:,} €)"

fig3, ax3 = plt.subplots()
ax3.pie(
    [einnahmen, ausgaben],
    labels=["Einnahmen", "Ausgaben"],
    autopct=lambda pct: pie_label(pct, [einnahmen, ausgaben]),
    startangle=90,
    colors=["#4CAF50", "#F44336"]
)
ax3.axis("equal")
st.pyplot(fig3)

# === 4. Heatmap: Ausgaben nach Wochentag und Monat ===
st.subheader("4. Heatmap: Ausgaben nach Wochentag und Monat")

filtered_df["Wochentag"] = filtered_df["Datum"].dt.day_name()
filtered_df["Monat_Year"] = filtered_df["Datum"].dt.to_period("M").astype(str)

pivot_table = filtered_df.pivot_table(
    index="Wochentag",
    columns="Monat_Year",
    values="Betrag",
    aggfunc="sum",
    fill_value=0
)

# Reihenfolge der Wochentage
ordered_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
pivot_table = pivot_table.reindex(ordered_days)

# Heatmap anzeigen
fig4, ax4 = plt.subplots(figsize=(10, 5))
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

# === Footer ===
st.caption("🔍 Tipp: Filter in der Sidebar anpassen für genauere Auswertungen!")

