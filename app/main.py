from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Load environment variables from .env file in app directory
load_dotenv("app/.env")

from routers import summarization, mcq, file_summarization, flashcards
from routes import priority

from database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (if needed)

app = FastAPI(
    title="BART Summarization Service",
    description="A FastAPI-based web service for text summarization using BART models",
    version="1.0.0",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="./static"), name="static")

app.include_router(summarization.router, prefix="/api/v1", tags=["summarization"])
app.include_router(mcq.router, prefix="/api/v1/mcq", tags=["mcq"])
app.include_router(file_summarization.router, prefix="/api/v1/files", tags=["file_processing"])
app.include_router(priority.router, tags=["priority"])
app.include_router(flashcards.router, prefix="/api/v1/flashcards", tags=["flashcards"])

@app.get("/")
async def read_root():
    return {"message": "BART Summarization Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port, 
        reload=True
    )
