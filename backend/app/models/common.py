from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional, Any
from datetime import datetime


T = TypeVar('T')

class ApiResponse(BaseModel):
    code: int = 0
    message: Optional[Any] = None
    data: Optional[Any] = None

class BaseResponse(BaseModel, Generic[T]):
    code: int
    data: Optional[T] = None
    message: str | None = None

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model"""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

class TimestampMixin(BaseModel):
    """Mixin for created_at and updated_at fields"""
    created_at: datetime
    updated_at: datetime

class ErrorResponse(BaseModel):
    """Standard error response model"""
    detail: str
    code: Optional[str] = None

class SuccessResponse(BaseModel):
    """Standard success response model"""
    message: str
    data: Optional[dict] = None
