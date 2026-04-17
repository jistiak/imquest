from __future__ import annotations

from imquest.providers.pixabay import PixabayProvider


class DummyResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def json(self) -> dict:
        return self._payload


def test_pixabay_search_parses_results(monkeypatch):
    payload = {
        "hits": [
            {
                "id": 22,
                "pageURL": "https://pixabay.com/photos/22",
                "imageWidth": 1280,
                "imageHeight": 720,
                "user": "Mira",
                "webformatURL": "https://pixabay.com/photo-22_640.jpg",
            }
        ]
    }

    def fake_get(*args, **kwargs):
        return DummyResponse(payload)

    monkeypatch.setattr("imquest.providers.pixabay.get_json", fake_get)

    provider = PixabayProvider(api_key="token")
    results = provider.search("ocean")

    assert len(results) == 1
    assert results[0].provider == "pixabay"
    assert results[0].photographer == "Mira"
