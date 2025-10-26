import re
from typing import List, Optional
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class QGModel:
    # class-level cache so the model loads only once for the whole process
    _cached_model = None
    _cached_tokenizer = None

    def __init__(self, model_name: str = "google/mt5-small"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None

    def _ensure_loaded(self):
        if QGModel._cached_model is None or QGModel._cached_tokenizer is None:
            print(f"Loading model {self.model_name}... (first time only)")
            # ✅ force slow tokenizer (SentencePiece-based)
            QGModel._cached_tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                use_fast=False
            )
            QGModel._cached_model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        self.tokenizer = QGModel._cached_tokenizer
        self.model = QGModel._cached_model

    def _clean_text(self, text: str) -> str:
        text = re.sub(r"<extra_id_\d+>", "", text)
        text = re.sub(r"(?i)^\s*generate question:\s*", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def generate_prompts(self, sentences: List[str], lang: Optional[str] = None, max_questions: int = 10) -> List[str]:
        """Generate candidate question prompts from sentences.

        Returns up to max_questions cleaned prompt strings.
        """
        self._ensure_loaded()
