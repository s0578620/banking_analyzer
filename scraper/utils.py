# scraper/utils.py
import re

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
