"""Openverse provider implementation."""

from __future__ import annotations

from imquest.enums import Orientation, Size
from imquest.exceptions import ProviderError
from imquest.http import get_json
from imquest.models import PhotoResult
from imquest.providers.base import BaseProvider


class OpenverseProvider(BaseProvider):
    name = "openverse"
    base_url = "https://api.openverse.org/v1/images/"

    def __init__(self, timeout: float = 10.0) -> None:
        self.timeout = timeout

    def is_configured(self) -> bool:
        # Public endpoint; no API key required for basic access.
        return True

    def search(
        self,
        query: str,
        *,
        orientation: Orientation | None = None,
        size: Size | None = None,
        per_page: int = 15,
    ) -> list[PhotoResult]:
        params: dict[str, str | int] = {
            "q": query,
            "page_size": per_page,
        }
        if orientation:
            aspect_map = {
                Orientation.LANDSCAPE: "wide",
                Orientation.PORTRAIT: "tall",
                Orientation.SQUARE: "square",
            }
            params["aspect_ratio"] = aspect_map[orientation]

        response = get_json(self.base_url, params=params, timeout=self.timeout)
        if response.status_code >= 400:
            raise ProviderError(f"Openverse request failed with status {response.status_code}")

        data = response.json()
        results = data.get("results", [])
        return [
            PhotoResult(
                id=item.get("id", ""),
                provider=self.name,
                url=item.get("foreign_landing_url") or item.get("url") or "",
                width=item.get("width"),
                height=item.get("height"),
                photographer=item.get("creator"),
                thumbnail_url=item.get("thumbnail") or item.get("url"),
            )
            for item in results
        ]
