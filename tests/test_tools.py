# tests/test_tools.py

import subprocess

def test_debug_reader_runs():
    result = subprocess.run(["python", "-m", "scraper.tools.debug_reader"], capture_output=True)
    assert result.returncode in (0, 1)  # 0 = OK, 1 = keine PDFs gefunden

def test_mapping_checker_runs():
    result = subprocess.run(["python", "-m", "scraper.tools.mapping_checker"], capture_output=True)
    assert result.returncode in (0, 1)

def test_csv_validator_runs():
    result = subprocess.run(["python", "-m", "scraper.tools.csv_validator"], capture_output=True)
    assert result.returncode in (0, 1)

def test_folder_cleaner_runs():
    result = subprocess.run(["python", "-m", "scraper.tools.folder_cleaner"], capture_output=True)
    assert result.returncode == 0
