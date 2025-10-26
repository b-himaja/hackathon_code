import re
from typing import List

def normalize_whitespace(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def split_sentences(text: str) -> List[str]:
    # naive splitter that works reasonably for many languages
    # you can replace with spaCy or syntok for better splits
    parts = re.split(r'(?<=[.!?।؟])\s+', text)
    return [p.strip() for p in parts if p.strip()]

def preprocess_text(text: str, lang: str) -> List[str]:
    text = normalize_whitespace(text)
    sentences = split_sentences(text)
    # filter very short or noisy sentences
    sentences = [s for s in sentences if len(s.split()) >= 5]
    return sentences
