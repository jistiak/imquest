from __future__ import annotations

from imquest.providers.pexels import PexelsProvider


class DummyResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def json(self) -> dict:
        return self._payload


def test_pexels_search_parses_results(monkeypatch):
    payload = {
        "photos": [
            {
                "id": 1,
                "url": "https://www.pexels.com/photo/1",
                "width": 100,
                "height": 200,
                "photographer": "Bob",
                "src": {"medium": "https://images.pexels.com/1.jpg"},
            }
        ]
    }

    def fake_get(*args, **kwargs):
        return DummyResponse(payload)

    monkeypatch.setattr("imquest.providers.pexels.get_json", fake_get)

    provider = PexelsProvider(api_key="token")
    results = provider.search("ocean")

    assert len(results) == 1
    assert results[0].provider == "pexels"
    assert results[0].photographer == "Bob"
