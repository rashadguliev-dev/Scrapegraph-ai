import pytest
from calculator import calculate_landed_cost, calculate_profit

def test_calculate_landed_cost_japan():
    # Example from TOR:
    # Price: ¥2,800,000 -> $19,040 (approx, depends on rate)
    # Rate JPY = 0.0068
    # 2,800,000 * 0.0068 = 19,040
    # Shipping JPY = 350,000 -> 350,000 * 0.0068 = 2,380 (TOR says $2450? Rates might vary slightly in TOR example vs code constants)
    # Let's test the LOGIC based on constants in calculator.py

    price_jpy = 2800000
    result = calculate_landed_cost(price_jpy, "JPY")

    # Base USD
    expected_base = 2800000 * 0.0068
    assert result['base_price_usd'] == pytest.approx(expected_base, 0.01)

    # VAT 10%
    expected_vat = expected_base * 0.10
    assert result['vat_usd'] == pytest.approx(expected_vat, 0.01)

    # Customs 5%
    expected_customs = expected_base * 0.05
    assert result['customs_usd'] == pytest.approx(expected_customs, 0.01)

    # Shipping (JPY 350,000 * 0.0068)
    expected_shipping = 350000 * 0.0068
    assert result['shipping_usd'] == pytest.approx(expected_shipping, 0.01)

    # Port
    assert result['port_delivery_usd'] == 350.0

def test_calculate_landed_cost_usa():
    # USA Shipping is $2500 fixed in calculator.py
    price_usd = 20000
    result = calculate_landed_cost(price_usd, "USD")

    assert result['base_price_usd'] == 20000
    assert result['shipping_usd'] == 2500
    assert result['vat_usd'] == 2000 # 10%
    assert result['customs_usd'] == 1000 # 5%

def test_calculate_profit():
    # UAE Avg: 33250
    # Landed: 24697
    # Selling Cost: 1000
    # Profit = 33250 - 24697 - 1000 = 7553

    profit, roi = calculate_profit(33250, 24697)
    assert profit == pytest.approx(7553, 0.1)

    # ROI = 7553 / 24697 * 100 = 30.58%
    assert roi == pytest.approx(30.6, 0.1) # Rounding in function is to 1 decimal

def test_calculate_profit_loss():
    # Landed > UAE
    profit, roi = calculate_profit(20000, 25000)
    # Profit = 20000 - 25000 - 1000 = -6000
    assert profit == -6000
    assert roi == pytest.approx(-24.0, 0.1)
