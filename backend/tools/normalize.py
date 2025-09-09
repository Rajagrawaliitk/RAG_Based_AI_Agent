from backend.schemas import Product

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
