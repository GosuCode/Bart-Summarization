from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.flashcard_service import MCQGenerator
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize the new MCQ generator service
mcq_generator = MCQGenerator()

class MCQRequest(BaseModel):
    text: str
    num_questions: int = 5

class MCQResponse(BaseModel):
    mcqs: list
    total_questions: int
    text_length: int
    chunks_processed: int
    processing_time: float
    service: str

@router.post("/generate", response_class=JSONResponse)
async def generate_mcq(req: MCQRequest):
    """Generate multiple choice questions from text using the new flashcards service"""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Input text is empty")
    
    if req.num_questions < 1 or req.num_questions > 20:
        raise HTTPException(status_code=400, detail="Number of questions must be between 1 and 20")
    
    try:
        import time
        start_time = time.time()
        
        # Convert num_questions to questions_per_chunk for the new service
        # Estimate chunks needed based on text length
        words = len(req.text.split())
        questions_per_chunk = max(1, min(req.num_questions, 5))  # Cap at 5 per chunk
        
        # Generate MCQs using the new service
        mcqs = mcq_generator.generate_mcqs(req.text, questions_per_chunk)
        
        # Limit to requested number of questions
        mcqs = mcqs[:req.num_questions]
        
        processing_time = time.time() - start_time
        
        # Calculate chunks processed
        chunks_processed = max(1, (words // 400) + (1 if words % 400 > 0 else 0))
        
        return MCQResponse(
            mcqs=mcqs,
            total_questions=len(mcqs),
            text_length=len(req.text),
            chunks_processed=chunks_processed,
            processing_time=round(processing_time, 3),
            service="Flashcards MCQ Service"
        )
        
    except Exception as e:
        logger.error(f"Error generating MCQ: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating MCQ: {str(e)}")

@router.get("/health")
async def mcq_health():
    """Health check for MCQ service"""
    return {
        "status": "healthy",
        "service": "MCQ Service (Flashcards Integration)",
        "flashcard_service_ready": True,
        "features": [
            "Text chunking with overlap",
            "T5-based question generation",
            "Smart distractor generation",
            "Fallback to basic generation"
        ]
    }
