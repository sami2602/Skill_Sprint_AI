"""
SkillSprint AI — Authentication & Token Security Services
Handles password hashing (PBKDF2-HMAC-SHA256), JWT token generation, and FastAPI security dependencies.
"""

import os
import hmac
import hashlib
import base64
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.database import get_db
from backend.models.models import User
from security.rbac import RBACManager, RBACPermissionError

# OAuth2 Password Bearer scheme for Swagger UI & Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    """Hashes a password using PBKDF2-HMAC-SHA256 with a random salt."""
    salt = secrets.token_bytes(16)
    iterations = 100000
    derived_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
    salt_hex = salt.hex()
    hash_hex = derived_key.hex()
    return f"$pbkdf2-sha256${iterations}${salt_hex}${hash_hex}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against a stored PBKDF2 hash."""
    if not hashed_password or not hashed_password.startswith("$pbkdf2-sha256$"):
        return False
    try:
        parts = hashed_password.split("$")
        if len(parts) != 5:
            return False
        _, _, iterations_str, salt_hex, expected_hash_hex = parts
        iterations = int(iterations_str)
        salt = bytes.fromhex(salt_hex)
        derived_key = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, iterations)
        return hmac.compare_digest(derived_key.hex(), expected_hash_hex)
    except Exception:
        return False


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')


def _base64url_decode(data_str: str) -> bytes:
    padding = '=' * (4 - (len(data_str) % 4))
    return base64.urlsafe_b64encode(base64.urlsafe_b64decode(data_str + padding))  # safe decode


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a signed JWT access token using HMAC-SHA256."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"iat": int(now.timestamp()), "exp": int(expire.timestamp())})
    
    header = {"alg": "HS256", "typ": "JWT"}
    header_json = json.dumps(header, separators=(',', ':')).encode('utf-8')
    payload_json = json.dumps(to_encode, separators=(',', ':')).encode('utf-8')
    
    header_b64 = _base64url_encode(header_json)
    payload_b64 = _base64url_encode(payload_json)
    
    signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
    signature = hmac.new(settings.SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
    signature_b64 = _base64url_encode(signature)
    
    return f"{header_b64}.{payload_b64}.{signature_b64}"


def decode_access_token(token: str) -> dict:
    """Decodes and verifies a JWT token. Raises HTTPException on invalid/expired token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    parts = token.split(".")
    if len(parts) != 3:
        raise credentials_exception
    
    header_b64, payload_b64, signature_b64 = parts
    signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
    
    expected_sig = hmac.new(settings.SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
    expected_sig_b64 = _base64url_encode(expected_sig)
    
    if not hmac.compare_digest(signature_b64, expected_sig_b64):
        raise credentials_exception
    
    try:
        # Decode payload
        padding = '=' * ((4 - len(payload_b64) % 4) % 4)
        payload_bytes = base64.urlsafe_b64decode(payload_b64 + padding)
        payload = json.loads(payload_bytes.decode('utf-8'))
        
        # Check expiration
        exp = payload.get("exp")
        if exp and int(datetime.now(timezone.utc).timestamp()) > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise credentials_exception


def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """FastAPI dependency to retrieve currently authenticated user from Bearer token."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(token)
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensures the authenticated user is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user account.")
    return current_user


def require_role(allowed_roles: List[str]):
    """FastAPI dependency checking that current user role is among allowed roles."""
    def dependency(current_user: User = Depends(get_current_active_user)) -> User:
        user_role = (current_user.role or "").upper()
        allowed_upper = [r.upper() for r in allowed_roles]
        if user_role not in allowed_upper:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Role '{current_user.role}' is not authorized for this resource. Required: {allowed_roles}"
            )
        return current_user
    return dependency


def require_permission(required_permission: str):
    """FastAPI dependency checking RBAC permission."""
    def dependency(current_user: User = Depends(get_current_active_user)) -> User:
        try:
            RBACManager.verify_permission(current_user.role, required_permission)
        except RBACPermissionError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e.detail if hasattr(e, 'detail') else e)
            )
        return current_user
    return dependency
