"""
Auth controller - registration, login, refresh, profile.

Controllers are thin: they only validate input (via Depends get_db) and
delegate to AuthService. HTTPException from services is unwrapped directly.
"""
from jose import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.base import get_db
from app.repositories.users_repository import UserRepository
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserOut
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


def _auth(db: Session) -> AuthService:
    return AuthService(UserRepository(db))


@router.post("/register", response_model=TokenResponse, summary="Register a new account")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    return _auth(db).register(data)


@router.post("/login", response_model=TokenResponse, summary="Login (username or email)")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return _auth(db).login(data)


@router.post("/refresh", response_model=TokenResponse, summary="Refresh an access token")
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    try:
        return _auth(db).refresh(data.refresh_token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")


@router.get("/me", response_model=UserOut, summary="Current authenticated user")
def me(user=Depends(get_current_user)):
    return UserOut.model_validate(user)