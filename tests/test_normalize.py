from backend.tools.normalize import normalize_fakestore

def test_normalize():
    sample = [{"id":1, "title":"T-Shirt", "price":10, "image":"", "rating":{"rate":4.5,"count":12}}]
    prods = normalize_fakestore(sample)
    assert prods[0].title == "T-Shirt"
    assert prods[0].rating == 4.5
