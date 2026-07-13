"""The 6 check-in questions. 2 picked at random per session."""
import random

QUESTIONS = [
    {"id": 0, "text": "How would you rate your sleep, from 0 to 10?"},
    {"id": 1, "text": "Are you waking up feeling rested, or still tired?"},
    {"id": 2, "text": "Are there any recurring aches, tension spots, or symptoms you keep ignoring?"},
    {"id": 3, "text": "How do you feel after you eat — steady, or sluggish and crashing?"},
    {"id": 4, "text": "Have you noticed any new symptoms since starting or changing this medication?"},
    {"id": 5, "text": "Are there physical signs you're noticing — rash, dizziness, nausea, headache, or changes in weight?"},
]

_BY_ID = {q["id"]: q for q in QUESTIONS}


def pick_two():
    """2 distinct random questions from all 6."""
    return random.sample(QUESTIONS, 2)


def text_for(question_id):
    q = _BY_ID.get(question_id)
    return q["text"] if q else None
