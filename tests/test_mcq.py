import pytest
from app.services.mcq import MCQGenerator

def test_mcq_generation():
    """Test MCQ generation from text"""
    text = "Machine learning is a subset of artificial intelligence. It involves training algorithms on data to make predictions or decisions. Deep learning uses neural networks with multiple layers."
    
    questions = MCQGenerator.generate_mcq_from_text(text, num_questions=3)
    
    assert len(questions) == 3
    assert all(isinstance(q, dict) for q in questions)
    assert all('question' in q for q in questions)
    assert all('options' in q for q in questions)
    assert all('correct_answer_index' in q for q in questions)

def test_mcq_with_short_text():
    """Test MCQ generation with short text"""
    text = "Short text."
    questions = MCQGenerator.generate_mcq_from_text(text, num_questions=5)
    
    # Should handle short text gracefully
    assert len(questions) <= 5

def test_mcq_options_structure():
    """Test that MCQ options are properly structured"""
    text = "This is a test sentence for MCQ generation."
    questions = MCQGenerator.generate_mcq_from_text(text, num_questions=1)
    
    if questions:
        question = questions[0]
        assert len(question['options']) == 4  # 1 correct + 3 incorrect
        assert question['correct_answer_index'] < len(question['options'])
        assert question['correct_answer_index'] >= 0
