# tests/test_main.py

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import os

@pytest.fixture
def setup_input_folder(tmp_path, monkeypatch):
    # Simuliere die Ordnerstruktur: /somepath/src/ (main.py liegt hier) und daneben /input/
    src_folder = tmp_path / "src"
    input_folder = tmp_path / "input"
    src_folder.mkdir()
    input_folder.mkdir()

    dummy_file = input_folder / "kontoauszug_vom_2025.04.01.pdf"
    dummy_file.write_text("Dummy Inhalt")

    # Mock BASE_DIR => src_folder
    monkeypatch.setattr("scraper.main.os.path.abspath", lambda _: str(src_folder / "main.py"))

    return dummy_file

@patch("scraper.main.parse_volksbank")
@patch("scraper.main.parse_mastercard")
def test_main_parses_files(mock_parse_mastercard, mock_parse_volksbank, setup_input_folder):
    from scraper.main import main

    mock_parse_volksbank.return_value = pd.DataFrame([
        {"Datum": pd.to_datetime("2025-04-01"), "Verwendungszweck": "Test", "Betrag": 10.0}
    ])

    mock_parse_mastercard.return_value = pd.DataFrame(columns=["Datum", "Betrag", "Verwendungszweck"])
    main()

    mock_parse_volksbank.assert_called_once()
    mock_parse_mastercard.assert_not_called()

@patch("scraper.main.parse_volksbank")
@patch("scraper.main.parse_mastercard")
def test_main_handles_no_files(mock_parse_mastercard, mock_parse_volksbank, tmp_path, monkeypatch):
    src_folder = tmp_path / "src"
    src_folder.mkdir()

    # Kein input-Ordner

    monkeypatch.setattr("scraper.main.os.path.abspath", lambda _: str(src_folder / "main.py"))

    from scraper.main import main

    main()

    mock_parse_volksbank.assert_not_called()
    mock_parse_mastercard.assert_not_called()
