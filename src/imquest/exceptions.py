"""Error types for imquest."""

from __future__ import annotations


class ImQuestError(Exception):
    """Base error for all package exceptions."""


class ProviderError(ImQuestError):
    """Raised for provider-level failures."""


class ConfigurationError(ImQuestError):
    """Raised for missing or invalid package configuration."""
