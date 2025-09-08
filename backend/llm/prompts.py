SYSTEM_PROMPT = """
You are a shopping assistant. 
Always ground your answers in retrieved buying guides. 
If you don't know, say you don't know. 
"""

EXPLAIN_TEMPLATE = """
User is looking for {category} with budget {budget_max} and min rating {rating_min}.
Explain why this product is relevant. Include pros and cons if available.
Sources:
{sources}
"""
