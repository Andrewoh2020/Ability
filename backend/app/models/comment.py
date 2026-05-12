from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlmodel import Field, SQLModel

from app.models.user import UserLite


class CommentLite(BaseModel):
    id: UUID
    parent_id: Optional[UUID] = None
    content: str
    replies_count: int
    creator: UserLite
    created_at: datetime
    likes_count: int
    is_like: Optional[bool] = None

class ReplyLite(BaseModel):
    id: UUID
    parent_id: UUID
    content: str
    creator: UserLite
    created_at: datetime
    likes_count: int
    is_like: Optional[bool] = None

class Comment(SQLModel, table=True):
    __tablename__ = "comments"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    parent_id: Optional[UUID] = Field(default=None, index=True)
    content: str = Field(nullable=False)
    likes_count: int = Field(default=0)
    replies_count: int = Field(default=0)
    app_id: UUID = Field(foreign_key="apps.id", index=True)
    user_id: UUID = Field(foreign_key="profiles.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    deleted_at: Optional[datetime] = Field(default=None)

class CommentLikes(SQLModel, table=True):
    __tablename__ = "comment_likes"

    user_id: UUID = Field(foreign_key="profiles.id", primary_key=True)
    comment_id: UUID = Field(foreign_key="comments.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
