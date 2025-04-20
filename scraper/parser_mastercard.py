# scraper/parser_mastercard.py
import re
import pandas as pd
import pdfplumber

def parse_mastercard(pdf_path):
    print(f"🛠️ parse_mastercard() wird aufgerufen für {pdf_path}")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"❌ Fehler beim Lesen von {pdf_path}: {e}")
        return pd.DataFrame()

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    buchungen = []
    current = None
    start_parsing = False

    for idx, line in enumerate(lines):
        print(f"[{idx}] Zeile: {line}")

        # Warten bis Buchungsbereich startet
        if not start_parsing:
            if "Buchungs-Beleg-" in line:
                print(f"🚀 Starte Buchungsbereich bei Zeile [{idx}]")
                start_parsing = True
            continue

        # Stoppen wenn Dokument-Ende erreicht
        if "Seite:" in line or "Zwischensaldo" in line:
            print(f"🛑 Stoppe Parsing bei Zeile [{idx}] wegen Stoppwort: {line}")
            break

        # Versuchen Buchung zu erkennen
        match = re.match(r"(\d{2}\.\d{2}\.)\s+(\d{2}\.\d{2}\.)\s+(.*)\s+(\d{1,3}(?:\.\d{3})*,\d{2})([+-])$", line)

        if match:
            if current:
                print(f"✅ Speichere Buchung: {current}")
                buchungen.append(current)

            datum_buchung = match.group(1)
            belegdatum = match.group(2)
            verwendungszweck = match.group(3).strip()
            betrag_raw = match.group(4)
            vorzeichen = match.group(5)

            betrag = float(betrag_raw.replace(".", "").replace(",", "."))
            if vorzeichen == "-":
                betrag = -betrag

            current = {
                "Datum": datum_buchung,
                "Belegdatum": belegdatum,
                "Verwendungszweck": verwendungszweck,
                "Betrag": betrag
            }

            print(f"🛠️ Neue Buchung begonnen: {current}")
        else:
            # Zusatzzeilen (z.B. Mobil bezahlter Umsatz) anhängen
            if current:
                print(f"➕ Zusatz zu [{current['Datum']}]: {line}")
                current["Verwendungszweck"] += " " + line.strip()

    # Letzte Buchung speichern
    if current:
        print(f"✅ Speichere letzte Buchung: {current}")
        buchungen.append(current)

    print(f"✅ Insgesamt {len(buchungen)} Mastercard-Buchungen extrahiert!")

    # Ins DataFrame umwandeln
    df = pd.DataFrame(buchungen)

    # Wenn Daten vorhanden sind: Datum ergänzen + konvertieren
    if not df.empty:
        # Jahr ergänzen
        df["Datum"] = df["Datum"].str.replace(r"\.$", ".2024", regex=True)
        df["Belegdatum"] = df["Belegdatum"].str.replace(r"\.$", ".2024", regex=True)

        # In datetime umwandeln
        df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")
        df["Belegdatum"] = pd.to_datetime(df["Belegdatum"], format="%d.%m.%Y", errors="coerce")

    print(df.head())

    return df
