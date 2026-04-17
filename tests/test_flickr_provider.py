from __future__ import annotations

from imquest.providers.flickr import FlickrProvider


class DummyResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def json(self) -> dict:
        return self._payload


def test_flickr_search_parses_results(monkeypatch):
    payload = {
        "stat": "ok",
        "photos": {
            "photo": [
                {
                    "id": "123",
                    "ownername": "Alice",
                    "url_m": "https://img.example.com/123.jpg",
                    "latitude": "37.1",
                    "longitude": "-122.1",
                }
            ]
        },
    }

    def fake_get(*args, **kwargs):
        return DummyResponse(payload)

    monkeypatch.setattr("imquest.providers.flickr.get_json", fake_get)

    provider = FlickrProvider(api_key="x")
    results = provider.search("sunset")

    assert len(results) == 1
    assert results[0].id == "123"
    assert results[0].provider == "flickr"
    assert results[0].location == "37.1,-122.1"
