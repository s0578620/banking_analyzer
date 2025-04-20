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
├── input/                 # Input folder for PDF files
│   └── *.pdf
│
├── output/                # Output folder for generated CSV files
│   └── transactions_*.csv
│
├── scraper/               # Main logic (Parser, Utilities, Main Script)
│   ├── __init__.py
│   ├── main.py
│   ├── parser_volksbank.py
│   ├── parser_mastercard.py
│   ├── utils.py
│   └── debug_reader.py
│
├── .venv/                 # (optional) Virtual environment
│
├── requirements.txt       # Dependencies
├── README.md              # This project description
└── .gitignore             # Files/Folders to ignore in Git
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
```bash
python -m scraper.main
```

# Development
```bash
  pip freeze > requirements.txt
```