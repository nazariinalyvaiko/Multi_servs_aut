"""Tests for Slack service."""

import pytest
from unittest.mock import Mock, patch
from services.slack_service import SlackService


@pytest.fixture
def slack_service():
    """Create SlackService instance for testing."""
    return SlackService(bot_token="test-token")


@pytest.mark.asyncio
async def test_send_message_success(slack_service):
    """Test successful message sending."""
    mock_response = {
        "ok": True,
        "ts": "1234567890.123456",
        "channel": "C1234567890",
        "message": {"text": "Test message"}
    }
    
    with patch.object(slack_service.client, 'chat_postMessage', return_value=mock_response):
        result = await slack_service.send_message(
            channel="C1234567890",
            text="Test message"
        )
        
        assert result["success"] is True
        assert result["message_id"] == "1234567890.123456"
        assert result["channel"] == "C1234567890"


@pytest.mark.asyncio
async def test_send_message_failure(slack_service):
    """Test message sending failure."""
    mock_response = {
        "ok": False,
        "error": "channel_not_found"
    }
    
    with patch.object(slack_service.client, 'chat_postMessage', return_value=mock_response):
        result = await slack_service.send_message(
            channel="invalid-channel",
            text="Test message"
        )
        
        assert result["success"] is False
        assert result["error"] == "channel_not_found"


@pytest.mark.asyncio
async def test_get_channel_info_success(slack_service):
    """Test successful channel info retrieval."""
    mock_response = {
        "ok": True,
        "channel": {
            "id": "C1234567890",
            "name": "test-channel",
            "is_private": False
        }
    }
    
    with patch.object(slack_service.client, 'conversations_info', return_value=mock_response):
        result = await slack_service.get_channel_info("C1234567890")
        
        assert result["success"] is True
        assert result["channel"]["id"] == "C1234567890"
        assert result["channel"]["name"] == "test-channel"


@pytest.mark.asyncio
async def test_list_channels_success(slack_service):
    """Test successful channels listing."""
    mock_response = {
        "ok": True,
        "channels": [
            {"id": "C1234567890", "name": "general"},
            {"id": "C0987654321", "name": "random"}
        ]
    }
    
    with patch.object(slack_service.client, 'conversations_list', return_value=mock_response):
        result = await slack_service.list_channels()
        
        assert result["success"] is True
        assert len(result["channels"]) == 2
        assert result["channels"][0]["name"] == "general"
