from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel
from transformers import BartForConditionalGeneration, BartTokenizerFast
import torch
import os

# Router instance
router = APIRouter()

# Model setup
enabled_device = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_DIR = os.getenv("MODEL_DIR", "./model")
DEVICE = os.getenv("DEVICE", enabled_device)

# Load model and tokenizer
tokenizer = BartTokenizerFast.from_pretrained(MODEL_DIR)
model = BartForConditionalGeneration.from_pretrained(MODEL_DIR).to(DEVICE)
model.eval()

# Pydantic models
class SummarizationRequest(BaseModel):
    text: str
    max_length: int = 128
    num_beams: int = 4

# Routes
@router.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML interface"""
    return FileResponse("./static/index.html")

@router.post("/summarize", response_class=JSONResponse)
async def summarize(req: SummarizationRequest):
    """Generate text summary using BART model"""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Input text is empty")
    
    inputs = tokenizer(
        req.text, return_tensors="pt", truncation=True, max_length=1024
    ).to(DEVICE)
    
    generated_ids = model.generate(
        **inputs,
        max_length=req.max_length,
        num_beams=req.num_beams,
        length_penalty=2.0,
        early_stopping=True
    )
    
    summary = tokenizer.decode(
        generated_ids[0],
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    )
    
    return {"summary": summary}
