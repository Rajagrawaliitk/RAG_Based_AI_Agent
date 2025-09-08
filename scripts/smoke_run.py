import asyncio
from backend.graph import build_graph
from backend.state import AgentState

async def main():
    graph = build_graph()
    state = AgentState(messages=[], preferences={"category": "shirt", "budget_max":50, "rating_min":3})
    result = await graph.invoke(state)
    print("Top products:", [p.title for p in result.get("topk", [])])
    print("Cart URL:", result.get("cart_url"))

if __name__ == "__main__":
    asyncio.run(main())
