import math

def score_and_rank(candidates, prefs, k=10, rag_boost: dict | None = None):
    # rag_boost: optional dict {product_id: bonus_float}
    w = {"rating":0.35,"price":0.20,"reviews":0.15,"features":0.20,"brand":0.05,"rag":0.05}

    prices = [c.price for c in candidates if c.price]
    mean = sum(prices)/len(prices) if prices else 0
    var = sum((p-mean)**2 for p in prices)/len(prices) if prices else 1
    std = (var or 1) ** 0.5
    def inv_z(p): return 0 if not p else -(p-mean)/std

    want = set((prefs.get("must_have") or []))
    def feat_match(c):
        have = set(k for k,v in (c.attributes or {}).items() if v is True or v=="yes")
        return len(want & have)/max(1, len(want)) if want else 0.0

    for c in candidates:
        reviews = math.log(1+(c.reviews_count or 0))
        brand = 0.0
        if prefs.get("brands"):
            brand = 1.0 if any(b.lower() in (c.title or "").lower() for b in prefs["brands"]) else 0.0
        rag = 0.0
        if rag_boost and c.id in rag_boost:
            rag = rag_boost[c.id]
        c.score = (
            w["rating"]*(c.rating or 0) +
            w["price"]*inv_z(c.price) +
            w["reviews"]*reviews +
            w["features"]*feat_match(c) +
            w["brand"]*brand +
            w["rag"]*rag
        )

    rating_min = prefs.get("rating_min") or 0
    budget_max = prefs.get("budget_max") or float("inf")
    filtered = [c for c in candidates if (c.rating or 0) >= rating_min and (c.price or 0) <= budget_max]
    return sorted(filtered, key=lambda x: x.score, reverse=True)[:k]
