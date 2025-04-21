# scraper/tools/folder_cleaner.py

import os
from scraper.utils.logger import setup_logger

logger = setup_logger(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
FOLDERS_TO_CLEAN = [
    os.path.join(BASE_DIR, "output", "parser_output"),
    os.path.join(BASE_DIR, "output", "processed"),
]

def clean_folders():
    for folder in FOLDERS_TO_CLEAN:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    os.remove(file_path)
                    logger.info(f"🧹 Gelöscht: {file_path}")
                except Exception as e:
                    logger.error(f"⚠️ Fehler beim Löschen {file_path}: {e}")
        else:
            logger.warning(f"⚠️ Ordner existiert nicht: {folder}")

if __name__ == "__main__":
    clean_folders()
