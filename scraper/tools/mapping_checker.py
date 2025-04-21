# scraper/tools/mapping_checker.py

import os
import pandas as pd
from scraper.utils.logger import setup_logger
from scraper.processor.processor import load_mapping
from scraper.utils.utils import normalize_text

logger = setup_logger(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
INPUT_FOLDER = os.path.join(BASE_DIR, "output", "parser_output")

def check_mappings():
    mapping = load_mapping()
    known_providers = [normalize_text(k) for k in mapping.keys()]

    unmatched = set()

    for filename in os.listdir(INPUT_FOLDER):
        if filename.endswith(".csv"):
            df = pd.read_csv(os.path.join(INPUT_FOLDER, filename))
            for vz in df["Verwendungszweck"].dropna():
                vz_norm = normalize_text(vz)
                if not any(provider in vz_norm for provider in known_providers):
                    unmatched.add(vz)

    if unmatched:
        logger.warning("❌ Nicht zugeordnete Verwendungszwecke gefunden:")
        for vz in unmatched:
            logger.warning(f" - {vz}")
    else:
        logger.info("✅ Alle Verwendungszwecke korrekt zugeordnet.")

if __name__ == "__main__":
    check_mappings()
