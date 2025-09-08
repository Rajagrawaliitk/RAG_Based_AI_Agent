from backend.tools.scoring import score_and_rank
from backend.schemas import Product

def test_scoring():
    p1 = Product(id="1", source="fake", title="Cheap", price=10, rating=4.0)
    p2 = Product(id="2", source="fake", title="Expensive", price=100, rating=5.0)
    ranked = score_and_rank([p1,p2], {"budget_max":200,"rating_min":0}, k=2)
    assert len(ranked) == 2
