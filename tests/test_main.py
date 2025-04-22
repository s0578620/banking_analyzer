# tests/test_main.py

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import os

@pytest.fixture
def setup_input_folder(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "parser_output"
    input_folder.mkdir()
    output_folder.mkdir()

    dummy_file = input_folder / "kontoauszug_vom_2025.04.01.pdf"
    dummy_file.write_text("Dummy Inhalt")

    return input_folder, output_folder

@patch("scraper.main.parse_volksbank")
@patch("scraper.main.parse_mastercard")
def test_main_parses_files(mock_parse_mastercard, mock_parse_volksbank, setup_input_folder):
    from scraper.main import main

    input_folder, output_folder = setup_input_folder

    mock_parse_volksbank.return_value = pd.DataFrame([
        {"Datum": pd.to_datetime("2025-04-01"), "Verwendungszweck": "Test", "Betrag": 10.0}
    ])
    mock_parse_mastercard.return_value = pd.DataFrame(columns=["Datum", "Betrag", "Verwendungszweck"])

    main(input_folder=str(input_folder), output_folder=str(output_folder))

    mock_parse_volksbank.assert_called_once()
    mock_parse_mastercard.assert_not_called()

@patch("scraper.main.parse_volksbank")
@patch("scraper.main.parse_mastercard")
def test_main_handles_no_files(mock_parse_mastercard, mock_parse_volksbank, tmp_path):
    from scraper.main import main

    input_folder = tmp_path / "input"
    output_folder = tmp_path / "parser_output"
    input_folder.mkdir()
    output_folder.mkdir()

    # Keine PDFs drin → main() sollte nichts parsen

    main(input_folder=str(input_folder), output_folder=str(output_folder))

    mock_parse_volksbank.assert_not_called()
    mock_parse_mastercard.assert_not_called()
