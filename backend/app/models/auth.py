from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel


# SQLModel requires to define a Model for each scheme. As we want
# to reference to the auth.user table in the public scheme
# we define it here.


# Note that the real table holds more columns than expressed here,
# but we only need the id column for the reference.
# This table will also be skipped during alembic autogeneration.
class AuthSchemeModel(SQLModel, table=True):
    __tablename__ = "auth.users"
    __table_args__ = {"schema": "auth"}

    id: UUID = Field(default_factory=uuid4, primary_key=True)


class TokenResponse(BaseModel):
    """Token response model"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request model"""

    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request model"""

    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Password reset request model"""

    email: EmailStr


class PasswordUpdateRequest(BaseModel):
    """Password update request model"""

    current_password: str
    new_password: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None
