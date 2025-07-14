import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, date
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import pickle

from app.config import get_settings
from app.database import get_db_session
from app.models import CalendarEvent, User

logger = logging.getLogger(__name__)

class CalendarManager:
    """
    Calendar management service with Google Calendar integration
    Handles calendar events, scheduling, and smart suggestions
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.service = None
        self.scopes = [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.events'
        ]
        
    async def initialize(self):
        """Initialize the calendar manager"""
        try:
            # Google Calendar is optional, so don't fail if not configured
            if self.settings.google_calendar_credentials_file:
                await self._setup_google_calendar()
            else:
                logger.warning("Google Calendar credentials not configured - using local calendar only")
            
            logger.info("Calendar manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize calendar manager: {str(e)}")
            # Don't raise - allow app to continue without Google Calendar
    
    async def _setup_google_calendar(self):
        """Setup Google Calendar API client"""
        try:
            creds = None
            token_file = self.settings.google_calendar_token_file or "token.pickle"
            
            # Load existing credentials
            if os.path.exists(token_file):
                with open(token_file, 'rb') as token:
                    creds = pickle.load(token)
            
            # Refresh or create credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.settings.google_calendar_credentials_file):
                        logger.warning("Google Calendar credentials file not found")
                        return
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.settings.google_calendar_credentials_file, 
                        self.scopes
                    )
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for future use
                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)
            
            # Build service
            self.service = build('calendar', 'v3', credentials=creds)
            logger.info("Google Calendar API client initialized")
            
        except Exception as e:
            logger.error(f"Google Calendar setup error: {str(e)}")
            self.service = None
    
    async def get_today_events(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get today's events for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List of today's events
        """
        try:
            today = date.today()
            start_time = datetime.combine(today, datetime.min.time())
            end_time = datetime.combine(today, datetime.max.time())
            
            # Get events from local database
            local_events = await self._get_local_events(user_id, start_time, end_time)
            
            # Get events from Google Calendar if available
            google_events = []
            if self.service:
                google_events = await self._get_google_events(user_id, start_time, end_time)
            
            # Combine and deduplicate events
            all_events = local_events + google_events
            return self._deduplicate_events(all_events)
            
        except Exception as e:
            logger.error(f"Error getting today's events: {str(e)}")
            return []
    
    async def _get_local_events(self, user_id: int, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get events from local database"""
        try:
            with get_db_session() as db:
                events = db.query(CalendarEvent).filter(
                    CalendarEvent.user_id == user_id,
                    CalendarEvent.start_time >= start_time,
                    CalendarEvent.start_time <= end_time
                ).order_by(CalendarEvent.start_time).all()
                
                return [
                    {
                        "id": event.id,
                        "title": event.title,
                        "description": event.description,
                        "start_time": event.start_time.isoformat(),
                        "end_time": event.end_time.isoformat(),
                        "location": event.location,
                        "source": "local"
                    }
                    for event in events
                ]
                
        except Exception as e:
            logger.error(f"Error getting local events: {str(e)}")
            return []
    
    async def _get_google_events(self, user_id: int, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get events from Google Calendar"""
        try:
            if not self.service:
                return []
            
            # Convert to RFC3339 format
            time_min = start_time.isoformat() + 'Z'
            time_max = end_time.isoformat() + 'Z'
            
            # Get events from primary calendar
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    "id": event['id'],
                    "title": event.get('summary', 'No Title'),
                    "description": event.get('description', ''),
                    "start_time": start,
                    "end_time": end,
                    "location": event.get('location', ''),
                    "source": "google"
                })
            
            return formatted_events
            
        except HttpError as e:
            logger.error(f"Google Calendar API error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error getting Google events: {str(e)}")
            return []
    
    def _deduplicate_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate events based on title and time"""
        seen = set()
        unique_events = []
        
        for event in events:
            key = (event['title'], event['start_time'])
            if key not in seen:
                seen.add(key)
                unique_events.append(event)
        
        return sorted(unique_events, key=lambda x: x['start_time'])
    
    async def create_event(self, user_id: int, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new calendar event
        
        Args:
            user_id: User ID
            event_data: Event information
            
        Returns:
            Created event data
        """
        try:
            # Create event in local database
            local_event = await self._create_local_event(user_id, event_data)
            
            # Create event in Google Calendar if available
            google_event = None
            if self.service:
                google_event = await self._create_google_event(event_data)
            
            return {
                "success": True,
                "local_event": local_event,
                "google_event": google_event
            }
            
        except Exception as e:
            logger.error(f"Error creating event: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _create_local_event(self, user_id: int, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create event in local database"""
        try:
            with get_db_session() as db:
                event = CalendarEvent(
                    user_id=user_id,
                    title=event_data['title'],
                    description=event_data.get('description', ''),
                    location=event_data.get('location', ''),
                    start_time=datetime.fromisoformat(event_data['start_time']),
                    end_time=datetime.fromisoformat(event_data['end_time']),
                    timezone=event_data.get('timezone', 'UTC')
                )
                
                db.add(event)
                db.commit()
                db.refresh(event)
                
                return {
                    "id": event.id,
                    "title": event.title,
                    "start_time": event.start_time.isoformat(),
                    "end_time": event.end_time.isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error creating local event: {str(e)}")
            raise
    
    async def _create_google_event(self, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create event in Google Calendar"""
        try:
            if not self.service:
                return None
            
            google_event = {
                'summary': event_data['title'],
                'description': event_data.get('description', ''),
                'location': event_data.get('location', ''),
                'start': {
                    'dateTime': event_data['start_time'],
                    'timeZone': event_data.get('timezone', 'UTC')
                },
                'end': {
                    'dateTime': event_data['end_time'],
                    'timeZone': event_data.get('timezone', 'UTC')
                }
            }
            
            event = self.service.events().insert(
                calendarId='primary', 
                body=google_event
            ).execute()
            
            return {
                "id": event['id'],
                "title": event['summary'],
                "start_time": event['start']['dateTime'],
                "end_time": event['end']['dateTime']
            }
            
        except HttpError as e:
            logger.error(f"Google Calendar create error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error creating Google event: {str(e)}")
            return None
    
    async def suggest_meeting_times(self, user_id: int, duration_minutes: int = 60, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """
        Suggest available meeting times
        
        Args:
            user_id: User ID
            duration_minutes: Meeting duration in minutes
            days_ahead: How many days ahead to look
            
        Returns:
            List of suggested time slots
        """
        try:
            suggestions = []
            
            # Look for slots in the next few days
            for day_offset in range(days_ahead):
                target_date = date.today() + timedelta(days=day_offset)
                
                # Skip weekends for work meetings
                if target_date.weekday() >= 5:
                    continue
                
                day_slots = await self._find_free_slots(user_id, target_date, duration_minutes)
                suggestions.extend(day_slots)
                
                # Limit to 10 suggestions
                if len(suggestions) >= 10:
                    break
            
            return suggestions[:10]
            
        except Exception as e:
            logger.error(f"Error suggesting meeting times: {str(e)}")
            return []
    
    async def _find_free_slots(self, user_id: int, target_date: date, duration_minutes: int) -> List[Dict[str, Any]]:
        """Find free time slots for a specific date"""
        try:
            # Define work hours (9 AM to 6 PM)
            work_start = datetime.combine(target_date, datetime.min.time().replace(hour=9))
            work_end = datetime.combine(target_date, datetime.min.time().replace(hour=18))
            
            # Get existing events for the day
            events = await self.get_today_events(user_id) if target_date == date.today() else []
            
            # Convert to datetime objects and sort
            busy_slots = []
            for event in events:
                start = datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
                end = datetime.fromisoformat(event['end_time'].replace('Z', '+00:00'))
                busy_slots.append((start, end))
            
            busy_slots.sort(key=lambda x: x[0])
            
            # Find free slots
            free_slots = []
            current_time = work_start
            
            for busy_start, busy_end in busy_slots:
                # Check if there's a free slot before this busy period
                if current_time + timedelta(minutes=duration_minutes) <= busy_start:
                    free_slots.append({
                        "date": target_date.isoformat(),
                        "start_time": current_time.isoformat(),
                        "end_time": (current_time + timedelta(minutes=duration_minutes)).isoformat(),
                        "duration_minutes": duration_minutes
                    })
                
                current_time = max(current_time, busy_end)
            
            # Check for slot after last busy period
            if current_time + timedelta(minutes=duration_minutes) <= work_end:
                free_slots.append({
                    "date": target_date.isoformat(),
                    "start_time": current_time.isoformat(),
                    "end_time": (current_time + timedelta(minutes=duration_minutes)).isoformat(),
                    "duration_minutes": duration_minutes
                })
            
            return free_slots
            
        except Exception as e:
            logger.error(f"Error finding free slots: {str(e)}")
            return []
    
    async def get_upcoming_events(self, user_id: int, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Get upcoming events for the next few days"""
        try:
            start_time = datetime.now()
            end_time = start_time + timedelta(days=days_ahead)
            
            # Get events from local database
            local_events = await self._get_local_events(user_id, start_time, end_time)
            
            # Get events from Google Calendar if available
            google_events = []
            if self.service:
                google_events = await self._get_google_events(user_id, start_time, end_time)
            
            # Combine and deduplicate
            all_events = local_events + google_events
            return self._deduplicate_events(all_events)
            
        except Exception as e:
            logger.error(f"Error getting upcoming events: {str(e)}")
            return []
    
    async def analyze_schedule_patterns(self, user_id: int) -> Dict[str, Any]:
        """Analyze user's schedule patterns for insights"""
        try:
            # Get past 30 days of events
            end_time = datetime.now()
            start_time = end_time - timedelta(days=30)
            
            events = await self._get_local_events(user_id, start_time, end_time)
            
            if not events:
                return {"insights": [], "patterns": {}}
            
            # Analyze patterns
            patterns = {
                "busiest_day": self._find_busiest_day(events),
                "common_meeting_times": self._find_common_meeting_times(events),
                "average_meeting_duration": self._calculate_average_duration(events),
                "meeting_frequency": len(events) / 30
            }
            
            # Generate insights
            insights = self._generate_schedule_insights(patterns)
            
            return {
                "patterns": patterns,
                "insights": insights
            }
            
        except Exception as e:
            logger.error(f"Error analyzing schedule patterns: {str(e)}")
            return {"insights": [], "patterns": {}}
    
    def _find_busiest_day(self, events: List[Dict[str, Any]]) -> str:
        """Find the busiest day of the week"""
        day_counts = {}
        for event in events:
            start_time = datetime.fromisoformat(event['start_time'])
            day_name = start_time.strftime('%A')
            day_counts[day_name] = day_counts.get(day_name, 0) + 1
        
        return max(day_counts, key=day_counts.get) if day_counts else "Unknown"
    
    def _find_common_meeting_times(self, events: List[Dict[str, Any]]) -> List[str]:
        """Find common meeting times"""
        time_counts = {}
        for event in events:
            start_time = datetime.fromisoformat(event['start_time'])
            hour = start_time.hour
            time_counts[hour] = time_counts.get(hour, 0) + 1
        
        # Get top 3 most common hours
        sorted_times = sorted(time_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        return [f"{hour}:00" for hour, _ in sorted_times]
    
    def _calculate_average_duration(self, events: List[Dict[str, Any]]) -> float:
        """Calculate average meeting duration in minutes"""
        if not events:
            return 0
        
        total_duration = 0
        for event in events:
            start = datetime.fromisoformat(event['start_time'])
            end = datetime.fromisoformat(event['end_time'])
            duration = (end - start).total_seconds() / 60
            total_duration += duration
        
        return total_duration / len(events)
    
    def _generate_schedule_insights(self, patterns: Dict[str, Any]) -> List[str]:
        """Generate insights from schedule patterns"""
        insights = []
        
        if patterns.get('busiest_day'):
            insights.append(f"Your busiest day is {patterns['busiest_day']}")
        
        if patterns.get('common_meeting_times'):
            times = ', '.join(patterns['common_meeting_times'])
            insights.append(f"Your most common meeting times are {times}")
        
        avg_duration = patterns.get('average_meeting_duration', 0)
        if avg_duration > 0:
            insights.append(f"Your average meeting duration is {avg_duration:.0f} minutes")
        
        frequency = patterns.get('meeting_frequency', 0)
        if frequency > 1:
            insights.append(f"You have an average of {frequency:.1f} meetings per day")
        
        return insights
    
    async def cleanup(self):
        """Cleanup resources"""
        self.service = None
        logger.info("Calendar manager cleaned up successfully") 