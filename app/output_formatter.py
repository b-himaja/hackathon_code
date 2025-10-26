# Add this new file: output_formatter.py
from typing import List, Dict

def format_cloze_questions(clozes: List[Dict]) -> str:
    output = "=== CLOZE QUESTIONS ===\n\n"
    for i, cloze in enumerate(clozes, 1):
        output += f"{i}. {cloze['question']}\n"
        output += f"   Answer: {cloze['answer']}\n\n"
    return output

def format_mcq_questions(mcqs: List[Dict]) -> str:
    output = "=== MULTIPLE CHOICE QUESTIONS ===\n\n"
    for i, mcq in enumerate(mcqs, 1):
        output += f"{i}. {mcq['question']}\n"
        for j, choice in enumerate(mcq['choices'], 1):
            output += f"   {chr(64+j)}. {choice}\n"
        output += f"   Correct answer: {mcq['answer']}\n\n"
    return output

def format_short_answer_questions(questions: List[Dict]) -> str:
    output = "=== SHORT ANSWER QUESTIONS ===\n\n"
    for i, q in enumerate(questions, 1):
        output += f"{i}. {q['question']}\n\n"
    return output

def format_all_questions(clozes: List[Dict], mcqs: List[Dict], short_answers: List[Dict]) -> str:
    output = "QUESTIONS GENERATED\n"
    output += "=" * 50 + "\n\n"
    
    output += format_cloze_questions(clozes)
    output += format_mcq_questions(mcqs) 
    output += format_short_answer_questions(short_answers)
    
    output += f"\nTotal questions generated:\n"
    output += f"- Cloze: {len(clozes)}\n"
    output += f"- Multiple Choice: {len(mcqs)}\n"
    output += f"- Short Answer: {len(short_answers)}\n"
    
    return output