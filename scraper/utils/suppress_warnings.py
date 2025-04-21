# scraper/suppress_warnings.py
import warnings
import logging

def suppress_warnings():
    warnings.filterwarnings("ignore", category=UserWarning, module="pdfminer")

    logging.getLogger("pdfminer").setLevel(logging.ERROR)
    logging.getLogger("pdfplumber").setLevel(logging.ERROR)
