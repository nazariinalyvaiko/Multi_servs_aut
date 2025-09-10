"""Tests for Telegram service."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from services.telegram_service import TelegramService


@pytest.fixture
def telegram_service():
    """Create TelegramService instance for testing."""
    return TelegramService(bot_token="test-token")


@pytest.mark.asyncio
async def test_send_message_success(telegram_service):
    """Test successful message sending."""
    mock_message = Mock()
    mock_message.message_id = 123
    mock_message.chat_id = 456
    mock_message.text = "Test message"
    
    with patch.object(telegram_service.bot, 'send_message', new_callable=AsyncMock, return_value=mock_message):
        result = await telegram_service.send_message(
            chat_id="456",
            text="Test message"
        )
        
        assert result["success"] is True
        assert result["message_id"] == "123"
        assert result["chat_id"] == "456"
        assert result["text"] == "Test message"


@pytest.mark.asyncio
async def test_send_message_failure(telegram_service):
    """Test message sending failure."""
    from telegram.error import TelegramError
    
    with patch.object(telegram_service.bot, 'send_message', new_callable=AsyncMock, side_effect=TelegramError("Bad Request")):
        result = await telegram_service.send_message(
            chat_id="invalid-chat",
            text="Test message"
        )
        
        assert result["success"] is False
        assert "Bad Request" in result["error"]


@pytest.mark.asyncio
async def test_get_chat_info_success(telegram_service):
    """Test successful chat info retrieval."""
    mock_chat = Mock()
    mock_chat.id = 456
    mock_chat.title = "Test Chat"
    mock_chat.type = "group"
    mock_chat.username = "testchat"
    
    with patch.object(telegram_service.bot, 'get_chat', new_callable=AsyncMock, return_value=mock_chat):
        result = await telegram_service.get_chat_info("456")
        
        assert result["success"] is True
        assert result["chat"]["id"] == 456
        assert result["chat"]["title"] == "Test Chat"
        assert result["chat"]["type"] == "group"


@pytest.mark.asyncio
async def test_set_webhook_success(telegram_service):
    """Test successful webhook setting."""
    with patch.object(telegram_service.bot, 'set_webhook', new_callable=AsyncMock, return_value=True):
        result = await telegram_service.set_webhook("https://example.com/webhook")
        
        assert result["success"] is True
        assert result["webhook_url"] == "https://example.com/webhook"


@pytest.mark.asyncio
async def test_verify_webhook_valid(telegram_service):
    """Test webhook verification with valid data."""
    valid_data = {
        "update_id": 123,
        "message": {
            "message_id": 456,
            "text": "Test message"
        }
    }
    
    assert telegram_service.verify_webhook(valid_data) is True


@pytest.mark.asyncio
async def test_verify_webhook_invalid(telegram_service):
    """Test webhook verification with invalid data."""
    invalid_data = {
        "update_id": 123
        # Missing message field
    }
    
    assert telegram_service.verify_webhook(invalid_data) is False
