"""Message sending routes for unified communication."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.api.v1.auth import get_current_user
from app.schemas.message import (
    UnifiedMessage, 
    UnifiedMessageResponse, 
    MessageResponse,
    SlackMessage,
    TelegramMessage
)
from services.slack_service import SlackService
from services.telegram_service import TelegramService

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/send", response_model=UnifiedMessageResponse)
async def send_unified_message(
    message: UnifiedMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send message to multiple services simultaneously."""
    results = []
    total_sent = 0
    total_failed = 0
    
    # Initialize services
    slack_service = SlackService()
    telegram_service = TelegramService()
    
    # Send to Slack
    if "slack" in message.services:
        if not message.slack_channel:
            results.append(MessageResponse(
                success=False,
                service="slack",
                error="Slack channel not specified"
            ))
            total_failed += 1
        else:
            slack_result = await slack_service.send_message(
                channel=message.slack_channel,
                text=message.content,
                thread_ts=message.thread_ts
            )
            
            results.append(MessageResponse(
                success=slack_result["success"],
                service="slack",
                message_id=slack_result.get("message_id"),
                error=slack_result.get("error")
            ))
            
            if slack_result["success"]:
                total_sent += 1
            else:
                total_failed += 1
    
    # Send to Telegram
    if "telegram" in message.services:
        if not message.telegram_chat_id:
            results.append(MessageResponse(
                success=False,
                service="telegram",
                error="Telegram chat ID not specified"
            ))
            total_failed += 1
        else:
            telegram_result = await telegram_service.send_message(
                chat_id=message.telegram_chat_id,
                text=message.content,
                reply_to_message_id=message.reply_to_message_id
            )
            
            results.append(MessageResponse(
                success=telegram_result["success"],
                service="telegram",
                message_id=telegram_result.get("message_id"),
                error=telegram_result.get("error")
            ))
            
            if telegram_result["success"]:
                total_sent += 1
            else:
                total_failed += 1
    
    return UnifiedMessageResponse(
        success=total_failed == 0,
        results=results,
        total_sent=total_sent,
        total_failed=total_failed
    )


@router.post("/slack", response_model=MessageResponse)
async def send_slack_message(
    message: SlackMessage,
    current_user: User = Depends(get_current_user)
):
    """Send message to Slack only."""
    slack_service = SlackService()
    
    result = await slack_service.send_message(
        channel=message.channel,
        text=message.content,
        thread_ts=message.thread_ts
    )
    
    return MessageResponse(
        success=result["success"],
        service="slack",
        message_id=result.get("message_id"),
        error=result.get("error")
    )


@router.post("/telegram", response_model=MessageResponse)
async def send_telegram_message(
    message: TelegramMessage,
    current_user: User = Depends(get_current_user)
):
    """Send message to Telegram only."""
    telegram_service = TelegramService()
    
    result = await telegram_service.send_message(
        chat_id=message.chat_id,
        text=message.content,
        parse_mode=message.parse_mode,
        reply_to_message_id=message.reply_to_message_id
    )
    
    return MessageResponse(
        success=result["success"],
        service="telegram",
        message_id=result.get("message_id"),
        error=result.get("error")
    )


@router.get("/slack/channels")
async def list_slack_channels(current_user: User = Depends(get_current_user)):
    """List available Slack channels."""
    slack_service = SlackService()
    result = await slack_service.list_channels()
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    return {"channels": result["channels"]}


@router.get("/telegram/webhook-info")
async def get_telegram_webhook_info(current_user: User = Depends(get_current_user)):
    """Get Telegram webhook information."""
    telegram_service = TelegramService()
    result = await telegram_service.get_webhook_info()
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    return result["webhook_info"]
