import httpx
import os

SCRAPER_URL = os.getenv("SCRAPER_URL", "http://127.0.0.1:5000")

async def search_products(query: str, page: int = 1):
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.get(f"{SCRAPER_URL}/api/search", params={"query": query, "page": page})
        r.raise_for_status()
        return r.json().get("results", [])

async def get_product_details(product_id: str):
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.get(f"{SCRAPER_URL}/api/product/{product_id}")
        if r.status_code == 200:
            return r.json()
        return None
