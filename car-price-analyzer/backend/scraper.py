import os
import asyncio
import logging
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperGraph
from crawl4ai import AsyncWebCrawler
import google.generativeai as genai
from typing import List, Dict, Optional

# Load environment variables
load_dotenv()

# Configure Logging
logging.basicConfig(
    filename='errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    logger.warning("GOOGLE_API_KEY not found in .env")

# ScrapeGraphAI Config
graph_config = {
    "llm": {
        "model": "gemini-1.5-flash",
        "api_key": api_key,
    },
    "embeddings": {
        "model": "gemini-embedding-001",
        "api_key": api_key,
    },
    "verbose": True,
    "headless": True,
}

async def scrape_with_crawl4ai(url: str) -> str:
    """Быстрый краулинг с Crawl4AI"""
    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)
            return result.markdown
    except Exception as e:
        logger.error(f"Crawl4AI error on {url}: {e}")
        raise e

async def scrape_with_scrapegraph(url: str, prompt: str) -> Dict:
    """AI-парсинг с ScrapeGraphAI + Gemini"""
    try:
        # SmartScraperGraph run() is synchronous/blocking.
        # We run it in an executor to avoid blocking the asyncio loop.
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: _run_smart_scraper(url, prompt))
        return result
    except Exception as e:
        logger.error(f"ScrapeGraphAI error on {url}: {e}")
        return {"error": str(e)}

def _run_smart_scraper(url, prompt):
    smart_scraper = SmartScraperGraph(
        prompt=prompt,
        source=url,
        config=graph_config
    )
    return smart_scraper.run()

async def get_car_prices(url: str) -> Optional[Dict]:
    # Exact prompt from TOR
    prompt = """
    Извлеки информацию о автомобилях:
    - Год выпуска
    - Модель
    - Цена (с валютой)
    - Ссылка на объявление
    Игнорируй битые авто и авто без цены.

    Return a list of objects under key 'cars'.
    Example format:
    {
      "cars": [
        {"year": 2022, "model": "Camry", "price": 20000, "currency": "USD", "link": "..."},
        ...
      ]
    }
    """

    try:
        # Вариант 1: Быстрый краулинг (optional usage per logic)
        # content = await scrape_with_crawl4ai(url)

        # Вариант 2: AI-извлечение данных direct from URL via ScrapeGraph
        data = await scrape_with_scrapegraph(url, prompt)

        return data
    except Exception as e:
        logger.error(f"❌ Ошибка на {url}: {e}")
        return None

async def scrape_with_retry(url: str, max_retries: int = 3) -> Dict:
    """
    Парсинг с повторными попытками
    """
    for attempt in range(max_retries):
        try:
            # Таймаут 30 секунд
            async with asyncio.timeout(30):
                result = await get_car_prices(url)
                # Validation: check if result has cars
                if result and 'cars' in result:
                    # Enrich with source site for later processing
                    result['source_url'] = url
                    return result

                # If valid JSON but no cars or error key
                if result and 'error' in result:
                     raise Exception(result['error'])

                # If result is None or empty
                if not result:
                    raise Exception("Empty result")

                return result

        except asyncio.TimeoutError:
            logger.error(f"Timeout на {url}, попытка {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                await asyncio.sleep(5)  # Пауза перед повтором

        except Exception as e:
            logger.error(f"Ошибка на {url}: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(5)

    # Если все попытки провалились
    return {"error": f"Не удалось получить данные с {url}"}
