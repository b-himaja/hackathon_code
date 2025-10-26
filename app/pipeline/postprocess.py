import re

def clean_question(q: str) -> str:
    q = q.strip()
    q = re.sub(r'\s+', ' ', q)
    # ensure it ends with a question mark for interrogatives
    if not q.endswith('?') and any(q.lower().startswith(w) for w in ['what','why','how','when','where','who','which','whom']):
        q += '?'
    return q
