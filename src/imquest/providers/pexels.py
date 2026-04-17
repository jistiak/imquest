"""Pexels provider implementation."""

from __future__ import annotations

from imquest.enums import Orientation, Size
from imquest.exceptions import ProviderError
from imquest.http import get_json
from imquest.models import PhotoResult
from imquest.providers.base import BaseProvider


class PexelsProvider(BaseProvider):
    name = "pexels"
    base_url = "https://api.pexels.com/v1/search"

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

        params: dict[str, str | int] = {"query": query, "per_page": per_page}
        if orientation:
            params["orientation"] = orientation.value
        if size:
            params["size"] = size.value

        response = get_json(
            self.base_url,
            headers={"Authorization": self.api_key or ""},
            params=params,
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            raise ProviderError(f"Pexels request failed with status {response.status_code}")

        data = response.json()
        photos = data.get("photos", [])
        return [
            PhotoResult(
                id=str(item.get("id")),
                provider=self.name,
                url=item.get("url") or item.get("src", {}).get("original") or "",
                width=item.get("width"),
                height=item.get("height"),
                photographer=item.get("photographer"),
                thumbnail_url=item.get("src", {}).get("medium"),
            )
            for item in photos
        ]
