# test_formatter.py - Simple test
from utils.formatter import format_questions_readable

# Test with your example data
test_data = {
  "language": "en",
  "counts": {
    "cloze": 5,
    "short_answer": 1,
    "mcq": 1
  },
  "questions": {
    "cloze": [
      {
        "question": "The cat (Felis catus), also referred to as the ____ cat or house cat, is a small domesticated carnivorous mammal.",
        "answer": "domestic"
      },
      {
        "question": "It is the only domesticated ____ of the family Felidae.",
        "answer": "species"
      }
    ],
    "short_answer": [
      {
        "question": "Population control includes spaying and neutering",
        "answer_type": "short"
      }
    ],
    "mcq": [
      {
        "question": "Population control includes spaying and neutering?",
        "choices": [
          "spaying",
          "screening",
          "migration",
          "education"
        ],
        "answer": "spaying"
      }
    ]
  },
  "evaluation": {
    "cloze": 0.9504761904761906,
    "short_answer": 0.8,
    "mcq": 0.8
  }
}

print(format_questions_readable(test_data))