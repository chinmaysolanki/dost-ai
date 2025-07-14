from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import asyncio
import logging
from datetime import datetime
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="DOST - Your AI Friend",
    description="A personal AI assistant that grows with you",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage (replace with database in production)
conversations: List[Dict[str, Any]] = []
users: Dict[str, Dict[str, Any]] = {}
tasks: List[Dict[str, Any]] = []

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    user_id: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: datetime

class UserCreate(BaseModel):
    name: str
    email: str
    preferences: Optional[Dict[str, Any]] = {}

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    due_date: Optional[datetime] = None
    user_id: str

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_connections[user_id] = websocket

    def disconnect(self, websocket: WebSocket, user_id: str):
        self.active_connections.remove(websocket)
        if user_id in self.user_connections:
            del self.user_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.user_connections:
            await self.user_connections[user_id].send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = WebSocketManager()

# API Routes
@app.get("/")
async def root():
    return {"message": "Welcome to DOST - Your AI Friend! 🤖"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

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
            "created_at": datetime.now()
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
    """Simple chat endpoint without OpenAI integration"""
    try:
        # Simple echo response for now
        conversation_id = request.conversation_id or f"conv_{len(conversations) + 1}"
        
        # Store conversation
        conversation = {
            "id": conversation_id,
            "user_id": request.user_id,
            "message": request.message,
            "response": f"I hear you saying: '{request.message}'. This is a simplified version of DOST. Full AI capabilities will be enabled once all dependencies are installed.",
            "timestamp": datetime.now()
        }
        conversations.append(conversation)
        
        # Send real-time update
        await manager.send_personal_message(
            json.dumps({
                "type": "chat_response",
                "conversation_id": conversation_id,
                "response": conversation["response"]
            }), 
            request.user_id
        )
        
        logger.info(f"Chat processed for user {request.user_id}")
        return ChatResponse(
            response=conversation["response"],
            conversation_id=conversation_id,
            timestamp=conversation["timestamp"]
        )
        
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process chat")

@app.get("/conversations/{user_id}")
async def get_conversations(user_id: str):
    """Get user's conversation history"""
    user_conversations = [
        conv for conv in conversations 
        if conv["user_id"] == user_id
    ]
    return {"conversations": user_conversations}

@app.post("/tasks", response_model=Dict[str, Any])
async def create_task(task: TaskCreate):
    """Create a new task"""
    try:
        task_id = f"task_{len(tasks) + 1}"
        new_task = {
            "id": task_id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "due_date": task.due_date,
            "user_id": task.user_id,
            "status": "pending",
            "created_at": datetime.now()
        }
        tasks.append(new_task)
        
        # Send real-time update
        await manager.send_personal_message(
            json.dumps({
                "type": "task_created",
                "task": new_task
            }), 
            task.user_id
        )
        
        logger.info(f"Created task: {task_id}")
        return {"task_id": task_id, "message": "Task created successfully"}
        
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create task")

@app.get("/tasks/{user_id}")
async def get_tasks(user_id: str):
    """Get user's tasks"""
    user_tasks = [task for task in tasks if task["user_id"] == user_id]
    return {"tasks": user_tasks}

@app.put("/tasks/{task_id}")
async def update_task(task_id: str, updates: Dict[str, Any]):
    """Update a task"""
    try:
        task = next((t for t in tasks if t["id"] == task_id), None)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Update task
        for key, value in updates.items():
            if key in task:
                task[key] = value
        
        task["updated_at"] = datetime.now()
        
        # Send real-time update
        await manager.send_personal_message(
            json.dumps({
                "type": "task_updated",
                "task": task
            }), 
            task["user_id"]
        )
        
        logger.info(f"Updated task: {task_id}")
        return {"message": "Task updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating task: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update task")

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            logger.info(f"Received WebSocket message from {user_id}: {data}")
            
            # Echo back for now
            await websocket.send_text(f"Echo: {data}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info(f"WebSocket disconnected: {user_id}")

@app.get("/status")
async def get_status():
    """Get system status"""
    return {
        "status": "running",
        "version": "1.0.0 (simplified)",
        "features": {
            "basic_chat": True,
            "task_management": True,
            "websocket": True,
            "voice_processing": False,
            "ai_brain": False,
            "calendar": False,
            "learning": False
        },
        "stats": {
            "total_users": len(users),
            "total_conversations": len(conversations),
            "total_tasks": len(tasks),
            "active_connections": len(manager.active_connections)
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 