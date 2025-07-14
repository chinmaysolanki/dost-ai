from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date

# User schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    preferences: Optional[Dict[str, Any]] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    preferences: Optional[Dict[str, Any]] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool
    context: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Conversation schemas
class ConversationBase(BaseModel):
    user_message: str
    ai_response: str
    context: Optional[Dict[str, Any]] = None

class ConversationCreate(ConversationBase):
    user_id: int

class ConversationResponse(ConversationBase):
    id: int
    user_id: int
    timestamp: datetime
    emotion_score: Optional[float] = None
    intent: Optional[str] = None
    confidence: Optional[float] = None
    has_audio: bool = False
    audio_duration: Optional[float] = None
    
    class Config:
        from_attributes = True

# Task schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    due_date: Optional[date] = None
    
    @validator('priority')
    def validate_priority(cls, v):
        if v not in ['low', 'medium', 'high', 'urgent']:
            raise ValueError('Priority must be one of: low, medium, high, urgent')
        return v

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None
    estimated_duration: Optional[int] = None
    actual_duration: Optional[int] = None
    tags: Optional[List[str]] = None
    
    @validator('status')
    def validate_status(cls, v):
        if v and v not in ['pending', 'in_progress', 'completed', 'cancelled']:
            raise ValueError('Status must be one of: pending, in_progress, completed, cancelled')
        return v

class TaskResponse(TaskBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    tags: Optional[List[str]] = None
    estimated_duration: Optional[int] = None
    actual_duration: Optional[int] = None
    
    class Config:
        from_attributes = True

# Memory schemas
class MemoryBase(BaseModel):
    memory_type: str
    content: str
    importance: float = 0.5
    tags: Optional[List[str]] = None
    
    @validator('memory_type')
    def validate_memory_type(cls, v):
        if v not in ['preference', 'fact', 'event', 'relationship']:
            raise ValueError('Memory type must be one of: preference, fact, event, relationship')
        return v
    
    @validator('importance')
    def validate_importance(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Importance must be between 0.0 and 1.0')
        return v

class MemoryCreate(MemoryBase):
    pass

class MemoryResponse(MemoryBase):
    id: int
    user_id: int
    created_at: datetime
    last_accessed: datetime
    expires_at: Optional[datetime] = None
    context: Optional[Dict[str, Any]] = None
    source: Optional[str] = None
    
    class Config:
        from_attributes = True

# Voice message schemas
class VoiceMessage(BaseModel):
    text: str
    audio_url: Optional[str] = None
    duration: Optional[float] = None
    language: str = "en"
    confidence: Optional[float] = None

class VoiceResponse(BaseModel):
    transcription: str
    ai_response: str
    audio_available: bool = False
    context: Optional[Dict[str, Any]] = None

# Calendar event schemas
class CalendarEventBase(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: datetime
    end_time: datetime
    timezone: str = "UTC"
    is_all_day: bool = False

class CalendarEventCreate(CalendarEventBase):
    pass

class CalendarEventResponse(CalendarEventBase):
    id: int
    user_id: int
    status: str
    visibility: str
    external_id: Optional[str] = None
    external_source: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Context schemas
class ContextUpdate(BaseModel):
    data: Dict[str, Any]
    context_type: Optional[str] = None

class UserContextBase(BaseModel):
    context_type: str
    value: str
    confidence: float = 1.0
    metadata: Optional[Dict[str, Any]] = None

class UserContextCreate(UserContextBase):
    pass

class UserContextResponse(UserContextBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Learning data schemas
class LearningDataBase(BaseModel):
    data_type: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    accuracy: float = 0.0
    confidence: float = 0.0
    feedback_score: Optional[float] = None

class LearningDataCreate(LearningDataBase):
    pass

class LearningDataResponse(LearningDataBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_version: Optional[str] = None
    experiment_id: Optional[str] = None
    
    class Config:
        from_attributes = True

# Notification schemas
class NotificationBase(BaseModel):
    title: str
    message: str
    notification_type: str
    priority: str = "medium"
    scheduled_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class NotificationCreate(NotificationBase):
    pass

class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    is_sent: bool
    sent_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Chat message schemas
class ChatMessage(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, Any]]] = None
    confidence: Optional[float] = None

# Insights schemas
class InsightBase(BaseModel):
    insight_type: str
    title: str
    description: str
    confidence: float
    actionable: bool = False
    actions: Optional[List[str]] = None

class InsightsResponse(BaseModel):
    insights: List[InsightBase]
    generated_at: datetime
    summary: Optional[str] = None

# WebSocket message schemas
class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: Optional[datetime] = None

# Schedule schemas
class ScheduleResponse(BaseModel):
    events: List[Dict[str, Any]]
    tasks: List[Dict[str, Any]]
    summary: str
    date: date 