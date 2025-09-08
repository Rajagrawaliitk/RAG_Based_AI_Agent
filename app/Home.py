import streamlit as st
import asyncio
from backend.graph import build_graph
from backend.state import AgentState

st.set_page_config(page_title="RAG Shopper (Free)", layout="wide")
st.title("Shopping Copilot — Free Stack")

if "graph" not in st.session_state:
    st.session_state.graph = build_graph()
if "state" not in st.session_state:
    st.session_state.state = AgentState(messages=[], preferences={}, selected_ids=[])


with st.sidebar:
    st.header("Preferences")
    cat = st.text_input("Category", placeholder="e.g., headphones")
    budget_max = st.number_input("Max Budget", min_value=0.0, value=0.0, step=100.0)
    rating_min = st.slider("Min Rating", 0.0, 5.0, 4.0, 0.1)
    if st.button("Search"):
        st.session_state.state["preferences"] = {
            "category": cat,
            "budget_max": float(budget_max) if budget_max else None,
            "rating_min": float(rating_min),
        }
        # ✅ Use async API because your nodes are async
        st.session_state.state = asyncio.run(
            st.session_state.graph.ainvoke(st.session_state.state)
        )

s = st.session_state.state
if s.get("missing"):
    st.warning("Missing: " + ", ".join(s["missing"]))
elif s.get("topk"):
    cols = st.columns(3)
    for i, p in enumerate(s["topk"]):
        with cols[i % 3]:
            # if p.image: 
            #     st.image(p.image, use_column_width=True)
            st.markdown(f"**{p.title}**")
            st.write(f"{p.currency} {p.price} • ⭐ {p.rating} ({p.reviews_count})")
            st.caption(p.source)
            st.write(s["explanations"].get(p.id, ""))
            pick = st.checkbox(f"Select ({p.id})")
            if pick and p.id not in s["selected_ids"]:
                s["selected_ids"].append(p.id)

    if st.button("Add selected to Amazon cart"):
        s = st.session_state.graph.invoke(s)
        url = s.get("cart_url")
        if url:
            st.markdown(f"[Open cart link]({url})", unsafe_allow_html=True)
