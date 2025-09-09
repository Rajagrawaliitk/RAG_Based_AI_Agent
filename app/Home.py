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

st.subheader("What are you looking for?")
free_query = st.text_area(
    "Describe in your own words (brand wishes, budget, features, rating, use case, etc.)",
    placeholder="e.g., lightweight over-ear headphones with good mic, ANC, under $120, Sony/Bose preferred",
    height=100,
    label_visibility="collapsed",
)

with st.expander("Advanced (optional)"):
    col1, col2 = st.columns(2)
    with col1:
        budget_max = st.number_input("Max Budget", min_value=0.0, value=0.0, step=50.0, help="Leave 0 if no cap")
    with col2:
        rating_min = st.slider("Min Rating", 0.0, 5.0, 0.0, 0.1)

go = st.button("Search")

if go:
        # after computing preferences
    st.session_state.state["preferences"] = {
        "free_query": (free_query or "").strip(),
        "budget_max": float(budget_max) if budget_max else None,
        "rating_min": float(rating_min) if rating_min else None,
        "k": 3,  # <-- control top-K end-to-end
    }

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
            # Uncomment if you want images once you use a provider that returns them
            # if p.image: st.image(p.image, use_column_width=True)
            st.markdown(f"**{p.title}**")
            price_txt = f"{p.currency or ''} {p.price}" if p.price is not None else "—"
            rating_txt = f"⭐ {p.rating} ({p.reviews_count})" if p.rating is not None else ""
            st.write(f"{price_txt} • {rating_txt}")
            st.caption(p.source)
            st.write(s["explanations"].get(p.id, ""))
            pick = st.checkbox(f"Select ({p.id})", key=f"sel-{p.id}")
            if pick and p.id not in s["selected_ids"]:
                s["selected_ids"].append(p.id)

    if st.button("Add selected to Amazon cart"):
        s = st.session_state.graph.ainvoke(s)   # cart node is sync
        url = s.get("")
        if url:
            st.markdown(f"[Open cart link]({url})", unsafe_allow_html=True)

elif go:
    st.header("No relevant product found")
    

