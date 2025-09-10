"""Tests for Google Sheets service."""

import pytest
from unittest.mock import Mock, patch
from services.sheets_service import SheetsService


@pytest.fixture
def sheets_service():
    """Create SheetsService instance for testing."""
    with patch('services.sheets_service.Credentials.from_service_account_file'):
        with patch('services.sheets_service.build'):
            return SheetsService(credentials_file="test-credentials.json")


@pytest.mark.asyncio
async def test_append_row_success(sheets_service):
    """Test successful row appending."""
    mock_result = {
        'updates': {
            'updatedCells': 5,
            'updatedRange': 'Sheet1!A1:E1'
        }
    }
    
    with patch.object(sheets_service.service.spreadsheets().values(), 'append', return_value=mock_result):
        result = await sheets_service.append_row(
            spreadsheet_id="test-spreadsheet-id",
            range_name="Sheet1!A:Z",
            values=["value1", "value2", "value3"]
        )
        
        assert result["success"] is True
        assert result["updated_cells"] == 5
        assert result["updated_range"] == "Sheet1!A1:E1"


@pytest.mark.asyncio
async def test_append_row_failure(sheets_service):
    """Test row appending failure."""
    from googleapiclient.errors import HttpError
    
    mock_error = HttpError(Mock(status=400), b'{"error": "Invalid range"}')
    
    with patch.object(sheets_service.service.spreadsheets().values(), 'append', side_effect=mock_error):
        result = await sheets_service.append_row(
            spreadsheet_id="test-spreadsheet-id",
            range_name="InvalidRange",
            values=["value1", "value2"]
        )
        
        assert result["success"] is False
        assert "Invalid range" in str(result["error"])


@pytest.mark.asyncio
async def test_read_range_success(sheets_service):
    """Test successful range reading."""
    mock_result = {
        'values': [
            ['Header1', 'Header2', 'Header3'],
            ['Value1', 'Value2', 'Value3']
        ],
        'range': 'Sheet1!A1:C2',
        'majorDimension': 'ROWS'
    }
    
    with patch.object(sheets_service.service.spreadsheets().values(), 'get', return_value=mock_result):
        result = await sheets_service.read_range(
            spreadsheet_id="test-spreadsheet-id",
            range_name="Sheet1!A1:C2"
        )
        
        assert result["success"] is True
        assert len(result["values"]) == 2
        assert result["values"][0] == ['Header1', 'Header2', 'Header3']
        assert result["range"] == "Sheet1!A1:C2"


@pytest.mark.asyncio
async def test_get_spreadsheet_info_success(sheets_service):
    """Test successful spreadsheet info retrieval."""
    mock_result = {
        'properties': {
            'title': 'Test Spreadsheet'
        },
        'sheets': [
            {
                'properties': {
                    'title': 'Sheet1',
                    'sheetId': 0,
                    'gridProperties': {
                        'rowCount': 100,
                        'columnCount': 10
                    }
                }
            }
        ]
    }
    
    with patch.object(sheets_service.service.spreadsheets(), 'get', return_value=mock_result):
        result = await sheets_service.get_spreadsheet_info("test-spreadsheet-id")
        
        assert result["success"] is True
        assert result["title"] == "Test Spreadsheet"
        assert len(result["sheets"]) == 1
        assert result["sheets"][0]["title"] == "Sheet1"
        assert result["sheets"][0]["row_count"] == 100
