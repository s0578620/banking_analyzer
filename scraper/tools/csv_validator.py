# scraper/tools/csv_validator.py

import os
import pandas as pd
from scraper.utils.logger import setup_logger

logger = setup_logger(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
INPUT_FOLDER = os.path.join(BASE_DIR, "output", "processed")

REQUIRED_COLUMNS = ["Datum", "Betrag", "Provider", "Kategorie"]

def validate_csvs():
    for filename in os.listdir(INPUT_FOLDER):
        if filename.endswith(".csv"):
            path = os.path.join(INPUT_FOLDER, filename)
            df = pd.read_csv(path)

            missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
            if missing_cols:
                logger.error(f"❌ {filename}: Fehlende Spalten: {missing_cols}")
            else:
                logger.info(f"✅ {filename}: Alle Spalten vorhanden.")

if __name__ == "__main__":
    validate_csvs()
