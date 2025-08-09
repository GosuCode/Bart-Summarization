import pytest
from app.models import Question

def test_question_creation():
    """Test Question model creation with required fields"""
    question = Question(
        topic="Machine Learning",
        marks=10.0,
        year=2024
    )
    
    assert question.topic == "Machine Learning"
    assert question.marks == 10.0
    assert question.year == 2024
    assert question.id is None  # Not yet saved to DB

def test_question_repr():
    """Test Question model string representation"""
    question = Question(
        topic="Python Programming",
        marks=15.0,
        year=2023
    )
    
    repr_str = repr(question)
    assert "Question" in repr_str
    assert "Python Programming" in repr_str
    assert "15.0" in repr_str
    assert "2023" in repr_str
