from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import asyncio
import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import io
import uuid

from app.database import get_db, init_db
from app.models import User, Conversation, Memory, Task, UserContext
from app.services.ai_brain import AIBrain
from app.services.voice_processor import VoiceProcessor
from app.services.calendar_manager import CalendarManager
from app.services.learning_system import LearningSystem
from app.services.websocket_manager import WebSocketManager
from app.schemas import (
    UserCreate, UserResponse, ConversationCreate, ConversationResponse,
    VoiceMessage, TaskCreate, TaskResponse, ContextUpdate
)
from app.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

# Initialize services
ai_brain = AIBrain()
voice_processor = VoiceProcessor()
calendar_manager = CalendarManager()
learning_system = LearningSystem()
websocket_manager = WebSocketManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing AI Assistant...")
    init_db()
    await ai_brain.initialize()
    await voice_processor.initialize()
    await calendar_manager.initialize()
    await learning_system.initialize()
    logger.info("AI Assistant initialized successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Assistant...")
    await ai_brain.cleanup()
    await voice_processor.cleanup()

app = FastAPI(
    title="DOST - Your AI Assistant",
    description="A powerful AI assistant that listens, learns, and grows with you",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to DOST - Your AI Assistant", "status": "active"}

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# User Management
@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    db_user = User(
        name=user.name,
        email=user.email,
        preferences=user.preferences or {}
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Voice Processing
@app.post("/voice/transcribe")
async def transcribe_voice(
    audio: UploadFile = File(...),
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    """Transcribe voice message and process with AI"""
    try:
        # Read audio file
        audio_content = await audio.read()
        
        # Transcribe audio
        transcription = await voice_processor.transcribe_audio(audio_content)
        
        if not transcription:
            raise HTTPException(status_code=400, detail="Could not transcribe audio")
        
        # Get user context
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Process with AI brain
        response = await ai_brain.process_message(
            message=transcription,
            user_id=user_id,
            context=user.context or {}
        )
        
        # Save conversation
        conversation = Conversation(
            user_id=user_id,
            user_message=transcription,
            ai_response=response["message"],
            context=response.get("context", {}),
            timestamp=datetime.utcnow()
        )
        db.add(conversation)
        db.commit()
        
        # Update user context
        await learning_system.update_user_context(user_id, response["context"])
        
        # Generate audio response
        audio_response = await voice_processor.text_to_speech(response["message"])
        
        # Send real-time update via WebSocket
        await websocket_manager.broadcast_to_user(user_id, {
            "type": "conversation",
            "data": {
                "user_message": transcription,
                "ai_response": response["message"],
                "timestamp": datetime.utcnow().isoformat()
            }
        })
        
        return {
            "transcription": transcription,
            "ai_response": response["message"],
            "context": response["context"],
            "audio_available": bool(audio_response)
        }
        
    except Exception as e:
        logger.error(f"Voice processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/voice/audio/{conversation_id}")
async def get_audio_response(conversation_id: int, db: Session = Depends(get_db)):
    """Get audio response for a conversation"""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    audio_content = await voice_processor.text_to_speech(conversation.ai_response)
    if not audio_content:
        raise HTTPException(status_code=404, detail="Audio not available")
    
    return StreamingResponse(
        io.BytesIO(audio_content),
        media_type="audio/wav",
        headers={"Content-Disposition": "attachment; filename=response.wav"}
    )

# Text Chat
@app.post("/chat/message")
async def send_text_message(
    message: str,
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    """Send text message and get AI response"""
    try:
        # Get user context
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Process with AI brain
        response = await ai_brain.process_message(
            message=message,
            user_id=user_id,
            context=user.context or {}
        )
        
        # Save conversation
        conversation = Conversation(
            user_id=user_id,
            user_message=message,
            ai_response=response["message"],
            context=response.get("context", {}),
            timestamp=datetime.utcnow()
        )
        db.add(conversation)
        db.commit()
        
        # Update user context
        await learning_system.update_user_context(user_id, response["context"])
        
        # Send real-time update via WebSocket
        await websocket_manager.broadcast_to_user(user_id, {
            "type": "conversation",
            "data": {
                "user_message": message,
                "ai_response": response["message"],
                "timestamp": datetime.utcnow().isoformat()
            }
        })
        
        return {
            "message": response["message"],
            "context": response["context"],
            "actions": response.get("actions", [])
        }
        
    except Exception as e:
        logger.error(f"Text chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Calendar & Task Management
@app.post("/tasks/", response_model=TaskResponse)
async def create_task(task: TaskCreate, user_id: int = 1, db: Session = Depends(get_db)):
    """Create a new task"""
    db_task = Task(
        user_id=user_id,
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        priority=task.priority,
        status="pending"
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Notify via WebSocket
    await websocket_manager.broadcast_to_user(user_id, {
        "type": "task_created",
        "data": {
            "id": db_task.id,
            "title": db_task.title,
            "due_date": db_task.due_date.isoformat() if db_task.due_date else None
        }
    })
    
    return db_task

@app.get("/tasks/", response_model=List[TaskResponse])
async def get_tasks(user_id: int = 1, db: Session = Depends(get_db)):
    """Get all tasks for a user"""
    tasks = db.query(Task).filter(Task.user_id == user_id).all()
    return tasks

@app.get("/calendar/today")
async def get_today_schedule(user_id: int = 1, db: Session = Depends(get_db)):
    """Get today's schedule and tasks"""
    try:
        # Get calendar events
        events = await calendar_manager.get_today_events(user_id)
        
        # Get tasks due today
        today = datetime.now().date()
        tasks = db.query(Task).filter(
            Task.user_id == user_id,
            Task.due_date == today,
            Task.status != "completed"
        ).all()
        
        return {
            "events": events,
            "tasks": [{"id": t.id, "title": t.title, "priority": t.priority} for t in tasks],
            "summary": await ai_brain.generate_day_summary(events, tasks)
        }
        
    except Exception as e:
        logger.error(f"Calendar error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket Connection
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """WebSocket endpoint for real-time communication"""
    await websocket_manager.connect(websocket, user_id)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle different message types
            if message_data.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            elif message_data.get("type") == "voice_start":
                # Handle voice recording start
                await websocket.send_text(json.dumps({"type": "voice_ready"}))
            
    except WebSocketDisconnect:
        await websocket_manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket_manager.disconnect(user_id)

# Learning & Context
@app.post("/context/update")
async def update_context(
    context: ContextUpdate,
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    """Update user context and preferences"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update context
    current_context = user.context or {}
    current_context.update(context.data)
    user.context = current_context
    
    db.commit()
    
    # Learn from context update
    await learning_system.learn_from_context(user_id, context.data)
    
    return {"message": "Context updated successfully", "context": current_context}

@app.get("/conversations/", response_model=List[ConversationResponse])
async def get_conversations(
    user_id: int = 1,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get conversation history"""
    conversations = db.query(Conversation).filter(
        Conversation.user_id == user_id
    ).order_by(Conversation.timestamp.desc()).offset(offset).limit(limit).all()
    
    return conversations

# AI Insights
@app.get("/insights/")
async def get_insights(user_id: int = 1, db: Session = Depends(get_db)):
    """Get AI insights about user patterns and suggestions"""
    try:
        insights = await learning_system.generate_insights(user_id)
        return {
            "insights": insights,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Insights error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 