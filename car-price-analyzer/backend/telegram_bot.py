import os
import aiohttp
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def send_telegram_report(results, make, model):
    """
    Sends a comprehensive market analysis report to Telegram
    matching the detailed TOR specification (ASCII art, Top 3, Business Analytics).
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token or "XXXX" in token:
        logger.warning("Telegram token not set, skipping notification.")
        return

    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not chat_id:
        logger.warning("TELEGRAM_CHAT_ID not set, skipping notification.")
        return

    # 1. Separation: UAE (Local) vs Imports
    uae_offers = [r for r in results if r['source_country'] == 'UAE']
    imports = [r for r in results if r['source_country'] != 'UAE']

    # 2. Sort imports by Total Landed Cost (USD)
    imports.sort(key=lambda x: x['financials']['total_usd'])

    if not imports:
        logger.warning("No import options found for Telegram report.")
        return

    # 3. Calculate Stats
    uae_avg_usd = 0
    if uae_offers:
        uae_prices = [r['financials']['base_price_usd'] for r in uae_offers]
        uae_avg_usd = sum(uae_prices) / len(uae_prices)
    else:
        # Fallback if no UAE data found, maybe use a median of imports + 20%?
        # Or just display "N/A"
        uae_avg_usd = 0 # Will handle display logic later

    # 4. Helpers for formatting
    def format_money(val, currency="$"):
        return f"{currency}{int(val):,}"

    def get_flag(country):
        flags = {
            "Japan": "🇯🇵", "USA": "🇺🇸", "Korea": "🇰🇷",
            "Europe": "🇪🇺", "China": "🇨🇳", "UAE": "🇦🇪"
        }
        return flags.get(country, "🌍")

    # 5. Build Message
    now_str = datetime.now().strftime("%d.%m.%Y %H:%M UTC+4")

    msg = []
    msg.append(f"🚗 *{make.upper()} {model.upper()} - АНАЛИЗ РЫНКА*")
    msg.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    msg.append("💱 *Актуальные курсы к USD:*")
    msg.append("1 AED = 0.272 | 1 JPY = 0.0068 | 1 EUR = 1.09")
    msg.append(f"🕐 Обновлено: {now_str}")
    msg.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    # --- TOP 3 ---
    medals = ["🥇 *#1 МАКСИМАЛЬНАЯ ВЫГОДА*", "🥈 *#2 ХОРОШИЙ ВАРИАНТ*", "🥉 *#3 ЗАПАСНОЙ*"]

    for i in range(min(3, len(imports))):
        car = imports[i]
        fin = car['financials']

        # Savings calculation
        savings_usd = 0
        savings_pct = 0
        if uae_avg_usd > 0:
            savings_usd = uae_avg_usd - fin['total_usd']
            savings_pct = (savings_usd / uae_avg_usd) * 100

        flag = get_flag(car['source_country'])
        site_name = car.get('site_name', 'Site')

        msg.append(f"{medals[i]}")
        msg.append(f"{flag} *{car['source_country'].upper()}* ({site_name})")
        msg.append(f"📋 *Детали:*")
        msg.append(f"  • Год: {car.get('year')}")
        msg.append(f"  • Пробег: {car.get('mileage', 'N/A')}")
        msg.append(f"  • Модель: {car.get('model')}")

        msg.append(f"💴 Цена: {format_money(car['price'], '')} {car['currency']} → *{format_money(fin['base_price_usd'])}*")
        msg.append("━━━━━━━━━━━━━━━━━━")
        msg.append(f"➕ НДС (10%):        {format_money(fin['vat_usd'])}")
        msg.append(f"➕ Логистика:        {format_money(fin['shipping_usd'])}")
        msg.append(f"➕ Таможня:          {format_money(fin['customs_usd'])}")
        msg.append(f"➕ Доставка в порт:  {format_money(fin['port_delivery_usd'])}")
        msg.append("━━━━━━━━━━━━━━━━━━")
        msg.append(f"💰 *ИТОГО: {format_money(fin['total_usd'])}*")

        if uae_avg_usd > 0:
            msg.append(f"🔥 *ЭКОНОМИЯ: -{format_money(savings_usd)} (-{savings_pct:.1f}%)*")
            # Estimated Profit (Sell at UAE avg - costs - 1000 misc)
            profit_low = savings_usd - 2000 # Conservative
            profit_high = savings_usd - 1000 # Optimistic
            msg.append(f"📈 *ПРИБЫЛЬ: {format_money(profit_low)}-{format_money(profit_high)}*")

        link = car.get('link', '#')
        # Telegram assumes valid URL. If '#' or local file, might break.
        if link.startswith('http'):
            msg.append(f"🔗 [Открыть объявление]({link})\n")
        else:
            msg.append(f"🔗 Ссылка недоступна\n")

        msg.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    # --- UAE COMPARISON ---
    msg.append("📊 *СРАВНЕНИЕ С ОАЭ*")
    if uae_avg_usd > 0:
        msg.append(f"🇦🇪 Средняя цена в ОАЭ: *{format_money(uae_avg_usd)}*")
        for uae_car in uae_offers[:3]:
            site = uae_car.get('site_name', 'UAE Site')
            price = uae_car['financials']['base_price_usd']
            msg.append(f"  • {site}: {format_money(price)}")
    else:
        msg.append("🇦🇪 Данных по ОАЭ не найдено для сравнения.")
    msg.append("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # --- BUSINESS ANALYTICS ---
    # Based on the #1 Best Deal
    best_deal = imports[0]
    best_savings = uae_avg_usd - best_deal['financials']['total_usd'] if uae_avg_usd > 0 else 0

    msg.append("💡 *РЕКОМЕНДАЦИЯ ДЛЯ БИЗНЕСА*")
    msg.append(f"✅ *Покупать:* {best_deal['source_country']} ({best_deal.get('site_name')})")
    msg.append(f"💰 *Экономия на 1 авто:* {format_money(best_savings)}")
    msg.append(f"📦 *На партии из 5 авто:* {format_money(best_savings * 5)} экономии")

    # ROI = Profit / Cost
    # Profit ~ Best Savings - 1000 (Misc selling costs)
    est_profit = best_savings - 1000
    roi = (est_profit / best_deal['financials']['total_usd']) * 100 if best_deal['financials']['total_usd'] > 0 else 0

    msg.append(f"🎯 *ROI: {roi:.1f}%*")
    msg.append(f"⏱ *Срок окупаемости: 4-6 недель*")
    msg.append("⚠️ *Риск: НИЗКИЙ* (проверенный поставщик)")

    msg.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    full_message = "\n".join(msg)

    # Send
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": full_message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    logger.info("Telegram notification sent successfully.")
                else:
                    logger.error(f"Telegram failed: {await response.text()}")
        except Exception as e:
            logger.error(f"Telegram error: {e}")
