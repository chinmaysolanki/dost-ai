from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import uvicorn
from openai import OpenAI
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="DOST AI - Your AI Friend", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage
conversations: List[Dict[str, Any]] = []
users: Dict[str, Dict[str, Any]] = {}

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    user_id: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: datetime
    tokens_used: Optional[int] = None

class UserCreate(BaseModel):
    name: str
    email: str
    preferences: Optional[Dict[str, Any]] = {}

def get_ai_response(message: str, user_context: Dict = None) -> tuple[str, int]:
    """Get AI response from OpenAI"""
    try:
        # Create context-aware prompt
        system_prompt = """You are DOST, a friendly and helpful AI assistant. You are designed to be:
        - Supportive and encouraging
        - Helpful with tasks and questions
        - Conversational and engaging
        - Proactive in offering assistance
        
        Keep responses concise but warm. You're like a helpful friend who's always there to assist."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using GPT-3.5 for cost efficiency
            messages=messages,
            max_tokens=150,  # Keep responses concise
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        return ai_response, tokens_used
        
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        # Fallback response if OpenAI fails
        return f"I'm having trouble connecting to my AI brain right now. Here's what I heard: '{message}'. Please try again in a moment!", 0

@app.get("/")
async def root():
    return {
        "message": "🤖 DOST AI - Your AI Friend is LIVE with OpenAI!", 
        "status": "success",
        "ai_enabled": True,
        "model": "gpt-3.5-turbo"
    }

@app.get("/health")
async def health():
    # Check if OpenAI API key is available
    openai_status = "configured" if os.getenv("OPENAI_API_KEY") else "missing"
    
    return {
        "status": "healthy", 
        "platform": "Render", 
        "ai_enabled": openai_status == "configured",
        "openai_status": openai_status,
        "service": "dost-ai-v2"
    }

@app.post("/users", response_model=Dict[str, Any])
async def create_user(user: UserCreate):
    """Create a new user"""
    try:
        user_id = f"user_{len(users) + 1}"
        users[user_id] = {
            "id": user_id,
            "name": user.name,
            "email": user.email,
            "preferences": user.preferences,
            "created_at": datetime.now(),
            "total_conversations": 0
        }
        
        logger.info(f"Created user: {user_id}")
        return {"user_id": user_id, "message": "User created successfully"}
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create user")

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    """Get user information"""
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    return users[user_id]

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with DOST AI using OpenAI"""
    try:
        # Get user context
        user_context = users.get(request.user_id, {})
        
        # Get AI response
        ai_response, tokens_used = get_ai_response(request.message, user_context)
        
        # Generate conversation ID
        conversation_id = request.conversation_id or f"conv_{len(conversations) + 1}"
        
        # Store conversation
        conversation = {
            "id": conversation_id,
            "user_id": request.user_id,
            "user_message": request.message,
            "ai_response": ai_response,
            "tokens_used": tokens_used,
            "timestamp": datetime.now()
        }
        conversations.append(conversation)
        
        # Update user stats
        if request.user_id in users:
            users[request.user_id]["total_conversations"] += 1
        
        logger.info(f"AI chat processed for user {request.user_id}, tokens: {tokens_used}")
        
        return ChatResponse(
            response=ai_response,
            conversation_id=conversation_id,
            timestamp=conversation["timestamp"],
            tokens_used=tokens_used
        )
        
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process chat")

@app.get("/conversations/{user_id}")
async def get_conversations(user_id: str):
    """Get user's conversation history"""
    user_conversations = [
        {
            "id": conv["id"],
            "user_message": conv["user_message"],
            "ai_response": conv["ai_response"],
            "tokens_used": conv["tokens_used"],
            "timestamp": conv["timestamp"]
        }
        for conv in conversations 
        if conv["user_id"] == user_id
    ]
    return {"conversations": user_conversations}

@app.get("/status")
async def get_status():
    """Get system status"""
    openai_configured = bool(os.getenv("OPENAI_API_KEY"))
    
    return {
        "status": "running",
        "version": "2.0.0 (AI-enabled)",
        "features": {
            "ai_chat": openai_configured,
            "user_management": True,
            "conversation_history": True,
            "token_tracking": True
        },
        "stats": {
            "total_users": len(users),
            "total_conversations": len(conversations),
            "total_tokens_used": sum(conv.get("tokens_used", 0) for conv in conversations)
        },
        "openai_status": "configured" if openai_configured else "missing_api_key"
    }

@app.get("/ping")
async def ping():
    return {"ping": "pong", "ai_enabled": bool(os.getenv("OPENAI_API_KEY"))}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info") 