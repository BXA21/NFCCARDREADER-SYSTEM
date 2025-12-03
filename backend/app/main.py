"""
Main FastAPI application entry point.
Configures middleware, routes, and startup/shutdown events.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup: Create database tables
    print("Starting NFC Attendance System...")
    print(f"Application: {settings.APP_NAME}")
    print(f"Company: {settings.COMPANY_NAME}")
    
    # Import all models to ensure they're registered with Base
    from app.models import (
        Employee, User, Card, AttendanceEvent, 
        CorrectionRequest, Shift, EmployeeShift, 
        Device, AuditLog
    )
    
    # Create tables (in production, use Alembic migrations)
    async with engine.begin() as conn:
        if settings.DEBUG:
            await conn.run_sync(Base.metadata.create_all)
            print("Database tables created successfully")
    
    yield
    
    # Shutdown
    print("Shutting down NFC Attendance System...")
    await engine.dispose()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Complete NFC-based attendance and leave management system",
    version="1.0.0",
    lifespan=lifespan,
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "company": settings.COMPANY_NAME,
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint providing basic API information.
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "company": settings.COMPANY_NAME,
        "docs": "/docs",
        "health": "/health"
    }


# Include routers
from app.routers import auth, employees, cards, shifts, attendance, cards_advanced, websocket, manual
from app.middleware.audit import AuditMiddleware

# Add audit middleware (added first so it's processed after CORS)
app.add_middleware(AuditMiddleware)

# Configure CORS (added last so it's processed first for preflight requests)
# For development, allow all origins
print(f"CORS Origins: {settings.allowed_origins_list}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=False,  # Cannot use credentials with wildcard origin
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(employees.router, prefix="/api/v1/employees", tags=["Employees"])
app.include_router(cards.router, prefix="/api/v1", tags=["Cards"])
app.include_router(cards_advanced.router, prefix="/api/v1", tags=["Cards Advanced"])
app.include_router(shifts.router, prefix="/api/v1/shifts", tags=["Shifts"])
app.include_router(attendance.router, prefix="/api/v1", tags=["Attendance"])
app.include_router(manual.router, prefix="/api/v1", tags=["Manual Operations"])

# Include WebSocket router for real-time updates
app.include_router(websocket.router, tags=["WebSocket"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

