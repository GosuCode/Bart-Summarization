from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from services.priority import calculate_priority_scores
from db import get_db
from typing import Optional

router = APIRouter()

@router.get("/priority-topics/{subject_id}")
async def get_priority_topics(
    subject_id: int, 
    frequency_weight: Optional[float] = Query(0.6, description="Weight for frequency in scoring"),
    marks_weight: Optional[float] = Query(0.4, description="Weight for marks in scoring"),
    db: Session = Depends(get_db)
):
    """
    Get ranked topics by priority score for a given subject.
    Priority score = (frequency * frequency_weight) + (avg_marks_per_year * marks_weight)
    
    Weights are automatically normalized if they don't sum to 1.0.
    """
    result = calculate_priority_scores(db, subject_id, frequency_weight, marks_weight)
    return result
