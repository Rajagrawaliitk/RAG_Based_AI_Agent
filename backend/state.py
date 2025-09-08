from typing import TypedDict, List, Dict
from backend.schemas import Product

class AgentState(TypedDict, total=False):
    messages: List[Dict]
    preferences: Dict
    missing: List[str]
    raw_results: List[Dict]
    candidates: List[Product]
    topk: List[Product]
    explanations: Dict[str, str]      # product_id -> markdown with citations
    selected_ids: List[str]
    cart_url: str
