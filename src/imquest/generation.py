"""AI image generation providers and fallback orchestration."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Protocol

from imquest.exceptions import GenerationError
from imquest.http import post_json
from imquest.models import GeneratedImage


class BaseImageGenerator(Protocol):
    name: str

    def is_configured(self) -> bool: ...

    def generate(self, prompt: str, *, size: str = "1024x1024") -> GeneratedImage: ...


class OpenAIImageGenerator:
    """OpenAI Images API generator."""

    name = "openai"
    endpoint = "https://api.openai.com/v1/images/generations"

    def __init__(self, api_key: str | None, model: str = "gpt-image-1", timeout: float = 60.0) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def generate(self, prompt: str, *, size: str = "1024x1024") -> GeneratedImage:
        if not self.is_configured():
            raise GenerationError("OpenAI generator is not configured (OPENAI_API_KEY missing)")

        response = post_json(
            self.endpoint,
            headers={"Authorization": f"Bearer {self.api_key}"},
            payload={
                "model": self.model,
                "prompt": prompt,
                "size": size,
            },
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            err = response.json().get("error", {})
            raise GenerationError(f"OpenAI generation failed: {err}")

        payload = response.json()
        data = payload.get("data", [])
        if not data:
            raise GenerationError("OpenAI generation returned no images")

        first = data[0]
        b64 = first.get("b64_json")
        if not b64:
            raise GenerationError("OpenAI generation response missing b64_json")

        image_bytes = base64.b64decode(b64)
        return GeneratedImage(
            provider=self.name,
            prompt=prompt,
            revised_prompt=first.get("revised_prompt"),
            image_bytes=image_bytes,
            mime_type="image/png",
        )


class GoogleImageGenerator:
    """Google Gemini image generation via generateContent."""

    name = "google"

    def __init__(
        self,
        api_key: str | None,
        model: str = "gemini-2.5-flash-image",
        timeout: float = 60.0,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def generate(self, prompt: str, *, size: str = "1024x1024") -> GeneratedImage:
        if not self.is_configured():
            raise GenerationError("Google generator is not configured (GOOGLE_GENAI_API_KEY missing)")

        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        response = post_json(
            endpoint,
            headers={"x-goog-api-key": self.api_key or ""},
            payload={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
            },
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            raise GenerationError(f"Google generation failed: {response.json()}")

        payload = response.json()
        candidates = payload.get("candidates", [])
        if not candidates:
            raise GenerationError("Google generation returned no candidates")

        parts = candidates[0].get("content", {}).get("parts", [])
        for part in parts:
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                image_bytes = base64.b64decode(inline["data"])
                mime_type = inline.get("mimeType") or inline.get("mime_type") or "image/png"
                return GeneratedImage(
                    provider=self.name,
                    prompt=prompt,
                    revised_prompt=None,
                    image_bytes=image_bytes,
                    mime_type=mime_type,
                )

        raise GenerationError("Google generation response did not include inline image data")


@dataclass(slots=True)
class GenerationAttempt:
    provider: str
    success: bool
    error: str | None = None


@dataclass(slots=True)
class GenerationResponse:
    image: GeneratedImage | None
    attempts: list[GenerationAttempt]


class AIGenerationService:
    def __init__(self, generators: list[BaseImageGenerator]) -> None:
        self.generators = generators

    def configured_generators(self) -> list[BaseImageGenerator]:
        return [generator for generator in self.generators if generator.is_configured()]

    def generate(
        self,
        prompt: str,
        *,
        size: str = "1024x1024",
        providers: list[str] | None = None,
    ) -> GenerationResponse:
        configured = self.configured_generators()
        if providers:
            requested = {name.lower() for name in providers}
            configured = [generator for generator in configured if generator.name in requested]

        attempts: list[GenerationAttempt] = []
        for generator in configured:
            try:
                image = generator.generate(prompt, size=size)
                attempts.append(GenerationAttempt(provider=generator.name, success=True))
                return GenerationResponse(image=image, attempts=attempts)
            except Exception as exc:  # noqa: BLE001
                attempts.append(GenerationAttempt(provider=generator.name, success=False, error=str(exc)))

        return GenerationResponse(image=None, attempts=attempts)
