import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import openai
from openai import OpenAI
import re

from app.config import get_settings
from app.database import get_db_session
from app.models import User, Conversation, Memory, Task, UserContext

logger = logging.getLogger(__name__)

class AIBrain:
    """
    The AI Brain - Core intelligence system using GPT-4
    Handles conversation, context management, and intelligent responses
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        self.system_prompt = self._build_system_prompt()
        self.context_cache = {}
        
    async def initialize(self):
        """Initialize the AI Brain with OpenAI client"""
        try:
            if not self.settings.openai_api_key:
                raise ValueError("OpenAI API key is required")
            
            self.client = OpenAI(api_key=self.settings.openai_api_key)
            logger.info("AI Brain initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI Brain: {str(e)}")
            raise
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for the AI assistant"""
        return """
        You are DOST, a powerful AI assistant that serves as the user's best friend. You are:
        
        PERSONALITY:
        - Warm, empathetic, and genuinely caring
        - Intelligent and helpful, but not robotic
        - Conversational and engaging
        - Proactive in offering help and suggestions
        - Respectful of boundaries and privacy
        
        CAPABILITIES:
        - Voice conversation and text chat
        - Calendar and task management
        - Learning user preferences and patterns
        - Providing intelligent insights and suggestions
        - Emotional support and companionship
        - Helping with daily planning and organization
        
        BEHAVIOR:
        - Always maintain context from previous conversations
        - Adapt your communication style to the user's preferences
        - Offer proactive suggestions based on user patterns
        - Be concise but thorough in your responses
        - Use the user's name when appropriate
        - Remember important details about the user's life
        
        RESPONSE FORMAT:
        - Provide natural, conversational responses
        - Include relevant actions or suggestions when appropriate
        - Consider the user's current context (mood, time, location)
        - Maintain consistency with the user's established preferences
        
        Remember: You're not just an assistant, you're a trusted companion who grows smarter over time.
        """
    
    async def process_message(self, message: str, user_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a user message and generate intelligent response
        
        Args:
            message: User's message
            user_id: User ID
            context: Current conversation context
            
        Returns:
            Dict containing response message, updated context, and actions
        """
        try:
            # Get user information and history
            user_info = await self._get_user_info(user_id)
            conversation_history = await self._get_conversation_history(user_id, limit=10)
            user_memories = await self._get_user_memories(user_id)
            
            # Analyze message intent and entities
            intent_analysis = await self._analyze_intent(message)
            
            # Build conversation context
            conversation_context = self._build_conversation_context(
                user_info, conversation_history, user_memories, context, intent_analysis
            )
            
            # Generate response using GPT-4
            response = await self._generate_response(message, conversation_context)
            
            # Extract actions from response
            actions = self._extract_actions(response, intent_analysis)
            
            # Update context based on conversation
            updated_context = await self._update_context(
                user_id, context, message, response, intent_analysis
            )
            
            # Process any identified actions
            await self._process_actions(user_id, actions)
            
            return {
                "message": response,
                "context": updated_context,
                "actions": actions,
                "intent": intent_analysis.get("intent"),
                "confidence": intent_analysis.get("confidence", 0.0)
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "message": "I apologize, but I'm having trouble understanding right now. Could you please try again?",
                "context": context,
                "actions": [],
                "error": str(e)
            }
    
    async def _get_user_info(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user information"""
        with get_db_session() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {}
            
            return {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "preferences": user.preferences or {},
                "context": user.context or {},
                "created_at": user.created_at.isoformat()
            }
    
    async def _get_conversation_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history"""
        with get_db_session() as db:
            conversations = db.query(Conversation).filter(
                Conversation.user_id == user_id
            ).order_by(Conversation.timestamp.desc()).limit(limit).all()
            
            return [
                {
                    "user_message": conv.user_message,
                    "ai_response": conv.ai_response,
                    "timestamp": conv.timestamp.isoformat(),
                    "context": conv.context or {}
                }
                for conv in reversed(conversations)
            ]
    
    async def _get_user_memories(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user memories for context"""
        with get_db_session() as db:
            memories = db.query(Memory).filter(
                Memory.user_id == user_id,
                Memory.importance > 0.3
            ).order_by(Memory.importance.desc()).limit(20).all()
            
            return [
                {
                    "type": mem.memory_type,
                    "content": mem.content,
                    "importance": mem.importance,
                    "tags": mem.tags or []
                }
                for mem in memories
            ]
    
    async def _analyze_intent(self, message: str) -> Dict[str, Any]:
        """Analyze user intent and extract entities"""
        try:
            # Simple intent analysis - can be enhanced with ML models
            intents = {
                "task_creation": ["create", "add", "remind", "schedule", "plan"],
                "question": ["what", "how", "when", "where", "why", "who"],
                "calendar": ["calendar", "meeting", "appointment", "event"],
                "information": ["tell me", "explain", "show me", "find"],
                "casual": ["hi", "hello", "how are you", "thanks", "bye"]
            }
            
            message_lower = message.lower()
            detected_intent = "casual"
            confidence = 0.5
            
            for intent, keywords in intents.items():
                if any(keyword in message_lower for keyword in keywords):
                    detected_intent = intent
                    confidence = 0.8
                    break
            
            # Extract entities (dates, times, names, etc.)
            entities = self._extract_entities(message)
            
            return {
                "intent": detected_intent,
                "confidence": confidence,
                "entities": entities,
                "original_message": message
            }
            
        except Exception as e:
            logger.error(f"Intent analysis error: {str(e)}")
            return {
                "intent": "casual",
                "confidence": 0.5,
                "entities": {},
                "original_message": message
            }
    
    def _extract_entities(self, message: str) -> Dict[str, Any]:
        """Extract entities from message"""
        entities = {}
        
        # Extract dates
        date_patterns = [
            r'\b(today|tomorrow|yesterday)\b',
            r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
            r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                entities["dates"] = matches
        
        # Extract times
        time_patterns = [
            r'\b(\d{1,2}:\d{2})\b',
            r'\b(\d{1,2}(am|pm))\b'
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                entities["times"] = matches
        
        return entities
    
    def _build_conversation_context(
        self, 
        user_info: Dict[str, Any], 
        history: List[Dict[str, Any]], 
        memories: List[Dict[str, Any]], 
        context: Dict[str, Any],
        intent_analysis: Dict[str, Any]
    ) -> str:
        """Build conversation context for GPT-4"""
        
        context_parts = [
            f"User: {user_info.get('name', 'User')}",
            f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Intent: {intent_analysis.get('intent', 'casual')}",
        ]
        
        if user_info.get('preferences'):
            context_parts.append(f"User preferences: {json.dumps(user_info['preferences'])}")
        
        if memories:
            memory_text = "\n".join([f"- {m['content']} (importance: {m['importance']})" for m in memories[:5]])
            context_parts.append(f"Important memories about user:\n{memory_text}")
        
        if history:
            history_text = "\n".join([
                f"User: {h['user_message']}\nYou: {h['ai_response']}"
                for h in history[-3:]  # Last 3 conversations
            ])
            context_parts.append(f"Recent conversation history:\n{history_text}")
        
        if context:
            context_parts.append(f"Current context: {json.dumps(context)}")
        
        return "\n\n".join(context_parts)
    
    async def _generate_response(self, message: str, context: str) -> str:
        """Generate response using GPT-4"""
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "system", "content": f"Context: {context}"},
                {"role": "user", "content": message}
            ]
            
            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=messages,
                max_tokens=self.settings.max_tokens,
                temperature=self.settings.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"GPT-4 generation error: {str(e)}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again."
    
    def _extract_actions(self, response: str, intent_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract actionable items from AI response"""
        actions = []
        
        # Check for task creation intent
        if intent_analysis.get("intent") == "task_creation":
            entities = intent_analysis.get("entities", {})
            actions.append({
                "type": "create_task",
                "title": response[:100],  # Use first part of response as title
                "due_date": entities.get("dates", [None])[0] if entities.get("dates") else None,
                "priority": "medium"
            })
        
        # Check for calendar events
        if intent_analysis.get("intent") == "calendar":
            entities = intent_analysis.get("entities", {})
            actions.append({
                "type": "calendar_event",
                "title": response[:100],
                "date": entities.get("dates", [None])[0] if entities.get("dates") else None,
                "time": entities.get("times", [None])[0] if entities.get("times") else None
            })
        
        return actions
    
    async def _update_context(
        self, 
        user_id: int, 
        current_context: Dict[str, Any], 
        user_message: str, 
        ai_response: str,
        intent_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update conversation context"""
        updated_context = current_context.copy()
        
        # Update conversation metadata
        updated_context["last_interaction"] = datetime.now().isoformat()
        updated_context["last_intent"] = intent_analysis.get("intent")
        updated_context["conversation_count"] = updated_context.get("conversation_count", 0) + 1
        
        # Analyze user mood/sentiment (simple implementation)
        mood_indicators = {
            "positive": ["happy", "great", "awesome", "good", "excellent"],
            "negative": ["sad", "bad", "terrible", "awful", "horrible"],
            "neutral": ["ok", "fine", "alright"]
        }
        
        message_lower = user_message.lower()
        for mood, indicators in mood_indicators.items():
            if any(indicator in message_lower for indicator in indicators):
                updated_context["mood"] = mood
                break
        
        return updated_context
    
    async def _process_actions(self, user_id: int, actions: List[Dict[str, Any]]):
        """Process identified actions"""
        for action in actions:
            try:
                if action["type"] == "create_task":
                    await self._create_task_action(user_id, action)
                elif action["type"] == "calendar_event":
                    await self._create_calendar_event_action(user_id, action)
                # Add more action types as needed
            except Exception as e:
                logger.error(f"Error processing action {action['type']}: {str(e)}")
    
    async def _create_task_action(self, user_id: int, action: Dict[str, Any]):
        """Create task from action"""
        with get_db_session() as db:
            task = Task(
                user_id=user_id,
                title=action["title"],
                priority=action.get("priority", "medium"),
                status="pending"
            )
            db.add(task)
            db.commit()
            logger.info(f"Created task for user {user_id}: {action['title']}")
    
    async def _create_calendar_event_action(self, user_id: int, action: Dict[str, Any]):
        """Create calendar event from action"""
        # This would integrate with calendar service
        logger.info(f"Calendar event action for user {user_id}: {action}")
    
    async def generate_day_summary(self, events: List[Dict[str, Any]], tasks: List[Dict[str, Any]]) -> str:
        """Generate intelligent day summary"""
        try:
            context = f"""
            Today's schedule:
            Events: {json.dumps(events, indent=2)}
            Tasks: {json.dumps(tasks, indent=2)}
            
            Please provide a concise, friendly summary of today's schedule including:
            - Key events and meetings
            - Important tasks to complete
            - Any potential conflicts or suggestions
            - Overall day assessment (busy/light/balanced)
            """
            
            messages = [
                {"role": "system", "content": "You are a helpful assistant that provides concise, friendly daily summaries."},
                {"role": "user", "content": context}
            ]
            
            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=messages,
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Day summary generation error: {str(e)}")
            return "Here's your schedule for today. You have several items planned - I'll help you stay organized!"
    
    async def cleanup(self):
        """Cleanup resources"""
        # Clear context cache
        self.context_cache.clear()
        logger.info("AI Brain cleaned up successfully") 