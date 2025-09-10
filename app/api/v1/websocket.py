"""WebSocket endpoints for real-time updates."""

import json
import logging
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import verify_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ws", tags=["websocket"])

# Store active connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"User {user_id} connected via WebSocket")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"User {user_id} disconnected from WebSocket")

    async def send_personal_message(self, message: Dict[str, Any], user_id: str):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {str(e)}")
                self.disconnect(user_id)

    async def broadcast(self, message: Dict[str, Any]):
        for user_id, connection in self.active_connections.items():
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to user {user_id}: {str(e)}")
                self.disconnect(user_id)

manager = ConnectionManager()


def get_user_from_token(token: str, db: Session) -> User:
    """Get user from JWT token."""
    email = verify_token(token)
    if not email:
        return None
    
    return db.query(User).filter(User.email == email).first()


@router.websocket("/connect")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    """WebSocket endpoint for real-time updates."""
    if not token:
        await websocket.close(code=1008, reason="Authentication required")
        return

    # Get database session
    db = next(get_db())
    try:
        user = get_user_from_token(token, db)
        if not user:
            await websocket.close(code=1008, reason="Invalid token")
            return

        await manager.connect(websocket, str(user.id))
        
        # Send welcome message
        await manager.send_personal_message({
            "type": "connection",
            "message": "Connected to real-time updates",
            "user_id": user.id,
            "timestamp": str(datetime.utcnow())
        }, str(user.id))

        try:
            while True:
                # Keep connection alive and handle incoming messages
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": str(datetime.utcnow())
                    }, str(user.id))
                
        except WebSocketDisconnect:
            manager.disconnect(str(user.id))
        except Exception as e:
            logger.error(f"WebSocket error for user {user.id}: {str(e)}")
            manager.disconnect(str(user.id))
    
    finally:
        db.close()


# Utility functions for sending updates
async def send_message_update(user_id: str, service: str, message_data: Dict[str, Any]):
    """Send message update to specific user."""
    await manager.send_personal_message({
        "type": "message_update",
        "service": service,
        "data": message_data,
        "timestamp": str(datetime.utcnow())
    }, user_id)


async def send_sheet_update(user_id: str, sheet_data: Dict[str, Any]):
    """Send sheet update to specific user."""
    await manager.send_personal_message({
        "type": "sheet_update",
        "data": sheet_data,
        "timestamp": str(datetime.utcnow())
    }, user_id)


async def broadcast_system_update(update_data: Dict[str, Any]):
    """Broadcast system update to all connected users."""
    await manager.broadcast({
        "type": "system_update",
        "data": update_data,
        "timestamp": str(datetime.utcnow())
    })
