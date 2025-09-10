"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Multi-Service Automation Platform" in response.json()["message"]


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_user():
    """Test user registration."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123"
    }
    
    with patch('app.api.v1.auth.get_user_by_email', return_value=None):
        with patch('app.core.database.SessionLocal') as mock_db:
            mock_db.return_value.add = Mock()
            mock_db.return_value.commit = Mock()
            mock_db.return_value.refresh = Mock(side_effect=lambda x: setattr(x, 'id', 1))
            
            response = client.post("/api/v1/auth/register", json=user_data)
            assert response.status_code == 200
            assert response.json()["email"] == "test@example.com"


def test_register_user_duplicate_email():
    """Test user registration with duplicate email."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123"
    }
    
    mock_user = Mock()
    mock_user.email = "test@example.com"
    
    with patch('app.api.v1.auth.get_user_by_email', return_value=mock_user):
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]


def test_login_user():
    """Test user login."""
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    
    mock_user = Mock()
    mock_user.email = "test@example.com"
    mock_user.hashed_password = "hashed_password"
    
    with patch('app.api.v1.auth.authenticate_user', return_value=mock_user):
        with patch('app.core.security.verify_password', return_value=True):
            response = client.post("/api/v1/auth/login", data=login_data)
            assert response.status_code == 200
            assert "access_token" in response.json()


def test_login_user_invalid_credentials():
    """Test user login with invalid credentials."""
    login_data = {
        "username": "test@example.com",
        "password": "wrongpassword"
    }
    
    with patch('app.api.v1.auth.authenticate_user', return_value=None):
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]


@patch('services.slack_service.SlackService.send_message')
@patch('services.telegram_service.TelegramService.send_message')
def test_send_unified_message(mock_telegram, mock_slack):
    """Test unified message sending."""
    # Mock successful responses
    mock_slack.return_value = {"success": True, "message_id": "slack-123"}
    mock_telegram.return_value = {"success": True, "message_id": "telegram-456"}
    
    message_data = {
        "content": "Test message",
        "services": ["slack", "telegram"],
        "slack_channel": "C1234567890",
        "telegram_chat_id": "456789"
    }
    
    # Mock authentication
    with patch('app.api.v1.messages.get_current_user', return_value=Mock()):
        response = client.post("/api/v1/messages/send", json=message_data)
        assert response.status_code == 200
        assert response.json()["total_sent"] == 2
        assert response.json()["total_failed"] == 0


@patch('services.sheets_service.SheetsService.append_row')
def test_append_to_sheet(mock_append):
    """Test appending to Google Sheet."""
    mock_append.return_value = {
        "success": True,
        "updated_cells": 3,
        "updated_range": "Sheet1!A1:C1"
    }
    
    sheet_data = {
        "spreadsheet_id": "test-spreadsheet-id",
        "range_name": "Sheet1!A:Z",
        "values": ["value1", "value2", "value3"]
    }
    
    # Mock authentication
    with patch('app.api.v1.sheets.get_current_user', return_value=Mock()):
        response = client.post("/api/v1/sheets/append", json=sheet_data)
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert response.json()["updated_cells"] == 3
