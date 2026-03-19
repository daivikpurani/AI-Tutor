"""
Security utilities for authentication and authorization.
"""

from typing import Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from app.config import settings


# Security scheme for JWT tokens
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time
    
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode.update({"exp": expire})
    
    if not settings.secret_key:
        raise ValueError("SECRET_KEY not configured")
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    Verify JWT token from Authorization header.
    
    Args:
        credentials: HTTP authorization credentials
    
    Returns:
        Decoded token payload
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    
    try:
        if not settings.secret_key:
            raise ValueError("SECRET_KEY not configured")
        
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Dependency for protected routes
async def get_current_user(token_data: dict = Depends(verify_token)) -> dict:
    """
    Get current authenticated user from token.
    
    Args:
        token_data: Decoded token data
    
    Returns:
        User information
    """
    # TODO: Implement user lookup from database
    return token_data


# Note: Authentication is optional for initial development phase
# Uncomment and implement when security is required
