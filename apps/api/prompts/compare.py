"""
Compare Prompt
Template for comparing two documents
"""

COMPARE_PROMPT = """
Compare these two documents. Return:
1. Key similarities (2-3 points)
2. Key differences (2-3 points)
3. A one-sentence overall verdict

Document A ({doc_id_a}):
{content_a}

Document B ({doc_id_b}):
{content_b}
"""
