import pytest
import pandas as pd
from scraper.processor.processor import map_verwendungszweck

@pytest.fixture
def sample_mapping():
    return {
        "Netflix": "Entertainment",
        "Rewe": "Lebensmittel"
    }

def test_map_verwendungszweck_exact_match(sample_mapping):
    provider, category = map_verwendungszweck("Rewe Supermarkt", sample_mapping)
    assert provider == "Rewe"
    assert category == "Lebensmittel"

def test_map_verwendungszweck_no_match(sample_mapping):
    provider, category = map_verwendungszweck("Unbekannter Shop", sample_mapping)
    assert provider == "Sonstiges"
    assert category == "Sonstiges"
