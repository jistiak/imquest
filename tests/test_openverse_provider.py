from __future__ import annotations

from imquest.providers.openverse import OpenverseProvider


class DummyResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def json(self) -> dict:
        return self._payload


def test_openverse_search_parses_results(monkeypatch):
    payload = {
        "results": [
            {
                "id": "ov1",
                "foreign_landing_url": "https://source.example/ov1",
                "thumbnail": "https://source.example/ov1-thumb.jpg",
                "creator": "Dana",
                "width": 1024,
                "height": 768,
            }
        ]
    }

    def fake_get(*args, **kwargs):
        return DummyResponse(payload)

    monkeypatch.setattr("imquest.providers.openverse.get_json", fake_get)

    provider = OpenverseProvider()
    results = provider.search("forest")

    assert len(results) == 1
    assert results[0].id == "ov1"
    assert results[0].provider == "openverse"
