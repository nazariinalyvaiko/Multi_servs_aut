"""Google Sheets integration routes."""

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.core.database import get_db
from app.models.user import User
from app.api.v1.auth import get_current_user
from services.sheets_service import SheetsService

router = APIRouter(prefix="/sheets", tags=["sheets"])


class SheetAppendRequest(BaseModel):
    """Request schema for appending data to a sheet."""
    spreadsheet_id: str = Field(..., description="Google Sheets spreadsheet ID")
    range_name: str = Field(..., description="Range to append to (e.g., 'Sheet1!A:Z')")
    values: List[Any] = Field(..., description="Values to append")


class SheetReadRequest(BaseModel):
    """Request schema for reading data from a sheet."""
    spreadsheet_id: str = Field(..., description="Google Sheets spreadsheet ID")
    range_name: str = Field(..., description="Range to read (e.g., 'Sheet1!A1:Z100')")


class SheetUpdateRequest(BaseModel):
    """Request schema for updating data in a sheet."""
    spreadsheet_id: str = Field(..., description="Google Sheets spreadsheet ID")
    range_name: str = Field(..., description="Range to update (e.g., 'Sheet1!A1:Z100')")
    values: List[List[Any]] = Field(..., description="2D array of values to write")


@router.post("/append")
async def append_to_sheet(
    request: SheetAppendRequest,
    current_user: User = Depends(get_current_user)
):
    """Append a row to a Google Sheet."""
    sheets_service = SheetsService()
    
    result = await sheets_service.append_row(
        spreadsheet_id=request.spreadsheet_id,
        range_name=request.range_name,
        values=request.values
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    return result


@router.post("/read")
async def read_from_sheet(
    request: SheetReadRequest,
    current_user: User = Depends(get_current_user)
):
    """Read data from a Google Sheet."""
    sheets_service = SheetsService()
    
    result = await sheets_service.read_range(
        spreadsheet_id=request.spreadsheet_id,
        range_name=request.range_name
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    return result


@router.post("/update")
async def update_sheet(
    request: SheetUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update data in a Google Sheet."""
    sheets_service = SheetsService()
    
    result = await sheets_service.update_range(
        spreadsheet_id=request.spreadsheet_id,
        range_name=request.range_name,
        values=request.values
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    return result


@router.get("/info/{spreadsheet_id}")
async def get_sheet_info(
    spreadsheet_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get information about a Google Sheet."""
    sheets_service = SheetsService()
    
    result = await sheets_service.get_spreadsheet_info(spreadsheet_id)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    return result
