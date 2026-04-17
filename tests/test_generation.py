from __future__ import annotations

from imquest.generation import AIGenerationService
from imquest.models import GeneratedImage


class FakeGenerator:
    def __init__(self, name: str, configured: bool, should_fail: bool = False) -> None:
        self.name = name
        self._configured = configured
        self._should_fail = should_fail

    def is_configured(self) -> bool:
        return self._configured

    def generate(self, prompt: str, *, size: str = "1024x1024") -> GeneratedImage:
        if self._should_fail:
            raise RuntimeError("boom")
        return GeneratedImage(provider=self.name, prompt=prompt, revised_prompt=None, image_bytes=b"png")


def test_generation_service_fallback_to_next_provider():
    service = AIGenerationService(
        generators=[
            FakeGenerator("openai", configured=True, should_fail=True),
            FakeGenerator("google", configured=True, should_fail=False),
        ]
    )

    response = service.generate("a fox")

    assert response.image is not None
    assert response.image.provider == "google"
    assert len(response.attempts) == 2
    assert response.attempts[0].success is False
    assert response.attempts[1].success is True


def test_generation_service_returns_none_when_no_configured_generators():
    service = AIGenerationService(generators=[FakeGenerator("openai", configured=False)])
    response = service.generate("a fox")

    assert response.image is None
    assert response.attempts == []
