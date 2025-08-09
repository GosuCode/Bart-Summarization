from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

# Import routers
from routers import summarization

# Create FastAPI app instance
app = FastAPI(
    title="BART Summarization Service",
    description="A FastAPI-based web service for text summarization using BART models",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="./static"), name="static")

# Include routers
app.include_router(summarization.router, prefix="/api/v1", tags=["summarization"])

# Root endpoint
@app.get("/")
async def read_root():
    return {"message": "BART Summarization Service", "version": "1.0.0"}

# Health check
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
