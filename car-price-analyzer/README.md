# Car Price Analyzer 🚗

Локальное веб-приложение для анализа цен на автомобили для перепродажи в ОАЭ с использованием **Gemini + Crawl4AI + ScrapeGraphAI**.

## 📋 Особенности
- **AI-Парсинг:** Использование Gemini 1.5 Flash для извлечения данных.
- **Мульти-регион:** Поиск по 6 регионам (ОАЭ, США, Япония, Корея, Китай, Европа).
- **Финансы:** Автоматический расчет стоимости "под ключ" (НДС, Логистика, Таможня).
- **Сравнение:** Выделение лучших предложений и сравнение с рынком ОАЭ.
- **Telegram Бот:** Отправка детальных отчетов с ROI и бизнес-аналитикой.

## 🛠 Технический стек
- **Backend:** FastAPI, Python 3.10+
- **AI/Scraping:** ScrapeGraphAI, Crawl4AI, Google Gemini API
- **Frontend:** Vanilla JS, Tailwind CSS
- **Database:** (In-memory for this version)

## 🚀 Установка и запуск

### 1. Клонирование
```bash
git clone https://github.com/rashadguliev-dev/Scrapegraph-ai.git
cd car-price-analyzer
```

### 2. Установка зависимостей
```bash
pip install -r backend/requirements.txt
```

### 3. Настройка окружения
Создайте файл `backend/.env` и добавьте ваши ключи:
```env
GOOGLE_API_KEY=AIzaSy...
TELEGRAM_BOT_TOKEN=123456...
TELEGRAM_CHAT_ID=987654...
```

### 4. Запуск сервера
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Использование
Откройте браузер по адресу: [http://localhost:8000](http://localhost:8000)

## 📁 Структура проекта
```
car-price-analyzer/
├── backend/
│   ├── main.py              # FastAPI сервер & Оркестрация
│   ├── scraper.py           # ScrapeGraphAI + Crawl4AI логика
│   ├── calculator.py        # Финансовые расчеты (Logistics, VAT)
│   ├── config.py            # Конфигурация сайтов и шаблонов поиска
│   ├── telegram_bot.py      # Модуль отправки отчетов
│   ├── .env                 # API Keys
│   └── requirements.txt
├── frontend/
│   ├── index.html           # UI (Tailwind)
│   └── app.js               # Frontend Logic
└── README.md
```

## ⚠️ Отказ от ответственности
Приложение использует скрапинг данных. Убедитесь, что вы соблюдаете условия использования (Terms of Service) целевых сайтов.
