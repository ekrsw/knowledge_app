"""
FastAPI application entry point for Knowledge Revision System
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title="KSAP - Knowledge System Approval Platform",
    description="""
    ## Knowledge System Approval Platform API
    
    KSAP provides a comprehensive knowledge revision proposal and approval system with the following capabilities:
    
    ### Core Features
    - **Proposal Management**: Create, edit, submit, and track knowledge revision proposals
    - **Approval Workflow**: Structured approval process with role-based access control
    - **Diff Analysis**: Advanced change detection and impact assessment
    - **Notification System**: Real-time notifications and communication
    - **Analytics & Reporting**: Comprehensive metrics and performance insights
    
    ### User Roles
    - **User**: Can create and manage their own proposals
    - **Approver**: Can review and approve/reject proposals in their domain
    - **Admin**: Full system access including user management and system configuration
    
    ### Authentication
    All endpoints (except public ones) require JWT Bearer token authentication.
    
    ### API Structure
    - **Base URL**: `/api/v1`
    - **Authentication**: JWT Bearer tokens
    - **Response Format**: JSON
    - **Error Handling**: Standardized HTTP status codes with detailed error messages
    
    ### Support
    For technical support or feature requests, please contact the development team.
    """,
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.ENVIRONMENT != "production" else None,
    contact={
        "name": "KSAP Development Team",
        "email": "dev-team@company.com",
    },
    license_info={
        "name": "Proprietary License",
        "url": "https://company.com/license",
    },
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    """Root endpoint - API Welcome"""
    return {
        "message": "Welcome to KSAP - Knowledge System Approval Platform",
        "version": "0.1.0",
        "status": "operational",
        "documentation": "/docs",
        "api_base": "/api/v1",
        "health_check": "/health"
    }

@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2025-01-30T00:00:00Z",
        "version": "0.1.0"
    }