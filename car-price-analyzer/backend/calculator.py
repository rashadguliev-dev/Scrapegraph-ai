
# 💰 ФИНАНСОВАЯ ФОРМУЛА С УЧЕТОМ ВАЛЮТ

EXCHANGE_RATES = {
    "AED": 0.272,
    "EUR": 1.09,
    "JPY": 0.0068,
    "KRW": 0.00076,
    "CNY": 0.14,
    "USD": 1.0,
}

# Стоимость доставки из разных регионов в ОАЭ
# Значения могут быть в разных валютах, поэтому нормализуем при расчете
# Но согласно ТЗ "SHIPPING_COSTS" дан как словарь.
# В ТЗ:
# "AED": 9000,   # ~$2500
# "USD": 2500,
# "JPY": 350000, # ~$2500
# "EUR": 2300,
# "KRW": 3000000, # ~$2500
# "CNY": 18000,  # ~$2500

SHIPPING_COSTS = {
    "AED": 9000,
    "USD": 2500,
    "JPY": 350000,
    "EUR": 2300,
    "KRW": 3000000,
    "CNY": 18000,
}

def convert_to_usd(price, currency):
    """Converts price to USD using fixed rates from TOR."""
    rate = EXCHANGE_RATES.get(currency, 1.0)
    return price * rate

def calculate_landed_cost(base_price, currency):
    """
    Расчет стоимости "под ключ" согласно ТЗ.
    Returns dictionary with details in USD.
    """
    VAT_RATE = 0.10  # 10% НДС

    # 1. Определяем стоимость доставки в валюте региона
    # Если валюты нет в списке, используем дефолт $2500 (как USD)
    shipping_local = SHIPPING_COSTS.get(currency, 2500)

    # 2. Основная формула из ТЗ: total = (base_price + vat) + shipping
    # Но для корректного сложения всё должно быть в одной валюте или конвертироваться.
    # ТЗ не уточняет валюту shipping_local в формуле, но логично, что SHIPPING_COSTS
    # заданы в валюте региона (JPY 350000 ~ $2500).

    # Конвертируем все компоненты в USD для унификации
    base_price_usd = convert_to_usd(base_price, currency)
    shipping_usd = convert_to_usd(shipping_local, currency)

    # НДС считается от цены авто (по ТЗ пример: $19040 -> $1904)
    vat_usd = base_price_usd * VAT_RATE

    # Таможня/Пошлина (Customs/Duty)
    # В примере ТЗ: Price $19,040 -> Customs $953. Это ровно 5% (стандарт ОАЭ).
    customs_usd = base_price_usd * 0.05

    # Доставка в порт (Port Delivery)
    # В примере ТЗ: $350. Зафиксируем среднее.
    port_delivery_usd = 350.0

    # ИТОГО ПОД КЛЮЧ
    # Пример ТЗ: Base + VAT + Logistics + Customs + Port Delivery
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

def calculate_profit(uae_avg_price_usd, landed_cost_usd):
    """
    Прибыль = Средняя цена UAE ($33,250) - Цена под ключ - Расходы на продажу ($1,000)
    """
    SELLING_COSTS = 1000.0
    if uae_avg_price_usd <= 0:
        return 0, 0

    profit = uae_avg_price_usd - landed_cost_usd - SELLING_COSTS
    roi = (profit / landed_cost_usd) * 100 if landed_cost_usd > 0 else 0

    return round(profit, 2), round(roi, 1)
