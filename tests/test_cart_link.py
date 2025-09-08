from backend.tools.cart_link import build_amazon_add_to_cart_url

def test_cart_link():
    url = build_amazon_add_to_cart_url([{"asin":"B000123","qty":1}])
    assert "ASIN.1=B000123" in url
