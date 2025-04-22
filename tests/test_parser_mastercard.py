
from scraper.parser import parser_mastercard

def test_parse_mastercard_returns_dataframe(monkeypatch):
    class DummyPDF:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        @property
        def pages(self):
            class DummyPage:
                def extract_text(self):
                    return (
                        "Buchungs-Beleg-Nummer\n"
                        "01.01.   02.01.   Netflix   9,99"
                    )
            return [DummyPage()]

    monkeypatch.setattr(parser_mastercard.pdfplumber, "open", lambda _: DummyPDF())
    df = parser_mastercard.parse_mastercard("dummy_path.pdf")
    assert not df.empty
    assert "Netflix" in df.iloc[0]["Verwendungszweck"]
    assert df.iloc[0]["Betrag"] == 9.99
