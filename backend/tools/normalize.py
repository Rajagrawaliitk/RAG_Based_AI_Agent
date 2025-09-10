from backend.schemas import Product
from rich.console import Console
console = Console()
def normalize_fakestore(items):
    out = []
    for it in items:
        out.append(Product(
            id=str(it.get("id")),
            source="fakestore",
            title=it.get("title") or "",
            image=it.get("image"),
            price=float(it.get("price", 0)) if it.get("price") is not None else None,
            currency="USD",
            rating=(it.get("rating") or {}).get("rate"),
            reviews_count=(it.get("rating") or {}).get("count", 0),
            link=f'https://fakestoreapi.com/products/{it.get("id")}',
            attributes={}   # you can parse description to extract booleans later
        ))
    return out


def normalize_amazon(items):
    out = []
    for it in items:
        # --- price ---
        price = None
        currency = "INR"
        raw_price = it.get("price")

        if isinstance(raw_price, (int, float, str)):
            try:
                price = float(str(raw_price).replace("₹", "").replace(",", "").strip())
            except Exception:
                price = None
        elif isinstance(raw_price, dict):
            # Amazon scraper returns {"current": "₹2,999", "original": "...", "discount": "..."}
            val = raw_price.get("current") or raw_price.get("value")
            if val:
                try:
                    price = float(str(val).replace("₹", "").replace(",", "").strip())
                except Exception:
                    price = None
            currency = raw_price.get("currency") or currency

        # --- rating & reviews ---
        rating_val = None
        reviews_val = 0
        raw_rating = it.get("rating")
        if isinstance(raw_rating, (int, float, str)):
            try:
                rating_val = float(str(raw_rating))
            except Exception:
                rating_val = None
        elif isinstance(raw_rating, dict):
            stars = raw_rating.get("stars")
            if stars:
                try:
                    rating_val = float(str(stars))
                except Exception:
                    rating_val = None
            count = raw_rating.get("count")
            if count:
                try:
                    reviews_val = int(str(count).replace(",", ""))
                except Exception:
                    reviews_val = 0

        out.append(Product(
            id=str(it.get("asin") or it.get("id")),
            source="amazon",
            title=it.get("title") or "",
            image=it.get("image_url") or it.get("image"),
            price=price,
            currency=currency,
            rating=rating_val,
            reviews_count=reviews_val,
            link=it.get("product_url") or it.get("link") or f"https://www.amazon.in/dp/{it.get('asin')}",
            attributes={
                "prime": it.get("prime_eligible") or it.get("is_prime", False),
                "delivery": it.get("delivery_info", ""),
                "discount": (raw_price or {}).get("discount") if isinstance(raw_price, dict) else None,
                "original_price": (raw_price or {}).get("original") if isinstance(raw_price, dict) else None,
            }
        ))
        console.log(f"Normalized Amazon item: {out[-1]}")
    return out
