import os
import pandas as pd
import pytest
from unittest.mock import patch
import shutil

@pytest.fixture
def dummy_input_folder(tmp_path):
    input_folder = tmp_path / "input"
    input_folder.mkdir(parents=True, exist_ok=True)

    dummy_pdf = input_folder / "kreditkarten-umsatzaufstellung_vom_2025.04.01.pdf"
    dummy_pdf.write_text("01.01. 02.01. Netflix 9,99")
    return input_folder

@pytest.fixture
def dummy_mapping(tmp_path):
    mapping_folder = tmp_path / "mapping"
    mapping_folder.mkdir(parents=True, exist_ok=True)
    (mapping_folder / "provider_mapping.json").write_text('{"netflix": "Streaming"}')
    return mapping_folder

@patch("scraper.main.parse_mastercard")
@patch("scraper.utils.utils.extract_jahr_from_filename", return_value=2025)
@patch("scraper.parser.parser_mastercard.pdfplumber.open")
def test_e2e_pipeline(mock_pdfplumber_open, mock_extract_jahr, mock_parse_mastercard, dummy_input_folder, tmp_path, dummy_mapping):
    from scraper.main import main as scraper_main

    class DummyPDF:
        def __enter__(self): return self
        def __exit__(self, *args): pass

        @property
        def pages(self):
            class DummyPage:
                def extract_text(self):
                    return (
                        "01.01.24 02.01.24 NETFLIX.COM 9,99\n"
                        "02.01.24 03.01.24 AMAZON.DE 19,99\n"
                    )
            return [DummyPage()]

    mock_pdfplumber_open.return_value = DummyPDF()

    mock_parse_mastercard.return_value = pd.DataFrame([
        {"Datum": pd.to_datetime("2025-01-02"), "Verwendungszweck": "NETFLIX.COM", "Betrag": 9.99},
        {"Datum": pd.to_datetime("2025-02-03"), "Verwendungszweck": "AMAZON.DE", "Betrag": 19.99},
    ])

    parser_output_dir = tmp_path / "parser_output"
    parser_output_dir.mkdir()

    try:
        scraper_main(input_folder=str(dummy_input_folder), output_folder=str(parser_output_dir))

        # Check CSV-Dateien vorhanden
        parsed_files = list(parser_output_dir.glob("*.csv"))
        assert parsed_files, "❌ Keine Parser-Output CSVs gefunden!"

        # Zusätzlich: Inhalt prüfen
        df = pd.read_csv(parsed_files[0])
        assert "NETFLIX.COM" in df["Verwendungszweck"].values
        assert "AMAZON.DE" in df["Verwendungszweck"].values

    finally:
        # Aufräumen: Parser-Output löschen, falls erzeugt
        if parser_output_dir.exists():
            shutil.rmtree(parser_output_dir)
