"""High-level photo search client."""

from __future__ import annotations

from dataclasses import dataclass

from imquest.config import ProviderCredentials
from imquest.enums import Orientation, Size
from imquest.exceptions import ConfigurationError
from imquest.models import PhotoResult
from imquest.providers.base import BaseProvider
from imquest.providers.flickr import FlickrProvider
from imquest.providers.google_cse import GoogleCSEProvider
from imquest.providers.openverse import OpenverseProvider
from imquest.providers.pexels import PexelsProvider
from imquest.providers.pixabay import PixabayProvider
from imquest.providers.unsplash import UnsplashProvider
from imquest.providers.wikimedia import WikimediaCommonsProvider


@dataclass(slots=True)
class SearchResponse:
    """Response wrapper for aggregate searches."""

    query: str | None
    total_results: int
    results: list[PhotoResult]


class ImQuestClient:
    """Unified API for searching images across supported providers."""

    def __init__(
        self,
        *,
        credentials: ProviderCredentials | None = None,
        providers: list[BaseProvider] | None = None,
        timeout: float = 10.0,
    ) -> None:
        if providers is not None:
            self.providers = providers
            return

        creds = credentials or ProviderCredentials.from_env()
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
