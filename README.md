![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![Python Tests](https://github.com/s0578620/banking_analyzer/actions/workflows/python-tests.yml/badge.svg)

# 🏦 Bank Data Scraper


A simple Python tool for automatically reading bank documents
(Volksbank account statements and Mastercard credit card statements)
and saving the transactions as CSV files, including powerful visual analytics.
---
## ✨ Project Features
- 📄 Automatic processing of Volksbank and Mastercard PDFs
- 🏷️ Recognition of bank type based on the file name
- 🗓️ Automatic year assignment from the file name
- 🧹 Structured output as CSV files
- 🐛 Debugging mode for better traceability during parsing
- 🧠 Intelligent mapping of transactions to providers and categories
- 📊 Visual analysis via Streamlit dashboards (Cashflow, Top Provider, Category Analysis, Heatmap)
- 📦 Clear project structure and modular codebase
---

## 🗂️ Project Structure

```plaintext
bankdaten_scraper/
│
├── .github/                    # Folder for GitHub Workflows (e.g., CI/CD pipelines)
│
├── input/                      # Folder for incoming PDF files
├── logs/                       # Log files generated during execution
├── mapping/                    # provider_mapping.json for mapping companies to categories
│
├── output/                     
│   ├── parser_output/          # Raw parsed CSVs (not yet mapped)
│   └── processed/              # Final categorized and cleaned CSVs
│
├── scraper/                    
│   ├── parser/                 # Different PDF parsers (Mastercard, Volksbank)
│   ├── processor/              # Post-processing and mapping logic
│   ├── tools/                  # Developer tools (debugging, validation, cleaning)
│   ├── utils/                  # Utility functions (logger, warnings suppression, normalizers)
│   └── main.py                 # Main script for parsing PDFs
│
├── tests/                      # Pytest structure for automated testing
│   ├── dummy_data/             # Dummy data for testing purposes
│   ├── conftest.py             # Global pytest configurations and fixtures
│   ├── test_parser_mastercard.py
│   ├── test_parser_volksbank.py
│   ├── test_processor.py
│   └── test_utils.py
│
├── .gitignore                  # Ignored files and folders for Git
├── launcher.py                 # Script to automate parsing and processing steps
├── pytest.ini                  # Pytest configuration file
├── README.md                   # Project documentation (recently updated ✨)
├── requirements.txt            # Project dependencies (for production)
├── requirements-dev.txt        # Developer dependencies (testing, linting, etc.)
├── visualizer_pro.py           # Streamlit dashboard for powerful visualization


```
# ⚙️ Setup
1. Create a virtual environmen
```bash
  python -m venv .venv
```
2. Activate the virtual environment (Windows CMD)
```bash
  .venv\Scripts\activate
```
2. Activate the virtual environment (Windows PowerShell)
```bash
  .\.venv\Scripts\Activate.ps1
```
3. Install dependencies
```bash
  pip install -r requirements.txt
```
# Start
Parse PDFs from the input/ folder and generate CSV files:
```bash
  python -m scraper.main
```
Process and map parsed CSVs:
```bash
  python -m scraper.processor.processor
```
Auto-Process
```bash
  python launcher.py
```
Visualizer
```bash
  streamlit run visualizer_pro.py
```
# Developer Tools
Debug: Read raw text from PDFs (for parser development)
```bash
  python -m scraper.tools.debug_reader
```
Check if all transactions have valid mapping:
```bash
  python -m scraper.tools.mapping_checker
```
Validate final processed CSVs for missing columns:
```bash
  python -m scraper.tools.csv_validator
```
Clean output folders (parser_output/ and processed/):
```bash
  python -m scraper.tools.folder_cleaner
```
# Development Utilities
```bash
  pip freeze > requirements.txt
```
Tests + Coverage in Terminal
```bash
python -m pytest --cov=scraper --cov-report=term-missing
```