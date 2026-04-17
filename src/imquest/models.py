"""Core models returned by imquest."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PhotoResult:
    """Normalized image search result from any provider."""

    id: str
    provider: str
    url: str
    width: int | None = None
    height: int | None = None
    photographer: str | None = None
    thumbnail_url: str | None = None
    location: str | None = None
