
EXCHANGE_RATES = {
    "AED": 0.272,
    "EUR": 1.09,
    "JPY": 0.0068,
    "KRW": 0.00076,
    "CNY": 0.14,
    "USD": 1.0,
}

# Shipping costs in LOCAL currency (based on prompt)
SHIPPING_COSTS = {
    "AED": 9000,     # ~$2500
    "USD": 2500,
    "JPY": 350000,   # ~$2500
    "EUR": 2300,
    "KRW": 3000000,  # ~$2500
    "CNY": 18000,    # ~$2500
}

def convert_to_usd(price, currency):
    """Converts price to USD using fixed rates."""
    rate = EXCHANGE_RATES.get(currency, 1.0)
    return price * rate

def calculate_landed_cost(base_price, currency):
    """
    Calculates "landed cost" and returns breakdown in USD.
    Formula from TOR:
    vat = base_price * 0.10
    total_local = (base_price + vat) + shipping_local
    Then convert to USD for comparison.
    Also adds Customs/Duty and Port Delivery for the "Key USD" breakdown.
    """
    VAT_RATE = 0.10  # 10% VAT

    # 1. Get Shipping Cost in Local Currency
    shipping_local = SHIPPING_COSTS.get(currency, 2500) # Default to 2500 if unknown (assuming USD) if currency not found?
    # Actually if currency is not in map, we might have an issue.
    # Let's assume if not found, it's 0 or we treat it as USD 2500 converted?
    # For safety, if currency not in list, assume USD 2500 equivalent.
    if currency not in SHIPPING_COSTS and currency != "USD":
        # Fallback
        shipping_local = 0

    # 2. Calculate components in Local Currency
    vat_local = base_price * VAT_RATE

    # The prompt formula for "Total" seems to be Landed Cost in UAE?
    # "Total = (Base + VAT) + Shipping"
    # But wait, VAT is usually paid in UAE upon import? Or in source country?
    # "VAT (10%)" usually refers to UAE VAT on arrival + Customs.
    # However, the prompt says "VAT (10%): $1,904" for a Japanese car priced $19,040.
    # So it's 10% of the car price.

    # Let's follow the prompt's visual breakdown logic for the final USD numbers:
    # Price: $19,040
    # + VAT (10%): $1,904
    # + Logistics JP->UAE: $2,450
    # + Customs/Duty: $953  (This looks like ~5% of Price)
    # + Port Delivery: $350
    # = TOTAL: $24,697

    # So:
    # 1. Convert Base Price to USD.
    base_price_usd = convert_to_usd(base_price, currency)

    # 2. Calculate components in USD based on the Base Price USD
    vat_usd = base_price_usd * 0.10

    # Shipping is fixed per region. We can take the shipping_local and convert it to USD,
    # OR just use the ~2500 USD approximation for simplicity if the rates fluctuate,
    # BUT the prompt gave specific local numbers. Let's convert the local shipping to USD.
    shipping_usd = convert_to_usd(shipping_local, currency)

    # Customs: 5% of Base Price (Standard UAE)
    customs_usd = base_price_usd * 0.05

    # Port Delivery: Fixed ~$350-$450. Prompt says $350 in one, $450 in another. Let's avg or use $400.
    port_delivery_usd = 400.0

    total_usd = base_price_usd + vat_usd + shipping_usd + customs_usd + port_delivery_usd

    return {
        "base_price": base_price,
        "currency": currency,
        "base_price_usd": round(base_price_usd, 2),
        "vat_usd": round(vat_usd, 2),
        "shipping_usd": round(shipping_usd, 2),
        "customs_usd": round(customs_usd, 2),
        "port_delivery_usd": port_delivery_usd,
        "total_usd": round(total_usd, 2)
    }
