# main.py - Fixed to ensure formatter is applied
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import List, Optional
import uvicorn
import re
import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import utilities
try:
    from app.utils.lang import detect_language
    from app.pipeline.preprocess import preprocess_text
    from app.models.qg_model import QGModel
    from app.generators.cloze import make_cloze_questions
    from app.generators.mcq import make_mcq_questions
    from app.pipeline.evaluation import evaluate_batch
    
    # Handle short_answer import
    try:
        from app.generators.short_answer import make_short_answer_questions
    except ImportError:
        from app.generators.short_answer import make_short_answer_questions
        
    # Import formatter
    try:
        from utils.formatter import format_questions_readable
    except ImportError:
        # Create a simple formatter if import fails
        def format_questions_readable(data):
            return f"LANGUAGE: {data.get('language', 'unknown').upper()}\n" + \
                   "Error: Formatter module not found properly"
                   
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback function if all imports fail
    def format_questions_readable(data):
        return "Error: Could not load formatter module"

app = FastAPI(title="Multilingual Question Generation", version="0.2.0")

app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")
templates = Jinja2Templates(directory="app/templates")

qg_model = QGModel()

class GenerateRequest(BaseModel):
    text: str = Field(..., description="Textbook-like input passage")
    targets: List[str] = Field(default=["mcq", "cloze", "short_answer"])
    num_questions: int = Field(5, description="Number of questions per type")
    language_hint: Optional[str] = None
    output_format: str = Field("json", description="Output format: 'json' or 'text'")

def _clean_item(item):
    """Clean strings to remove leftover tokens."""
    if isinstance(item, str):
        s = re.sub(r"<extra_id_\d+>", "", item)
        s = re.sub(r"\s+", " ", s).strip()
        return s
    if isinstance(item, dict):
        return {k: _clean_item(v) for k, v in item.items()}
    if isinstance(item, list):
        return [_clean_item(v) for v in item]
    return item

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# main.py - Add more detailed debugging
@app.post("/api/generate")
async def generate_questions(req: GenerateRequest):
    try:
        # Debug: Print the entire request
        print(f"DEBUG: Full request data: {req.dict()}")
        print(f"DEBUG: Output format from request: {req.output_format}")
        
        text = req.text.strip()
        if not text:
            return JSONResponse({"error": "No text provided"}, status_code=400)
        
        lang = req.language_hint or detect_language(text)
        clean_sentences = preprocess_text(text, lang)
        
        if not clean_sentences:
            return JSONResponse({"error": "No valid sentences found in text"}, status_code=400)
        
        # Ensure we have enough sentences
        if len(clean_sentences) < req.num_questions:
            needed = req.num_questions - len(clean_sentences)
            clean_sentences.extend(clean_sentences[:needed])

        # Generate prompts
        prompts = None
        try:
            prompts = qg_model.generate_prompts(
                clean_sentences, 
                lang=lang, 
                max_questions=max(10, req.num_questions * 3)
            )
        except Exception as gen_err:   ### FIX: catch model errors safely
            print(f"WARNING: Failed to generate prompts: {gen_err}")
            prompts = []

        if not prompts:   ### FIX: ensure prompts is always a list
            print("DEBUG: No prompts generated, using empty list")
            prompts = []

        out = {"language": lang, "counts": {}, "questions": {}}

        # Generate each question type
        if "cloze" in req.targets:
            clozes = make_cloze_questions(clean_sentences, lang, limit=req.num_questions)
            clozes = [_clean_item(c) for c in clozes]
            out["questions"]["cloze"] = clozes
            out["counts"]["cloze"] = len(clozes)

        if "short_answer" in req.targets:
            base_inputs = prompts if prompts else clean_sentences  # fallback
            shorts = make_short_answer_questions(base_inputs, lang, limit=req.num_questions)  ### FIX
            shorts = [_clean_item(s) for s in shorts]
            out["questions"]["short_answer"] = shorts
            out["counts"]["short_answer"] = len(shorts)

        if "mcq" in req.targets:
            base_inputs = prompts if prompts else clean_sentences  # fallback
            mcqs = make_mcq_questions(base_inputs, lang, limit=req.num_questions)     ### FIX
            mcqs = [_clean_item(m) for m in mcqs]
            out["questions"]["mcq"] = mcqs
            out["counts"]["mcq"] = len(mcqs)

        # Evaluate questions
        scores = evaluate_batch(out["questions"])
        out["evaluation"] = scores

        print(f"DEBUG: Requested format = '{req.output_format}'")  # Debug output
        
        # Return appropriate format
        if req.output_format and req.output_format.lower() == "text":
            print("DEBUG: Returning TEXT format")  # Debug output
            print(out)
            readable_output = format_questions_readable(out)
            return PlainTextResponse(readable_output)
        else:
            print("DEBUG: Returning JSON format")  # Debug output
            return JSONResponse(out)

    except Exception as e:
        print(f"Error generating questions: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)
    
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
