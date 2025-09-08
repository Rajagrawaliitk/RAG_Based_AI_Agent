import httpx

BASE = "https://fakestoreapi.com"

async def search_products(query: str, limit: int = 30):
    # No real search in FakeStore; fetch all and filter locally
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(f"{BASE}/products")
        r.raise_for_status()
        data = r.json()
    q = query.lower().strip()
    items = [p for p in data if q in p["title"].lower() or q in p.get("category","").lower()]
    return items[:limit]
