"""
User repository - the only place that talks to the users table.

WHY A REPOSITORY
    Services depend on this abstraction, not on SQLAlchemy directly.
    This keeps persistence logic in one file and makes services
    trivially unit-testable with a fake repository.
"""
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_identifier(self, identifier: str) -> User | None:
        """Login accepts username OR email."""
        return (self.db.query(User)
                .filter((User.username == identifier) | (User.email == identifier))
                .first())

    def create(self, username: str, email: str, hashed_password: str,
               full_name: str | None = None, role: str = "user") -> User:
        user = User(username=username, email=email, hashed_password=hashed_password,
                    full_name=full_name, role=role)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.db.query(User).order_by(User.created_at.desc()).offset(skip).limit(limit).all()

    def count(self) -> int:
        return self.db.query(User).count()

    def save(self, user: User) -> None:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)