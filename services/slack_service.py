"""Slack service for sending and receiving messages."""

import logging
from typing import Optional, Dict, Any
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from app.core.config import settings

logger = logging.getLogger(__name__)


class SlackService:
    """Service for interacting with Slack API."""
    
    def __init__(self, bot_token: Optional[str] = None):
        """Initialize Slack service with bot token."""
        self.bot_token = bot_token or settings.slack_bot_token
        self.client = WebClient(token=self.bot_token)
    
    async def send_message(
        self, 
        channel: str, 
        text: str, 
        thread_ts: Optional[str] = None,
        blocks: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Send a message to a Slack channel.
        
        Args:
            channel: Channel ID or name (e.g., '#general' or 'C1234567890')
            text: Message text
            thread_ts: Optional thread timestamp for replies
            blocks: Optional rich formatting blocks
            
        Returns:
            Dict containing success status and message details
        """
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                thread_ts=thread_ts,
                blocks=blocks
            )
            
            if response["ok"]:
                logger.info(f"Message sent to Slack channel {channel}")
                return {
                    "success": True,
                    "message_id": response["ts"],
                    "channel": response["channel"],
                    "text": response["message"]["text"]
                }
            else:
                logger.error(f"Failed to send message to Slack: {response['error']}")
                return {
                    "success": False,
                    "error": response["error"]
                }
                
        except SlackApiError as e:
            logger.error(f"Slack API error: {e.response['error']}")
            return {
                "success": False,
                "error": e.response["error"]
            }
        except Exception as e:
            logger.error(f"Unexpected error sending Slack message: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_channel_info(self, channel: str) -> Dict[str, Any]:
        """
        Get information about a Slack channel.
        
        Args:
            channel: Channel ID or name
            
        Returns:
            Dict containing channel information
        """
        try:
            response = self.client.conversations_info(channel=channel)
            if response["ok"]:
                return {
                    "success": True,
                    "channel": response["channel"]
                }
            else:
                return {
                    "success": False,
                    "error": response["error"]
                }
        except SlackApiError as e:
            logger.error(f"Slack API error getting channel info: {e.response['error']}")
            return {
                "success": False,
                "error": e.response["error"]
            }
    
    async def list_channels(self, types: str = "public_channel,private_channel") -> Dict[str, Any]:
        """
        List available channels.
        
        Args:
            types: Channel types to include
            
        Returns:
            Dict containing list of channels
        """
        try:
            response = self.client.conversations_list(types=types)
            if response["ok"]:
                return {
                    "success": True,
                    "channels": response["channels"]
                }
            else:
                return {
                    "success": False,
                    "error": response["error"]
                }
        except SlackApiError as e:
            logger.error(f"Slack API error listing channels: {e.response['error']}")
            return {
                "success": False,
                "error": e.response["error"]
            }
    
    def verify_webhook(self, timestamp: str, body: str, signature: str) -> bool:
        """
        Verify Slack webhook signature.
        
        Args:
            timestamp: Request timestamp
            body: Request body
            signature: Request signature
            
        Returns:
            True if signature is valid
        """
        try:
            from slack_sdk.signature import SignatureVerifier
            verifier = SignatureVerifier(settings.slack_signing_secret)
            return verifier.is_valid(timestamp, body, signature)
        except Exception as e:
            logger.error(f"Error verifying Slack webhook: {str(e)}")
            return False
