"""User model for authentication and service connections."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    """User model for authentication and service management."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Service connection flags
    slack_connected = Column(Boolean, default=False)
    telegram_connected = Column(Boolean, default=False)
    google_sheets_connected = Column(Boolean, default=False)
    
    # Service tokens/secrets (encrypted in production)
    slack_token = Column(Text, nullable=True)
    telegram_chat_id = Column(String(100), nullable=True)
    google_credentials = Column(Text, nullable=True)
    
    # Relationships
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def has_permission(self, resource: str, action: str) -> bool:
        """Check if user has specific permission."""
        if self.is_superuser:
            return True
        
        for role in self.roles:
            for permission in role.permissions:
                if permission.resource == resource and permission.action == action:
                    return True
        return False
    
    def has_role(self, role_name: str) -> bool:
        """Check if user has specific role."""
        return any(role.name == role_name for role in self.roles)
