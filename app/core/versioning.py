"""API versioning utilities."""

from typing import Dict, Any, Optional
from fastapi import Request, HTTPException, status
from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse
from datetime import datetime

class APIVersion:
    """API version management."""
    
    def __init__(self, version: str, is_deprecated: bool = False, deprecation_date: Optional[str] = None):
        self.version = version
        self.is_deprecated = is_deprecated
        self.deprecation_date = deprecation_date
    
    def to_header(self) -> str:
        """Convert to API-Version header value."""
        header = f"version={self.version}"
        if self.is_deprecated:
            header += f", deprecated=true"
            if self.deprecation_date:
                header += f", sunset={self.deprecation_date}"
        return header


class VersionedAPIRoute(APIRoute):
    """Custom route that handles API versioning."""
    
    def __init__(self, *args, **kwargs):
        self.api_version = kwargs.pop('api_version', 'v1')
        super().__init__(*args, **kwargs)
    
    def get_route_handler(self):
        """Get route handler with version checking."""
        original_route_handler = super().get_route_handler()
        
        async def versioned_route_handler(request: Request) -> Any:
            # Check API version in header
            api_version = request.headers.get('API-Version', 'v1')
            
            # Validate version
            if not self._is_valid_version(api_version):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "error": {
                            "type": "InvalidVersion",
                            "message": f"Unsupported API version: {api_version}",
                            "supported_versions": ["v1", "v2"],
                            "status_code": 400
                        }
                    }
                )
            
            # Check if version is deprecated
            if self._is_deprecated_version(api_version):
                response = await original_route_handler(request)
                if hasattr(response, 'headers'):
                    response.headers['Deprecation'] = 'true'
                    response.headers['Sunset'] = '2025-12-31'
                return response
            
            return await original_route_handler(request)
        
        return versioned_route_handler
    
    def _is_valid_version(self, version: str) -> bool:
        """Check if version is valid."""
        return version in ['v1', 'v2']
    
    def _is_deprecated_version(self, version: str) -> bool:
        """Check if version is deprecated."""
        # v1 is deprecated, v2 is current
        return version == 'v1'


class VersionManager:
    """Manages API versions and deprecation."""
    
    def __init__(self):
        self.versions = {
            'v1': APIVersion('v1', is_deprecated=True, deprecation_date='2025-12-31'),
            'v2': APIVersion('v2', is_deprecated=False)
        }
        self.current_version = 'v2'
        self.default_version = 'v1'  # For backward compatibility
    
    def get_version_info(self, version: str) -> Optional[APIVersion]:
        """Get version information."""
        return self.versions.get(version)
    
    def get_supported_versions(self) -> list:
        """Get list of supported versions."""
        return list(self.versions.keys())
    
    def get_current_version(self) -> str:
        """Get current API version."""
        return self.current_version
    
    def is_version_supported(self, version: str) -> bool:
        """Check if version is supported."""
        return version in self.versions
    
    def is_version_deprecated(self, version: str) -> bool:
        """Check if version is deprecated."""
        version_info = self.get_version_info(version)
        return version_info.is_deprecated if version_info else False
    
    def get_deprecation_warning(self, version: str) -> Optional[Dict[str, Any]]:
        """Get deprecation warning for version."""
        version_info = self.get_version_info(version)
        if not version_info or not version_info.is_deprecated:
            return None
        
        warning = {
            "warning": "This API version is deprecated",
            "version": version,
            "current_version": self.current_version,
            "deprecation_date": version_info.deprecation_date
        }
        
        return warning


# Global version manager
version_manager = VersionManager()


def require_version(version: str):
    """Decorator to require specific API version."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if hasattr(arg, 'headers'):
                    request = arg
                    break
            
            if request:
                api_version = request.headers.get('API-Version', 'v1')
                if api_version != version:
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={
                            "error": {
                                "type": "VersionMismatch",
                                "message": f"Endpoint requires API version {version}, got {api_version}",
                                "required_version": version,
                                "provided_version": api_version,
                                "status_code": 400
                            }
                        }
                    )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def add_version_headers(response: JSONResponse, version: str) -> JSONResponse:
    """Add version headers to response."""
    version_info = version_manager.get_version_info(version)
    if version_info:
        response.headers['API-Version'] = version_info.to_header()
    
    return response
