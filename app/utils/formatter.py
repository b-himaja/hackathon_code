# utils/formatter.py - Ensure this exists and works
from typing import Dict, List

def format_questions_readable(data: Dict) -> str:
    """Format all questions in a human-readable text format"""
    output = []
    output.append(f"LANGUAGE: {data.get('language', 'unknown').upper()}")
    output.append("=" * 50)
    output.append("")
    
    # Cloze Questions
    cloze_questions = data.get('questions', {}).get('cloze', [])
    if cloze_questions:
        output.append("CLOZE QUESTIONS:")
        output.append("-" * 30)
        for i, q in enumerate(cloze_questions, 1):
            output.append(f"{i}. {q.get('question', '')}")
            output.append(f"   Answer: {q.get('answer', '')}")
            output.append("")
    
    # Short Answer Questions
    short_questions = data.get('questions', {}).get('short_answer', [])
    if short_questions:
        output.append("SHORT ANSWER QUESTIONS:")
        output.append("-" * 30)
        for i, q in enumerate(short_questions, 1):
            output.append(f"{i}. {q.get('question', '')}")
            output.append("")
    
    # Multiple Choice Questions
    mcq_questions = data.get('questions', {}).get('mcq', [])
    if mcq_questions:
        output.append("MULTIPLE CHOICE QUESTIONS:")
        output.append("-" * 30)
        for i, q in enumerate(mcq_questions, 1):
            output.append(f"{i}. {q.get('question', '')}")
            choices = q.get('choices', [])
            for j, choice in enumerate(choices):
                output.append(f"   {chr(65 + j)}. {choice}")
            output.append(f"   Correct Answer: {q.get('answer', '')}")
            output.append("")
    
    # Evaluation Scores
    evaluation = data.get('evaluation', {})
    if evaluation:
        output.append("EVALUATION SCORES:")
        output.append("-" * 30)
        for question_type, score in evaluation.items():
            percentage = f"{score * 100:.1f}"
            output.append(f"{question_type}: {percentage}%")
        output.append("")
    
    # Question Counts
    counts = data.get('counts', {})
    if counts:
        output.append("QUESTION COUNTS:")
        output.append("-" * 30)
        for question_type, count in counts.items():
            plural = "s" if count != 1 else ""
            output.append(f"{question_type}: {count} question{plural}")
    
    return "\n".join(output)