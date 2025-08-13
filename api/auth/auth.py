"""
Authentication and authorization for StudyMate API
JWT-based authentication with refresh tokens
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from uuid import UUID

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..config import settings
from ..database import get_async_db
from ..models.database import User, UserSession
from ..schemas.schemas import TokenData

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Security
security = HTTPBearer()

class AuthenticationError(Exception):
    """Custom authentication error"""
    pass

class AuthorizationError(Exception):
    """Custom authorization error"""
    pass

class AuthManager:
    """Authentication and authorization manager"""
    
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        self.refresh_token_expire_days = settings.refresh_token_expire_days
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create a JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)
        
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> TokenData:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get("type") != token_type:
                raise JWTError("Invalid token type")
            
            username: str = payload.get("sub")
            user_id: str = payload.get("user_id")
            
            if username is None or user_id is None:
                raise JWTError("Invalid token payload")
            
            return TokenData(username=username, user_id=UUID(user_id))
            
        except JWTError as e:
            logger.warning(f"Token verification failed: {e}")
            raise AuthenticationError("Invalid token")
    
    async def authenticate_user(self, db: AsyncSession, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password"""
        try:
            # Get user by username or email
            stmt = select(User).where(
                (User.username == username) | (User.email == username)
            ).where(User.is_active == True)
            
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            if not self.verify_password(password, user.hashed_password):
                return None
            
            return user
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    async def get_user_by_token(self, db: AsyncSession, token: str) -> Optional[User]:
        """Get user by JWT token"""
        try:
            token_data = self.verify_token(token)
            
            stmt = select(User).where(
                User.id == token_data.user_id,
                User.is_active == True
            )
            
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            return user
            
        except AuthenticationError:
            return None
        except Exception as e:
            logger.error(f"Token user lookup error: {e}")
            return None
    
    async def create_user_session(
        self, 
        db: AsyncSession, 
        user: User, 
        session_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserSession:
        """Create a new user session"""
        expires_at = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)
        
        session = UserSession(
            user_id=user.id,
            session_token=session_token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(session)
        await db.commit()
        await db.refresh(session)
        
        return session
    
    async def invalidate_user_session(self, db: AsyncSession, session_token: str) -> bool:
        """Invalidate a user session"""
        try:
            stmt = select(UserSession).where(
                UserSession.session_token == session_token,
                UserSession.is_active == True
            )
            
            result = await db.execute(stmt)
            session = result.scalar_one_or_none()
            
            if session:
                session.is_active = False
                await db.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Session invalidation error: {e}")
            return False
    
    async def cleanup_expired_sessions(self, db: AsyncSession) -> int:
        """Clean up expired sessions"""
        try:
            from sqlalchemy import update
            
            stmt = update(UserSession).where(
                UserSession.expires_at < datetime.now(timezone.utc)
            ).values(is_active=False)
            
            result = await db.execute(stmt)
            await db.commit()
            
            return result.rowcount
            
        except Exception as e:
            logger.error(f"Session cleanup error: {e}")
            return 0

# Global auth manager
auth_manager = AuthManager()

# Dependencies
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_db)
) -> User:
    """Dependency to get the current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        user = await auth_manager.get_user_by_token(db, token)
        
        if user is None:
            raise credentials_exception
        
        return user
        
    except Exception as e:
        logger.warning(f"Authentication failed: {e}")
        raise credentials_exception

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency to get the current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Dependency to get the current superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# Optional authentication (for public endpoints that can benefit from user context)
async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_async_db)
) -> Optional[User]:
    """Dependency to optionally get the current user"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user = await auth_manager.get_user_by_token(db, token)
        return user if user and user.is_active else None
    except Exception:
        return None
