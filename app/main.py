from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from routers import summarization, mcq, file_summarization
from routes import priority

from database import init_db

app = FastAPI(
    title="BART Summarization Service",
    description="A FastAPI-based web service for text summarization using BART models",
    version="1.0.0"
)
 
app.mount("/static", StaticFiles(directory="./static"), name="static")

@app.on_event("startup")
async def startup_event():
    init_db()

app.include_router(summarization.router, prefix="/api/v1", tags=["summarization"])
app.include_router(mcq.router, prefix="/api/v1/mcq", tags=["mcq"])
app.include_router(file_summarization.router, prefix="/api/v1/files", tags=["file_processing"])
app.include_router(priority.router, tags=["priority"])

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
