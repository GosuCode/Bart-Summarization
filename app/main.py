from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
import logging

from routers import summarization, mcq, file_summarization, flashcards
from routes import priority

from database import init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BART Summarization Service (Memory Optimized)",
    description="A FastAPI-based web service for text summarization using BART models with lazy loading",
    version="1.0.0"
)
 
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    """Startup event - only initialize database, not models"""
    logger.info("🚀 Starting BART Summarization Service (Memory Optimized)")
    logger.info("📚 Models will be loaded on-demand to save memory")
    
    try:
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")

app.include_router(summarization.router, prefix="/api/v1", tags=["summarization"])
app.include_router(mcq.router, prefix="/api/v1/mcq", tags=["mcq"])
app.include_router(file_summarization.router, prefix="/api/v1/files", tags=["file_processing"])
app.include_router(flashcards.router, prefix="/api/v1/flashcards", tags=["flashcards"])
app.include_router(priority.router, tags=["priority"])

@app.get("/")
async def read_root():
    return {
        "message": "BART Summarization Service (Memory Optimized)",
        "version": "1.0.0",
        "mode": "lazy_loading",
        "memory_optimized": True
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "mode": "memory_optimized"}

@app.get("/memory")
async def memory_info():
    """Get memory usage information"""
    try:
        from services.model_manager import model_manager
        return model_manager.get_memory_info()
    except Exception as e:
        return {"error": f"Failed to get memory info: {e}"}

@app.post("/memory/unload")
async def unload_models():
    """Unload models to free memory"""
    try:
        from services.model_manager import model_manager
        model_manager.unload_models()
        return {"message": "Models unloaded successfully", "memory_freed": True}
    except Exception as e:
        return {"error": f"Failed to unload models: {e}"}

@app.get("/memory")
async def memory_info():
    """Get memory usage information"""
    from services.model_manager import model_manager
    return model_manager.get_memory_info()

@app.post("/memory/unload")
async def unload_models():
    """Unload models to free memory"""
    from services.model_manager import model_manager
    model_manager.unload_models()
    return {"message": "Models unloaded successfully"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port, 
        reload=True
    )
