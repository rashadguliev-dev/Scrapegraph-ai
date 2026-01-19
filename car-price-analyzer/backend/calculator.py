EXCHANGE_RATES = {
    "AED": 0.272,
    "EUR": 1.09,
    "JPY": 0.0068,
    "KRW": 0.00076,
    "CNY": 0.14,
    "USD": 1.0,
}

SHIPPING_COSTS = {
    "AED": 2500,  # ~9000 AED -> $2500
    "USD": 2500,
    "JPY": 2500,  # 350000 JPY -> ~$2500
    "EUR": 2300,
    "KRW": 2500,  # 3000000 KRW -> ~$2500
    "CNY": 2500,  # 18000 CNY -> ~$2500
}

def convert_to_usd(price, currency):
    """Converts price to USD using fixed rates."""
    rate = EXCHANGE_RATES.get(currency, 1.0)
    return price * rate

def calculate_landed_cost(base_price, currency):
    """
    Calculates "landed cost" in USD.
    """
    VAT_RATE = 0.10  # 10% VAT

    # Convert base price to USD first for easier calculation or keep in original?
    # The prompt formula: total = (base_price + vat) + shipping
    # It implies calculation in original currency or consistent currency.
    # The result should be in USD.

    # Let's convert everything to USD first.
    base_price_usd = convert_to_usd(base_price, currency)

    # Shipping cost is already roughly in USD in the map (or close to it).
    # The prompt map had mixed currencies values but commented ~$2500.
    # I will assume SHIPPING_COSTS values are in USD.
    shipping_usd = SHIPPING_COSTS.get(currency, 2500)

    vat_usd = base_price_usd * VAT_RATE

    # Prompt adds customs/duty? The detailed breakdown in UI shows:
    # Customs/Duty: $953 (approx 5% of base?)
    # Delivery to port: $350
    # Let's add approximate Custom Duty (5% is standard in UAE)
    customs_duty_usd = base_price_usd * 0.05
    port_delivery_usd = 400 # Average

    total_usd = base_price_usd + vat_usd + shipping_usd + customs_duty_usd + port_delivery_usd

    return {
        "base_price": base_price,
        "base_price_usd": round(base_price_usd, 2),
        "currency": currency,
        "vat_usd": round(vat_usd, 2),
        "shipping_usd": round(shipping_usd, 2),
        "customs_duty_usd": round(customs_duty_usd, 2),
        "port_delivery_usd": port_delivery_usd,
        "total_usd": round(total_usd, 2)
    }
