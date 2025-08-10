from typing import List, Dict
from collections import defaultdict
from sqlalchemy.orm import Session
from models import Question
from sqlalchemy import func

def calculate_priority_scores(db: Session, subject_id: int, frequency_weight: float = 0.6, marks_weight: float = 0.4) -> Dict:
    """
    Calculate priority scores for topics using weighted formula:
    priority_score = (frequency * frequency_weight) + (avg_marks_per_year * marks_weight)
    
    Returns dict with topics list and optional warning about normalized weights.
    """
    # Normalize weights if they don't sum to 1.0
    total_weight = frequency_weight + marks_weight
    warning = None
    
    if abs(total_weight - 1.0) > 0.001:  # Allow small floating point precision errors
        normalized_freq_weight = frequency_weight / total_weight
        normalized_marks_weight = marks_weight / total_weight
        warning = f"Weights normalized from ({frequency_weight}, {marks_weight}) to ({normalized_freq_weight:.3f}, {normalized_marks_weight:.3f})"
        frequency_weight = normalized_freq_weight
        marks_weight = normalized_marks_weight
    
    # Query questions grouped by topic with aggregation
    results = db.query(
        Question.topic,
        func.count(Question.id).label('frequency'),
        func.avg(Question.marks).label('avg_marks')
    ).filter(
        Question.subject_id == subject_id
    ).group_by(
        Question.topic
    ).all()
    
    # If no results found for this subject_id, return empty response
    if not results:
        return {
            "topics": [],
            "weights_used": {
                "frequency_weight": round(frequency_weight, 3),
                "marks_weight": round(marks_weight, 3)
            },
            "message": f"No questions found for subject_id: {subject_id}"
        }
    
    priority_scores = []
    
    for result in results:
        topic = result.topic
        frequency = result.frequency
        avg_marks_per_year = float(result.avg_marks)
        
        priority_score = (frequency * frequency_weight) + (avg_marks_per_year * marks_weight)
        
        priority_scores.append({
            "topic": topic,
            "frequency": frequency,
            "avg_marks_per_year": round(avg_marks_per_year, 2),
            "priority_score": round(priority_score, 3)
        })
    
    # Sort by priority score descending
    priority_scores.sort(key=lambda x: x["priority_score"], reverse=True)
    
    response = {
        "topics": priority_scores,
        "weights_used": {
            "frequency_weight": round(frequency_weight, 3),
            "marks_weight": round(marks_weight, 3)
        }
    }
    
    if warning:
        response["warning"] = warning
    
    return response
