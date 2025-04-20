# scraper/main.py
import os
import pandas as pd
from scraper.parser_volksbank import parse_volksbank
from scraper.parser_mastercard import parse_mastercard
from scraper.utils import detect_bank_typ, extract_year_from_filename

def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    input_folder = os.path.join(BASE_DIR, "..", "input")
    output_folder = os.path.join(BASE_DIR, "..", "output")

    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    volksbank_buchungen = []
    mastercard_buchungen = []

    for filename in os.listdir(input_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_folder, filename)
            print(f"📄 Verarbeite {filename}...")

            bank_typ = detect_bank_typ(filename)
            jahr = extract_year_from_filename(filename)

            if bank_typ == "volksbank":
                buchungen = parse_volksbank(pdf_path, jahr)
                for buchung in buchungen:
                    buchung["Jahr"] = jahr
                volksbank_buchungen.extend(buchungen)

            elif bank_typ == "mastercard":
                buchungen = parse_mastercard(pdf_path)
                for buchung in buchungen.to_dict(orient="records"):
                    buchung["Jahr"] = jahr
                mastercard_buchungen.extend(buchungen.to_dict(orient="records"))

            else:
                print(f"⚠️ Unbekannter Dateityp: {filename}")

    if not volksbank_buchungen and not mastercard_buchungen:
        print("❗ Keine Buchungen gefunden.")
        return

    # Speichern Volksbank
    if volksbank_buchungen:
        df_vb = pd.DataFrame(volksbank_buchungen)
        df_vb["Datum"] = pd.to_datetime(df_vb["Datum"], dayfirst=True, errors="coerce")
        df_vb = df_vb.dropna(subset=["Datum"])

        jahr_vb = df_vb["Jahr"].iloc[0] if "Jahr" in df_vb.columns else "unbekannt"
        output_path_vb = os.path.join(output_folder, f"buchungen_volksbank_{jahr_vb}.csv")
        df_vb.to_csv(output_path_vb, index=False)
        print(f"✅ Volksbank-Buchungen gespeichert: {output_path_vb}")

    # Speichern Mastercard
    if mastercard_buchungen:
        df_mc = pd.DataFrame(mastercard_buchungen)
        df_mc["Datum"] = pd.to_datetime(df_mc["Datum"], dayfirst=True, errors="coerce")
        df_mc = df_mc.dropna(subset=["Datum"])

        jahr_mc = df_mc["Jahr"].iloc[0] if "Jahr" in df_mc.columns else "unbekannt"
        output_path_mc = os.path.join(output_folder, f"buchungen_mastercard_{jahr_mc}.csv")
        df_mc.to_csv(output_path_mc, index=False)
        print(f"✅ Mastercard-Buchungen gespeichert: {output_path_mc}")

if __name__ == "__main__":
    main()