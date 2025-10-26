# mcq.py - Modified
from typing import List, Dict
from transformers import AutoModelForMaskedLM, AutoTokenizer, pipeline
import random
import re

_fill_mask = None
_mask_token = None

def _get_fill_mask():
    global _fill_mask, _mask_token
    if _fill_mask is None:
        model_name = "xlm-roberta-base"
        tok = AutoTokenizer.from_pretrained(model_name)
        mdl = AutoModelForMaskedLM.from_pretrained(model_name)
        _mask_token = tok.mask_token
        _fill_mask = pipeline("fill-mask", model=mdl, tokenizer=tok, top_k=20)
    return _fill_mask, _mask_token

def _mask_one_word(text: str):
    # Find all candidate words (4-12 characters, alphanumeric)
    words = re.findall(r'\b[a-zA-Z]{4,12}\b', text)
    if not words:
        return text, ""
    target = random.choice(words)
    masked = re.sub(r'\b' + re.escape(target) + r'\b', "<mask>", text, 1)
    return masked, target

def _is_valid_token(tok: str, original_answer: str) -> bool:
    tok = tok.strip()
    if not tok:
        return False
    if re.search(r"[<>]", tok):
        return False
    if re.fullmatch(r"[\W_]+", tok):
        return False
    if len(tok) == 1 and len(original_answer) > 1:
        return False
    if len(tok) > 40:
        return False
    return True

def make_mcq_questions(prompts: List[str], lang: str, limit: int = 5) -> List[Dict]:
    fm, mask_tok = _get_fill_mask()
    out: List[Dict] = []
    
    # Process more prompts to ensure we reach the limit
    for p in prompts[:limit * 3]:
        if len(out) >= limit:
            break
            
        masked, answer = _mask_one_word(p)
        if "<mask>" not in masked or not answer:
            continue
            
        masked = masked.replace("<mask>", mask_tok)
        try:
            candidates = fm(masked)
            options = []
            seen = set([answer.lower()])
            
            for cand in candidates:
                if len(options) >= 3:
                    break
                tok = cand.get("token_str", "").strip()
                if _is_valid_token(tok, answer) and tok.lower() not in seen:
                    options.append(tok)
                    seen.add(tok.lower())
            
            if len(options) >= 2:  # Need at least 2 distractors + answer = 3 choices
                choices = options[:3] + [answer]
                random.shuffle(choices)
                out.append({
                    "question": p if p.endswith("?") else p + "?",
                    "choices": choices,
                    "answer": answer
                })
                
        except Exception as e:
            continue
    
    return out[:limit]  # Ensure exact limit