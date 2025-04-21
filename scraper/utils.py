# scraper/utils.py
import re
import unicodedata

def normalize_text(text):
    text = str(text).lower()
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text.strip()

def detect_bank_typ(filename):
    name = filename.lower()
    if "kontoauszug" in name or "volksbank" in name:
        return "volksbank"
    elif "kreditkarten-umsatzaufstellung" in name or "mastercard" in name:
        return "mastercard"
    else:
        return "unbekannt"

def extract_year_from_filename(filename):
    matches = re.findall(r'(?:^|[^0-9])(20\d{2})(?:[^0-9]|$)', filename)
    if matches:
        jahr = int(matches[0])
        if 2000 <= jahr <= 2100:
            return jahr
    return None

def map_company(verwendungszweck, mapping):
    verwendungszweck = verwendungszweck.lower()
    for anbieter, kategorie in mapping.items():
        if anbieter.lower() in verwendungszweck:
            return kategorie
    return "Sonstiges"
