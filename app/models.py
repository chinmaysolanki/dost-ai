from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any, Optional

from app.database import Base

class User(Base):
    """User model for managing user profiles and preferences"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # User preferences and context
    preferences = Column(JSON, default=dict)
    context = Column(JSON, default=dict)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user")
    tasks = relationship("Task", back_populates="user")
    memories = relationship("Memory", back_populates="user")
    user_contexts = relationship("UserContext", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, name={self.name})>"

class Conversation(Base):
    """Conversation model for storing chat history"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Conversation metadata
    context = Column(JSON, default=dict)
    emotion_score = Column(Float, default=0.0)
    intent = Column(String(100))
    confidence = Column(Float, default=0.0)
    
    # Audio metadata
    has_audio = Column(Boolean, default=False)
    audio_duration = Column(Float)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id})>"

class Task(Base):
    """Task model for managing user tasks and reminders"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="pending")  # pending, in_progress, completed, cancelled
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    
    # Dates
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    due_date = Column(Date)
    completed_at = Column(DateTime(timezone=True))
    
    # Task metadata
    tags = Column(JSON, default=list)
    estimated_duration = Column(Integer)  # in minutes
    actual_duration = Column(Integer)  # in minutes
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    
    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"

class Memory(Base):
    """Memory model for storing important information about users"""
    __tablename__ = "memories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    memory_type = Column(String(50), nullable=False)  # preference, fact, event, relationship
    content = Column(Text, nullable=False)
    importance = Column(Float, default=0.5)  # 0.0 to 1.0
    
    # Dates
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    
    # Memory metadata
    tags = Column(JSON, default=list)
    context = Column(JSON, default=dict)
    source = Column(String(100))  # conversation, task, event, etc.
    
    # Relationships
    user = relationship("User", back_populates="memories")
    
    def __repr__(self):
        return f"<Memory(id={self.id}, type={self.memory_type}, importance={self.importance})>"

class UserContext(Base):
    """User context model for storing dynamic user state"""
    __tablename__ = "user_contexts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    context_type = Column(String(50), nullable=False)  # mood, location, activity, etc.
    value = Column(String(255), nullable=False)
    confidence = Column(Float, default=1.0)
    
    # Dates
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True))
    
    # Context metadata
    metadata = Column(JSON, default=dict)
    
    # Relationships
    user = relationship("User", back_populates="user_contexts")
    
    def __repr__(self):
        return f"<UserContext(id={self.id}, type={self.context_type}, value={self.value})>"

class CalendarEvent(Base):
    """Calendar event model for managing user schedules"""
    __tablename__ = "calendar_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    location = Column(String(255))
    
    # Time information
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    timezone = Column(String(50))
    is_all_day = Column(Boolean, default=False)
    
    # Event metadata
    status = Column(String(50), default="confirmed")  # confirmed, tentative, cancelled
    visibility = Column(String(50), default="default")  # default, public, private
    recurrence = Column(JSON, default=dict)
    
    # External calendar integration
    external_id = Column(String(255))
    external_source = Column(String(50))  # google, outlook, etc.
    
    # Dates
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<CalendarEvent(id={self.id}, title={self.title})>"

class LearningData(Base):
    """Learning data model for AI improvement"""
    __tablename__ = "learning_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    data_type = Column(String(50), nullable=False)  # pattern, preference, behavior
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON, nullable=False)
    
    # Learning metrics
    accuracy = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)
    feedback_score = Column(Float)
    
    # Dates
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Metadata
    model_version = Column(String(50))
    experiment_id = Column(String(100))
    
    def __repr__(self):
        return f"<LearningData(id={self.id}, type={self.data_type})>"

class Notification(Base):
    """Notification model for user alerts and reminders"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # reminder, alert, info
    
    # Status
    is_read = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    
    # Timing
    scheduled_at = Column(DateTime(timezone=True))
    sent_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Metadata
    metadata = Column(JSON, default=dict)
    
    def __repr__(self):
        return f"<Notification(id={self.id}, title={self.title})>" 