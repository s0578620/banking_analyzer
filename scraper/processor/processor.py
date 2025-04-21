# scraper/processor/processor.py
import os
import pandas as pd
import json
import re
import datetime
from scraper.utils.utils import normalize_text
from scraper.utils.logger import setup_logger

logger = setup_logger(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
INPUT_FOLDER = os.path.join(BASE_DIR, "output", "parser_output")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "output", "processed")


def load_mapping():
    mapping_path = os.path.join(BASE_DIR, "mapping", "provider_mapping.json")
    if not os.path.exists(mapping_path):
        raise FileNotFoundError(f"Mapping-Datei nicht gefunden: {mapping_path}")

    with open(mapping_path, "r", encoding="utf-8") as f:
        return json.load(f)


def map_verwendungszweck(zeile, mapping):
    verwendungszweck = normalize_text(str(zeile))
    matches = []
    for provider, kategorie in mapping.items():
        normalized_provider = normalize_text(provider)
        if normalized_provider in verwendungszweck:
            matches.append((provider, kategorie))

    if matches:
        provider, kategorie = sorted(matches, key=lambda x: len(x[0]), reverse=True)[0]
        return provider, kategorie

    return "Sonstiges", "Sonstiges"


ENTGELT_KEYWORDS = ["Auslandseinsatzentgelt", "Barauszahlungsgebühr"]

def extract_entgelt_and_create_new_rows(df):
    new_rows = []

    for index, row in df.iterrows():
        verwendungszweck = row['Verwendungszweck']

        for keyword in ENTGELT_KEYWORDS:
            if keyword in verwendungszweck:
                match = re.search(rf"{re.escape(keyword)}\s*([0-9]+,[0-9]+|-?[0-9]+\.[0-9]+|-?[0-9]+)", verwendungszweck)
                if match:
                    betrag_raw = match.group(1).replace(',', '.').strip()

                    if betrag_raw.endswith('-'):
                        betrag_raw = '-' + betrag_raw[:-1]

                    betrag_float = float(betrag_raw)

                    # Jetzt neue Zusatzzeile erstellen
                    new_row = {
                        'Datum': row['Datum'],
                        'Verwendungszweck': keyword,
                        'Betrag': betrag_float,
                        'Provider': row.get('Provider', ''),
                        'Kategorie': row.get('Kategorie', ''),
                    }


                    if 'Konto' in df.columns:
                        new_row['Konto'] = row['Konto']

                    new_rows.append(new_row)

    if new_rows:
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)

    return df


def process_file(csv_path):
    logger.info(f"🔧 Verarbeite {csv_path}...")
    df = pd.read_csv(csv_path)

    mapping = load_mapping()

    df[["Provider", "Kategorie"]] = df["Verwendungszweck"].apply(
        lambda vz: pd.Series(map_verwendungszweck(vz, mapping))
    )

    df = extract_entgelt_and_create_new_rows(df)

    if 'Verwendungszweck' in df.columns:
        df.drop(columns=['Verwendungszweck'], inplace=True)
    output_folder = OUTPUT_FOLDER

    os.makedirs(output_folder, exist_ok=True)

    original_filename = os.path.basename(csv_path)
    clean_filename = original_filename.replace("buchungen_", "").replace(".csv", "")

    today_str = datetime.datetime.now().strftime("%Y%m%d")
    final_filename = f"{clean_filename}_mapped_{today_str}.csv"

    output_path = os.path.join(output_folder, final_filename)

    df.to_csv(output_path, index=False)
    logger.info(f"✅ Datei gespeichert unter {output_path}")


if __name__ == "__main__":
    for filename in os.listdir(INPUT_FOLDER):
        if filename.endswith(".csv"):
            process_file(os.path.join(INPUT_FOLDER, filename))

