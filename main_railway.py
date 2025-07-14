from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="DOST AI - Railway Test")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "🎉 DOST AI is LIVE on Railway!", "status": "success"}

@app.get("/health")
async def health():
    return {"status": "healthy", "platform": "Railway", "port": os.getenv("PORT", "8000")}

@app.get("/test")
async def test():
    return {
        "message": "Railway deployment successful!",
        "features": ["Basic API", "CORS enabled", "Health checks"],
        "next_steps": ["Add AI features", "Connect frontend", "Scale up"]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 