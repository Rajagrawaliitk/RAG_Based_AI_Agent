from urllib.parse import urlencode

def build_amazon_add_to_cart_url(items, marketplace="https://www.amazon.in", associate_tag=None):
    """
    Build a URL to redirect user to Amazon with items prefilled.
    items: [{"asin": "B0CXYZ", "qty": 1}, ...]
    """
    # params = {}
    # if associate_tag:
    #     params["AssociateTag"] = associate_tag
    # for i, it in enumerate(items, start=1):
    #     params[f"ASIN.{i}"] = it["asin"]
    #     params[f"Quantity.{i}"] = str(it.get("qty", 1))
    # return f"{marketplace}/gp/aws/cart/add.html?{urlencode(params)}"
    return [f"{marketplace}/dp/{it['asin']}" for it in items]
