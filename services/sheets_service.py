"""Google Sheets service for reading and writing data."""

import logging
import json
from typing import Optional, Dict, Any, List
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.core.config import settings

logger = logging.getLogger(__name__)


class SheetsService:
    """Service for interacting with Google Sheets API."""
    
    def __init__(self, credentials_file: Optional[str] = None):
        """Initialize Google Sheets service with credentials."""
        self.credentials_file = credentials_file or settings.google_credentials_file
        self.scopes = settings.google_sheets_scopes
        self.service = None
        self._authenticate()
    
    def _authenticate(self) -> None:
        """Authenticate with Google Sheets API."""
        try:
            credentials = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=self.scopes
            )
            self.service = build('sheets', 'v4', credentials=credentials)
            logger.info("Successfully authenticated with Google Sheets API")
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Sheets API: {str(e)}")
            self.service = None
    
    async def append_row(
        self, 
        spreadsheet_id: str, 
        range_name: str, 
        values: List[Any]
    ) -> Dict[str, Any]:
        """
        Append a row to a Google Sheet.
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            range_name: The range to append to (e.g., 'Sheet1!A:Z')
            values: List of values to append
            
        Returns:
            Dict containing success status and details
        """
        if not self.service:
            return {
                "success": False,
                "error": "Google Sheets service not authenticated"
            }
        
        try:
            body = {
                'values': [values]
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            logger.info(f"Row appended to sheet {spreadsheet_id}")
            return {
                "success": True,
                "updated_cells": result.get('updates', {}).get('updatedCells', 0),
                "updated_range": result.get('updates', {}).get('updatedRange', ''),
                "spreadsheet_id": spreadsheet_id
            }
            
        except HttpError as e:
            logger.error(f"Google Sheets API error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error appending to Google Sheet: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def read_range(
        self, 
        spreadsheet_id: str, 
        range_name: str
    ) -> Dict[str, Any]:
        """
        Read data from a Google Sheet range.
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            range_name: The range to read (e.g., 'Sheet1!A1:Z100')
            
        Returns:
            Dict containing success status and data
        """
        if not self.service:
            return {
                "success": False,
                "error": "Google Sheets service not authenticated"
            }
        
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            logger.info(f"Read {len(values)} rows from sheet {spreadsheet_id}")
            return {
                "success": True,
                "values": values,
                "range": result.get('range', ''),
                "major_dimension": result.get('majorDimension', 'ROWS')
            }
            
        except HttpError as e:
            logger.error(f"Google Sheets API error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error reading Google Sheet: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_range(
        self, 
        spreadsheet_id: str, 
        range_name: str, 
        values: List[List[Any]]
    ) -> Dict[str, Any]:
        """
        Update a range in a Google Sheet.
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            range_name: The range to update (e.g., 'Sheet1!A1:Z100')
            values: 2D list of values to write
            
        Returns:
            Dict containing success status and details
        """
        if not self.service:
            return {
                "success": False,
                "error": "Google Sheets service not authenticated"
            }
        
        try:
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            logger.info(f"Range updated in sheet {spreadsheet_id}")
            return {
                "success": True,
                "updated_cells": result.get('updatedCells', 0),
                "updated_range": result.get('updatedRange', ''),
                "spreadsheet_id": spreadsheet_id
            }
            
        except HttpError as e:
            logger.error(f"Google Sheets API error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error updating Google Sheet: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_spreadsheet_info(self, spreadsheet_id: str) -> Dict[str, Any]:
        """
        Get information about a Google Sheet.
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            
        Returns:
            Dict containing spreadsheet information
        """
        if not self.service:
            return {
                "success": False,
                "error": "Google Sheets service not authenticated"
            }
        
        try:
            result = self.service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            sheets = []
            for sheet in result.get('sheets', []):
                sheets.append({
                    'title': sheet.get('properties', {}).get('title', ''),
                    'sheet_id': sheet.get('properties', {}).get('sheetId', 0),
                    'row_count': sheet.get('properties', {}).get('gridProperties', {}).get('rowCount', 0),
                    'column_count': sheet.get('properties', {}).get('gridProperties', {}).get('columnCount', 0)
                })
            
            return {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "title": result.get('properties', {}).get('title', ''),
                "sheets": sheets
            }
            
        except HttpError as e:
            logger.error(f"Google Sheets API error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error getting spreadsheet info: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
