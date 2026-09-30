"""
AuthService - registration, login, refresh and admin bootstrap.

WHY SEPARATE FROM THE ROUTE
    The route only parses HTTP; this class owns the security rules:
    - duplicate username/email rejection,
    - bcrypt hashing,
    - JWT minting,
    - last_login tracking.
"""
from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.repositories.users_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, UserOut


class AuthService:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    def register(self, data: RegisterRequest) -> dict:
        if self.repo.get_by_username(data.username):
            raise HTTPException(status.HTTP_409_CONFLICT, "Username already taken")
        if self.repo.get_by_email(data.email):
            raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")

        user = self.repo.create(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
        )
        return self._token_pair(user)

    def login(self, data: LoginRequest) -> dict:
        user = self.repo.get_by_identifier(data.username)
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")

        user.last_login = datetime.now(timezone.utc)
        self.repo.save(user)
        return self._token_pair(user)

    def refresh(self, token: str) -> dict:
        from app.core.security import decode_token

        payload = decode_token(token)  # raises JWTError -> 401 handled in route
        user = self.repo.get_by_identifier(payload.get("sub", ""))
        if not user:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")
        return self._token_pair(user)

    @staticmethod
    def _token_pair(user) -> dict:
        subject = user.username
        return {
            "access_token": create_access_token(subject),
            "refresh_token": create_refresh_token(subject),
            "token_type": "bearer",
        }

    @staticmethod
    def to_schema(user) -> UserOut:
        return UserOut.model_validate(user)