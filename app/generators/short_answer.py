# short_answers.py - Modified
from typing import List, Dict
from ..pipeline.postprocess import clean_question

def make_short_answer_questions(prompts: List[str], lang: str, limit: int = 5) -> List[Dict]:
    out: List[Dict] = []
    for p in prompts[:limit]:
        q = clean_question(p)
        out.append({"question": q, "answer_type": "short"})
    return out[:limit]  # Ensure exact limit