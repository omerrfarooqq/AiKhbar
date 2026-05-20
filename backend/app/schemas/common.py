"""Shared / generic schemas."""
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Generic paginated response envelope."""

    items: list[T]
    total: int
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)

    @property
    def pages(self) -> int:
        return max(1, -(-self.total // self.page_size))


class MessageResponse(BaseModel):
    message: str


class JobResponse(BaseModel):
    """Returned when a background job is accepted."""

    job_id: str
    status: str
    message: str
