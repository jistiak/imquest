from __future__ import annotations

from imquest.providers.wikimedia import WikimediaCommonsProvider


class DummyResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def json(self) -> dict:
        return self._payload


def test_wikimedia_search_parses_results(monkeypatch):
    payload = {
        "query": {
            "pages": {
                "123": {
                    "pageid": 123,
                    "title": "File:Example.jpg",
                    "imageinfo": [
                        {
                            "descriptionurl": "https://commons.wikimedia.org/wiki/File:Example.jpg",
                            "thumburl": "https://upload.wikimedia.org/example-thumb.jpg",
                            "width": 800,
                            "height": 600,
                        }
                    ],
                }
            }
        }
    }

    def fake_get(*args, **kwargs):
        return DummyResponse(payload)

    monkeypatch.setattr("imquest.providers.wikimedia.get_json", fake_get)

    provider = WikimediaCommonsProvider()
    results = provider.search("mountain")

    assert len(results) == 1
    assert results[0].provider == "wikimedia"
    assert results[0].id == "123"
