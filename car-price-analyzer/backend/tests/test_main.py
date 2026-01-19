from fastapi.testclient import TestClient
from main import app, clean_year, clean_price
import pytest

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_clean_year():
    assert clean_year("2022") == 2022
    assert clean_year("Model 2022") == 2022
    assert clean_year("1999") == 1999
    assert clean_year("2100") == 0
    assert clean_year("abc") == 0

def test_clean_price():
    assert clean_price("20000") == 20000.0
    assert clean_price("$20,000") == 20000.0

    # European thousands separator handling
    assert clean_price("20.000") == 20000.0
    assert clean_price("20.000 EUR") == 20000.0

    # Mixed handling (Ambiguous but logic tries best)
    assert clean_price("20,000.00") == 20000.0
    assert clean_price("20.000,00") == 20000.0

def test_search_validation_invalid_year():
    payload = {
        "make": "Toyota",
        "model": "Camry",
        "year_min": 1800, # Invalid
        "year_max": 2023
    }
    response = client.post("/search", json=payload)
    assert response.status_code == 422 # Unprocessable Entity

def test_search_validation_future_year():
    payload = {
        "make": "Toyota",
        "model": "Camry",
        "year_min": 2020,
        "year_max": 3000 # Invalid
    }
    response = client.post("/search", json=payload)
    assert response.status_code == 422
