import streamlit as st
import asyncio
from backend.graph import build_graph
from backend.state import AgentState
# k=9
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
        "k": 9,  # <-- control top-K end-to-end
    }

    st.session_state.state = asyncio.run(
        st.session_state.graph.ainvoke(st.session_state.state)
    )

s = st.session_state.state

if s.get("missing"):
    st.warning("Missing: " + ", ".join(s["missing"]))
    
elif s.get("topk"):
    cols = st.columns(3)

    seen = set()
    unique_products = []
    for p in s["topk"]:
        if p.id not in seen:
            unique_products.append(p)
            seen.add(p.id)

    for i, p in enumerate(unique_products):
        with cols[i % 3]:
            # Show image if available
            if p.image:
                # st.image(str(p.image), use_column_width=True)
                st.image(p.image, width='stretch')

            # Title
            st.markdown(f"**{p.title}**")

            # Price with discount/original if present
            price_txt = f"{p.currency or ''} {p.price}" if p.price is not None else "—"
            if "discount" in p.attributes or "original_price" in p.attributes:
                discount = p.attributes.get("discount")
                original = p.attributes.get("original_price")
                if original:
                    st.write(f"~~{original}~~ → {price_txt} {f'({discount} off)' if discount else ''}")
                else:
                    st.write(price_txt)
            else:
                st.write(price_txt)

            # Rating
            rating_txt = f"⭐ {p.rating} ({p.reviews_count})" if p.rating is not None else ""
            if rating_txt:
                st.write(rating_txt)

            # Prime badge
            if p.attributes.get("prime"):
                st.success("Prime Eligible")

            # Delivery info
            if p.attributes.get("delivery"):
                st.caption(f"Delivery: {p.attributes['delivery']}")

            # Source + explanation
            st.caption(p.source)
            st.write(s["explanations"].get(p.id, ""))

            # Checkbox to select product
            pick = st.checkbox(f"Select ({p.id})", key=f"sel-{p.id}")
            if pick and p.id not in s["selected_ids"]:
                s["selected_ids"].append(p.id)

    if st.button("Get selected Products' Links"):
        s = asyncio.run(st.session_state.graph.ainvoke(s))  # cart node
        urls = s.get("cart_url")
        # if urls:
        #     st.success("Click the links below to open the products on Amazon:")
        #     for u in urls:
        #         st.markdown(f"[]({u})")
        if urls:
            st.success("Click the links below to open the products on Amazon:")
            # map asin -> title
            title_by_id = {p.id: p.title for p in s.get("topk", [])}
            for u in urls:
                asin = u.split("/dp/")[-1]
                title = title_by_id.get(asin, asin)
                st.markdown(f"**{title}** → [Open product]({u})")

elif go:
    st.header("No relevant product found")
    

