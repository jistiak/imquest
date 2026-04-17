"""Unsplash provider implementation."""

from __future__ import annotations

from imquest.enums import Orientation, Size
from imquest.exceptions import ProviderError
from imquest.http import get_json
from imquest.models import PhotoResult
from imquest.providers.base import BaseProvider


class UnsplashProvider(BaseProvider):
    name = "unsplash"
    base_url = "https://api.unsplash.com/search/photos"

    def __init__(self, access_key: str | None, timeout: float = 10.0) -> None:
        self.access_key = access_key
        self.timeout = timeout

    def is_configured(self) -> bool:
        return bool(self.access_key)

    def search(
        self,
        query: str,
        *,
        orientation: Orientation | None = None,
        size: Size | None = None,
        per_page: int = 15,
    ) -> list[PhotoResult]:
        if not self.is_configured():
            return []

        params: dict[str, str | int] = {"query": query, "per_page": per_page}
        if orientation:
            params["orientation"] = orientation.value
        if size:
            # Unsplash doesn't expose this directly; approximate via query enrichment.
            params["query"] = f"{query} {size.value}"

        response = get_json(
            self.base_url,
            headers={"Authorization": f"Client-ID {self.access_key}"},
            params=params,
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            raise ProviderError(f"Unsplash request failed with status {response.status_code}")

        data = response.json()
        photos = data.get("results", [])
        return [
            PhotoResult(
                id=item.get("id", ""),
                provider=self.name,
                url=item.get("links", {}).get("html") or item.get("urls", {}).get("full") or "",
                width=item.get("width"),
                height=item.get("height"),
                photographer=item.get("user", {}).get("name"),
                thumbnail_url=item.get("urls", {}).get("small"),
            )
            for item in photos
        ]
