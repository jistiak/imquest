"""Base provider contract."""

from __future__ import annotations

from abc import ABC, abstractmethod

from imquest.enums import Orientation, Size
from imquest.models import PhotoResult


class BaseProvider(ABC):
    """Abstract photo provider."""

    name: str

    @abstractmethod
    def is_configured(self) -> bool:
        """Return true if provider can execute API requests."""

    @abstractmethod
    def search(
        self,
        query: str,
        *,
        orientation: Orientation | None = None,
        size: Size | None = None,
        per_page: int = 15,
    ) -> list[PhotoResult]:
        """Perform a keyword-based search."""

    def search_by_location(
        self,
        latitude: float,
        longitude: float,
        *,
        per_page: int = 15,
    ) -> list[PhotoResult]:
        """Perform a location-based search when supported."""
        return []
