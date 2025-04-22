import re
import pandas as pd
from pdfminer.high_level import extract_text
from scraper.utils.utils import extract_jahr_from_filename
from scraper.utils.logger import setup_logger

logger = setup_logger(__name__)

def parse_volksbank(pdf_path):
    buchungen = []
    logger.info(f"\n🔨 parse_volksbank() wird aufgerufen für {pdf_path}")

    try:
        text = extract_text(pdf_path)
    except Exception as e:
        logger.warning(f"❌ Fehler beim Lesen von {pdf_path}: {e}")
        return pd.DataFrame()

    lines = text.splitlines()
    current_buchung = None

    # ➡️ Jahr direkt aus Dateinamen auslesen:
    jahr_from_filename = extract_jahr_from_filename(pdf_path)

    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = re.match(r"(\d{2}\.\d{2}\.)\s+(\d{2}\.\d{2}\.)\s+(.*?)\s+(\d{1,3}(?:\.\d{3})*,\d{2})\s+([SH])$", line)

        if match:
            if current_buchung:
                buchungen.append(current_buchung)

            datum_raw = match.group(1)
            verwendungszweck = match.group(3).strip()
            betrag_raw = match.group(4)
            soll_haben = match.group(5)

            betrag = float(betrag_raw.replace('.', '').replace(',', '.'))
            if soll_haben == 'S':
                betrag = -betrag

            # 📅 Datum verarbeiten:
            try:
                datum = pd.to_datetime(f"{datum_raw}{jahr_from_filename}", format="%d.%m.%Y", errors="coerce")
            except Exception:
                datum = pd.NaT

            current_buchung = {
                "Datum": datum,
                "Verwendungszweck": verwendungszweck,
                "Betrag": betrag
            }
        else:
            if current_buchung:
                current_buchung["Verwendungszweck"] += " " + line

    if current_buchung:
        buchungen.append(current_buchung)

    logger.info(f"✅ {len(buchungen)} Buchungen erfolgreich extrahiert!")
    return pd.DataFrame(buchungen)
