from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from transformers import BartForConditionalGeneration, BartTokenizerFast
import PyPDF2
from docx import Document
import io
import re
import torch
import os
from typing import List, Dict, Any
import logging

router = APIRouter()

enabled_device = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_DIR = os.getenv("MODEL_DIR", "./model")
DEVICE = os.getenv("DEVICE", enabled_device)

tokenizer = BartTokenizerFast.from_pretrained(MODEL_DIR)
model = BartForConditionalGeneration.from_pretrained(MODEL_DIR).to(DEVICE)
model.eval()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """
    Clean extracted text by removing extra whitespace, line breaks, and unnecessary symbols.
    """
    # Remove extra whitespace and normalize line breaks
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}]', '', text)
    
    # Split into sentences and rejoin with proper spacing
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Rejoin with proper spacing
    cleaned_text = ' '.join(sentences)
    
    return cleaned_text

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file content."""
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text_content = []
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            if page_text.strip():
                text_content.append(page_text)
        
        return '\n\n'.join(text_content)
    
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to extract text from PDF: {str(e)}")

def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file content."""
    try:
        docx_file = io.BytesIO(file_content)
        doc = Document(docx_file)
        
        text_content = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_content.append(paragraph.text)
        
        return '\n\n'.join(text_content)
    
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to extract text from DOCX: {str(e)}")

def chunk_text(text: str, max_length: int = 1000) -> List[str]:
    """Split text into chunks that fit within the summarizer's token limit."""
    # Split by sentences to maintain coherence
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_length:
            current_chunk += sentence + " "
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    
    # Add the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def summarize_text(text: str, max_length: int = 128) -> str:
    """Generate summary using BART model."""
    try:
        inputs = tokenizer(
            text, return_tensors="pt", truncation=True, max_length=1024
        ).to(DEVICE)
        
        generated_ids = model.generate(
            **inputs,
            max_length=max_length,
            num_beams=4,
            length_penalty=2.0,
            early_stopping=True
        )
        
        summary = tokenizer.decode(
            generated_ids[0],
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )
        
        return summary
    except Exception as e:
        logger.error(f"Error in summarization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

@router.post("/upload-and-summarize")
async def upload_and_summarize_file(
    file: UploadFile = File(...),
    max_length: int = 150,
    chunk_size: int = 1000
) -> Dict[str, Any]:
    """
    Upload a PDF or DOCX file, extract text, and generate a summary using BART.
    """
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Debug logging
        logger.info(f"Received file: {file.filename}, content_type: {file.content_type}")
        
        file_extension = file.filename.lower().split('.')[-1]
        logger.info(f"Detected file extension: {file_extension}")
        
        if file_extension not in ['pdf', 'docx']:
            raise HTTPException(
                status_code=400, 
                detail=f"Only PDF and DOCX files are supported. Received: {file_extension}"
            )
        
        # Read file content
        file_content = await file.read()
        logger.info(f"Processing file: {file.filename}, size: {len(file_content)} bytes")
        
        # Extract text based on file type
        if file_extension == 'pdf':
            extracted_text = extract_text_from_pdf(file_content)
        else:  # docx
            extracted_text = extract_text_from_docx(file_content)
        
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from the file")
        
        # Clean the extracted text
        cleaned_text = clean_text(extracted_text)
        logger.info(f"Extracted and cleaned text length: {len(cleaned_text)} characters")
        
        # Check if text needs chunking
        if len(cleaned_text) > chunk_size:
            logger.info("Text exceeds chunk size, processing in chunks")
            chunks = chunk_text(cleaned_text, chunk_size)
            
            # Summarize each chunk
            chunk_summaries = []
            for i, chunk in enumerate(chunks):
                logger.info(f"Processing chunk {i+1}/{len(chunks)}")
                chunk_summary = summarize_text(chunk, max_length)
                chunk_summaries.append(chunk_summary)
            
            # Combine chunk summaries
            combined_summary = ' '.join(chunk_summaries)
            
            # Final summarization of combined summaries
            final_summary = summarize_text(combined_summary, max_length)
            
        else:
            # Direct summarization
            final_summary = summarize_text(cleaned_text, max_length)
        
        # Prepare response
        response = {
            "filename": file.filename,
            "file_type": file_extension.upper(),
            "original_text_length": len(extracted_text),
            "cleaned_text_length": len(cleaned_text),
            "summary": final_summary,
            "summary_length": len(final_summary),
            "max_length": max_length,
            "chunk_size": chunk_size,
            "processing_method": "chunked" if len(cleaned_text) > chunk_size else "direct"
        }
        
        logger.info(f"Successfully processed {file.filename}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/extract-text")
async def extract_text_only(
    file: UploadFile = File(...)
) -> Dict[str, Any]:
    """
    Extract text from PDF or DOCX file without summarization.
    """
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_extension = file.filename.lower().split('.')[-1]
        if file_extension not in ['pdf', 'docx']:
            raise HTTPException(
                status_code=400, 
                detail="Only PDF and DOCX files are supported"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Extract text based on file type
        if file_extension == 'pdf':
            extracted_text = extract_text_from_pdf(file_content)
        else:  # docx
            extracted_text = extract_text_from_docx(file_content)
        
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from the file")
        
        # Clean the extracted text
        cleaned_text = clean_text(extracted_text)
        
        return {
            "filename": file.filename,
            "file_type": file_extension.upper(),
            "original_text": extracted_text,
            "cleaned_text": cleaned_text,
            "original_text_length": len(extracted_text),
            "cleaned_text_length": len(cleaned_text)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/supported-formats")
async def get_supported_formats() -> Dict[str, Any]:
    """Get information about supported file formats and processing capabilities."""
    return {
        "supported_formats": ["PDF", "DOCX"],
        "max_file_size": "50MB",
        "max_text_length": "Unlimited (chunked processing)",
        "processing_features": [
            "Text extraction",
            "Text cleaning",
            "BART summarization",
            "Chunked processing for large files",
            "Paragraph structure preservation"
        ]
    }
