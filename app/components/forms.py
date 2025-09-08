import streamlit as st

def preference_form():
    st.header("Preferences")
    cat = st.text_input("Category", placeholder="e.g., laptop")
    budget_max = st.number_input("Max Budget", min_value=0.0, value=0.0, step=100.0)
    rating_min = st.slider("Min Rating", 0.0, 5.0, 4.0, 0.1)
    brands = st.text_input("Brand preference (comma separated)")
    prefs = {
        "category": cat,
        "budget_max": float(budget_max) if budget_max else None,
        "rating_min": float(rating_min),
        "brands": [b.strip() for b in brands.split(",") if b.strip()]
    }
    return prefs, st.button("Search")
