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
    "verbose": True,
    "headless": True,
}

async def scrape_with_crawl4ai(url: str) -> str:
    """Fast crawling with Crawl4AI"""
    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)
            return result.markdown
    except Exception as e:
        logger.error(f"Crawl4AI error on {url}: {e}")
        raise e

async def scrape_with_scrapegraph(url: str, prompt: str) -> Dict:
    """AI scraping with ScrapeGraphAI"""
    try:
        # SmartScraperGraph is synchronous in run(), need to wrap it?
        # Actually it might make http calls.
        # But for now let's run it directly.
        smart_scraper = SmartScraperGraph(
            prompt=prompt,
            source=url,
            config=graph_config
        )
        result = smart_scraper.run()
        return result
    except Exception as e:
        logger.error(f"ScrapeGraphAI error on {url}: {e}")
        return {"error": str(e)}

async def get_car_prices(url: str, make: str, model: str, year_min: int, year_max: int) -> Optional[Dict]:
    prompt = f"""
    Extract information about used cars matching: {make} {model} between years {year_min} and {year_max}.
    For each car found, extract:
    - Year
    - Model
    - Price (numeric value)
    - Currency (AED, USD, JPY, EUR, KRW, CNY)
    - Mileage (with unit)
    - Link to ad

    Return a list of objects under key 'cars'.
    Ignore damaged cars or cars without price.
    """

    try:
        # Strategy: Try ScrapeGraphAI directly as it handles extraction best.
        # If it fails, could fall back to Crawl4AI + LLM parsing manually,
        # but ScrapeGraphAI does that internally.

        # Note: ScrapeGraphAI run() is blocking. In async app, better run in executor.
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: smart_scraper_run(url, prompt))
        return data
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return None

def smart_scraper_run(url, prompt):
    smart_scraper = SmartScraperGraph(
        prompt=prompt,
        source=url,
        config=graph_config
    )
    return smart_scraper.run()

async def scrape_with_retry(url: str, make: str, model: str, year_min: int, year_max: int, max_retries: int = 3) -> Dict:
    for attempt in range(max_retries):
        try:
            async with asyncio.timeout(60): # Increased timeout
                result = await get_car_prices(url, make, model, year_min, year_max)
                if result and 'cars' in result and result['cars']:
                    # Post-process to ensure source url is included if needed
                    for car in result['cars']:
                        car['source_site'] = url
                    return result
                # If result is empty or error, retry?
                if result and 'error' in result:
                    raise Exception(result['error'])
        except Exception as e:
            logger.error(f"Retry {attempt + 1}/{max_retries} failed for {url}: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(5)

    return {"error": f"Failed to scrape {url} after {max_retries} attempts"}
