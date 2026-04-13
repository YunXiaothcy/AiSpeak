"""
Authentication service for user registration and login.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.exceptions import AuthenticationError, ValidationError
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, TokenResponse
from app.repositories.user_repo import UserRepository
from app.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repo = user_repository
    
    async def register_user(
        self,
        user_data: UserCreate,
        db: AsyncSession
    ) -> User:
        """
        Register a new user account.
        
        Validates email uniqueness, hashes password, and persists to database.
        """
        logger.info(f"Registering new user: {user_data.email}")
        
        # Check if email already exists
        existing = await self.user_repo.get_by_email(user_data.email)
        if existing:
            raise ValidationError(
                message="Email already registered",
                field_errors={"email": "This email is already in use"}
            )
        
        # Hash password and create user
        hashed_pw = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            hashed_password=hashed_pw,
            full_name=user_data.full_name,
        )
        
        created_user = await self.user_repo.create(new_user)
        logger.info(f"User registered successfully: {created_user.id}")
        return created_user
    
    async def authenticate_user(
        self,
        credentials: UserLogin,
        db: AsyncSession
    ) -> TokenResponse:
        """
        Authenticate user and issue JWT token.
        """
        logger.info(f"Authentication attempt: {credentials.email}")
        
        # Verify credentials
        user = await self.user_repo.get_by_email(credentials.email)
        
        if not user or not verify_password(credentials.password, user.hashed_password):
            logger.warning(f"Failed login attempt: {credentials.email}")
            raise AuthenticationError("Invalid email or password")
        
        if not user.is_active:
            raise AuthenticationError("Account is disabled")
        
        # Generate JWT token
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id}
        )
        
        logger.info(f"User authenticated: {user.id}")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    
    async def get_current_user(self, user_id: int) -> User:
        """Get current user by ID."""
        return await self.user_repo.get_or_404(user_id, "User")
