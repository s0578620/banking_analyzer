# scraper/parser_volksbank.py
import re
import pandas as pd
from pdfminer.high_level import extract_text

def parse_volksbank(pdf_path):
    buchungen = []
    print(f"\n🔨 parse_volksbank() wird aufgerufen für {pdf_path}")

    try:
        text = extract_text(pdf_path)
    except Exception as e:
        print(f"❌ Fehler beim Lesen von {pdf_path}: {e}")
        return pd.DataFrame()

    lines = text.splitlines()
    current_buchung = None

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

            # 📅 Datum reparieren und Jahr bestimmen:
            parts = datum_raw.rstrip('.').split('.')
            day = int(parts[0])
            month = int(parts[1])

            if month == 12:
                jahr = 2024
            elif month == 1:
                jahr = 2025
            else:
                jahr = 2024

            datum = pd.to_datetime(f"{day}.{month}.{jahr}", format="%d.%m.%Y", errors="coerce")

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

    print(f"✅ {len(buchungen)} Buchungen erfolgreich extrahiert!")
    return pd.DataFrame(buchungen)
