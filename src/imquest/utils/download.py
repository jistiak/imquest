"""Download utilities for fetched or generated images."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from imquest.http import download_bytes
from imquest.models import GeneratedImage, PhotoResult


def download_photo(photo: PhotoResult, dest_dir: str | Path) -> Path:
    directory = Path(dest_dir)
    directory.mkdir(parents=True, exist_ok=True)

    source_url = photo.thumbnail_url or photo.url
    suffix = _guess_suffix(source_url)
    filename = f"{photo.provider}_{photo.id}{suffix}"
    output = directory / _sanitize(filename)
    output.write_bytes(download_bytes(source_url))
    return output


def save_generated_image(image: GeneratedImage, dest_dir: str | Path, filename: str | None = None) -> Path:
    directory = Path(dest_dir)
    directory.mkdir(parents=True, exist_ok=True)

    suffix = ".png" if image.mime_type.endswith("png") else ".jpg"
    file_name = filename or f"generated_{image.provider}{suffix}"
    output = directory / _sanitize(file_name)
    output.write_bytes(image.image_bytes)
    return output


def _guess_suffix(url: str) -> str:
    path = urlparse(url).path
    suffix = Path(path).suffix.lower()
    return suffix if suffix in {".png", ".jpg", ".jpeg", ".webp"} else ".jpg"


def _sanitize(name: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"_", "-", "."} else "_" for ch in name)
