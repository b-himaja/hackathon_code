# cloze.py - Modified
from typing import List, Dict
import re
from collections import Counter

def top_keywords(sentences: List[str], k: int = 10) -> List[str]:
    words = []
    for s in sentences:
        for w in re.findall(r"\b\w{4,}\b", s):
            words.append(w.lower())
    freq = Counter(words)
    return [w for w,_ in freq.most_common(k)]

def make_cloze_questions(sentences: List[str], lang: str, limit: int = 5) -> List[Dict]:
    clozes: List[Dict] = []
    kws = top_keywords(sentences, k=limit*3)  # Get more keywords to ensure we can reach limit
    
    for s in sentences:
        if len(clozes) >= limit:
            break
            
        # Try all keywords for this sentence
        for kw in kws:
            if len(clozes) >= limit:
                break
                
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, s, re.IGNORECASE):
                blanked = re.sub(pattern, "____", s, 1, re.IGNORECASE)
                clozes.append({"question": blanked, "answer": kw})
                break  # Only use one keyword per sentence
    
    # If we didn't get enough, try again with less strict matching
    if len(clozes) < limit:
        for s in sentences:
            if len(clozes) >= limit:
                break
            for kw in kws:
                if len(clozes) >= limit:
                    break
                if kw in s.lower() and kw not in [c["answer"] for c in clozes]:
                    blanked = re.sub(re.escape(kw), "____", s, 1, re.IGNORECASE)
                    clozes.append({"question": blanked, "answer": kw})
    
    return clozes[:limit]  # Ensure exact limit