from langgraph.graph import StateGraph, END
from backend.state import AgentState
from backend.tools.normalize import normalize_amazon
from backend.tools.scoring import score_and_rank
from backend.tools.rag_explainer import explain_products
from backend.tools.cart_link import build_amazon_add_to_cart_url
from backend.tools.providers import amazon_api
from backend.retrieval.vectordb import upsert_products, query_products_semantic
from backend.llm.models import get_llm
from backend.llm.prompts import REWRITE_SYSTEM, REWRITE_USER
from rich.console import Console
import json

console = Console()
_llm = get_llm()


# ---------------- Nodes ----------------
def node_collect(s: AgentState) -> AgentState:
    prefs = s.get("preferences", {})
    missing = []
    if not (prefs.get("free_query") and prefs["free_query"].strip()):
        missing.append("free_query")
    s["missing"] = missing
    return s

import re, json

def safe_json_parse(content: str):
    # Remove triple backticks and language markers
    cleaned = re.sub(r"^```(?:json)?|```$", "", content.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except Exception as e:
        from rich.console import Console
        Console().log(f"[red]Failed to parse rewrite output:[/red] {content} -> {e}")
        return {}


def node_rewrite(s: AgentState) -> AgentState:
    """LLM rewrites free text into structured JSON preferences"""
    if s.get("missing"):
        return s

    user_prompt = REWRITE_USER.format(
        free_text=s["preferences"]["free_query"],
        min_rating=s["preferences"].get("rating_min"),
        budget_max=s["preferences"].get("budget_max"),
    )

    # out = _llm.invoke(f"{REWRITE_SYSTEM}\n\n{user_prompt}")
    out =user_prompt
    if hasattr(out, "content"):
        raw_text = out.content
    elif isinstance(out, dict):
        raw_text = out.get("content", str(out))
    else:
        raw_text = str(out).strip()

    # Now safely parse
    try:
        parsed = json.loads(raw_text)
    except Exception as e:
        from rich.console import Console
        Console().log(f"[red]Failed to parse rewrite output: {raw_text} ({e})")
        parsed = {}
    # try:
    #     parsed = safe_json_parse(out.content)
    # except Exception as e:
    #     console.log(f"[red]Failed to parse rewrite output:[/red] {out} ({e})")
    #     parsed = {}

    # merge rewritten fields back into preferences
    s["rewritten"] = parsed
    s["preferences"].update({
        "category": parsed.get("category"),
        "brands": parsed.get("brands"),
        "budget_max": parsed.get("budget_max") or s["preferences"].get("budget_max"),
        "rating_min": parsed.get("min_rating") or s["preferences"].get("rating_min"),
    })
    return s


async def node_search(s: AgentState) -> AgentState:
    if s.get("missing"):
        return s

    q = s.get("rewritten", {}).get("category") or s["preferences"]["free_query"]
    page = int(s["preferences"].get("page", 1))

    # Amazon scraper
    items = await amazon_api.search_products(q, page=page)
    s["raw_results"] = items

    # Index into vector DB
    upsert_products(items)

    # Semantic retrieval for boosting
    s["product_hits"] = query_products_semantic(q, k=12)

    return s


def node_rank(s: AgentState) -> AgentState:
    k = int(s["preferences"].get("k", 9))
    s["candidates"] = normalize_amazon(s["raw_results"])

    boost = {h["id"]: 1.0 for h in s.get("product_hits", [])}
    s["topk"] = score_and_rank(s["candidates"], s["preferences"], k=k, rag_boost=boost)
    return s


def node_explain(s: AgentState) -> AgentState:
    s["explanations"] = explain_products(s["topk"], s["preferences"])
    return s


def node_cart(s: AgentState) -> AgentState:
    if s.get("selected_ids"):
        items = [{"asin": pid, "qty": 1} for pid in s["selected_ids"]]
        s["cart_url"] = build_amazon_add_to_cart_url(items)
    return s


# ---------------- Graph ----------------
def build_graph():
    g = StateGraph(AgentState)
    g.add_node("collect", node_collect)
    g.add_node("rewrite", node_rewrite)   # NEW
    g.add_node("search", node_search)
    g.add_node("rank", node_rank)
    g.add_node("explain", node_explain)
    g.add_node("cart", node_cart)

    g.set_entry_point("collect")
    g.add_edge("collect", "rewrite")   # collect → rewrite
    g.add_edge("rewrite", "search")    # rewrite → search
    g.add_edge("search", "rank")
    g.add_edge("rank", "explain")
    g.add_edge("explain", "cart")
    g.add_edge("cart", END)

    return g.compile()
