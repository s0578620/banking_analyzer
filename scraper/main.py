# scraper/main.py

import sys
import os
import pandas as pd

# Append Projekt-Wurzelverzeichnis
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Danach normale Imports
from scraper.parser.parser_mastercard import parse_mastercard
from scraper.parser.parser_volksbank import parse_volksbank
from scraper.utils.utils import detect_bank_typ
from scraper.utils.logger import setup_logger
from scraper.utils.suppress_warnings import suppress_warnings

# Setup
logger = setup_logger(__name__)
suppress_warnings()

def main(input_folder=None):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    if input_folder is None:
        input_folder = os.path.join(BASE_DIR, "..", "input")
    output_folder = os.path.join(BASE_DIR, "..", "output", "parser_output")

    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    volksbank_buchungen = []
    mastercard_buchungen = []

    # Alle PDFs verarbeiten
    for filename in os.listdir(input_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_folder, filename)
            logger.info(f"📄 Verarbeite {filename}...")

            bank_typ = detect_bank_typ(filename)

            if bank_typ == "volksbank":
                df_vb = parse_volksbank(pdf_path)
                volksbank_buchungen.append(df_vb)

            elif bank_typ == "mastercard":
                df_mc = parse_mastercard(pdf_path)
                mastercard_buchungen.append(df_mc)

            else:
                logger.warning(f"⚠️ Unbekannter Dateityp: {filename}")

    # ➔ Funktion zum Speichern
    def save_bookings(df_list, bank_name):
        if df_list:
            df = pd.concat(df_list, ignore_index=True)
            if "Datum" in df.columns:
                df["Datum"] = pd.to_datetime(df["Datum"], errors="coerce")
                df = df.dropna(subset=["Datum"])
                if not df.empty:
                    for jahr, group in df.groupby(df["Datum"].dt.year):
                        output_path = os.path.join(output_folder, f"buchungen_{bank_name}_{jahr}.csv")
                        group.to_csv(output_path, index=False)
                        logger.info(f"✅ {bank_name.capitalize()}-Buchungen für {jahr} gespeichert: {output_path}")

    # ➔ Speichern für beide Banktypen
    save_bookings(volksbank_buchungen, "volksbank")
    save_bookings(mastercard_buchungen, "mastercard")

if __name__ == "__main__":
    main()
