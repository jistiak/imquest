from __future__ import annotations

from imquest.providers.google_cse import GoogleCSEProvider


class DummyResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def json(self) -> dict:
        return self._payload


def test_google_cse_search_parses_results(monkeypatch):
    payload = {
        "items": [
            {
                "cacheId": "abc",
                "link": "https://img.example.com/pic.jpg",
                "image": {
                    "contextLink": "https://example.com/page",
                    "thumbnailLink": "https://img.example.com/thumb.jpg",
                    "width": "1200",
                    "height": "800",
                },
            }
        ]
    }

    def fake_get(*args, **kwargs):
        return DummyResponse(payload)

    monkeypatch.setattr("imquest.providers.google_cse.get_json", fake_get)

    provider = GoogleCSEProvider(api_key="key", cse_id="cx")
    results = provider.search("kittens")

    assert len(results) == 1
    assert results[0].provider == "google_cse"
    assert results[0].width == 1200
