import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib.ticker as ticker

# === Settings ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, "output", "processed")

# === Config ===
st.set_page_config(page_title="💸 Finanz-Visualizer", layout="wide")

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
st.sidebar.title("🔧 Einstellungen")

with st.sidebar.expander("📚 Basis-Auswahl", expanded=True):
    bank_types = st.multiselect(
        "Kontotyp(en)",
        ("volksbank", "mastercard"),
        default=("volksbank", "mastercard")
    )

    available_years = ["2022", "2023", "2024", "2025"]
    selected_years = st.multiselect("Jahre", available_years, default=available_years)

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

# === Kategorie Filter aktualisieren ===
available_categories = sorted(df["Kategorie"].dropna().unique().tolist())
available_categories.insert(0, "Alle")
selected_category = st.sidebar.selectbox("Kategorie filtern", options=available_categories)

# === Hauptseite ===
st.title("📈 Finanzdaten Visualisierung")
st.markdown("---")

# === Filter Sektion ===
with st.container():
    st.subheader("🌟 Filtereinstellungen")

    col1, col2, col3 = st.columns(3)
    with col1:
        min_date, max_date = st.date_input("Zeitraum", value=[df["Datum"].min(), df["Datum"].max()])
    with col2:
        betrag_range = st.slider("Betragsbereich (€)", float(df["Betrag"].min()), float(df["Betrag"].max()),
                                 (float(df["Betrag"].min()), float(df["Betrag"].max())))
    with col3:
        top_n = st.slider("Top N Anbieter", 3, 30, 10)

# === Daten filtern ===
filtered_df = df[
    (df["Datum"] >= pd.to_datetime(min_date)) &
    (df["Datum"] <= pd.to_datetime(max_date)) &
    (df["Betrag"] >= betrag_range[0]) &
    (df["Betrag"] <= betrag_range[1])
]
if selected_category != "Alle":
    filtered_df = filtered_df[filtered_df["Kategorie"] == selected_category]

# === Tabs ===
tab1, tab2, tab3, tab4 = st.tabs(["📈 Cashflow", "📊 Top Provider", "📚 Kategorie Analyse", "🗓️ Heatmap"])

# === Cashflow Verlauf ===
with tab1:
    st.subheader("📈 Monatlicher Cashflow Verlauf")
    fig, ax = plt.subplots(figsize=(12, 6))
    for (banktyp, jahr), group in filtered_df.groupby(["Banktyp", "Jahr"]):
        monthly_sum = group.groupby(group["Datum"].dt.month)["Betrag"].sum()
        monthly_sum = monthly_sum.reindex(range(1, 13), fill_value=0)
        label = f"{banktyp.capitalize()} {jahr}"
        monthly_sum.plot(kind="line", marker="o", ax=ax, label=label)

    ax.set_ylabel("Saldo (€)")
    ax.set_xlabel("Monat")
    ax.legend(title="Banktyp / Jahr")
    ax.grid(True)
    st.pyplot(fig)

# === Top Provider ===
with tab2:
    st.subheader("🏆 Top Anbieter Auswertung")
    if "Provider" in filtered_df.columns:
        top_provider_df = (
            filtered_df.groupby("Provider")["Betrag"]
            .sum()
            .abs()
            .sort_values(ascending=False)
            .head(top_n)
            .reset_index()
        )

        fig3, ax3 = plt.subplots(figsize=(12, 6))
        sns.barplot(data=top_provider_df, x="Betrag", y="Provider", ax=ax3, palette="viridis")
        ax3.set_xlabel("Betrag (€)")
        ax3.set_ylabel("Provider")
        st.pyplot(fig3)
    else:
        st.info("ℹ️ Keine Provider-Daten vorhanden.")

# === Kategorie Analyse ===
with tab3:
    st.subheader("📚 Ausgabenanalyse nach Kategorie")

    if filtered_df.empty:
        st.warning("⚠️ Keine Daten für die Auswahl gefunden.")
    else:
        pivot = filtered_df.pivot_table(
            index="Provider",
            columns="Jahr",
            values="Betrag",
            aggfunc="sum",
            fill_value=0
        )
        pivot["Gesamt"] = pivot.sum(axis=1)
        pivot = pivot.sort_values("Gesamt", ascending=False).head(top_n)

        st.dataframe(pivot.style.format("{:.2f} €").background_gradient(cmap="RdYlGn", axis=1))

        available_providers = pivot.index.tolist()
        selected_providers = st.multiselect("Provider auswählen für Diagramm", options=available_providers, default=available_providers)

        if selected_providers:
            filtered_pivot = pivot.loc[selected_providers]

            fig4, ax4 = plt.subplots(figsize=(10, 6))
            filtered_pivot.drop(columns="Gesamt").plot(kind="bar", ax=ax4)
            ax4.set_ylabel("Betrag (€)")
            ax4.set_xlabel("Provider")
            ax4.legend(title="Jahr")
            ax4.grid(True)
            ax4.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,} €"))
            ax4.set_xticklabels(ax4.get_xticklabels(), rotation=45, ha="right")
            st.pyplot(fig4)

        st.download_button(
            label="⬇️ Tabelle als CSV herunterladen",
            data=pivot.to_csv().encode('utf-8'),
            file_name=f"ausgaben_{selected_category.lower()}_{'_'.join(selected_years)}.csv",
            mime='text/csv'
        )

# === Heatmap Tab ===
with tab4:
    st.subheader("🗓️ Heatmap: Ausgaben pro Wochentag und Monat")

    if filtered_df.empty:
        st.warning("⚠️ Keine Daten für die Heatmap vorhanden.")
    else:
        available_providers_heatmap = sorted(filtered_df["Provider"].dropna().unique().tolist())
        selected_providers_heatmap = st.multiselect("Provider auswählen für Heatmap", options=available_providers_heatmap, default=available_providers_heatmap)

        heatmap_df = filtered_df[filtered_df["Provider"].isin(selected_providers_heatmap)]

        heatmap_df["Wochentag"] = heatmap_df["Datum"].dt.day_name()
        heatmap_df["Monat_Year"] = heatmap_df["Datum"].dt.to_period("M").astype(str)

        pivot_table = heatmap_df.pivot_table(
            index="Wochentag",
            columns="Monat_Year",
            values="Betrag",
            aggfunc="sum",
            fill_value=0
        )

        ordered_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        pivot_table = pivot_table.reindex(ordered_days)

        fig5, ax5 = plt.subplots(figsize=(14, 6))
        sns.heatmap(pivot_table, cmap="RdYlGn", linewidths=0.5, annot=True, fmt=".0f", ax=ax5)
        ax5.set_ylabel("Wochentag")
        ax5.set_xlabel("Monat")
        st.pyplot(fig5)

# === Footer ===
st.markdown("---")
st.caption("✨ Powered by Streamlit, Matplotlib & Seaborn")