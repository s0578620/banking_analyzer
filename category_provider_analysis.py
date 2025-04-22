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
    filename = f"{bank_type.lower()}_{year}_mapped_20250422.csv"
    filepath = os.path.join(DATA_FOLDER, filename)
    if not os.path.exists(filepath):
        return pd.DataFrame()
    df = pd.read_csv(filepath, parse_dates=["Datum"])
    df["Monat"] = df["Datum"].dt.to_period("M").astype(str)
    return df

# === Sidebar ===
st.sidebar.title("🎯 Kategorie-Analyse pro Jahr & Provider")

bank_types = st.sidebar.multiselect(
    "Kontotyp(en) auswählen:",
    ("volksbank", "mastercard"),
    default=("volksbank", "mastercard")
)

available_years = ["2022","2023", "2024", "2025"]
selected_years = st.sidebar.multiselect(
    "Jahr(e) auswählen:",
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
    st.error("❌ Keine Daten für die Auswahl gefunden.")
    st.stop()

df = pd.concat(all_dfs, ignore_index=True)

# === Kategorie-Auswahl ===
available_categories = sorted(df["Kategorie"].dropna().unique())
selected_category = st.sidebar.selectbox(
    "Kategorie auswählen:",
    available_categories
)

# === Top N Provider Auswahl ===
top_n = st.sidebar.slider("Top N Provider (nach Betrag):", 3, 30, 10)
sort_descending = st.sidebar.checkbox("🔀 Absteigend sortieren", value=True)

# === Filter ===
filtered_df = df[df["Kategorie"] == selected_category]

if filtered_df.empty:
    st.warning("⚠️ Keine Daten für die ausgewählte Kategorie.")
    st.stop()

# === Pivot Tabelle ===
pivot = filtered_df.pivot_table(
    index="Provider",
    columns="Jahr",
    values="Betrag",
    aggfunc="sum",
    fill_value=0
)

pivot["Gesamt"] = pivot.sum(axis=1)

# Sortieren
pivot = pivot.sort_values("Gesamt", ascending=not sort_descending)

# Nur Top N Provider anzeigen
pivot = pivot.head(top_n)

# === Anzeige ===
st.title("📊 Ausgabenanalyse nach Kategorie")
st.subheader(f"Kategorie: {selected_category}")

# Tabelle
st.dataframe(pivot.style.format("{:.2f} €").background_gradient(cmap="RdYlGn", axis=1))

# Balkendiagramm
fig, ax = plt.subplots(figsize=(10, 6))
pivot.drop(columns="Gesamt").plot(kind="bar", ax=ax)

ax.set_ylabel("Betrag (€)")
ax.set_xlabel("Provider")
ax.legend(title="Jahr")
ax.grid(True)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,} €"))
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")

st.pyplot(fig)

# === Download Option ===
st.download_button(
    label="⬇️ Tabelle als CSV herunterladen",
    data=pivot.to_csv().encode('utf-8'),
    file_name=f"ausgaben_{selected_category.lower()}_{'_'.join(selected_years)}.csv",
    mime='text/csv'
)

st.caption("✨ Tipp: Mit den Filtern links kannst du deine Analyse fein einstellen!")
