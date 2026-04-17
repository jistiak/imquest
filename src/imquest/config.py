"""Configuration utilities for credentials and defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class ProviderCredentials:
    pexels_api_key: str | None = None
    unsplash_access_key: str | None = None
    flickr_api_key: str | None = None
    pixabay_api_key: str | None = None
    google_api_key: str | None = None
    google_cse_id: str | None = None
    openai_api_key: str | None = None
    google_genai_api_key: str | None = None

    @classmethod
    def from_env(cls) -> "ProviderCredentials":
        """Load provider API keys from environment variables."""
        return cls(
            pexels_api_key=os.getenv("PEXELS_API_KEY"),
            unsplash_access_key=os.getenv("UNSPLASH_ACCESS_KEY"),
            flickr_api_key=os.getenv("FLICKR_API_KEY"),
            pixabay_api_key=os.getenv("PIXABAY_API_KEY"),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            google_cse_id=os.getenv("GOOGLE_CSE_ID"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            google_genai_api_key=os.getenv("GOOGLE_GENAI_API_KEY"),
        )
