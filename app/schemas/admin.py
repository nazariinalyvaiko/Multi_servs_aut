"""Admin panel Pydantic schemas."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.user import UserResponse


class UserStats(BaseModel):
    """User statistics schema."""
    total: int
    active: int
    verified: int
    recent_registrations: int


class SystemStats(BaseModel):
    """System statistics schema."""
    users: UserStats
    services: Dict[str, int]
    sessions: int
    metrics: Dict[str, Any]


class UserListResponse(BaseModel):
    """User list response schema."""
    users: List[UserResponse]
    total: int
    page: int
    size: int
    pages: int


class RoleResponse(BaseModel):
    """Role response schema."""
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class PermissionResponse(BaseModel):
    """Permission response schema."""
    id: int
    name: str
    resource: str
    action: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class APIStats(BaseModel):
    """API statistics schema."""
    total_requests: int
    unique_users: int
    top_endpoints: List[Dict[str, Any]]
    response_times: Dict[str, float]
    error_rate: float


class CacheStats(BaseModel):
    """Cache statistics schema."""
    memory_used: str
    connected_clients: int
    total_commands_processed: int
    keyspace_hits: int
    keyspace_misses: int
    hit_rate: float


class SystemHealth(BaseModel):
    """System health schema."""
    status: str
    timestamp: datetime
    services: Dict[str, Dict[str, Any]]
    system_info: Dict[str, Any]
