import pytest
from scraper.utils.utils import normalize_text, detect_bank_typ, extract_jahr_from_filename

def test_normalize_text():
    assert normalize_text("München!") == "munchen"
    assert normalize_text(" Café ") == "cafe"

def test_detect_bank_typ():
    assert detect_bank_typ("kontoauszug_2024.pdf") == "volksbank"
    assert detect_bank_typ("kreditkarten-umsatzaufstellung_mastercard.pdf") == "mastercard"
    assert detect_bank_typ("irgendwas.pdf") == "unbekannt"

def test_extract_jahr_from_filename():
    assert extract_jahr_from_filename("umsatz_vom_2023.04.25.pdf") == 2023
