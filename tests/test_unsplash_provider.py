from __future__ import annotations

from imquest.providers.unsplash import UnsplashProvider


class DummyResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def json(self) -> dict:
        return self._payload


def test_unsplash_search_parses_results(monkeypatch):
    payload = {
        "results": [
            {
                "id": "u1",
                "width": 500,
                "height": 300,
                "links": {"html": "https://unsplash.com/photos/u1"},
                "urls": {"small": "https://images.unsplash.com/u1-small.jpg"},
                "user": {"name": "Chris"},
            }
        ]
    }

    def fake_get(*args, **kwargs):
        return DummyResponse(payload)

    monkeypatch.setattr("imquest.providers.unsplash.get_json", fake_get)

    provider = UnsplashProvider(access_key="token")
    results = provider.search("desert")

    assert len(results) == 1
    assert results[0].id == "u1"
    assert results[0].provider == "unsplash"
