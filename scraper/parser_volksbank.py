# scraper/parser_volksbank.py
import re
from pdfminer.high_level import extract_text

def parse_volksbank(pdf_path, jahr):
    buchungen = []
    print(f"🛠️ parse_volksbank() wird aufgerufen für {pdf_path}")

    try:
        text = extract_text(pdf_path)
    except Exception as e:
        print(f"❌ Fehler beim Lesen von {pdf_path}: {e}")
        return buchungen

    lines = text.splitlines()
    current_buchung = None

    for line in lines:
        line = line.strip()
        if not line:
            continue  # Leere Zeile überspringen

        # Neue Buchung erkennen
        match = re.match(
            r"(\d{2}\.\d{2}\.)\s+(\d{2}\.\d{2}\.)\s+(.*)\s+(\d{1,3}(?:\.\d{3})*,\d{2})\s+([SH])$",
            line
        )
        if match:
            # Alte Buchung abschließen
            if current_buchung:
                buchungen.append(current_buchung)

            datum = f"{match.group(1)}{jahr}"  # statt nur match.group(1)
            wertstellung = match.group(2)
            verwendungszweck = match.group(3).strip()
            betrag = float(match.group(4).replace('.', '').replace(',', '.'))
            soll_haben = match.group(5)

            if soll_haben == 'S':
                betrag = -betrag

            current_buchung = {
                "Datum": datum,
                "Wertstellung": wertstellung,
                "Verwendungszweck": verwendungszweck,
                "Betrag": betrag
            }
        else:
            # Zusatzzeile anhängen, wenn aktuelle Buchung existiert
            if current_buchung:
                current_buchung["Verwendungszweck"] += " " + line

    # Letzte Buchung speichern
    if current_buchung:
        buchungen.append(current_buchung)

    print(f"✅ {len(buchungen)} Buchungen erfolgreich extrahiert!")
    return buchungen
