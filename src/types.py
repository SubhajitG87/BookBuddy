"""Pydantic models for CSV schema validation and stat structure."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

# ── CSV Record ───────────────────────────────────────────────────────


class GoodreadsRecord(BaseModel):
    """A single book entry from a Goodreads CSV export."""

    title: str = Field(alias="Title")
    author: str = Field(alias="Author")
    isbn: str | None = Field(default=None, alias="ISBN")
    isbn13: str | None = Field(default=None, alias="ISBN13")
    my_rating: int = Field(alias="My Rating", ge=0, le=5)
    number_of_pages: int | None = Field(default=None, alias="Number of Pages", ge=0)
    date_read: datetime | None = Field(default=None, alias="Date Read")
    bookshelves: str | None = Field(default=None, alias="Bookshelves")
    my_review: str | None = Field(default=None, alias="My Review")
    exclusive_shelf: str | None = Field(default=None, alias="Exclusive Shelf")
    read_count: int | None = Field(default=None, alias="Read Count", ge=0)

    @field_validator("date_read", mode="before")
    @classmethod
    def parse_date(cls, v: object) -> datetime | None:
        """Accept string dates in common Goodreads formats."""
        if v is None or v == "":
            return None
        if isinstance(v, datetime):
            return v
        for fmt in ("%Y/%m/%d", "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(str(v).strip(), fmt)
            except ValueError:
                continue
        return None

    @field_validator("my_rating", "number_of_pages", "read_count", mode="before")
    @classmethod
    def coerce_int(cls, v: object) -> int:
        """Coerce numeric-like strings to int, defaulting to 0."""
        if v is None or v == "":
            return 0
        try:
            return int(float(str(v)))
        except (ValueError, TypeError):
            return 0

    model_config = {"populate_by_name": True, "extra": "ignore"}
