import streamlit as st
from backend.schemas import Product

def product_card(p: Product, explanation: str = ""):
    st.markdown("---")
    if p.image:
        st.image(p.image, width=180)
    st.markdown(f"**{p.title}**")
    st.write(f"{p.currency} {p.price} • ⭐ {p.rating} ({p.reviews_count})")
    if explanation:
        st.caption(explanation)
    return st.checkbox(f"Select {p.id}", key=f"sel-{p.id}")
