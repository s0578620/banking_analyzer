# scraper/parser_mastercard.py
import re
import pandas as pd
import pdfplumber
from scraper.utils.logger import setup_logger
logger = setup_logger(__name__)

def parse_mastercard(pdf_path):
    logger.info(f"\n🔨 parse_mastercard() wird aufgerufen für {pdf_path}")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        logger.warning(f"❌ Fehler beim Lesen von {pdf_path}: {e}")
        return pd.DataFrame()

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    buchungen = []
    current = None
    start_parsing = False

    for idx, line in enumerate(lines):
        if not start_parsing:
            if "Buchungs-Beleg-" in line:
                start_parsing = True
            continue

        if "Seite:" in line or "Zwischensaldo" in line:
            break

        match = re.match(r"(\d{2}\.\d{2}\.)\s+(\d{2}\.\d{2}\.)\s+(.*?)\s+(\d{1,3}(?:\.\d{3})*,\d{2})([+-])$", line)

        if match:
            if current:
                buchungen.append(current)

            datum_buchung = match.group(1)
            belegdatum = match.group(2)
            verwendungszweck = match.group(3).strip()
            betrag_raw = match.group(4)
            vorzeichen = match.group(5)

            betrag = float(betrag_raw.replace('.', '').replace(',', '.'))
            if vorzeichen == "-":
                betrag = -betrag

            parts = datum_buchung.rstrip('.').split('.')
            day = int(parts[0])
            month = int(parts[1])

            if month == 12:
                jahr = 2024
            elif month == 1:
                jahr = 2025
            else:
                jahr = 2024

            datum = pd.to_datetime(f"{day}.{month}.{jahr}", format="%d.%m.%Y", errors="coerce")

            current = {
                "Datum": datum,
                "Verwendungszweck": verwendungszweck,
                "Betrag": betrag
            }
        else:
            if current:
                current["Verwendungszweck"] += " " + line

    if current:
        buchungen.append(current)

    logger.info(f"✅ Insgesamt {len(buchungen)} Mastercard-Buchungen extrahiert!")
    return pd.DataFrame(buchungen)
