import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from collections import defaultdict
import uuid

logger = logging.getLogger(__name__)

class WebSocketManager:
    """
    WebSocket manager for real-time communication
    Handles connections, broadcasting, and user-specific messaging
    """
    
    def __init__(self):
        # Store active connections: user_id -> Set of WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = defaultdict(set)
        
        # Store connection metadata
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        
        # Store user sessions
        self.user_sessions: Dict[int, Dict[str, Any]] = {}
        
        # Message queue for offline users
        self.offline_messages: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
        
        # Connection statistics
        self.connection_stats: Dict[str, Any] = {
            'total_connections': 0,
            'active_connections': 0,
            'messages_sent': 0,
            'messages_received': 0
        }
    
    async def connect(self, websocket: WebSocket, user_id: int, session_data: Dict[str, Any] = None):
        """
        Connect a new WebSocket for a user
        
        Args:
            websocket: WebSocket connection
            user_id: User ID
            session_data: Optional session data
        """
        try:
            # Accept the connection
            await websocket.accept()
            
            # Add to active connections
            self.active_connections[user_id].add(websocket)
            
            # Store connection metadata
            self.connection_metadata[websocket] = {
                'user_id': user_id,
                'connected_at': datetime.now().isoformat(),
                'session_id': str(uuid.uuid4()),
                'session_data': session_data or {}
            }
            
            # Update user session
            self.user_sessions[user_id] = {
                'user_id': user_id,
                'last_activity': datetime.now().isoformat(),
                'active_connections': len(self.active_connections[user_id]),
                'session_data': session_data or {}
            }
            
            # Update statistics
            self.connection_stats['total_connections'] += 1
            self.connection_stats['active_connections'] = sum(
                len(connections) for connections in self.active_connections.values()
            )
            
            logger.info(f"User {user_id} connected via WebSocket")
            
            # Send connection confirmation
            await self._send_to_connection(websocket, {
                'type': 'connection_confirmed',
                'data': {
                    'user_id': user_id,
                    'session_id': self.connection_metadata[websocket]['session_id'],
                    'timestamp': datetime.now().isoformat()
                }
            })
            
            # Send any offline messages
            await self._send_offline_messages(user_id)
            
        except Exception as e:
            logger.error(f"Error connecting WebSocket for user {user_id}: {str(e)}")
            await self.disconnect(user_id, websocket)
    
    async def disconnect(self, user_id: int, websocket: WebSocket = None):
        """
        Disconnect a WebSocket for a user
        
        Args:
            user_id: User ID
            websocket: Specific WebSocket connection (if None, disconnect all)
        """
        try:
            if websocket:
                # Disconnect specific connection
                if websocket in self.active_connections[user_id]:
                    self.active_connections[user_id].remove(websocket)
                
                # Remove connection metadata
                if websocket in self.connection_metadata:
                    del self.connection_metadata[websocket]
                
                # Close the connection
                try:
                    await websocket.close()
                except:
                    pass  # Connection might already be closed
                
            else:
                # Disconnect all connections for user
                connections_to_close = self.active_connections[user_id].copy()
                for conn in connections_to_close:
                    try:
                        await conn.close()
                    except:
                        pass
                    
                    if conn in self.connection_metadata:
                        del self.connection_metadata[conn]
                
                self.active_connections[user_id].clear()
            
            # Clean up empty connection sets
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            
            # Update user session
            if user_id in self.user_sessions:
                self.user_sessions[user_id]['active_connections'] = len(
                    self.active_connections.get(user_id, set())
                )
                
                # Remove session if no active connections
                if not self.active_connections.get(user_id):
                    del self.user_sessions[user_id]
            
            # Update statistics
            self.connection_stats['active_connections'] = sum(
                len(connections) for connections in self.active_connections.values()
            )
            
            logger.info(f"User {user_id} disconnected from WebSocket")
            
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket for user {user_id}: {str(e)}")
    
    async def send_to_user(self, user_id: int, message: Dict[str, Any]) -> bool:
        """
        Send a message to a specific user
        
        Args:
            user_id: User ID
            message: Message to send
            
        Returns:
            True if message was sent, False if user is offline
        """
        try:
            # Add timestamp to message
            message['timestamp'] = datetime.now().isoformat()
            
            # Check if user is online
            if user_id in self.active_connections:
                # Send to all active connections for this user
                connections = self.active_connections[user_id].copy()
                sent_successfully = False
                
                for websocket in connections:
                    try:
                        await self._send_to_connection(websocket, message)
                        sent_successfully = True
                    except WebSocketDisconnect:
                        # Connection was closed, remove it
                        await self.disconnect(user_id, websocket)
                    except Exception as e:
                        logger.error(f"Error sending message to user {user_id}: {str(e)}")
                        # Remove problematic connection
                        await self.disconnect(user_id, websocket)
                
                if sent_successfully:
                    self.connection_stats['messages_sent'] += 1
                    return True
            
            # User is offline, queue message
            await self._queue_offline_message(user_id, message)
            return False
            
        except Exception as e:
            logger.error(f"Error sending message to user {user_id}: {str(e)}")
            return False
    
    async def broadcast_to_all(self, message: Dict[str, Any], exclude_user: int = None):
        """
        Broadcast a message to all connected users
        
        Args:
            message: Message to broadcast
            exclude_user: User ID to exclude from broadcast
        """
        try:
            # Add timestamp to message
            message['timestamp'] = datetime.now().isoformat()
            
            # Send to all active connections
            for user_id, connections in self.active_connections.items():
                if exclude_user and user_id == exclude_user:
                    continue
                
                connections_copy = connections.copy()
                for websocket in connections_copy:
                    try:
                        await self._send_to_connection(websocket, message)
                        self.connection_stats['messages_sent'] += 1
                    except WebSocketDisconnect:
                        await self.disconnect(user_id, websocket)
                    except Exception as e:
                        logger.error(f"Error broadcasting to user {user_id}: {str(e)}")
                        await self.disconnect(user_id, websocket)
            
        except Exception as e:
            logger.error(f"Error broadcasting message: {str(e)}")
    
    async def broadcast_to_user(self, user_id: int, message: Dict[str, Any]):
        """
        Broadcast a message to a specific user (alias for send_to_user)
        
        Args:
            user_id: User ID
            message: Message to send
        """
        await self.send_to_user(user_id, message)
    
    async def _send_to_connection(self, websocket: WebSocket, message: Dict[str, Any]):
        """
        Send a message to a specific WebSocket connection
        
        Args:
            websocket: WebSocket connection
            message: Message to send
        """
        try:
            # Convert message to JSON string
            message_json = json.dumps(message, default=str)
            
            # Send the message
            await websocket.send_text(message_json)
            
        except Exception as e:
            logger.error(f"Error sending message to WebSocket: {str(e)}")
            raise
    
    async def _queue_offline_message(self, user_id: int, message: Dict[str, Any]):
        """
        Queue a message for offline user
        
        Args:
            user_id: User ID
            message: Message to queue
        """
        try:
            # Add to offline message queue
            self.offline_messages[user_id].append(message)
            
            # Limit queue size to prevent memory issues
            max_queue_size = 100
            if len(self.offline_messages[user_id]) > max_queue_size:
                # Remove oldest messages
                self.offline_messages[user_id] = self.offline_messages[user_id][-max_queue_size:]
            
            logger.info(f"Queued offline message for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error queuing offline message: {str(e)}")
    
    async def _send_offline_messages(self, user_id: int):
        """
        Send queued offline messages to a user
        
        Args:
            user_id: User ID
        """
        try:
            if user_id in self.offline_messages:
                messages = self.offline_messages[user_id].copy()
                
                # Send each queued message
                for message in messages:
                    await self.send_to_user(user_id, {
                        'type': 'offline_message',
                        'data': message
                    })
                
                # Clear offline messages
                self.offline_messages[user_id].clear()
                
                logger.info(f"Sent {len(messages)} offline messages to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error sending offline messages: {str(e)}")
    
    async def handle_message(self, websocket: WebSocket, message: str):
        """
        Handle incoming WebSocket message
        
        Args:
            websocket: WebSocket connection
            message: Incoming message
        """
        try:
            # Parse JSON message
            data = json.loads(message)
            
            # Get connection metadata
            connection_info = self.connection_metadata.get(websocket)
            if not connection_info:
                logger.warning("Received message from unknown connection")
                return
            
            user_id = connection_info['user_id']
            
            # Update statistics
            self.connection_stats['messages_received'] += 1
            
            # Update user session activity
            if user_id in self.user_sessions:
                self.user_sessions[user_id]['last_activity'] = datetime.now().isoformat()
            
            # Handle different message types
            message_type = data.get('type')
            
            if message_type == 'ping':
                await self._handle_ping(websocket, data)
            elif message_type == 'typing':
                await self._handle_typing(user_id, data)
            elif message_type == 'voice_data':
                await self._handle_voice_data(user_id, data)
            elif message_type == 'user_status':
                await self._handle_user_status(user_id, data)
            else:
                logger.warning(f"Unknown message type: {message_type}")
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON received from WebSocket")
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {str(e)}")
    
    async def _handle_ping(self, websocket: WebSocket, data: Dict[str, Any]):
        """Handle ping message"""
        try:
            await self._send_to_connection(websocket, {
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error handling ping: {str(e)}")
    
    async def _handle_typing(self, user_id: int, data: Dict[str, Any]):
        """Handle typing indicator"""
        try:
            # Broadcast typing status to other connections (if needed)
            typing_message = {
                'type': 'typing_status',
                'data': {
                    'user_id': user_id,
                    'is_typing': data.get('is_typing', False),
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            # Could broadcast to other users in a group chat scenario
            # For now, just log it
            logger.info(f"User {user_id} typing status: {data.get('is_typing', False)}")
            
        except Exception as e:
            logger.error(f"Error handling typing: {str(e)}")
    
    async def _handle_voice_data(self, user_id: int, data: Dict[str, Any]):
        """Handle voice data message"""
        try:
            # Process voice data (this could trigger voice processing)
            logger.info(f"Received voice data from user {user_id}")
            
            # Send acknowledgment
            await self.send_to_user(user_id, {
                'type': 'voice_received',
                'data': {
                    'status': 'processing',
                    'timestamp': datetime.now().isoformat()
                }
            })
            
        except Exception as e:
            logger.error(f"Error handling voice data: {str(e)}")
    
    async def _handle_user_status(self, user_id: int, data: Dict[str, Any]):
        """Handle user status update"""
        try:
            # Update user session with status
            if user_id in self.user_sessions:
                self.user_sessions[user_id]['status'] = data.get('status', 'online')
                self.user_sessions[user_id]['last_activity'] = datetime.now().isoformat()
            
            logger.info(f"User {user_id} status updated: {data.get('status', 'online')}")
            
        except Exception as e:
            logger.error(f"Error handling user status: {str(e)}")
    
    def get_active_users(self) -> List[int]:
        """Get list of active user IDs"""
        return list(self.active_connections.keys())
    
    def get_user_connection_count(self, user_id: int) -> int:
        """Get number of active connections for a user"""
        return len(self.active_connections.get(user_id, set()))
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics"""
        return {
            **self.connection_stats,
            'active_users': len(self.active_connections),
            'total_active_connections': sum(
                len(connections) for connections in self.active_connections.values()
            ),
            'offline_message_queues': len(self.offline_messages),
            'total_offline_messages': sum(
                len(messages) for messages in self.offline_messages.values()
            )
        }
    
    def get_user_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user session information"""
        return self.user_sessions.get(user_id)
    
    def get_all_user_sessions(self) -> Dict[int, Dict[str, Any]]:
        """Get all user sessions"""
        return self.user_sessions.copy()
    
    async def send_system_notification(self, message: str, user_id: int = None):
        """
        Send a system notification
        
        Args:
            message: Notification message
            user_id: Specific user ID (if None, send to all)
        """
        notification = {
            'type': 'system_notification',
            'data': {
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'severity': 'info'
            }
        }
        
        if user_id:
            await self.send_to_user(user_id, notification)
        else:
            await self.broadcast_to_all(notification)
    
    async def send_ai_response(self, user_id: int, response: str, context: Dict[str, Any] = None):
        """
        Send an AI response to a user
        
        Args:
            user_id: User ID
            response: AI response text
            context: Additional context
        """
        message = {
            'type': 'ai_response',
            'data': {
                'response': response,
                'context': context or {},
                'timestamp': datetime.now().isoformat()
            }
        }
        
        await self.send_to_user(user_id, message)
    
    async def send_task_notification(self, user_id: int, task_data: Dict[str, Any]):
        """
        Send a task-related notification
        
        Args:
            user_id: User ID
            task_data: Task information
        """
        message = {
            'type': 'task_notification',
            'data': {
                **task_data,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        await self.send_to_user(user_id, message)
    
    async def send_calendar_reminder(self, user_id: int, event_data: Dict[str, Any]):
        """
        Send a calendar reminder
        
        Args:
            user_id: User ID
            event_data: Event information
        """
        message = {
            'type': 'calendar_reminder',
            'data': {
                **event_data,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        await self.send_to_user(user_id, message)
    
    async def cleanup_inactive_connections(self):
        """Clean up inactive connections"""
        try:
            current_time = datetime.now()
            inactive_connections = []
            
            # Find inactive connections
            for websocket, metadata in self.connection_metadata.items():
                connected_at = datetime.fromisoformat(metadata['connected_at'])
                if (current_time - connected_at).total_seconds() > 3600:  # 1 hour timeout
                    inactive_connections.append((websocket, metadata['user_id']))
            
            # Disconnect inactive connections
            for websocket, user_id in inactive_connections:
                await self.disconnect(user_id, websocket)
            
            logger.info(f"Cleaned up {len(inactive_connections)} inactive connections")
            
        except Exception as e:
            logger.error(f"Error cleaning up inactive connections: {str(e)}")
    
    async def shutdown(self):
        """Shutdown the WebSocket manager"""
        try:
            # Disconnect all connections
            for user_id in list(self.active_connections.keys()):
                await self.disconnect(user_id)
            
            # Clear all data
            self.active_connections.clear()
            self.connection_metadata.clear()
            self.user_sessions.clear()
            self.offline_messages.clear()
            
            logger.info("WebSocket manager shut down successfully")
            
        except Exception as e:
            logger.error(f"Error shutting down WebSocket manager: {str(e)}") 