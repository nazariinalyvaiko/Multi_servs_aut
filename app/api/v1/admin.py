"""Admin panel API endpoints."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.rate_limiting import rate_limit
from app.core.cache import cache
from app.core.monitoring import metrics, APIAnalytics
from app.models.user import User
from app.models.role import Role, Permission, UserSession
from app.schemas.admin import (
    UserStats, SystemStats, APIStats, 
    UserListResponse, RoleResponse, PermissionResponse
)
from app.core.exceptions import AuthorizationError

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin privileges."""
    if not current_user.is_superuser and not current_user.has_role("admin"):
        raise AuthorizationError("Admin privileges required")
    return current_user


@router.get("/stats/overview", response_model=SystemStats)
@rate_limit(limit=10, window=60)
async def get_system_overview(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get system overview statistics."""
    
    # Get user statistics
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    verified_users = db.query(User).filter(User.is_verified == True).count()
    
    # Get recent registrations (last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_registrations = db.query(User).filter(
        User.created_at >= thirty_days_ago
    ).count()
    
    # Get service connection stats
    slack_connected = db.query(User).filter(User.slack_connected == True).count()
    telegram_connected = db.query(User).filter(User.telegram_connected == True).count()
    sheets_connected = db.query(User).filter(User.google_sheets_connected == True).count()
    
    # Get active sessions
    active_sessions = db.query(UserSession).filter(
        UserSession.is_active == True
    ).count()
    
    return SystemStats(
        users=UserStats(
            total=total_users,
            active=active_users,
            verified=verified_users,
            recent_registrations=recent_registrations
        ),
        services={
            "slack": slack_connected,
            "telegram": telegram_connected,
            "google_sheets": sheets_connected
        },
        sessions=active_sessions,
        metrics=metrics.get_metrics()
    )


@router.get("/users", response_model=UserListResponse)
@rate_limit(limit=20, window=60)
async def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List users with pagination and filtering."""
    
    query = db.query(User)
    
    # Apply filters
    if search:
        query = query.filter(
            (User.username.contains(search)) |
            (User.email.contains(search)) |
            (User.first_name.contains(search)) |
            (User.last_name.contains(search))
        )
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    users = query.offset(offset).limit(size).all()
    
    return UserListResponse(
        users=users,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.get("/users/{user_id}")
@rate_limit(limit=30, window=60)
async def get_user_details(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get detailed user information."""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get user sessions
    sessions = db.query(UserSession).filter(
        UserSession.user_id == user_id
    ).order_by(desc(UserSession.created_at)).limit(10).all()
    
    return {
        "user": user,
        "sessions": sessions,
        "roles": user.roles,
        "permissions": [p for role in user.roles for p in role.permissions]
    }


@router.get("/api/stats", response_model=APIStats)
@rate_limit(limit=10, window=60)
async def get_api_statistics(
    hours: int = Query(24, ge=1, le=168),  # Max 1 week
    current_user: User = Depends(require_admin)
):
    """Get API usage statistics."""
    
    # Get cached stats or generate new ones
    cache_key = f"api_stats:{hours}h"
    stats = await cache.get(cache_key)
    
    if not stats:
        stats = await APIAnalytics.get_usage_stats(hours)
        await cache.set(cache_key, stats, ttl=300)  # Cache for 5 minutes
    
    return APIStats(**stats)


@router.get("/roles", response_model=List[RoleResponse])
@rate_limit(limit=20, window=60)
async def list_roles(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all roles."""
    
    roles = db.query(Role).filter(Role.is_active == True).all()
    return roles


@router.get("/permissions", response_model=List[PermissionResponse])
@rate_limit(limit=20, window=60)
async def list_permissions(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all permissions."""
    
    permissions = db.query(Permission).all()
    return permissions


@router.post("/users/{user_id}/roles/{role_id}")
@rate_limit(limit=10, window=60)
async def assign_role(
    user_id: int,
    role_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Assign role to user."""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    if role not in user.roles:
        user.roles.append(role)
        db.commit()
    
    return {"message": f"Role {role.name} assigned to user {user.username}"}


@router.delete("/users/{user_id}/roles/{role_id}")
@rate_limit(limit=10, window=60)
async def remove_role(
    user_id: int,
    role_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Remove role from user."""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    if role in user.roles:
        user.roles.remove(role)
        db.commit()
    
    return {"message": f"Role {role.name} removed from user {user.username}"}


@router.post("/users/{user_id}/deactivate")
@rate_limit(limit=5, window=60)
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Deactivate user account."""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    user.is_active = False
    db.commit()
    
    return {"message": f"User {user.username} deactivated"}


@router.post("/users/{user_id}/activate")
@rate_limit(limit=5, window=60)
async def activate_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Activate user account."""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    db.commit()
    
    return {"message": f"User {user.username} activated"}


@router.get("/cache/stats")
@rate_limit(limit=10, window=60)
async def get_cache_statistics(
    current_user: User = Depends(require_admin)
):
    """Get cache statistics."""
    
    try:
        from app.core.cache import redis_client
        
        info = redis_client.info()
        
        return {
            "memory_used": info.get("used_memory_human"),
            "connected_clients": info.get("connected_clients"),
            "total_commands_processed": info.get("total_commands_processed"),
            "keyspace_hits": info.get("keyspace_hits"),
            "keyspace_misses": info.get("keyspace_misses"),
            "hit_rate": info.get("keyspace_hits", 0) / max(
                info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1
            )
        }
    except Exception as e:
        return {"error": str(e)}
