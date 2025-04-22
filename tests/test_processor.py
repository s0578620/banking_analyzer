# tests/test_processor.py

import pandas as pd
import pytest
from scraper.processor.processor import map_verwendungszweck, extract_entgelt_and_create_new_rows

@pytest.fixture
def mapping_fixture():
    return {
        "Netflix": "Streaming",
        "Edeka": "Lebensmittel"
    }

def test_map_verwendungszweck_match(mapping_fixture):
    verwendungszweck = "Bezahlung Netflix Subscription"
    provider, kategorie = map_verwendungszweck(verwendungszweck, mapping_fixture)
    assert provider == "Netflix"
    assert kategorie == "Streaming"

def test_map_verwendungszweck_no_match(mapping_fixture):
    verwendungszweck = "Irgendwas anderes"
    provider, kategorie = map_verwendungszweck(verwendungszweck, mapping_fixture)
    assert provider == "Sonstiges"
    assert kategorie == "Sonstiges"

def test_extract_entgelt_and_create_new_rows():
    df = pd.DataFrame({
        'Datum': [pd.Timestamp('2025-04-22')],
        'Verwendungszweck': ['Auslandseinsatzentgelt 3,50'],
        'Betrag': [-50.00]
    })
    df_result = extract_entgelt_and_create_new_rows(df)
    assert len(df_result) == 2  # Original + neu erzeugte Zusatzzeile
    assert any(df_result['Verwendungszweck'] == "Auslandseinsatzentgelt")
