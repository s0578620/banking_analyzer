import pytest
from scraper.parser import parser_volksbank

def test_parse_volksbank(monkeypatch):
    dummy_text = "01.01. 02.01. Amazon Bestellung 49,99 S"

    monkeypatch.setattr(parser_volksbank, "extract_text", lambda _: dummy_text)

    df = parser_volksbank.parse_volksbank("dummy_path.pdf")
    assert not df.empty
    assert set(df.columns) == {"Datum", "Verwendungszweck", "Betrag"}
    assert df.iloc[0]["Verwendungszweck"].startswith("Amazon")
    assert df.iloc[0]["Betrag"] < 0  # Soll-Buchung (S = negativ)
