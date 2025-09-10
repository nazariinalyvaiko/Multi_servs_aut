"""Telegram service for sending and receiving messages."""

import logging
from typing import Optional, Dict, Any
from telegram import Bot, Update
from telegram.error import TelegramError
from app.core.config import settings

logger = logging.getLogger(__name__)


class TelegramService:
    """Service for interacting with Telegram Bot API."""
    
    def __init__(self, bot_token: Optional[str] = None):
        """Initialize Telegram service with bot token."""
        self.bot_token = bot_token or settings.telegram_bot_token
        self.bot = Bot(token=self.bot_token)
    
    async def send_message(
        self, 
        chat_id: str, 
        text: str, 
        parse_mode: str = "HTML",
        reply_to_message_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send a message to a Telegram chat.
        
        Args:
            chat_id: Chat ID (user ID or group ID)
            text: Message text
            parse_mode: Message parse mode (HTML, Markdown, etc.)
            reply_to_message_id: Optional message ID to reply to
            
        Returns:
            Dict containing success status and message details
        """
        try:
            message = await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                reply_to_message_id=reply_to_message_id
            )
            
            logger.info(f"Message sent to Telegram chat {chat_id}")
            return {
                "success": True,
                "message_id": str(message.message_id),
                "chat_id": str(message.chat_id),
                "text": message.text
            }
            
        except TelegramError as e:
            logger.error(f"Telegram API error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram message: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_chat_info(self, chat_id: str) -> Dict[str, Any]:
        """
        Get information about a Telegram chat.
        
        Args:
            chat_id: Chat ID
            
        Returns:
            Dict containing chat information
        """
        try:
            chat = await self.bot.get_chat(chat_id=chat_id)
            return {
                "success": True,
                "chat": {
                    "id": chat.id,
                    "title": chat.title,
                    "type": chat.type,
                    "username": chat.username
                }
            }
        except TelegramError as e:
            logger.error(f"Telegram API error getting chat info: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def set_webhook(self, webhook_url: str) -> Dict[str, Any]:
        """
        Set webhook URL for receiving updates.
        
        Args:
            webhook_url: Webhook URL
            
        Returns:
            Dict containing success status
        """
        try:
            result = await self.bot.set_webhook(url=webhook_url)
            if result:
                logger.info(f"Webhook set to {webhook_url}")
                return {
                    "success": True,
                    "webhook_url": webhook_url
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to set webhook"
                }
        except TelegramError as e:
            logger.error(f"Telegram API error setting webhook: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_webhook(self) -> Dict[str, Any]:
        """
        Delete webhook.
        
        Returns:
            Dict containing success status
        """
        try:
            result = await self.bot.delete_webhook()
            if result:
                logger.info("Webhook deleted")
                return {
                    "success": True
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to delete webhook"
                }
        except TelegramError as e:
            logger.error(f"Telegram API error deleting webhook: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_webhook_info(self) -> Dict[str, Any]:
        """
        Get webhook information.
        
        Returns:
            Dict containing webhook information
        """
        try:
            webhook_info = await self.bot.get_webhook_info()
            return {
                "success": True,
                "webhook_info": {
                    "url": webhook_info.url,
                    "has_custom_certificate": webhook_info.has_custom_certificate,
                    "pending_update_count": webhook_info.pending_update_count,
                    "last_error_date": webhook_info.last_error_date,
                    "last_error_message": webhook_info.last_error_message,
                    "max_connections": webhook_info.max_connections,
                    "allowed_updates": webhook_info.allowed_updates
                }
            }
        except TelegramError as e:
            logger.error(f"Telegram API error getting webhook info: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_webhook(self, update_data: dict) -> bool:
        """
        Verify Telegram webhook data.
        
        Args:
            update_data: Update data from webhook
            
        Returns:
            True if data is valid
        """
        try:
            # Basic validation - in production, you might want more sophisticated validation
            return "update_id" in update_data and "message" in update_data
        except Exception as e:
            logger.error(f"Error verifying Telegram webhook: {str(e)}")
            return False
