"""
Authentication endpoints
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from app.api.dependencies import get_db, get_current_active_user
from app.core.config import settings
from app.core.security import create_access_token
from app.repositories.user import user_repository
from app.schemas.auth import Token, UserLogin, UserRegister
from app.schemas.user import User, UserCreate

router = APIRouter()


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """OAuth2 compatible token login, get an access token for future requests"""
    user = await user_repository.authenticate(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user.id), expires_delta=access_token_expires, role=user.role
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login/json", response_model=Token)
async def login_json(
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """JSON login endpoint"""
    user = await user_repository.authenticate_by_email(
        db, email=user_credentials.email, password=user_credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user.id), expires_delta=access_token_expires, role=user.role
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """Register new user"""
    # Check if username already exists
    existing_user = await user_repository.get_by_username(db, username=user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_user = await user_repository.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user with hashed password
    try:
        user_create = UserCreate(
            username=user_in.username,
            email=user_in.email,
            password=user_in.password,
            full_name=user_in.full_name,
            sweet_name=user_in.sweet_name,
            ctstage_name=user_in.ctstage_name
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    
    user = await user_repository.create_with_password(db, obj_in=user_create)
    return user


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return current_user


@router.post("/test-token", response_model=User)
async def test_token(
    current_user: User = Depends(get_current_active_user)
):
    """Test access token"""
    return current_user

@router.post("/logout")
async def logout():
    """JWT logout endpoint - for stateless JWT, client should discard token"""
    return {
        "message": "Successfully logged out", 
        "detail": "For stateless JWT authentication, please discard the token on client side"
    }


@router.get("/verify") 
async def verify_token(
    current_user: User = Depends(get_current_active_user)
):
    """Verify JWT token and return user info"""
    return {
        "valid": True,
        "user": current_user,
        "token_type": "bearer"
    }


@router.get("/status")
async def auth_status(
    current_user: User = Depends(get_current_active_user)  
):
    """Get current authentication status"""
    return {
        "authenticated": True,
        "user_id": str(current_user.id),
        "username": current_user.username,
        "role": current_user.role,
        "is_active": current_user.is_active
    }
