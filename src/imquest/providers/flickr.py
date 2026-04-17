"""Flickr provider implementation."""

from __future__ import annotations

from imquest.enums import Orientation, Size
from imquest.exceptions import ProviderError
from imquest.http import get_json
from imquest.models import PhotoResult
from imquest.providers.base import BaseProvider


class FlickrProvider(BaseProvider):
    name = "flickr"
    endpoint = "https://www.flickr.com/services/rest"

    def __init__(self, api_key: str | None, timeout: float = 10.0) -> None:
        self.api_key = api_key
        self.timeout = timeout

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def _base_params(self) -> dict[str, str]:
        return {
            "api_key": self.api_key or "",
            "format": "json",
            "nojsoncallback": "1",
            "extras": "owner_name,url_m,geo,date_taken",
            "content_type": "1",
            "safe_search": "1",
        }

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
            **self._base_params(),
            "method": "flickr.photos.search",
            "text": query,
            "per_page": per_page,
        }
        if orientation:
            params["text"] = f"{query} {orientation.value}"
        if size:
            params["text"] = f"{params['text']} {size.value}"

        return self._request(params)

    def search_by_location(
        self,
        latitude: float,
        longitude: float,
        *,
        per_page: int = 15,
    ) -> list[PhotoResult]:
        if not self.is_configured():
            return []

        params: dict[str, str | float | int] = {
            **self._base_params(),
            "method": "flickr.photos.search",
            "lat": latitude,
            "lon": longitude,
            "radius": 10,
            "per_page": per_page,
        }
        return self._request(params)

    def _request(self, params: dict[str, str | int | float]) -> list[PhotoResult]:
        response = get_json(self.endpoint, params=params, timeout=self.timeout)
        if response.status_code >= 400:
            raise ProviderError(f"Flickr request failed with status {response.status_code}")

        data = response.json()
        if data.get("stat") != "ok":
            raise ProviderError(f"Flickr error: {data.get('message', 'unknown error')}")

        photos = data.get("photos", {}).get("photo", [])
        results: list[PhotoResult] = []
        for item in photos:
            medium_url = item.get("url_m")
            if not medium_url:
                continue
            location = None
            lat = item.get("latitude")
            lon = item.get("longitude")
            if lat and lon and lat != "0" and lon != "0":
                location = f"{lat},{lon}"

            results.append(
                PhotoResult(
                    id=str(item.get("id")),
                    provider=self.name,
                    url=medium_url,
                    photographer=item.get("ownername"),
                    thumbnail_url=medium_url,
                    location=location,
                )
            )
        return results
