from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Request and Response models
class MCQRequest(BaseModel):
    text: str
    num_questions: int = 5

class MCQ(BaseModel):
    question: str
    options: List[str]
    answer: str

class MCQResponse(BaseModel):
    mcqs: List[MCQ]
    total_questions: int
    text_length: int
    processing_method: str
    service: str

def generate_simple_mcqs(text: str, num_questions: int) -> List[MCQ]:
    """Generate simple MCQs without heavy AI models"""
    import re
    import random
    
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    mcqs = []
    
    for i in range(min(num_questions, len(sentences))):
        sentence = sentences[i]
        words = [w for w in sentence.split() if len(w) > 3]
        
        if len(words) < 3:
            continue
        
        # Create a meaningful question
        question = f"What is the main topic discussed in: \"{sentence[:100]}...\"?"
        
        # Use key words as options
        options = [
            words[0] if words else "Topic A",
            words[len(words)//2] if len(words) > 1 else "Topic B",
            words[-1] if len(words) > 2 else "Topic C",
            "None of the above"
        ]
        
        # Shuffle options
        random.shuffle(options)
        
        mcqs.append(MCQ(
            question=question,
            options=options,
            answer=options[0]  # First option is correct
        ))
    
    return mcqs

@router.post("/generate", response_model=MCQResponse)
async def generate_mcq(request: MCQRequest):
    """Generate multiple-choice questions from academic text"""
    
    try:
        # Clean and process text
        text = request.text.strip()
        if not text:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(text) < 50:
            raise HTTPException(status_code=400, detail="Text must be at least 50 characters long")
        
        # Generate MCQs
        mcqs = generate_simple_mcqs(text, request.num_questions)
        
        if not mcqs:
            raise HTTPException(
                status_code=400, 
                detail="Could not generate MCQs from the provided text. Please try with longer text."
            )
        
        return MCQResponse(
            mcqs=mcqs,
            total_questions=len(mcqs),
            text_length=len(text),
            processing_method="simple_generation",
            service="FastAPI MCQ Service (Simple)"
        )
        
    except Exception as e:
        logger.error(f"Error generating MCQs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate MCQs: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "MCQ Generation Service",
        "models_loaded": {
            "simple_generator": True
        },
        "processing_method": "simple_generation"
    }
