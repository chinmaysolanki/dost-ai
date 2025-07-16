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

# Initialize OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

app = FastAPI(title="DOST AI - Your AI Friend (OpenRouter)", version="2.1.0")

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

# Available models on OpenRouter
AVAILABLE_MODELS = {
    "gpt-4o-mini": "openai/gpt-4o-mini",
    "gpt-4o": "openai/gpt-4o",
    "gpt-4": "openai/gpt-4",
    "gpt-3.5-turbo": "openai/gpt-3.5-turbo-16k",
    "claude-3-haiku": "anthropic/claude-3-haiku",
    "claude-3-sonnet": "anthropic/claude-3-sonnet",
    "llama-3.1-8b": "meta-llama/llama-3.1-8b-instruct",
    "llama-3.1-70b": "meta-llama/llama-3.1-70b-instruct",
    "mistral-7b": "mistralai/mistral-7b-instruct"
}

# Default model (cost-effective)
DEFAULT_MODEL = "gpt-4o-mini"

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    user_id: str
    conversation_id: Optional[str] = None
    model: Optional[str] = DEFAULT_MODEL

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: datetime
    tokens_used: Optional[int] = None
    model_used: str
    cost_estimate: Optional[float] = None

class UserCreate(BaseModel):
    name: str
    email: str
    preferences: Optional[Dict[str, Any]] = {}

def get_cost_estimate(model: str, tokens: int) -> float:
    """Estimate cost based on model and tokens (approximate)"""
    cost_per_1k_tokens = {
        "gpt-4o-mini": 0.00015,
        "gpt-4o": 0.0025,
        "gpt-4": 0.03,
        "gpt-3.5-turbo": 0.003,
        "claude-3-haiku": 0.00025,
        "claude-3-sonnet": 0.003,
        "llama-3.1-8b": 0.000015,
        "llama-3.1-70b": 0.0001,
        "mistral-7b": 0.000028
    }
    
    rate = cost_per_1k_tokens.get(model, 0.00015)
    return (tokens / 1000) * rate

