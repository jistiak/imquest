"""High-level photo search client."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from imquest.config import ProviderCredentials
from imquest.enums import Orientation, Size
from imquest.exceptions import ConfigurationError
from imquest.generation import (
    AIGenerationService,
    GoogleImageGenerator,
    OpenAIImageGenerator,
)
from imquest.models import GeneratedImage, PhotoResult
from imquest.providers.base import BaseProvider
from imquest.providers.flickr import FlickrProvider
from imquest.providers.google_cse import GoogleCSEProvider
from imquest.providers.openverse import OpenverseProvider
from imquest.providers.pexels import PexelsProvider
from imquest.providers.pixabay import PixabayProvider
from imquest.providers.unsplash import UnsplashProvider
from imquest.providers.wikimedia import WikimediaCommonsProvider
from imquest.utils.download import download_photo, save_generated_image


@dataclass(slots=True)
class SearchResponse:
    """Response wrapper for aggregate searches."""

    query: str | None
    total_results: int
    results: list[PhotoResult]


@dataclass(slots=True)
class DownloadResult:
    """Metadata for downloaded assets."""

    file_paths: list[Path]
    generated: bool


class ImQuestClient:
    """Unified API for searching images across supported providers."""

    def __init__(
        self,
        *,
        credentials: ProviderCredentials | None = None,
        providers: list[BaseProvider] | None = None,
        timeout: float = 10.0,
    ) -> None:
        creds = credentials or ProviderCredentials.from_env()
        self.generation_service = AIGenerationService(
            generators=[
                OpenAIImageGenerator(creds.openai_api_key, timeout=max(30.0, timeout * 3)),
                GoogleImageGenerator(creds.google_genai_api_key, timeout=max(30.0, timeout * 3)),
            ]
        )

        if providers is not None:
            self.providers = providers
            return

        self.providers = [
            OpenverseProvider(timeout=timeout),
            WikimediaCommonsProvider(timeout=timeout),
            PexelsProvider(creds.pexels_api_key, timeout=timeout),
            UnsplashProvider(creds.unsplash_access_key, timeout=timeout),
            FlickrProvider(creds.flickr_api_key, timeout=timeout),
            PixabayProvider(creds.pixabay_api_key, timeout=timeout),
            GoogleCSEProvider(creds.google_api_key, creds.google_cse_id, timeout=timeout),
        ]

    def configured_providers(self) -> list[BaseProvider]:
        """Return providers with valid credentials."""
        return [provider for provider in self.providers if provider.is_configured()]

    def search(
        self,
        query: str,
        *,
        orientation: Orientation | None = None,
        size: Size | None = None,
        per_page: int = 15,
        providers: list[str] | None = None,
    ) -> SearchResponse:
        """Search by keyword across one or more providers."""
        if not query.strip():
            raise ValueError("query must be a non-empty string")

        selected = self._select_providers(providers)
        all_results: list[PhotoResult] = []
        for provider in selected:
            all_results.extend(
                provider.search(
                    query,
                    orientation=orientation,
                    size=size,
                    per_page=per_page,
                )
            )
        return SearchResponse(query=query, total_results=len(all_results), results=all_results)

    def search_by_location(
        self,
        latitude: float,
        longitude: float,
        *,
        per_page: int = 15,
        provider: str = "flickr",
    ) -> SearchResponse:
        """Search by location; defaults to Flickr."""
        selected = self._select_providers([provider])
        if len(selected) != 1:
            raise ConfigurationError("Exactly one provider must be selected for location search")

        results = selected[0].search_by_location(latitude, longitude, per_page=per_page)
        return SearchResponse(query=None, total_results=len(results), results=results)

    def generate_image(
        self,
        prompt: str,
        *,
        size: str = "1024x1024",
        providers: list[str] | None = None,
    ) -> GeneratedImage | None:
        """Generate an image using configured AI generators."""
        response = self.generation_service.generate(prompt, size=size, providers=providers)
        return response.image

    def search_or_generate(
        self,
        query: str,
        *,
        orientation: Orientation | None = None,
        size: Size | None = None,
        per_page: int = 15,
        providers: list[str] | None = None,
        generate_if_empty: bool = True,
        generation_prompt: str | None = None,
        generation_providers: list[str] | None = None,
        generation_size: str = "1024x1024",
    ) -> tuple[SearchResponse, GeneratedImage | None]:
        """Search first, optionally generate with AI if nothing useful is found."""
        search_response = self.search(
            query,
            orientation=orientation,
            size=size,
            per_page=per_page,
            providers=providers,
        )
        if search_response.total_results > 0 or not generate_if_empty:
            return search_response, None

        prompt = generation_prompt or f"High quality editorial photo of: {query}"
        generated = self.generate_image(prompt, size=generation_size, providers=generation_providers)
        return search_response, generated

    def download(
        self,
        query: str,
        *,
        dest_dir: str | Path,
        limit: int = 5,
        generate_if_empty: bool = True,
        generation_providers: list[str] | None = None,
    ) -> DownloadResult:
        """Download top image results, with optional AI fallback generation."""
        search_response, generated = self.search_or_generate(
            query,
            per_page=limit,
            generate_if_empty=generate_if_empty,
            generation_providers=generation_providers,
        )

        paths: list[Path] = []
        for photo in search_response.results[:limit]:
            paths.append(download_photo(photo, dest_dir))

        if not paths and generated:
            paths.append(save_generated_image(generated, dest_dir, filename=f"{query}_generated.png"))
            return DownloadResult(file_paths=paths, generated=True)

        return DownloadResult(file_paths=paths, generated=False)

    def _select_providers(self, provider_names: list[str] | None) -> list[BaseProvider]:
        configured = self.configured_providers()
        if not configured:
            raise ConfigurationError(
                "No configured providers. Optional API keys: PEXELS_API_KEY, UNSPLASH_ACCESS_KEY, FLICKR_API_KEY, PIXABAY_API_KEY, GOOGLE_API_KEY + GOOGLE_CSE_ID"
            )

        if not provider_names:
            return configured

        names = {name.lower() for name in provider_names}
        chosen = [provider for provider in configured if provider.name in names]
        if not chosen:
            available = ", ".join(provider.name for provider in configured)
            raise ConfigurationError(f"Requested providers unavailable. Configured providers: {available}")
        return chosen
