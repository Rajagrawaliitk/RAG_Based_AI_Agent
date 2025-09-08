from langgraph.graph import StateGraph, END
from backend.state import AgentState
from backend.tools.providers.fakestore import search_products
from backend.tools.normalize import normalize_fakestore
from backend.tools.scoring import score_and_rank
from backend.tools.rag_explainer import explain_products
from backend.tools.cart_link import build_amazon_add_to_cart_url

async def node_collect(s: AgentState) -> AgentState:
    prefs = s.get("preferences", {})
    missing = []
    if not prefs.get("category"): missing.append("category")
    if prefs.get("budget_max") is None: missing.append("budget_max")
    if prefs.get("rating_min") is None: missing.append("rating_min")
    s["missing"] = missing
    return s

async def node_search(s: AgentState) -> AgentState:
    if s.get("missing"): return s
    items = await search_products(s["preferences"]["category"])
    s["raw_results"] = items
    return s

def node_rank(s: AgentState) -> AgentState:
    s["candidates"] = normalize_fakestore(s["raw_results"])
    s["topk"] = score_and_rank(s["candidates"], s["preferences"], k=9)
    return s

def node_explain(s: AgentState) -> AgentState:
    s["explanations"] = explain_products(s["topk"], s["preferences"])
    return s

def node_cart(s: AgentState) -> AgentState:
    if s.get("selected_ids"):
        items = [{"asin": pid, "qty": 1} for pid in s["selected_ids"]]  # using id as placeholder
        s["cart_url"] = build_amazon_add_to_cart_url(items)
    return s

def build_graph():
    g = StateGraph(AgentState)
    g.add_node("collect", node_collect)
    g.add_node("search", node_search)
    g.add_node("rank", node_rank)
    g.add_node("explain", node_explain)
    g.add_node("cart", node_cart)
    g.set_entry_point("collect")
    g.add_edge("collect", "search")
    g.add_edge("search", "rank")
    g.add_edge("rank", "explain")
    g.add_edge("explain", "cart")
    g.add_edge("cart", END)
    return g.compile()
