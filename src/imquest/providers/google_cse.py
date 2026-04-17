"""Google Programmable Search (image) provider implementation."""

from __future__ import annotations

from imquest.enums import Orientation, Size
from imquest.exceptions import ProviderError
from imquest.http import get_json
from imquest.models import PhotoResult
from imquest.providers.base import BaseProvider


class GoogleCSEProvider(BaseProvider):
    name = "google_cse"
    endpoint = "https://customsearch.googleapis.com/customsearch/v1"

    def __init__(self, api_key: str | None, cse_id: str | None, timeout: float = 10.0) -> None:
        self.api_key = api_key
        self.cse_id = cse_id
        self.timeout = timeout

    def is_configured(self) -> bool:
        return bool(self.api_key and self.cse_id)

    def search(
        self,
        query: str,
        *,
        orientation: Orientation | None = None,
        size: Size | None = None,
        per_page: int = 10,
    ) -> list[PhotoResult]:
        if not self.is_configured():
            return []

        num = max(1, min(per_page, 10))
        params: dict[str, str | int] = {
            "key": self.api_key or "",
            "cx": self.cse_id or "",
            "q": query,
            "searchType": "image",
            "safe": "active",
            "num": num,
        }
        if orientation:
            img_type = {
                Orientation.LANDSCAPE: "wide",
                Orientation.PORTRAIT: "tall",
                Orientation.SQUARE: "square",
            }
            params["imgType"] = img_type[orientation]
        if size:
            img_size = {Size.SMALL: "medium", Size.MEDIUM: "xlarge", Size.LARGE: "xxlarge"}
            params["imgSize"] = img_size[size]

        response = get_json(self.endpoint, params=params, timeout=self.timeout)
        if response.status_code >= 400:
            raise ProviderError(f"Google CSE request failed with status {response.status_code}")

        data = response.json()
        return [
            PhotoResult(
                id=item.get("cacheId") or item.get("link", ""),
                provider=self.name,
                url=item.get("image", {}).get("contextLink") or item.get("link") or "",
                width=_int_or_none(item.get("image", {}).get("width")),
                height=_int_or_none(item.get("image", {}).get("height")),
                photographer=None,
                thumbnail_url=item.get("image", {}).get("thumbnailLink"),
            )
            for item in data.get("items", [])
        ]


def _int_or_none(value: str | int | None) -> int | None:
    if value is None:
        return None
    return int(value)
