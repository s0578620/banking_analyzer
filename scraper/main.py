# scraper/main.py
import os
import pandas as pd
from parser_volksbank import parse_volksbank
from parser_mastercard import parse_mastercard
from utils import detect_bank_typ
from suppress_warnings import suppress_warnings

suppress_warnings()


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
            print(f"\n📄 Verarbeite {filename}...")

            bank_typ = detect_bank_typ(filename)

            if bank_typ == "volksbank":
                df_vb = parse_volksbank(pdf_path)
                volksbank_buchungen.append(df_vb)

            elif bank_typ == "mastercard":
                df_mc = parse_mastercard(pdf_path)
                mastercard_buchungen.append(df_mc)

            else:
                print(f"⚠️ Unbekannter Dateityp: {filename}")

    # Speichern Volksbank
    if volksbank_buchungen:
        df_vb = pd.concat(volksbank_buchungen, ignore_index=True)
        df_vb = df_vb.dropna(subset=["Datum"])

        for jahr, group in df_vb.groupby(df_vb["Datum"].dt.year):
            output_path = os.path.join(output_folder, f"buchungen_volksbank_{jahr}.csv")
            group.to_csv(output_path, index=False)
            print(f"✅ Volksbank-Buchungen für {jahr} gespeichert: {output_path}")

    # Speichern Mastercard
    if mastercard_buchungen:
        df_mc = pd.concat(mastercard_buchungen, ignore_index=True)
        df_mc = df_mc.dropna(subset=["Datum"])

        for jahr, group in df_mc.groupby(df_mc["Datum"].dt.year):
            output_path = os.path.join(output_folder, f"buchungen_mastercard_{jahr}.csv")
            group.to_csv(output_path, index=False)
            print(f"✅ Mastercard-Buchungen für {jahr} gespeichert: {output_path}")

if __name__ == "__main__":
    main()
