from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from services.flashcard_service import FlashcardGenerator, MCQGenerator
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
flashcard_generator = FlashcardGenerator()
mcq_generator = MCQGenerator()

class FlashcardRequest(BaseModel):
    text: str = Field(..., description="Input text to generate flashcards from")
    questions_per_chunk: int = Field(default=3, ge=1, le=10, description="Number of questions per text chunk")

class FlashcardResponse(BaseModel):
    flashcards: List[Dict[str, str]]
    total_flashcards: int
    text_length: int
    chunks_processed: int
    processing_time: Optional[float] = None

class MCQRequest(BaseModel):
    text: str = Field(..., description="Input text to generate MCQs from")
    questions_per_chunk: int = Field(default=3, ge=1, le=10, description="Number of questions per text chunk")

class MCQResponse(BaseModel):
    mcqs: List[Dict]
    total_mcqs: int
    text_length: int
    chunks_processed: int
    processing_time: Optional[float] = None

@router.post("/flashcards", response_model=FlashcardResponse)
async def generate_flashcards(request: FlashcardRequest):
    """
    Generate flashcards from long text input using chunking strategy
    
    The service will:
    1. Split text into ~400-word chunks with 50-word overlap
    2. Generate 3-5 question-answer pairs per chunk
    3. Return aggregated flashcards
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty")
    
    if len(request.text) < 50:
        raise HTTPException(status_code=400, detail="Input text must be at least 50 characters long")
    
    try:
        import time
        start_time = time.time()
        
        # Generate flashcards
        flashcards = flashcard_generator.generate_flashcards(
            request.text, 
            request.questions_per_chunk
        )
        
        processing_time = time.time() - start_time
        
        # Calculate chunks processed using the actual chunking logic
        from services.flashcard_service import TextChunker
        chunks = TextChunker.chunk_text(request.text)
        chunks_processed = len(chunks)
        
        return FlashcardResponse(
            flashcards=flashcards,
            total_flashcards=len(flashcards),
            text_length=len(request.text),
            chunks_processed=chunks_processed,
            processing_time=round(processing_time, 3)
        )
        
    except Exception as e:
        logger.error(f"Error generating flashcards: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate flashcards: {str(e)}")

@router.post("/mcqs", response_model=MCQResponse)
async def generate_mcqs(request: MCQRequest):
    """
    Generate multiple choice questions from long text input using chunking strategy
    
    The service will:
    1. Split text into ~400-word chunks with 50-word overlap
    2. Generate 3-5 question-answer pairs per chunk
    3. Convert each Q&A pair to MCQ with 3 plausible distractors
    4. Return aggregated MCQs
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty")
    
    if len(request.text) < 50:
        raise HTTPException(status_code=400, detail="Input text must be at least 50 characters long")
    
    try:
        import time
        start_time = time.time()
        
        # Generate MCQs
        mcqs = mcq_generator.generate_mcqs(
            request.text, 
            request.questions_per_chunk
        )
        
        processing_time = time.time() - start_time
        
        # Calculate chunks processed using the actual chunking logic
        from services.flashcard_service import TextChunker
        chunks = TextChunker.chunk_text(request.text)
        chunks_processed = len(chunks)
        
        return MCQResponse(
            mcqs=mcqs,
            total_mcqs=len(mcqs),
            text_length=len(request.text),
            chunks_processed=chunks_processed,
            processing_time=round(processing_time, 3)
        )
        
    except Exception as e:
        logger.error(f"Error generating MCQs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate MCQs: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check for flashcards and MCQ service"""
    return {
        "status": "healthy",
        "service": "flashcards-mcq",
        "flashcard_generator_ready": flashcard_generator.model is not None,
        "mcq_generator_ready": True
    }

@router.get("/supported-formats")
async def get_supported_formats():
    """Get information about supported input formats and limitations"""
    return {
        "input_formats": ["plain_text", "long_text"],
        "max_text_length": "No limit (handled by chunking)",
        "chunk_size": "Dynamic (20-400 words based on text length)",
        "chunk_overlap": "Dynamic (5-50 words based on chunk size)",
        "questions_per_chunk_range": [1, 10],
        "default_questions_per_chunk": 3,
        "features": [
            "Automatic text chunking",
            "Context preservation with overlap",
            "T5-based question generation",
            "Fallback to basic generation",
            "Smart distractor generation for MCQs"
        ]
    }
