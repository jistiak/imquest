from __future__ import annotations

import pytest

from imquest.client import ImQuestClient
from imquest.enums import Orientation, Size
from imquest.exceptions import ConfigurationError
from imquest.models import PhotoResult
from imquest.providers.base import BaseProvider


class FakeProvider(BaseProvider):
    def __init__(self, name: str, configured: bool = True) -> None:
        self.name = name
        self._configured = configured

    def is_configured(self) -> bool:
        return self._configured

    def search(self, query: str, *, orientation=None, size=None, per_page: int = 15):
        return [
            PhotoResult(
                id=f"{self.name}-1",
                provider=self.name,
                url=f"https://example.com/{self.name}/{query}",
            )
        ]

    def search_by_location(self, latitude: float, longitude: float, *, per_page: int = 15):
        return [
            PhotoResult(
                id=f"{self.name}-loc",
                provider=self.name,
                url=f"https://example.com/{self.name}/{latitude},{longitude}",
                location=f"{latitude},{longitude}",
            )
        ]


def test_aggregate_keyword_search_uses_all_configured_providers():
    client = ImQuestClient(providers=[FakeProvider("pexels"), FakeProvider("flickr")])
    response = client.search("forest", orientation=Orientation.LANDSCAPE, size=Size.MEDIUM)

    assert response.total_results == 2
    assert {item.provider for item in response.results} == {"pexels", "flickr"}


def test_location_search_uses_selected_provider():
    client = ImQuestClient(providers=[FakeProvider("flickr")])
    response = client.search_by_location(10.0, 20.0)

    assert response.total_results == 1
    assert response.results[0].location == "10.0,20.0"


def test_raises_when_no_provider_credentials_are_configured():
    client = ImQuestClient(providers=[FakeProvider("pexels", configured=False)])
    with pytest.raises(ConfigurationError):
        client.search("dog")


def test_raises_on_empty_query():
    client = ImQuestClient(providers=[FakeProvider("pexels")])
    with pytest.raises(ValueError):
        client.search("   ")
