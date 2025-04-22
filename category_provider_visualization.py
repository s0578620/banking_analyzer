# 📁 mega_visualizer_provider_per_category.py
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

available_years = ["2022","2023", "2024", "2025"]
selected_years = st.sidebar.multiselect(
    "Jahre auswählen:",
    options=available_years,
    default=available_years
)

# Kategorie Auswahl
category_selection = st.sidebar.selectbox("Kategorie auswählen:", ["Alle"])

# Top-N Auswahl
top_n = st.sidebar.slider("Top N Provider:", 5, 30, 10)

# Sortierung Auswahl
sort_descending = st.sidebar.checkbox("Sortierung nach Ausgaben absteigend", value=True)

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

# === Kategorie Liste aktualisieren ===
all_categories = sorted(df["Kategorie"].dropna().unique())
category_selection = st.sidebar.selectbox("Kategorie auswählen:", all_categories)

# === Daten filtern ===
filtered_df = df[df["Kategorie"] == category_selection]

# === Aggregieren ===
provider_year_summary = filtered_df.groupby(["Provider", "Jahr"]).agg({"Betrag": "sum"}).reset_index()

# Top Provider bestimmen (über alle Jahre zusammen)
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

# === Plot ===
st.title(f"📊 Provider-Ausgaben: {category_selection}")

fig, ax = plt.subplots(figsize=(12, 6))

for jahr in selected_years:
    df_year = filtered_summary[filtered_summary["Jahr"] == jahr]
    df_year = df_year.set_index("Provider").reindex(top_providers).fillna(0)
    ax.bar(
        [p + f" ({jahr})" for p in top_providers],
        df_year["Betrag"],
        label=jahr
    )

ax.set_ylabel("Betrag (€)")
ax.set_xlabel("Provider (nach Jahr)")
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
ax.legend(title="Jahr")
ax.grid(True, axis='y')
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,} €"))
st.pyplot(fig)

st.caption("🔍 Tipp: Nutze Top-N, Sortierung und Kategorie-Auswahl für scharfe Insights!")
