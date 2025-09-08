from backend.schemas import Product

def normalize_fakestore(items):
    out = []
    for it in items:
        out.append(Product(
            id=str(it["id"]),
            source="fakestore",
            title=it["title"],
            image=it.get("image"),
            price=float(it.get("price", 0)),
            currency="USD",               # Fake Store is USD
            rating=(it.get("rating") or {}).get("rate"),
            reviews_count=(it.get("rating") or {}).get("count", 0),
            link=f'https://fakestoreapi.com/products/{it["id"]}',
            attributes={}
        ))
    return out
