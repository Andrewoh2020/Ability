from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Column, String
from sqlalchemy.dialects.postgresql import JSONB, ARRAY


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)


class UserLite(BaseModel):
    id: UUID
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class User(UserBase, table=True):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    id: UUID = Field(
        default_factory=uuid4, primary_key=True, foreign_key="auth.users.id"
    )
    raw_user_meta_data: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB)
    )
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class UserProfile(BaseModel):
    id: UUID
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    birthday: Optional[date] = None
    country: Optional[str] = None
    city: Optional[str] = None
    interests: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

class UserProfileUpdate(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=50)
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=150)
    birthday: Optional[date] = None
    country: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    interests: Optional[List[str]] = None

class Profile(SQLModel, table=True):
    __tablename__ = "profiles"

    id: UUID = Field(primary_key=True)
    full_name: str = Field(nullable=True)
    avatar_url: str = Field(nullable=True)
    bio: Optional[str] = Field(default=None, nullable=True)
    birthday: Optional[date] = Field(default=None, nullable=True)
    country: Optional[str] = Field(default=None, nullable=True)
    city: Optional[str] = Field(default=None, nullable=True)
    interests: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(ARRAY(String))
    )
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=True)

class UserFollow(SQLModel, table=True):
    __tablename__ = "user_follows"

    follower_id: UUID = Field(foreign_key="profiles.id", primary_key=True)
    following_id: UUID = Field(foreign_key="profiles.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)

class UserSignUp(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

