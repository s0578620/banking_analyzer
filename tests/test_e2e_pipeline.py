import os
import pandas as pd
import pytest
from unittest.mock import patch

from scraper.main import main as scraper_main
from scraper.processor.processor import process_file

@pytest.fixture
def dummy_input_folder(tmp_path):
    input_folder = tmp_path / "input"
    input_folder.mkdir(parents=True, exist_ok=True)

    # Dummy PDF anlegen (hier reicht Text, weil pdfplumber im Parser benutzt wird)
    dummy_pdf = input_folder / "kreditkarten-umsatzaufstellung_vom_2025.04.01.pdf"
    dummy_pdf.write_text("01.01. 02.01. Netflix 9,99")
    return input_folder

@pytest.fixture
def dummy_mapping(tmp_path):
    mapping_folder = tmp_path / "mapping"
    mapping_folder.mkdir(parents=True, exist_ok=True)
    (mapping_folder / "provider_mapping.json").write_text('{"netflix": "Streaming"}')
    return mapping_folder

@patch("scraper.utils.utils.extract_jahr_from_filename", return_value=2025)
@patch("scraper.parser.parser_mastercard.pdfplumber.open")
def test_e2e_pipeline(mock_pdfplumber_open, mock_extract_jahr, dummy_input_folder, tmp_path, dummy_mapping):
    class DummyPDF:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        @property
        def pages(self):
            class DummyPage:
                def extract_text(self): return "01.01. 02.01. Netflix 9,99"
            return [DummyPage()]

    mock_pdfplumber_open.return_value = DummyPDF()

    # Starte Parsing
    scraper_main(input_folder=str(dummy_input_folder))

    # Check parser_output
    parser_output_dir = os.path.join(os.path.dirname(__file__), "..", "output", "parser_output")
    parsed_files = [f for f in os.listdir(parser_output_dir) if f.endswith(".csv")]
    assert parsed_files, "Keine Parser-Output CSVs gefunden"

    parsed_path = os.path.join(parser_output_dir, parsed_files[0])
    parsed_df = pd.read_csv(parsed_path)

    assert not parsed_df.empty, "Parser Output ist leer"
    assert set(["Datum", "Verwendungszweck", "Betrag"]).issubset(parsed_df.columns)

    # Jetzt verarbeite
    process_file(parsed_path)

    # Check processed/
    processed_dir = os.path.join(os.path.dirname(__file__), "..", "output", "processed")
    processed_files = [f for f in os.listdir(processed_dir) if f.endswith(".csv")]
    assert processed_files, "Keine Processed-CSV gefunden"

    processed_path = os.path.join(processed_dir, processed_files[0])
    processed_df = pd.read_csv(processed_path)

    assert not processed_df.empty, "Processed Output ist leer"
    assert set(["Datum", "Betrag", "Provider", "Kategorie"]).issubset(processed_df.columns)
