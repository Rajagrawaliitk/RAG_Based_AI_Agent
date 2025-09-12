from langgraph.graph import StateGraph, END
from backend.state import AgentState
from backend.tools.normalize import normalize_amazon   # updated
from backend.tools.scoring import score_and_rank
from backend.tools.rag_explainer import explain_products
from backend.tools.cart_link import build_amazon_add_to_cart_url
import json
from rich.console import Console
console = Console()
# NEW import: scraper provider
# k=9
from backend.tools.providers import amazon_api

def node_collect(s: AgentState) -> AgentState:
    prefs = s.get("preferences", {})
    missing = []
    if not (prefs.get("free_query") and prefs["free_query"].strip()):
        missing.append("free_query")
    s["missing"] = missing
    return s

async def node_search(s: AgentState) -> AgentState:
    if s.get("missing"):
        return s

    q = s["preferences"]["free_query"]
    page = int(s["preferences"].get("page", 1))

    # call your Flask scraper
    items = await amazon_api.search_products(q, page=page)

    # console.log(f"items from Amazon API: {items[0]}")
    s["raw_results"] = items
    return s

def node_rank(s: AgentState) -> AgentState:
    k = int(s["preferences"].get("k", 9))
    s["candidates"] = normalize_amazon(s["raw_results"])
    s["topk"] = score_and_rank(s["candidates"], s["preferences"], k=k)
    return s

def node_explain(s: AgentState) -> AgentState:
    s["explanations"] = explain_products(s["topk"], s["preferences"])
    return s

def node_cart(s: AgentState) -> AgentState:
    if s.get("selected_ids"):
        items = [{"asin": pid, "qty": 1} for pid in s["selected_ids"]]
        urls = build_amazon_add_to_cart_url(items)
        s["cart_url"] = urls
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
