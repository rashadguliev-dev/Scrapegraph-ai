# Car Price Analyzer 🚗

Local web application for analyzing car prices for resale in UAE using Gemini + Crawl4AI + ScrapeGraphAI.

## Features
- **Multi-market Scraping**: UAE, USA, Japan, Korea, China, Europe.
- **AI Analysis**: Uses Google Gemini to extract structured data.
- **Financial Calculator**: Calculates "landed cost" including shipping, VAT, and customs.
- **Comparison**: Compare import options with local UAE market prices.

## Setup

1. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   playwright install
   ```

2. **Configure Keys**
   - Edit `backend/.env` and add your `GOOGLE_API_KEY`.

3. **Run Application**
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

4. **Access UI**
   - Open `http://localhost:8000`

## Structure
- `backend/`: FastAPI app, scraper logic.
- `frontend/`: HTML/JS UI.
