"""Enum types used by imquest."""

from __future__ import annotations

from enum import Enum


class Orientation(str, Enum):
    """Supported image orientations across providers."""

    LANDSCAPE = "landscape"
    PORTRAIT = "portrait"
    SQUARE = "square"


class Size(str, Enum):
    """Coarse image size filters with provider-specific mappings."""

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
