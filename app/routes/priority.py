from fastapi import APIRouter
from services.priority import calculate_priority_scores

router = APIRouter()

@router.get("/priority-topics/{subject_id}")
async def get_priority_topics(subject_id: int):
    """
    Get ranked topics by priority score for a given subject.
    Priority score = (frequency * 0.6) + (avg_marks_per_year * 0.4)
    """
    # Note: subject_id is currently ignored, using mock data
    # In future, this would filter by actual subject_id from database
    topics = calculate_priority_scores()
    return topics
