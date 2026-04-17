from __future__ import annotations

from pathlib import Path

from imquest.client import ImQuestClient
from imquest.models import GeneratedImage, PhotoResult
from imquest.providers.base import BaseProvider


class EmptyProvider(BaseProvider):
    name = "empty"

    def is_configured(self) -> bool:
        return True

    def search(self, query: str, *, orientation=None, size=None, per_page: int = 15):
        return []


class OneProvider(BaseProvider):
    name = "one"

    def is_configured(self) -> bool:
        return True

    def search(self, query: str, *, orientation=None, size=None, per_page: int = 15):
        return [PhotoResult(id="1", provider="one", url="https://example.com/p.jpg")]


def test_search_or_generate_returns_generated_on_empty(monkeypatch):
    client = ImQuestClient(providers=[EmptyProvider()])

    monkeypatch.setattr(
        client,
        "generate_image",
        lambda prompt, size="1024x1024", providers=None: GeneratedImage(
            provider="openai", prompt=prompt, revised_prompt=None, image_bytes=b"img"
        ),
    )

    search, generated = client.search_or_generate("something")
    assert search.total_results == 0
    assert generated is not None
    assert generated.provider == "openai"


def test_download_uses_search_results(monkeypatch, tmp_path: Path):
    client = ImQuestClient(providers=[OneProvider()])

    monkeypatch.setattr(
        "imquest.client.download_photo",
        lambda photo, dest_dir: Path(dest_dir) / f"{photo.id}.jpg",
    )

    result = client.download("cat", dest_dir=tmp_path, limit=1)

    assert result.generated is False
    assert len(result.file_paths) == 1
    assert result.file_paths[0].name == "1.jpg"
