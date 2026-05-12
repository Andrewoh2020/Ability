from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel


class Sandbox(SQLModel, table=True):
    __tablename__ = "sandboxes"

    id: str = Field(primary_key=True)
    app_id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    connected_at: datetime = Field(nullable=True)
