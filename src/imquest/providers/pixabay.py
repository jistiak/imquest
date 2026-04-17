"""Pixabay provider implementation."""

from __future__ import annotations

from imquest.enums import Orientation, Size
from imquest.exceptions import ProviderError
from imquest.http import get_json
from imquest.models import PhotoResult
from imquest.providers.base import BaseProvider


class PixabayProvider(BaseProvider):
    name = "pixabay"
    base_url = "https://pixabay.com/api/"

    def __init__(self, api_key: str | None, timeout: float = 10.0) -> None:
        self.api_key = api_key
        self.timeout = timeout

    def is_configured(self) -> bool:
        return bool(self.api_key)

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

        params: dict[str, str | int] = {
            "key": self.api_key or "",
            "q": query,
            "per_page": per_page,
            "image_type": "photo",
            "safesearch": "true",
        }
        if orientation:
            params["orientation"] = orientation.value
        if size:
            min_width = {Size.SMALL: 320, Size.MEDIUM: 800, Size.LARGE: 1400}[size]
            params["min_width"] = min_width

        response = get_json(self.base_url, params=params, timeout=self.timeout)
        if response.status_code >= 400:
            raise ProviderError(f"Pixabay request failed with status {response.status_code}")

        data = response.json()
        return [
            PhotoResult(
                id=str(item.get("id")),
                provider=self.name,
                url=item.get("pageURL") or item.get("largeImageURL") or "",
                width=item.get("imageWidth"),
                height=item.get("imageHeight"),
                photographer=item.get("user"),
                thumbnail_url=item.get("webformatURL") or item.get("previewURL"),
            )
            for item in data.get("hits", [])
        ]
