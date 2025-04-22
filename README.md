# 🏦 Bank Data Scraper


A simple Python tool for automatically reading bank documents 
(Volksbank account statements and Mastercard credit card statements) 
and saving the transactions as CSV files.
---
## ✨ Project Features
- 📄 Automatic processing of Volksbank and Mastercard PDFs
- 🏷️ Recognition of bank type based on the file name
- 🗓️ Automatic year assignment from the file name
- 🧹 Structured output as CSV files
- 🐛 Debugging mode for better traceability during parsing
- 📦 Clear project structure and modular codebase
---

## 🗂️ Project Structure

```plaintext
bankdaten_scraper/
│
├── input/                        # Input folder for PDF files
│
├── output/                       # Output folder
│   ├── parser_output/            # Raw CSV output after parsing
│   └── processed/                # Final processed & categorized CSVs
│
├── mapping/                      # Mapping configuration (provider_mapping.json)
│
├── logs/                         # Log files generated during processing
│
├── scraper/                      # Main logic (parsers, processors, tools, utils)
│   ├── main.py                   # Entry point for parsing PDFs
│   ├── parser/                   # Parser for Volksbank and Mastercard
│   ├── processor/                # Processing and categorizing transactions
│   ├── tools/                    # Developer tools (debugging, checks)
│   └── utils/                    # Helper functions (logging, warnings)
│
├── .venv/                        # (optional) Virtual environment
│
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
└── .gitignore                    # Files/folders to ignore in Git

```
# ⚙️ Setup
![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
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
  streamlit run visualizer.py
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