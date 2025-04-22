# category_provider_visualization.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os

# === Settings ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, "output", "processed")

# === Load CSVs ===
@st.cache_data
def load_data(bank_type, year):
    filename = f"{bank_type.lower()}_{year}_mapped_20250422.csv"  # evtl. Datum anpassen
    filepath = os.path.join(DATA_FOLDER, filename)
    if not os.path.exists(filepath):
        return pd.DataFrame()
    df = pd.read_csv(filepath, parse_dates=["Datum"])
    df["Monat"] = df["Datum"].dt.to_period("M").astype(str)
    return df

# === Sidebar ===
st.sidebar.title("🔧 Mega-Provider-Visualisierung")

bank_types = st.sidebar.multiselect(
    "Kontotyp(en) auswählen:",
    ("volksbank", "mastercard"),
    default=("volksbank", "mastercard")
)

available_years = ["2022", "2023", "2024", "2025"]
selected_years = st.sidebar.multiselect(
    "Jahre auswählen:",
    options=available_years,
    default=available_years
)

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
    st.error("❌ Keine Daten gefunden.")
    st.stop()

df = pd.concat(all_dfs, ignore_index=True)

# === Kategorie Auswahl aktualisieren ===
all_categories = sorted(df["Kategorie"].dropna().unique())
category_selection = st.sidebar.selectbox("Kategorie auswählen:", all_categories)

# === Top-N und Sortierung ===
top_n = st.sidebar.slider("Top N Provider:", 5, 30, 10)
sort_descending = st.sidebar.checkbox("Sortierung nach Ausgaben absteigend", value=True)

# === Daten filtern ===
filtered_df = df[df["Kategorie"] == category_selection]

# === Tabs ===
tab1, tab2, tab3 = st.tabs(["📊 Übersicht nach Jahr", "📅 Drill-Down nach Monat", "📈 Monatsvergleich"])

# === 1. Übersicht nach Jahr ===
with tab1:
    st.header(f"Top Provider für {category_selection} (jährlich)")

    provider_year_summary = (
        filtered_df.groupby(["Provider", "Jahr"])
        .agg({"Betrag": "sum"})
        .reset_index()
    )

    # Top Provider bestimmen (über alle Jahre)
    top_providers = (
        provider_year_summary.groupby("Provider")["Betrag"]
        .sum()
        .abs()
        .sort_values(ascending=not sort_descending)
        .head(top_n)
        .index
        .tolist()
    )

    filtered_summary = provider_year_summary[provider_year_summary["Provider"].isin(top_providers)]

    fig1, ax1 = plt.subplots(figsize=(14, 7))

    for jahr in selected_years:
        df_year = filtered_summary[filtered_summary["Jahr"] == jahr]
        df_year = df_year.set_index("Provider").reindex(top_providers).fillna(0)
        ax1.bar(
            [f"{prov} ({jahr})" for prov in top_providers],
            df_year["Betrag"],
            label=jahr
        )

    ax1.set_ylabel("Betrag (€)")
    ax1.set_xlabel("Provider (nach Jahr)")
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha="right")
    ax1.legend(title="Jahr")
    ax1.grid(True, axis='y')
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,} €"))
    st.pyplot(fig1)

# === 2. Drill-Down nach Monat ===
with tab2:
    st.header(f"Drill-Down: {category_selection} (monatlich)")

    monthly_summary = (
        filtered_df.groupby(["Jahr", "Monat", "Provider"])
        .agg({"Betrag": "sum"})
        .reset_index()
    )

    selected_provider = st.selectbox("Provider auswählen:", top_providers)

    provider_monthly = monthly_summary[monthly_summary["Provider"] == selected_provider]

    fig2, ax2 = plt.subplots(figsize=(14, 7))

    for jahr in selected_years:
        data = provider_monthly[provider_monthly["Jahr"] == jahr]
        data = data.set_index("Monat").reindex(
            [f"{m:02d}" for m in range(1, 13)],
            fill_value=0
        )
        ax2.plot(
            data.index,
            data["Betrag"],
            marker="o",
            label=jahr
        )

    ax2.set_ylabel("Betrag (€)")
    ax2.set_xlabel("Monat")
    ax2.legend(title="Jahr")
    ax2.grid(True)
    ax2.set_xticks([f"{m:02d}" for m in range(1, 13)])
    ax2.set_xticklabels(["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"])
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,} €"))
    st.pyplot(fig2)

# === 3. Monatsvergleich ===
with tab3:
    st.header(f"Monatsvergleich: {category_selection}")

    selected_month = st.selectbox(
        "Monat auswählen:",
        [f"{m:02d}" for m in range(1, 13)],
        format_func=lambda m: ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"][int(m) - 1]
    )

    monthly_comp = (
        filtered_df[filtered_df["Datum"].dt.month == int(selected_month)]
        .groupby(["Provider", "Jahr"])
        .agg({"Betrag": "sum"})
        .reset_index()
    )

    monthly_top_providers = (
        monthly_comp.groupby("Provider")["Betrag"]
        .sum()
        .abs()
        .sort_values(ascending=not sort_descending)
        .head(top_n)
        .index
        .tolist()
    )

    monthly_filtered = monthly_comp[monthly_comp["Provider"].isin(monthly_top_providers)]

    fig3, ax3 = plt.subplots(figsize=(14, 7))

    for jahr in selected_years:
        df_jahr = monthly_filtered[monthly_filtered["Jahr"] == jahr]
        df_jahr = df_jahr.set_index("Provider").reindex(monthly_top_providers).fillna(0)
        ax3.bar(
            [f"{prov} ({jahr})" for prov in monthly_top_providers],
            df_jahr["Betrag"],
            label=jahr
        )

    ax3.set_ylabel("Betrag (€)")
    ax3.set_xlabel("Provider (nach Jahr)")
    ax3.legend(title="Jahr")
    ax3.grid(True, axis='y')
    ax3.set_xticklabels(ax3.get_xticklabels(), rotation=45, ha="right")
    ax3.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,} €"))
    st.pyplot(fig3)

# === Footer ===
st.caption("🔍 Drill-Down, Monatsvergleich und Top-Provider – alles flexibel auswählbar!")
