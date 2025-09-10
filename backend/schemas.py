from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict

class Product(BaseModel):
    id: str                      # asin or provider id
    source: str                  # "fakestore", "scraper:site"
    title: str
    image: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = "INR"
    rating: Optional[float] = None
    reviews_count: Optional[int] = 0
    link: Optional[HttpUrl] = None
    badges: List[str] = []
    delivery: Dict = {}
    attributes: Dict = {}
    pros: List[str] = []
    cons: List[str] = []
    score: float = 0.0

class Preferences(BaseModel):
    category: str
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    rating_min: Optional[float] = None
    brands: List[str] = []
    must_have: List[str] = []
