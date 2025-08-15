from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel
from transformers import BartForConditionalGeneration, BartTokenizerFast
import torch
import os
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

enabled_device = "cuda" if torch.cuda.is_available() else "cpu"
DEVICE = os.getenv("DEVICE", enabled_device)

# Try to load the BART model from Hugging Face (more reliable than local files)
try:
    logger.info("🔄 Loading BART model from Hugging Face...")
    tokenizer = BartTokenizerFast.from_pretrained("facebook/bart-base")
    model = BartForConditionalGeneration.from_pretrained("facebook/bart-base").to(DEVICE)
    model.eval()
    model_loaded = True
    logger.info(f"✅ BART model: WORKING on {DEVICE}")
except Exception as e:
    logger.info(f"❌ BART model: NOT WORKING - {e}")
    model_loaded = False
    tokenizer = None
    model = None

class SummarizationRequest(BaseModel):
    text: str
    max_length: int = 128
    num_beams: int = 4

def generate_fallback_summary(text: str, max_length: int = 128) -> str:
    """Generate a fallback summary when BART model is not available"""
    # Clean the text
    cleaned_text = re.sub(r'\s+', ' ', text.strip())
    
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', cleaned_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Take first few sentences as summary (simple extractive summarization)
    if len(sentences) <= 3:
        return ' '.join(sentences)
    
    # Calculate target length and select sentences
    target_length = max_length
    selected_sentences = []
    current_length = 0
    
    for sentence in sentences:
        if current_length + len(sentence) <= target_length:
            selected_sentences.append(sentence)
            current_length += len(sentence)
        else:
            break
    
    # If we didn't get enough content, add more sentences
    if len(selected_sentences) < 2 and len(sentences) > 2:
        selected_sentences = sentences[:2]
    
    return ' '.join(selected_sentences)

@router.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML interface"""
    return FileResponse("./static/index.html")

@router.post("/summarize", response_class=JSONResponse)
async def summarize(req: SummarizationRequest):
    """Generate text summary using BART model or fallback"""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Input text is empty")
    
    try:
        if model_loaded:
            # Use BART model for summarization
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
                "processing_method": "BART Model (AI)",
                "model_available": True
            }
        else:
            # Use fallback summarization
            summary = generate_fallback_summary(req.text, req.max_length)
            
            return {
                "summary": summary,
                "processing_method": "Fallback (Extractive)",
                "model_available": False
            }
        
    except Exception as e:
        # Final fallback: return first few sentences
        summary = generate_fallback_summary(req.text, req.max_length)
        
        return {
            "summary": summary,
            "processing_method": "Emergency Fallback",
            "model_available": False,
            "error": str(e)
        }

@router.get("/health")
async def health_check():
    """Health check for summarization service"""
    return {
        "status": "healthy" if model_loaded else "degraded",
        "model_loaded": model_loaded,
        "device": DEVICE
    }
