"""Message-related Pydantic schemas."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    """Base message schema."""
    content: str = Field(..., min_length=1, max_length=4000)
    channel: Optional[str] = None


class SlackMessage(MessageBase):
    """Schema for Slack message."""
    channel: str = Field(..., description="Slack channel ID or name")
    thread_ts: Optional[str] = Field(None, description="Thread timestamp for replies")


class TelegramMessage(MessageBase):
    """Schema for Telegram message."""
    chat_id: str = Field(..., description="Telegram chat ID")
    parse_mode: Optional[str] = Field("HTML", description="Message parse mode")
    reply_to_message_id: Optional[int] = Field(None, description="Message ID to reply to")


class UnifiedMessage(BaseModel):
    """Schema for unified message sending to multiple services."""
    content: str = Field(..., min_length=1, max_length=4000)
    services: List[str] = Field(..., description="List of services to send to: ['slack', 'telegram']")
    slack_channel: Optional[str] = Field(None, description="Slack channel ID or name")
    telegram_chat_id: Optional[str] = Field(None, description="Telegram chat ID")
    thread_ts: Optional[str] = Field(None, description="Slack thread timestamp")
    reply_to_message_id: Optional[int] = Field(None, description="Telegram reply to message ID")


class MessageResponse(BaseModel):
    """Schema for message sending response."""
    success: bool
    service: str
    message_id: Optional[str] = None
    error: Optional[str] = None


class UnifiedMessageResponse(BaseModel):
    """Schema for unified message response."""
    success: bool
    results: List[MessageResponse]
    total_sent: int
    total_failed: int
