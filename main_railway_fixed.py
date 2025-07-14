from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn

app = FastAPI(title="DOST AI - Railway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "🎉 DOST AI is LIVE on Railway!", 
        "status": "success",
        "port": os.getenv("PORT", "8000")
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "platform": "Railway", 
        "port": os.getenv("PORT", "8000"),
        "service": "dost-ai"
    }

@app.get("/ping")
async def ping():
    return {"ping": "pong"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info") 