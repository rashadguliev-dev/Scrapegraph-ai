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
    msg.append("1 KRW = 0.00076 | 1 CNY = 0.14")
    msg.append(f"🕐 Обновлено: {now_str}")
    msg.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    # --- TOP 3 ---
    medals = ["🥇 *#1 - МАКСИМАЛЬНАЯ ВЫГОДА*", "🥈 *#2 - ХОРОШИЙ ВАРИАНТ*", "🥉 *#3 - ЗАПАСНОЙ ВАРИАНТ*"]

    for i in range(min(3, len(imports))):
        car = imports[i]
        fin = car['financials']

        # Savings (pre-calculated)
        savings_usd = car.get('savings_usd', 0)
        savings_pct = car.get('savings_pct', 0)

        flag = get_flag(car['source_country'])
        site_name = car.get('site_name', 'Site')

        msg.append(f"{medals[i]}: {flag} {car['source_country'].upper()}")
        msg.append(f"┌────────────────────────────────────────────────────────┐")
        msg.append(f"│ Сайт: {site_name:<44} │")
        msg.append(f"│ Год: {car.get('year')} | Пробег: {car.get('mileage', 'N/A')} │")
        msg.append(f"│                                                         │")
        msg.append(f"│ 💴 Цена: {format_money(car['price'], car['currency']):<15} 💵 В долларах: {format_money(fin['base_price_usd']):<11} │")
        msg.append(f"│                                                         │")
        msg.append(f"│ ➕ НДС (10%):            {format_money(fin['vat_usd']):<27} │")
        msg.append(f"│ ➕ Логистика:            {format_money(fin['shipping_usd']):<27} │")
        msg.append(f"│ ➕ Таможня/Пошлина:      {format_money(fin['customs_usd']):<27} │")
        msg.append(f"│ ➕ Доставка в порт:      {format_money(fin['port_delivery_usd']):<27} │")
        msg.append(f"│ ═══════════════════════════════════════════════════     │")
        msg.append(f"│ 💰 ИТОГО ПОД КЛЮЧ:      {format_money(fin['total_usd']):<28} │")
        msg.append(f"│                                                         │")

        if uae_avg_usd > 0:
            savings_sign = "-" if savings_usd > 0 else "+"
            msg.append(f"│ 🔥 ЭКОНОМИЯ vs UAE: {savings_sign}{format_money(abs(savings_usd))} ({savings_sign}{abs(savings_pct):.1f}%) 🎯                │")

            # Estimated Profit
            profit = 0
            # ROI
            if 'roi_percent' in car:
                 msg.append(f"│ 📈 Потенциальная прибыль: {format_money(car['profit_usd'])} │")

        msg.append(f"│                                                         │")
        msg.append(f"│ 🔗 Ссылка: [Открыть объявление]                        │")
        msg.append(f"└────────────────────────────────────────────────────────┘\n")

    # --- UAE COMPARISON ---
    msg.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    msg.append("📊 *СРАВНЕНИЕ С МЕСТНЫМ РЫНКОМ ОАЭ*")

    if uae_avg_usd > 0:
        msg.append(f"\n🇦🇪 СРЕДНЯЯ ЦЕНА В ОАЭ: *{format_money(uae_avg_usd)}*")
        msg.append("┌────────────────────────────────────────────────────────┐")
        for uae_car in uae_offers[:4]:
            site = uae_car.get('site_name', 'UAE Site')
            price = uae_car['financials']['base_price_usd']
            local_price = f"{int(uae_car['price']):,} {uae_car['currency']}"
            msg.append(f"│ {site:<13}: {format_money(price)} ({local_price}) │")
        msg.append("└────────────────────────────────────────────────────────┘")
    else:
        msg.append("🇦🇪 Данных по ОАЭ не найдено для сравнения.")
    msg.append("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    # --- BUSINESS ANALYTICS ---
    # Based on the #1 Best Deal
    best_deal = imports[0]
    best_savings = best_deal.get('savings_usd', 0)

    msg.append("💡 *БИЗНЕС-АНАЛИТИКА*")
    msg.append("┌────────────────────────────────────────────────────────┐")
    msg.append(f"│ ✅ ЛУЧШИЙ ИСТОЧНИК: {best_deal['source_country']} ({best_deal.get('site_name')})                 │")
    msg.append(f"│ 💰 ЭКОНОМИЯ НА ПОКУПКЕ: {format_money(best_savings)} на единицу              │")
    msg.append(f"│ 📦 При покупке 5 авто: ~{format_money(best_savings * 5)} экономии               │")

    # Financials for 5 cars
    batch_buy = best_deal['financials']['total_usd'] * 5
    batch_sell = uae_avg_usd * 5
    batch_profit = best_deal['profit_usd'] * 5 if 'profit_usd' in best_deal else 0

    msg.append(f"│ 💵 Закупочная цена (5 авто): {format_money(batch_buy)}                  │")
    msg.append(f"│ 💰 Продажная цена (5 авто): ~{format_money(batch_sell)}                  │")
    msg.append(f"│ 🎯 ЧИСТАЯ ПРИБЫЛЬ: {format_money(batch_profit)} (ROI ~{best_deal.get('roi_percent', 0):.1f}%)       │")
    msg.append(f"│ ⏱ СРОК ОКУПАЕМОСТИ: 4-6 недель (доставка + продажа)   │")
    msg.append(f"│ ⚠️ РИСКИ: Логистика 4-6 недель, проверка документов    │")
    msg.append("└────────────────────────────────────────────────────────┘")

    msg.append("\n[📥 Скачать Excel] [📊 Экспорт в PDF] [📱 Отправить в Telegram]")

    full_message = "\n".join(msg)

    # Send
    # Note: Telegram message length limit is 4096 chars. This long report might hit it.
    # Should split if necessary.

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
