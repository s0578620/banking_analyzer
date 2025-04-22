# scraper/parser/parser_mastercard.py
import re
import pandas as pd
import pdfplumber
from scraper.utils.utils import extract_jahr_from_filename
from scraper.utils.logger import setup_logger
from scraper.utils.utils import create_empty_transaction_dataframe

logger = setup_logger(__name__)

def parse_mastercard(pdf_path):
    logger.info(f"\n🔨 parse_mastercard() wird aufgerufen für {pdf_path}")

    buchungen = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception as e:
        logger.warning(f"❌ Fehler beim Lesen von {pdf_path}: {e}")
        return pd.DataFrame()

    jahr = extract_jahr_from_filename(pdf_path)

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # Mastercard-Buchungserkennung
    pattern = re.compile(
        r"(\d{2}\.\d{2}\.)\s+(\d{2}\.\d{2}\.)\s+(.*?)\s+(\d{1,3}(?:\.\d{3})*,\d{2})([+-])?$"
    )

    current = None
    start_parsing = False

    for idx, line in enumerate(lines):
        if not start_parsing:
            if "Buchungs-Beleg-" in line or "Umsatzaufstellung" in line:
                start_parsing = True
            continue

        if "Seite:" in line or "Zwischensaldo" in line:
            break

        match = pattern.match(line)
        if match:
            if current:
                buchungen.append(current)

            datum_buchung = match.group(1)
            belegdatum = match.group(2)
            verwendungszweck = match.group(3).strip()
            betrag_raw = match.group(4)
            vorzeichen = match.group(5) if match.group(5) else "+"

            # Betrag verarbeiten
            betrag = float(betrag_raw.replace('.', '').replace(',', '.'))
            if vorzeichen == "-":
                betrag = -betrag

            # Datum verarbeiten
            try:
                datum = pd.to_datetime(f"{datum_buchung}{jahr}", format="%d.%m.%Y", errors="coerce")
            except Exception:
                datum = pd.NaT

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
    if not buchungen:
        return create_empty_transaction_dataframe()
    return pd.DataFrame(buchungen)

