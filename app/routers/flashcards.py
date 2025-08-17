from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from services.gemini_service import gemini_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class FlashcardRequest(BaseModel):
    text: str
    total_questions: int = 3

class MCQRequest(BaseModel):
    text: str
    total_questions: int = 3

@router.post("/flashcards")
async def generate_flashcards(request: FlashcardRequest):
    """Generate flashcards from text using Gemini API"""
    try:
        result = gemini_service.generate_flashcards(
            request.text, 
            request.total_questions
        )
        return result
    except Exception as e:
        logger.error(f"Error generating flashcards: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mcqs")
async def generate_mcqs(request: MCQRequest):
    """Generate MCQs from text using Gemini API"""
    try:
        result = gemini_service.generate_mcqs(
            request.text, 
            request.total_questions
        )
        return result
    except Exception as e:
        logger.error(f"Error generating MCQs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Check if Gemini service is available"""
    return {
        "status": "healthy",
        "gemini_available": gemini_service.client is not None,
        "service": "flashcards_mcq"
    }
