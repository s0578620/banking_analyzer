# scraper/debug_reader.py
import os
import pdfplumber

# === Einstellungen ===
input_folder = "input/"

# === Debug-Funktion: Zeigt Rohtext aus PDFs ===
def debug_zeige_rohtext(pdf_path, max_seiten=1):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, seite in enumerate(pdf.pages):
                if i >= max_seiten:
                    break
                text = seite.extract_text()
                print(f"\n--- Seite {i+1} ---\n")
                print(text[:1500])  # Nur die ersten 1500 Zeichen pro Seite zeigen
                print("\n--- Ende Seite ---\n")
    except Exception as e:
        print(f"❌ Fehler beim Lesen von {pdf_path}: {e}")


def main():
    print("\n=== DEBUG MODUS: Lese Rohtext aus PDFs ===\n")

    for filename in os.listdir(input_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_folder, filename)
            print(f"📄 Datei: {filename}")
            debug_zeige_rohtext(pdf_path)

    print("\n✅ Fertig. Jetzt können wir den Parser anpassen!")


if __name__ == "__main__":
    main()