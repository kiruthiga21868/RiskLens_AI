"""
Security utilities: password hashing and JWT handling.

WHY bcrypt (not passlib)
    bcrypt is the modern, actively-maintained password KDF. We hash
    passwords with it and verify in constant-time.

WHY python-jose for JWT
    libs-shaped tokens. We issue short-lived access tokens (30 min)
    and longer refresh tokens (7 days).

WHY TOKEN_TYPE
    Lets us mint both access and refresh tokens from one function and
    embed a claim so the auth middleware knows which is which.
"""
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from app.core.config import get_settings

settings = get_settings()


def hash_password(plain: str) -> str:
    """Hash a plaintext password with a fresh random salt."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches hashed."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    """Create a signed JWT with a subject, token-type and expiry."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(subject: str) -> str:
    return create_token(subject, "access", timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))


def create_refresh_token(subject: str) -> str:
    return create_token(subject, "refresh", timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS))


def decode_token(token: str) -> dict:
    """Decode and validate a token. Raises JWTError on failure."""
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])