
# 📄 Bankdaten Scraper

Ein Python-Tool zum automatisierten Auslesen von Konto- und Kreditkartenabrechnungen (PDFs).

## Installation
```bash
    python -m venv .venv
    source .venv/bin/activate   # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
```

## Benutzung
PDFs in `data/` ablegen, dann:
```bash
    python -m scraper.main
```
Excel-Dateien werden unter `output/` gespeichert.

---

