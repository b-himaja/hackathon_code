from typing import Dict, List, Any
import numpy as np

def readability_score(text: str) -> float:
    # Very rough heuristic: shorter sentences ~ higher score
    n = max(1, len(text.split()))
    return min(1.0, 20.0 / n)

def answerability_heuristic(q: str) -> float:
    # penalize questions with too few content words
    words = [w for w in q.split() if len(w) > 2]
    return min(1.0, len(words) / 10.0)

def evaluate_batch(questions: Dict[str, List[Any]]) -> Dict[str, float]:
    out = {}
    for k, items in questions.items():
        if not items:
            out[k] = 0.0
            continue
        if isinstance(items[0], dict) and 'question' in items[0]:
            texts = [x['question'] for x in items]
        else:
            texts = [str(x) for x in items]
        r = np.mean([readability_score(t) for t in texts])
        a = np.mean([answerability_heuristic(t) for t in texts])
        out[k] = float((r + a) / 2.0)
    return out
