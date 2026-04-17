"""Wikimedia Commons provider implementation."""

from __future__ import annotations

from imquest.enums import Orientation, Size
from imquest.exceptions import ProviderError
from imquest.http import get_json
from imquest.models import PhotoResult
from imquest.providers.base import BaseProvider


class WikimediaCommonsProvider(BaseProvider):
    name = "wikimedia"
    endpoint = "https://commons.wikimedia.org/w/api.php"

    def __init__(self, timeout: float = 10.0) -> None:
        self.timeout = timeout

    def is_configured(self) -> bool:
        return True

    def search(
        self,
        query: str,
        *,
        orientation: Orientation | None = None,
        size: Size | None = None,
        per_page: int = 15,
    ) -> list[PhotoResult]:
        gsr_query = f"file:{query}"
        params: dict[str, str | int] = {
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": gsr_query,
            "gsrnamespace": 6,
            "gsrlimit": per_page,
            "prop": "imageinfo",
            "iiprop": "url|size",
            "iiurlwidth": 640,
        }
        return self._request(params)

    def search_by_location(
        self,
        latitude: float,
        longitude: float,
        *,
        per_page: int = 15,
    ) -> list[PhotoResult]:
        params: dict[str, str | int | float] = {
            "action": "query",
            "format": "json",
            "generator": "geosearch",
            "ggsprimary": "all",
            "ggsnamespace": 6,
            "ggscoord": f"{latitude}|{longitude}",
            "ggsradius": 10000,
            "ggslimit": per_page,
            "prop": "imageinfo",
            "iiprop": "url|size",
            "iiurlwidth": 640,
        }
        return self._request(params, location=f"{latitude},{longitude}")

    def _request(
        self,
        params: dict[str, str | int | float],
        *,
        location: str | None = None,
    ) -> list[PhotoResult]:
        response = get_json(self.endpoint, params=params, timeout=self.timeout)
        if response.status_code >= 400:
            raise ProviderError(f"Wikimedia request failed with status {response.status_code}")

        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        results: list[PhotoResult] = []
        for page in pages.values():
            infos = page.get("imageinfo", [])
            if not infos:
                continue
            info = infos[0]
            results.append(
                PhotoResult(
                    id=str(page.get("pageid") or page.get("title", "")),
                    provider=self.name,
                    url=info.get("descriptionurl") or info.get("url") or "",
                    width=info.get("width"),
                    height=info.get("height"),
                    photographer=None,
                    thumbnail_url=info.get("thumburl") or info.get("url"),
                    location=location,
                )
            )
        return results
