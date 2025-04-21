import os
import json
import pandas as pd
from utils import map_company

def load_mapping(mapping_path):
    if not os.path.exists(mapping_path):
        return {}
    with open(mapping_path, "r", encoding="utf-8") as f:
        return json.load(f)

def scan_new_anbieter(output_folder, mapping):
    unknown_anbieter = set()

    # Suche alle CSVs durch
    for filename in os.listdir(output_folder):
        if filename.endswith(".csv"):
            file_path = os.path.join(output_folder, filename)
            df = pd.read_csv(file_path)

            if "Verwendungszweck" not in df.columns:
                continue  # Skip wenn keine Verwendungszweck-Spalte

            for verwendungszweck in df["Verwendungszweck"].dropna():
                verwendungszweck = str(verwendungszweck)
                if map_company(verwendungszweck, mapping) == "Sonstiges":
                    unknown_anbieter.add(verwendungszweck)

    return unknown_anbieter

def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    output_folder = os.path.join(BASE_DIR, "..", "output")
    mapping_path = os.path.join(BASE_DIR, "..", "provider_mapping.json")

    mapping = load_mapping(mapping_path)

    print("🔎 Scanne Buchungen auf unbekannte Anbieter...")

    unknown_anbieter = scan_new_anbieter(output_folder, mapping)

    if unknown_anbieter:
        print("\n🚨 Unbekannte Anbieter gefunden:")
        for anbieter in sorted(unknown_anbieter):
            print(f" - {anbieter}")
    else:
        print("\n✅ Alle Buchungen sind bekannten Anbietern zugeordnet!")

if __name__ == "__main__":
    main()
