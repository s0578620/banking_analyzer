# scraper/tools/debug_reader.py
import os
import pdfplumber
from scraper.utils.logger import setup_logger

logger = setup_logger(__name__)

input_folder = os.path.join(os.path.dirname(__file__), "..", "..", "input")

def debug_zeige_rohtext(pdf_path, max_seiten=1):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, seite in enumerate(pdf.pages):
                if i >= max_seiten:
                    break
                text = seite.extract_text()
                logger.info(f"\n--- Seite {i+1} ---\n{text[:1500]}\n--- Ende Seite ---")
    except Exception as e:
        logger.error(f"❌ Fehler beim Lesen von {pdf_path}: {e}")

def main():
    logger.info("=== DEBUG MODUS: Lese Rohtext aus PDFs ===")

    for filename in os.listdir(input_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_folder, filename)
            logger.info(f"📄 Datei: {filename}")
            debug_zeige_rohtext(pdf_path)

    logger.info("✅ Fertig. Jetzt können wir den Parser anpassen!")

if __name__ == "__main__":
    main()
