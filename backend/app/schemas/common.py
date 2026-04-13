"""
Common response models and utilities.
"""

from typing import Any, Generic, TypeVar, Optional, List
from pydantic import BaseModel

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """Standard API response wrapper."""
    success: bool = True
    message: str = "Operation successful"
    data: Optional[T] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model."""
    items: List[T]
    total: int
    page: int
    page_size: int
    has_more: bool


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: str
    status_code: int
    details: dict = {}
