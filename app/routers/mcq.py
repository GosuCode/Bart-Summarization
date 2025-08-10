from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.mcq import MCQGenerator
from transformers import BartForConditionalGeneration, BartTokenizerFast
import torch
import os

# Router instance
router = APIRouter()

# Model setup (reuse from summarization)
enabled_device = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_DIR = os.getenv("MODEL_DIR", "./model")
DEVICE = os.getenv("DEVICE", enabled_device)

# Load model and tokenizer
try:
    tokenizer = BartTokenizerFast.from_pretrained(MODEL_DIR)
    model = BartForConditionalGeneration.from_pretrained(MODEL_DIR).to(DEVICE)
    model.eval()
    model_loaded = True
except Exception as e:
    print(f"Warning: Could not load BART model: {e}")
    model_loaded = False
    tokenizer = None
    model = None

# Pydantic models
class MCQRequest(BaseModel):
    text: str
    num_questions: int = 5
    use_bart: bool = False

class MCQResponse(BaseModel):
    questions: list
    total_questions: int
    text_length: int
    model_used: str

# Routes
@router.post("/generate", response_class=JSONResponse)
async def generate_mcq(req: MCQRequest):
    """Generate multiple choice questions from text"""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Input text is empty")
    
    if req.num_questions < 1 or req.num_questions > 20:
        raise HTTPException(status_code=400, detail="Number of questions must be between 1 and 20")
    
    try:
        if req.use_bart and model_loaded:
            # Use BART model for generation
            questions = MCQGenerator.generate_mcq_with_bart(
                req.text, 
                req.num_questions, 
                model, 
                tokenizer
            )
            model_used = "BART"
        else:
            # Use basic generation
            questions = MCQGenerator.generate_mcq_from_text(req.text, req.num_questions)
            model_used = "Basic" if not req.use_bart else "Basic (BART not available)"
        
        return MCQResponse(
            questions=questions,
            total_questions=len(questions),
            text_length=len(req.text),
            model_used=model_used
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating MCQ: {str(e)}")

@router.get("/health")
async def mcq_health():
    """Health check for MCQ service"""
    return {
        "status": "healthy",
        "model_loaded": model_loaded,
        "device": DEVICE
    }
