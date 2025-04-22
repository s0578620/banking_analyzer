import pytest

@pytest.fixture
def sample_mapping():
    return {
        "Netflix": "Entertainment",
        "Rewe": "Lebensmittel",
        "Amazon": "Shopping"
    }
