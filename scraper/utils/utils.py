# scraper/utils.py

import re
import unicodedata
import pandas as pd

def normalize_text(text):
    """Normalisiert Text auf Kleinbuchstaben, ASCII und entfernt Sonderzeichen."""
    text = str(text).lower()
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text.strip()

def detect_bank_typ(filename):
    """Erkennt anhand des Dateinamens den Banktyp (Volksbank, Mastercard oder Unbekannt)."""
    name = filename.lower()
    if "kontoauszug" in name or "volksbank" in name:
        return "volksbank"
    elif "kreditkarten-umsatzaufstellung" in name or "mastercard" in name:
        return "mastercard"
    else:
        return "unbekannt"

def extract_jahr_from_filename(filename):
    """Extrahiert das Jahr aus einem Dateinamen im Format 'vom_YYYY.MM.DD'."""
    jahr_match = re.search(r"vom_(\d{4})\.\d{2}\.\d{2}", filename)
    if jahr_match:
        return int(jahr_match.group(1))
    return pd.Timestamp.now().year  # Fallback: aktuelles Jahr

def map_company(verwendungszweck, mapping):
    """Mapped einen Verwendungszweck auf einen bekannten Anbieter oder 'Sonstiges'."""
    verwendungszweck = normalize_text(verwendungszweck)
    for anbieter, kategorie in mapping.items():
        if normalize_text(anbieter) in verwendungszweck:
            return kategorie
    return "Sonstiges"
