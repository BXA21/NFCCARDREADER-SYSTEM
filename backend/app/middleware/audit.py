"""
Audit logging middleware for tracking system actions.
"""

import uuid
from datetime import datetime
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog
from app.database import AsyncSessionLocal


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log sensitive actions for audit purposes.
    Logs actions like create, update, delete operations.
    """
    
    # Actions that should be audited
    AUDIT_METHODS = ["POST", "PUT", "PATCH", "DELETE"]
    
    # Paths that should NOT be audited (to avoid noise)
    SKIP_PATHS = [
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/v1/auth/login",
        "/api/v1/auth/refresh"
    ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and log if necessary.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response from the handler
        """
        # Skip non-audit methods and paths
        if request.method not in self.AUDIT_METHODS or \
           any(request.url.path.startswith(path) for path in self.SKIP_PATHS):
            return await call_next(request)
        
        # Extract user information if available
        user_id = None
        try:
            # Try to get user from request state (set by auth dependency)
            if hasattr(request.state, "user"):
                user_id = request.state.user.id
        except Exception:
            pass
        
        # Get IP address
        ip_address = request.client.host if request.client else None
        
        # Get user agent
        user_agent = request.headers.get("user-agent", "")
        
        # Process request
        response = await call_next(request)
        
        # Only log successful operations (2xx status codes)
        if 200 <= response.status_code < 300:
            try:
                await self._create_audit_log(
                    actor_user_id=user_id,
                    action_type=self._determine_action_type(request),
                    entity_type=self._determine_entity_type(request),
                    ip_address=ip_address,
                    user_agent=user_agent,
                    request=request
                )
            except Exception as e:
                # Don't fail the request if audit logging fails
                print(f"Audit logging failed: {str(e)}")
        
        return response
    
    def _determine_action_type(self, request: Request) -> str:
        """
        Determine the action type from the request method and path.
        
        Args:
            request: HTTP request
            
        Returns:
            Action type string (e.g., "EMPLOYEE_CREATED")
        """
        method = request.method
        path = request.url.path
        
        # Extract entity from path
        entity = self._determine_entity_type(request)
        
        # Map method to action
        action_map = {
            "POST": "CREATED",
            "PUT": "UPDATED",
            "PATCH": "UPDATED",
            "DELETE": "DELETED"
        }
        
        action = action_map.get(method, "UNKNOWN")
        return f"{entity}_{action}"
    
    def _determine_entity_type(self, request: Request) -> str:
        """
        Determine the entity type from the request path.
        
        Args:
            request: HTTP request
            
        Returns:
            Entity type string (e.g., "Employee", "Card")
        """
        path = request.url.path
        
        # Map path patterns to entity types
        if "/employees" in path:
            return "Employee"
        elif "/cards" in path:
            return "Card"
        elif "/attendance" in path:
            return "AttendanceEvent"
        elif "/corrections" in path:
            return "CorrectionRequest"
        elif "/shifts" in path:
            return "Shift"
        elif "/devices" in path:
            return "Device"
        elif "/users" in path:
            return "User"
        else:
            return "Unknown"
    
    async def _create_audit_log(
        self,
        actor_user_id: Optional[uuid.UUID],
        action_type: str,
        entity_type: str,
        ip_address: Optional[str],
        user_agent: str,
        request: Request
    ):
        """
        Create an audit log entry in the database.
        
        Args:
            actor_user_id: ID of the user performing the action
            action_type: Type of action (e.g., "EMPLOYEE_CREATED")
            entity_type: Type of entity (e.g., "Employee")
            ip_address: IP address of the requester
            user_agent: User agent string
            request: HTTP request
        """
        async with AsyncSessionLocal() as db:
            audit_log = AuditLog(
                actor_user_id=actor_user_id,
                action_type=action_type,
                entity_type=entity_type,
                entity_id=None,  # Will be populated by the service layer if needed
                details={
                    "method": request.method,
                    "path": request.url.path,
                    "query_params": dict(request.query_params)
                },
                ip_address=ip_address,
                user_agent=user_agent[:500] if user_agent else None,  # Truncate if too long
                timestamp=datetime.utcnow()
            )
            
            db.add(audit_log)
            await db.commit()



