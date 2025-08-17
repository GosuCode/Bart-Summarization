from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.gemini_service import gemini_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class MCQRequest(BaseModel):
    text: str
    num_questions: int = 5

class MCQResponse(BaseModel):
    questions: list
    total_questions: int
    text_length: int
    processing_method: str

@router.post("/generate", response_class=JSONResponse)
async def generate_mcq(req: MCQRequest):
    """Generate multiple choice questions from text using Gemini API"""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Input text is empty")
    
    if req.num_questions < 1 or req.num_questions > 20:
        raise HTTPException(status_code=400, detail="Number of questions must be between 1 and 20")
    
    try:
        # Use Gemini API for MCQ generation
        result = gemini_service.generate_mcqs(req.text, req.num_questions)
        
        return MCQResponse(
            questions=result.get("mcqs", []),
            total_questions=result.get("total_mcqs", 0),
            text_length=result.get("text_length", len(req.text)),
            processing_method=result.get("processing_method", "gemini_api")
        )
        
    except Exception as e:
        logger.error(f"Error generating MCQ: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating MCQ: {str(e)}")

@router.get("/health")
async def mcq_health():
    """Health check for MCQ service"""
    return {
        "status": "healthy",
        "gemini_available": gemini_service.client is not None,
        "service": "mcq_generation"
    }
