import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import numpy as np
from collections import defaultdict, Counter
import statistics

from app.config import get_settings
from app.database import get_db_session
from app.models import User, Conversation, Memory, Task, UserContext, LearningData

logger = logging.getLogger(__name__)

class LearningSystem:
    """
    Adaptive learning system that helps the AI get smarter over time
    Learns from user interactions, preferences, and patterns
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.user_patterns = {}  # Cache for user patterns
        self.learning_cache = {}  # Cache for learning insights
        
    async def initialize(self):
        """Initialize the learning system"""
        try:
            # Load existing learning data
            await self._load_learning_patterns()
            logger.info("Learning system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize learning system: {str(e)}")
            raise
    
    async def _load_learning_patterns(self):
        """Load existing learning patterns from database"""
        try:
            with get_db_session() as db:
                # Load recent learning data
                recent_data = db.query(LearningData).filter(
                    LearningData.created_at >= datetime.now() - timedelta(days=30)
                ).all()
                
                # Process and cache patterns
                for data in recent_data:
                    user_id = data.user_id
                    if user_id not in self.user_patterns:
                        self.user_patterns[user_id] = defaultdict(list)
                    
                    self.user_patterns[user_id][data.data_type].append({
                        'input': data.input_data,
                        'output': data.output_data,
                        'accuracy': data.accuracy,
                        'timestamp': data.created_at
                    })
                
                logger.info(f"Loaded patterns for {len(self.user_patterns)} users")
                
        except Exception as e:
            logger.error(f"Error loading learning patterns: {str(e)}")
    
    async def update_user_context(self, user_id: int, context: Dict[str, Any]):
        """
        Update user context and learn from it
        
        Args:
            user_id: User ID
            context: Context data to learn from
        """
        try:
            # Update user context in database
            with get_db_session() as db:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    current_context = user.context or {}
                    current_context.update(context)
                    user.context = current_context
                    db.commit()
            
            # Learn from context update
            await self._learn_from_context_update(user_id, context)
            
        except Exception as e:
            logger.error(f"Error updating user context: {str(e)}")
    
    async def _learn_from_context_update(self, user_id: int, context: Dict[str, Any]):
        """Learn patterns from context updates"""
        try:
            # Initialize user patterns if not exists
            if user_id not in self.user_patterns:
                self.user_patterns[user_id] = defaultdict(list)
            
            # Learn from mood patterns
            if 'mood' in context:
                await self._learn_mood_patterns(user_id, context['mood'])
            
            # Learn from time patterns
            if 'last_interaction' in context:
                await self._learn_time_patterns(user_id, context['last_interaction'])
            
            # Learn from intent patterns
            if 'last_intent' in context:
                await self._learn_intent_patterns(user_id, context['last_intent'])
            
        except Exception as e:
            logger.error(f"Error learning from context: {str(e)}")
    
    async def _learn_mood_patterns(self, user_id: int, mood: str):
        """Learn user mood patterns"""
        try:
            current_time = datetime.now()
            
            # Store mood pattern
            mood_pattern = {
                'mood': mood,
                'timestamp': current_time.isoformat(),
                'hour': current_time.hour,
                'day_of_week': current_time.weekday()
            }
            
            self.user_patterns[user_id]['mood'].append(mood_pattern)
            
            # Keep only recent patterns (last 30 days)
            cutoff_date = current_time - timedelta(days=30)
            self.user_patterns[user_id]['mood'] = [
                p for p in self.user_patterns[user_id]['mood']
                if datetime.fromisoformat(p['timestamp']) > cutoff_date
            ]
            
            # Save to database
            await self._save_learning_data(user_id, 'mood_pattern', mood_pattern, {})
            
        except Exception as e:
            logger.error(f"Error learning mood patterns: {str(e)}")
    
    async def _learn_time_patterns(self, user_id: int, interaction_time: str):
        """Learn user time patterns"""
        try:
            interaction_dt = datetime.fromisoformat(interaction_time)
            
            time_pattern = {
                'hour': interaction_dt.hour,
                'day_of_week': interaction_dt.weekday(),
                'timestamp': interaction_time
            }
            
            self.user_patterns[user_id]['time'].append(time_pattern)
            
            # Keep only recent patterns
            cutoff_date = datetime.now() - timedelta(days=30)
            self.user_patterns[user_id]['time'] = [
                p for p in self.user_patterns[user_id]['time']
                if datetime.fromisoformat(p['timestamp']) > cutoff_date
            ]
            
            # Save to database
            await self._save_learning_data(user_id, 'time_pattern', time_pattern, {})
            
        except Exception as e:
            logger.error(f"Error learning time patterns: {str(e)}")
    
    async def _learn_intent_patterns(self, user_id: int, intent: str):
        """Learn user intent patterns"""
        try:
            current_time = datetime.now()
            
            intent_pattern = {
                'intent': intent,
                'timestamp': current_time.isoformat(),
                'hour': current_time.hour,
                'day_of_week': current_time.weekday()
            }
            
            self.user_patterns[user_id]['intent'].append(intent_pattern)
            
            # Keep only recent patterns
            cutoff_date = current_time - timedelta(days=30)
            self.user_patterns[user_id]['intent'] = [
                p for p in self.user_patterns[user_id]['intent']
                if datetime.fromisoformat(p['timestamp']) > cutoff_date
            ]
            
            # Save to database
            await self._save_learning_data(user_id, 'intent_pattern', intent_pattern, {})
            
        except Exception as e:
            logger.error(f"Error learning intent patterns: {str(e)}")
    
    async def _save_learning_data(self, user_id: int, data_type: str, input_data: Dict[str, Any], output_data: Dict[str, Any]):
        """Save learning data to database"""
        try:
            with get_db_session() as db:
                learning_data = LearningData(
                    user_id=user_id,
                    data_type=data_type,
                    input_data=input_data,
                    output_data=output_data,
                    accuracy=0.0,  # Will be updated with feedback
                    confidence=0.8,  # Default confidence
                    model_version="1.0"
                )
                
                db.add(learning_data)
                db.commit()
                
        except Exception as e:
            logger.error(f"Error saving learning data: {str(e)}")
    
    async def learn_from_context(self, user_id: int, context: Dict[str, Any]):
        """Learn from user context updates"""
        await self._learn_from_context_update(user_id, context)
    
    async def generate_insights(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Generate insights about user patterns and behavior
        
        Args:
            user_id: User ID
            
        Returns:
            List of insights
        """
        try:
            insights = []
            
            # Check cache first
            cache_key = f"insights_{user_id}"
            if cache_key in self.learning_cache:
                cached_insights = self.learning_cache[cache_key]
                if datetime.now() - cached_insights['timestamp'] < timedelta(hours=1):
                    return cached_insights['insights']
            
            # Generate mood insights
            mood_insights = await self._generate_mood_insights(user_id)
            insights.extend(mood_insights)
            
            # Generate time insights
            time_insights = await self._generate_time_insights(user_id)
            insights.extend(time_insights)
            
            # Generate intent insights
            intent_insights = await self._generate_intent_insights(user_id)
            insights.extend(intent_insights)
            
            # Generate task completion insights
            task_insights = await self._generate_task_insights(user_id)
            insights.extend(task_insights)
            
            # Generate conversation insights
            conversation_insights = await self._generate_conversation_insights(user_id)
            insights.extend(conversation_insights)
            
            # Cache insights
            self.learning_cache[cache_key] = {
                'insights': insights,
                'timestamp': datetime.now()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return []
    
    async def _generate_mood_insights(self, user_id: int) -> List[Dict[str, Any]]:
        """Generate insights about user mood patterns"""
        try:
            if user_id not in self.user_patterns or not self.user_patterns[user_id]['mood']:
                return []
            
            mood_data = self.user_patterns[user_id]['mood']
            insights = []
            
            # Analyze mood by time of day
            hourly_moods = defaultdict(list)
            for pattern in mood_data:
                hourly_moods[pattern['hour']].append(pattern['mood'])
            
            # Find patterns
            for hour, moods in hourly_moods.items():
                if len(moods) >= 3:  # Need at least 3 data points
                    mood_counter = Counter(moods)
                    most_common_mood = mood_counter.most_common(1)[0][0]
                    
                    if mood_counter[most_common_mood] / len(moods) >= 0.6:  # 60% consistency
                        insights.append({
                            'type': 'mood_pattern',
                            'title': f'Mood Pattern at {hour}:00',
                            'description': f'You tend to be {most_common_mood} around {hour}:00',
                            'confidence': mood_counter[most_common_mood] / len(moods),
                            'actionable': True,
                            'actions': [f'Schedule positive activities when you\'re typically {most_common_mood}']
                        })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating mood insights: {str(e)}")
            return []
    
    async def _generate_time_insights(self, user_id: int) -> List[Dict[str, Any]]:
        """Generate insights about user time patterns"""
        try:
            if user_id not in self.user_patterns or not self.user_patterns[user_id]['time']:
                return []
            
            time_data = self.user_patterns[user_id]['time']
            insights = []
            
            # Analyze most active hours
            hours = [pattern['hour'] for pattern in time_data]
            if hours:
                hour_counter = Counter(hours)
                most_active_hour = hour_counter.most_common(1)[0][0]
                
                insights.append({
                    'type': 'time_pattern',
                    'title': 'Most Active Hour',
                    'description': f'You\'re most active around {most_active_hour}:00',
                    'confidence': hour_counter[most_active_hour] / len(hours),
                    'actionable': True,
                    'actions': ['Schedule important tasks during your most active hours']
                })
            
            # Analyze day of week patterns
            days = [pattern['day_of_week'] for pattern in time_data]
            if days:
                day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                day_counter = Counter(days)
                most_active_day = day_counter.most_common(1)[0][0]
                
                insights.append({
                    'type': 'day_pattern',
                    'title': 'Most Active Day',
                    'description': f'You\'re most active on {day_names[most_active_day]}',
                    'confidence': day_counter[most_active_day] / len(days),
                    'actionable': True,
                    'actions': [f'Plan important activities on {day_names[most_active_day]}']
                })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating time insights: {str(e)}")
            return []
    
    async def _generate_intent_insights(self, user_id: int) -> List[Dict[str, Any]]:
        """Generate insights about user intent patterns"""
        try:
            if user_id not in self.user_patterns or not self.user_patterns[user_id]['intent']:
                return []
            
            intent_data = self.user_patterns[user_id]['intent']
            insights = []
            
            # Analyze most common intents
            intents = [pattern['intent'] for pattern in intent_data]
            if intents:
                intent_counter = Counter(intents)
                most_common_intent = intent_counter.most_common(1)[0][0]
                
                insights.append({
                    'type': 'intent_pattern',
                    'title': 'Primary Use Case',
                    'description': f'You primarily use me for {most_common_intent.replace("_", " ")}',
                    'confidence': intent_counter[most_common_intent] / len(intents),
                    'actionable': True,
                    'actions': [f'I can help you optimize {most_common_intent.replace("_", " ")} workflows']
                })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating intent insights: {str(e)}")
            return []
    
    async def _generate_task_insights(self, user_id: int) -> List[Dict[str, Any]]:
        """Generate insights about user task patterns"""
        try:
            with get_db_session() as db:
                # Get recent tasks
                tasks = db.query(Task).filter(
                    Task.user_id == user_id,
                    Task.created_at >= datetime.now() - timedelta(days=30)
                ).all()
                
                if not tasks:
                    return []
                
                insights = []
                
                # Analyze completion rate
                completed_tasks = [t for t in tasks if t.status == 'completed']
                completion_rate = len(completed_tasks) / len(tasks)
                
                insights.append({
                    'type': 'task_completion',
                    'title': 'Task Completion Rate',
                    'description': f'You complete {completion_rate:.1%} of your tasks',
                    'confidence': 1.0,
                    'actionable': completion_rate < 0.8,
                    'actions': ['Consider breaking large tasks into smaller ones'] if completion_rate < 0.8 else []
                })
                
                # Analyze priority patterns
                priorities = [t.priority for t in tasks]
                if priorities:
                    priority_counter = Counter(priorities)
                    most_common_priority = priority_counter.most_common(1)[0][0]
                    
                    insights.append({
                        'type': 'priority_pattern',
                        'title': 'Priority Preference',
                        'description': f'You mostly create {most_common_priority} priority tasks',
                        'confidence': priority_counter[most_common_priority] / len(priorities),
                        'actionable': True,
                        'actions': ['Consider using varied priority levels for better organization']
                    })
                
                return insights
                
        except Exception as e:
            logger.error(f"Error generating task insights: {str(e)}")
            return []
    
    async def _generate_conversation_insights(self, user_id: int) -> List[Dict[str, Any]]:
        """Generate insights about user conversation patterns"""
        try:
            with get_db_session() as db:
                # Get recent conversations
                conversations = db.query(Conversation).filter(
                    Conversation.user_id == user_id,
                    Conversation.timestamp >= datetime.now() - timedelta(days=30)
                ).all()
                
                if not conversations:
                    return []
                
                insights = []
                
                # Analyze conversation frequency
                daily_conversations = defaultdict(int)
                for conv in conversations:
                    day = conv.timestamp.date()
                    daily_conversations[day] += 1
                
                if daily_conversations:
                    avg_daily_conversations = statistics.mean(daily_conversations.values())
                    
                    insights.append({
                        'type': 'conversation_frequency',
                        'title': 'Daily Interaction',
                        'description': f'You have an average of {avg_daily_conversations:.1f} conversations per day',
                        'confidence': 1.0,
                        'actionable': False,
                        'actions': []
                    })
                
                # Analyze response satisfaction (based on follow-up questions)
                # This is a simplified metric - in practice, you'd want explicit feedback
                total_conversations = len(conversations)
                
                insights.append({
                    'type': 'engagement_level',
                    'title': 'Engagement Level',
                    'description': f'You\'ve had {total_conversations} conversations this month',
                    'confidence': 1.0,
                    'actionable': False,
                    'actions': []
                })
                
                return insights
                
        except Exception as e:
            logger.error(f"Error generating conversation insights: {str(e)}")
            return []
    
    async def predict_user_needs(self, user_id: int, current_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Predict user needs based on learned patterns
        
        Args:
            user_id: User ID
            current_context: Current user context
            
        Returns:
            List of predicted needs/suggestions
        """
        try:
            predictions = []
            
            # Predict based on time patterns
            current_hour = datetime.now().hour
            current_day = datetime.now().weekday()
            
            if user_id in self.user_patterns:
                # Check if user typically has certain intents at this time
                intent_patterns = self.user_patterns[user_id].get('intent', [])
                
                relevant_patterns = [
                    p for p in intent_patterns
                    if p['hour'] == current_hour and p['day_of_week'] == current_day
                ]
                
                if relevant_patterns:
                    intent_counter = Counter([p['intent'] for p in relevant_patterns])
                    most_likely_intent = intent_counter.most_common(1)[0][0]
                    
                    predictions.append({
                        'type': 'intent_prediction',
                        'prediction': most_likely_intent,
                        'confidence': intent_counter[most_likely_intent] / len(relevant_patterns),
                        'suggestion': f'Based on your patterns, you might want to {most_likely_intent.replace("_", " ")}'
                    })
            
            # Predict based on mood patterns
            if user_id in self.user_patterns:
                mood_patterns = self.user_patterns[user_id].get('mood', [])
                
                relevant_moods = [
                    p for p in mood_patterns
                    if p['hour'] == current_hour
                ]
                
                if relevant_moods:
                    mood_counter = Counter([p['mood'] for p in relevant_moods])
                    most_likely_mood = mood_counter.most_common(1)[0][0]
                    
                    predictions.append({
                        'type': 'mood_prediction',
                        'prediction': most_likely_mood,
                        'confidence': mood_counter[most_likely_mood] / len(relevant_moods),
                        'suggestion': f'You might be feeling {most_likely_mood} around this time'
                    })
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting user needs: {str(e)}")
            return []
    
    async def learn_from_feedback(self, user_id: int, feedback: Dict[str, Any]):
        """
        Learn from user feedback to improve predictions
        
        Args:
            user_id: User ID
            feedback: Feedback data
        """
        try:
            # Store feedback for future learning
            feedback_data = {
                'feedback_type': feedback.get('type'),
                'rating': feedback.get('rating'),
                'comment': feedback.get('comment'),
                'timestamp': datetime.now().isoformat()
            }
            
            await self._save_learning_data(user_id, 'feedback', feedback_data, {})
            
            # Update accuracy scores for related predictions
            if feedback.get('prediction_id'):
                await self._update_prediction_accuracy(user_id, feedback['prediction_id'], feedback['rating'])
            
        except Exception as e:
            logger.error(f"Error learning from feedback: {str(e)}")
    
    async def _update_prediction_accuracy(self, user_id: int, prediction_id: str, rating: float):
        """Update prediction accuracy based on feedback"""
        try:
            with get_db_session() as db:
                # Find related learning data
                learning_data = db.query(LearningData).filter(
                    LearningData.user_id == user_id,
                    LearningData.experiment_id == prediction_id
                ).first()
                
                if learning_data:
                    # Update accuracy score
                    learning_data.accuracy = rating / 5.0  # Normalize to 0-1
                    learning_data.feedback_score = rating
                    db.commit()
                    
        except Exception as e:
            logger.error(f"Error updating prediction accuracy: {str(e)}")
    
    async def get_learning_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get learning statistics for a user"""
        try:
            with get_db_session() as db:
                # Get learning data count
                learning_count = db.query(LearningData).filter(
                    LearningData.user_id == user_id
                ).count()
                
                # Get average accuracy
                avg_accuracy = db.query(LearningData).filter(
                    LearningData.user_id == user_id,
                    LearningData.accuracy > 0
                ).with_entities(LearningData.accuracy).all()
                
                avg_accuracy_score = statistics.mean([a[0] for a in avg_accuracy]) if avg_accuracy else 0
                
                return {
                    'total_learning_points': learning_count,
                    'average_accuracy': avg_accuracy_score,
                    'patterns_learned': len(self.user_patterns.get(user_id, {})),
                    'last_updated': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting learning statistics: {str(e)}")
            return {}
    
    async def cleanup(self):
        """Cleanup resources"""
        # Clear caches
        self.user_patterns.clear()
        self.learning_cache.clear()
        logger.info("Learning system cleaned up successfully") 