def get_ai_response(message: str, model: str = DEFAULT_MODEL, user_context: Dict = None) -> tuple[str, int, str]:
    """Get AI response from OpenRouter"""
    try:
        # Get the actual model name for OpenRouter
        openrouter_model = AVAILABLE_MODELS.get(model, AVAILABLE_MODELS[DEFAULT_MODEL])
        
        # Create context-aware prompt
        system_prompt = """You are DOST, a friendly and helpful AI assistant. You are designed to be:
        - Supportive and encouraging
        - Helpful with tasks and questions
        - Conversational and engaging
        - Proactive in offering assistance
        - Knowledgeable across many topics
        
        Keep responses concise but warm. You're like a helpful friend who's always there to assist.
        Feel free to ask follow-up questions to better help the user."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        # Add user context if available
        if user_context and user_context.get("name"):
            messages[0]["content"] += f"\n\nUser's name is {user_context['name']}."
        
        response = client.chat.completions.create(
            model=openrouter_model,
            messages=messages,
            max_tokens=200,  # Slightly higher for better responses
            temperature=0.7,
            extra_headers={
                "HTTP-Referer": "https://dost-ai.com",  # Replace with your domain
                "X-Title": "DOST AI Assistant"
            }
        )
        
        ai_response = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else 0
        
        return ai_response, tokens_used, model
        
    except Exception as e:
        logger.error(f"OpenRouter API error: {str(e)}")
        # Fallback response if OpenRouter fails
        return f"I'm having trouble connecting to my AI brain right now. Here's what I heard: '{message}'. Please try again in a moment!", 0, "fallback"

@app.get("/")
async def root():
    return {
        "message": "🤖 DOST AI - Your AI Friend is LIVE with OpenRouter!", 
        "status": "success",
        "ai_enabled": True,
        "available_models": list(AVAILABLE_MODELS.keys()),
        "default_model": DEFAULT_MODEL
    }

@app.get("/health")
async def health():
    # Check if OpenRouter API key is available
    openrouter_status = "configured" if os.getenv("OPENROUTER_API_KEY") else "missing"
    
    return {
        "status": "healthy", 
        "platform": "Render", 
        "ai_enabled": openrouter_status == "configured",
        "openrouter_status": openrouter_status,
        "service": "dost-ai-openrouter",
        "available_models": list(AVAILABLE_MODELS.keys())
    }

@app.get("/models")
async def get_models():
    """Get available AI models"""
    return {
        "available_models": AVAILABLE_MODELS,
        "default_model": DEFAULT_MODEL,
        "recommendations": {
            "fastest": "llama-3.1-8b",
            "cheapest": "llama-3.1-8b", 
            "best_quality": "gpt-4o",
            "balanced": "gpt-4o-mini"
        }
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
            "total_conversations": 0,
            "total_tokens_used": 0,
            "preferred_model": user.preferences.get("model", DEFAULT_MODEL)
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
    """Chat with DOST AI using OpenRouter"""
    try:
        # Validate model
        if request.model not in AVAILABLE_MODELS:
            request.model = DEFAULT_MODEL
        
        # Get user context
        user_context = users.get(request.user_id, {})
        
        # Get AI response
        ai_response, tokens_used, model_used = get_ai_response(
            request.message, 
            request.model, 
            user_context
        )
        
        # Calculate cost estimate
        cost_estimate = get_cost_estimate(request.model, tokens_used)
        
        # Generate conversation ID
        conversation_id = request.conversation_id or f"conv_{len(conversations) + 1}"
        
        # Store conversation
        conversation = {
            "id": conversation_id,
            "user_id": request.user_id,
            "user_message": request.message,
            "ai_response": ai_response,
            "model_used": model_used,
            "tokens_used": tokens_used,
            "cost_estimate": cost_estimate,
            "timestamp": datetime.now()
        }
        conversations.append(conversation)
        
        # Update user stats
        if request.user_id in users:
            users[request.user_id]["total_conversations"] += 1
            users[request.user_id]["total_tokens_used"] += tokens_used
        
        logger.info(f"AI chat processed for user {request.user_id}, model: {model_used}, tokens: {tokens_used}")
        
        return ChatResponse(
            response=ai_response,
            conversation_id=conversation_id,
            timestamp=conversation["timestamp"],
            tokens_used=tokens_used,
            model_used=model_used,
            cost_estimate=cost_estimate
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
            "model_used": conv["model_used"],
            "tokens_used": conv["tokens_used"],
            "cost_estimate": conv["cost_estimate"],
            "timestamp": conv["timestamp"]
        }
        for conv in conversations 
        if conv["user_id"] == user_id
    ]
    return {"conversations": user_conversations}

@app.get("/status")
async def get_status():
    """Get system status"""
    openrouter_configured = bool(os.getenv("OPENROUTER_API_KEY"))
    total_cost = sum(conv.get("cost_estimate", 0) for conv in conversations)
    
    return {
        "status": "running",
        "version": "2.1.0 (OpenRouter-enabled)",
        "features": {
            "ai_chat": openrouter_configured,
            "multiple_models": True,
            "user_management": True,
            "conversation_history": True,
            "token_tracking": True,
            "cost_estimation": True
        },
        "stats": {
            "total_users": len(users),
            "total_conversations": len(conversations),
            "total_tokens_used": sum(conv.get("tokens_used", 0) for conv in conversations),
            "estimated_total_cost": f"${total_cost:.4f}"
        },
        "openrouter_status": "configured" if openrouter_configured else "missing_api_key",
        "available_models": list(AVAILABLE_MODELS.keys())
    }

@app.get("/ping")
async def ping():
    return {
        "ping": "pong", 
        "ai_enabled": bool(os.getenv("OPENROUTER_API_KEY")),
        "provider": "OpenRouter"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info") 