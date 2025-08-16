from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel
from transformers import BartForConditionalGeneration, BartTokenizerFast
import torch
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

enabled_device = "cuda" if torch.cuda.is_available() else "cpu"
DEVICE = os.getenv("DEVICE", enabled_device)

# Load BART model from Hugging Face instead of local directory
try:
    logger.info("🔄 Loading BART model from Hugging Face...")
    tokenizer = BartTokenizerFast.from_pretrained("sshleifer/distilbart-cnn-12-6")
    model = BartForConditionalGeneration.from_pretrained("sshleifer/distilbart-cnn-12-6").to(DEVICE)
    model.eval()
    model_loaded = True
    logger.info(f"✅ BART model: WORKING on {DEVICE}")
except Exception as e:
    logger.error(f"❌ BART model: FAILED to load - {e}")
    model_loaded = False
    tokenizer = None
    model = None

class SummarizationRequest(BaseModel):
    text: str
    max_length: int = 128
    num_beams: int = 4

@router.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML interface"""
    return FileResponse("./static/index.html")

@router.post("/summarize", response_class=JSONResponse)
async def summarize(req: SummarizationRequest):
    """Generate text summary using BART model"""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Input text is empty")
    
    if not model_loaded or not tokenizer or not model:
        raise HTTPException(status_code=503, detail="BART model not available. Please check model configuration.")
    
    try:
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
        
        return {
            "summary": summary,
            "processing_method": "bart_generation",
            "model_available": True
        }
    except Exception as e:
        logger.error(f"Error during summarization: {e}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")
