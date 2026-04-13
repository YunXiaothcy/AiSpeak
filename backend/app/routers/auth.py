"""
Authentication API routes.
"""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
)
from app.services.auth.auth_service import AuthService
from app.repositories.user_repo import UserRepository

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user account."""
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    
    try:
        user = await auth_service.register_user(user_data, db)
        return user
    except Exception as e:
        if "already registered" in str(e):
            raise HTTPException(status_code=400, detail=str(e))
        raise


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate and get JWT token."""
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    
    try:
        token = await auth_service.authenticate_user(credentials, db)
        return token
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_me(current_user = Depends(lambda: None)):
    """Get current user info (placeholder)."""
    # Would use actual dependency injection
    raise HTTPException(status_code=501, detail="Not implemented yet")
