from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from enum import Enum
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from app.models.user import UserLite


class AppStage(str, Enum):
    DEFAULT = "default"
    PLANNING = "planning"
    BUILDING = "building"
    BUILT = "built"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"


class AppCategory(str, Enum):
    PRODUCTIVITY = "productivity"
    UTILITY = "utility"
    FINANCE = "finance"
    HEALTH_WELLNESS = "health_wellness"
    EDUCATION = "education"
    AI_APPS = "ai_apps"
    PHOTOGRAPHY = "photography"
    FRIENDS = "friends"
    SOCIAL = "social"
    DATING = "dating"
    ENTERTAINMENT = "entertainment"
    SPORTS = "sports"
    GAMING = "gaming"
    TRAVEL = "travel"
    STARTUP_B2B = "startup_b2b"
    PROTOTYPE = "prototype"


class AppLite(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    icon: Optional[str] = None
    cover: Optional[str] = None
    creator: UserLite
    created_at: Optional[datetime] = None


class AppUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=20)
    description: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = None
    icon: Optional[str] = None


class AppBase(SQLModel):
    name: str = Field(index=True, min_length=1, max_length=20)
    description: str = Field(min_length=1, max_length=255)
    category: Optional[str] = None
    icon: Optional[str] = None
    cover: Optional[str] = None


class App(AppBase, table=True):
    __tablename__ = "apps"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    likes_count: int = Field(default=0, nullable=False)
    bookmarks_count: int = Field(default=0, nullable=False)
    page_view: int = Field(default=0, nullable=False)
    user_id: UUID = Field(foreign_key="profiles.id", index=True)
    is_featured: bool = Field(default=False, nullable=False, index=True)

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(nullable=True)


class AppLike(SQLModel, table=True):
    __tablename__ = "app_likes"

    user_id: UUID = Field(foreign_key="profiles.id", primary_key=True)
    app_id: UUID = Field(foreign_key="apps.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)


class AppCollection(SQLModel, table=True):
    __tablename__ = "app_collections"

    user_id: UUID = Field(foreign_key="profiles.id", primary_key=True)
    app_id: UUID = Field(foreign_key="apps.id", primary_key=True)
    type: str = Field(default="owned")
    last_accessed_at: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)
