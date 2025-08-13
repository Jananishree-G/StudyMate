"""
Authentication API router for StudyMate
JWT-based authentication endpoints
"""

import logging
from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_db
from ..auth.auth import auth_manager, get_current_active_user
from ..models.database import User
from ..schemas.schemas import (
    UserLogin,
    UserCreate,
    UserResponse,
    Token,
    ErrorResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Register a new user"""
    try:
        from sqlalchemy import select
        
        # Check if username already exists
        stmt = select(User).where(User.username == user_data.username)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        stmt = select(User).where(User.email == user_data.email)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = auth_manager.get_password_hash(user_data.password)
        
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        logger.info(f"New user registered: {new_user.username}")
        
        return UserResponse.from_orm(new_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User registration failed: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_async_db)
):
    """Authenticate user and return JWT tokens"""
    try:
        # Authenticate user
        user = await auth_manager.authenticate_user(
            db, 
            user_credentials.username, 
            user_credentials.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create tokens
        access_token_expires = timedelta(minutes=auth_manager.access_token_expire_minutes)
        access_token = auth_manager.create_access_token(
            data={"sub": user.username, "user_id": str(user.id)},
            expires_delta=access_token_expires
        )
        
        refresh_token = auth_manager.create_refresh_token(
            data={"sub": user.username, "user_id": str(user.id)}
        )
        
        # Create user session
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        await auth_manager.create_user_session(
            db, user, refresh_token, client_ip, user_agent
        )
        
        logger.info(f"User logged in: {user.username}")
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=auth_manager.access_token_expire_minutes * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    request: Request,
    db: AsyncSession = Depends(get_async_db)
):
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token
        token_data = auth_manager.verify_token(refresh_token, token_type="refresh")
        
        # Get user
        from sqlalchemy import select
        stmt = select(User).where(
            User.id == token_data.user_id,
            User.is_active == True
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Verify session exists and is active
        from ..models.database import UserSession
        stmt = select(UserSession).where(
            UserSession.session_token == refresh_token,
            UserSession.user_id == user.id,
            UserSession.is_active == True
        )
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=auth_manager.access_token_expire_minutes)
        access_token = auth_manager.create_access_token(
            data={"sub": user.username, "user_id": str(user.id)},
            expires_delta=access_token_expires
        )
        
        # Update session last activity
        from datetime import datetime, timezone
        session.last_activity = datetime.now(timezone.utc)
        await db.commit()
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=auth_manager.access_token_expire_minutes * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )

@router.post("/logout")
async def logout(
    refresh_token: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Logout user and invalidate session"""
    try:
        # Invalidate session
        success = await auth_manager.invalidate_user_session(db, refresh_token)
        
        if success:
            logger.info(f"User logged out: {current_user.username}")
            return {"message": "Successfully logged out"}
        else:
            return {"message": "Session already invalid"}
        
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return UserResponse.from_orm(current_user)

@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Change user password"""
    try:
        # Verify current password
        if not auth_manager.verify_password(current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password"
            )
        
        # Validate new password
        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 8 characters long"
            )
        
        # Update password
        current_user.hashed_password = auth_manager.get_password_hash(new_password)
        await db.commit()
        
        logger.info(f"Password changed for user: {current_user.username}")
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change failed: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )

@router.get("/sessions")
async def get_user_sessions(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get user's active sessions"""
    try:
        from sqlalchemy import select
        from ..models.database import UserSession
        
        stmt = select(UserSession).where(
            UserSession.user_id == current_user.id,
            UserSession.is_active == True
        ).order_by(UserSession.last_activity.desc())
        
        result = await db.execute(stmt)
        sessions = result.scalars().all()
        
        session_data = []
        for session in sessions:
            session_data.append({
                "id": str(session.id),
                "created_at": session.created_at,
                "last_activity": session.last_activity,
                "ip_address": session.ip_address,
                "user_agent": session.user_agent,
                "expires_at": session.expires_at
            })
        
        return {
            "sessions": session_data,
            "total": len(session_data)
        }
        
    except Exception as e:
        logger.error(f"Failed to get user sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sessions"
        )

@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Revoke a specific user session"""
    try:
        from sqlalchemy import select
        from ..models.database import UserSession
        from uuid import UUID
        
        stmt = select(UserSession).where(
            UserSession.id == UUID(session_id),
            UserSession.user_id == current_user.id,
            UserSession.is_active == True
        )
        
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        session.is_active = False
        await db.commit()
        
        return {"message": "Session revoked successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to revoke session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke session"
        )
