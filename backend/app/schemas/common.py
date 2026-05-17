"""
AI CFO — Common Schemas

Shared Pydantic models used across multiple endpoints.
These define the standard error contract and pagination pattern.
"""

import uuid
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Single field-level error."""
    field: str | None = None
    message: str


class ErrorResponse(BaseModel):
    """Standard error response contract for all endpoints."""
    code: str
    message: str
    details: list[ErrorDetail] = []


class ErrorEnvelope(BaseModel):
    """Top-level error envelope."""
    error: ErrorResponse


class PaginationParams(BaseModel):
    """Pagination query parameters."""
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=50, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response envelope."""
    items: list[T]
    total: int
    page: int
    per_page: int
    total_pages: int

    @classmethod
    def create(
        cls, items: list[T], total: int, page: int, per_page: int
    ) -> "PaginatedResponse[T]":
        return cls(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=(total + per_page - 1) // per_page if per_page > 0 else 0,
        )
