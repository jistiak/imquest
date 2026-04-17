# imquest

`imquest` is a production-ready Python package for searching photos from multiple providers through one unified API.

It currently supports:

- **Pexels** (keyword search)
- **Unsplash** (keyword search)
- **Flickr** (keyword + geolocation search)

By default, keyword search runs across all configured providers and returns normalized results.

## Why imquest

- One API surface for multiple image platforms
- Unified result model (`PhotoResult`) across providers
- Filter support for orientation and size
- Optional provider targeting (`["pexels"]`, `["flickr"]`, etc.)
- Location-based search (lat/lon) with Flickr by default
- CLI for scripting and shell use

## Install

From source:

```bash
pip install .
```

Build wheel + source distribution:

```bash
python -m build
```

Then install built artifacts:

```bash
pip install dist/imquest-0.1.0-py3-none-any.whl
```

## API credentials

Set any provider keys you want to use. You can configure one, two, or all three.

```bash
export PEXELS_API_KEY="..."
export UNSPLASH_ACCESS_KEY="..."
export FLICKR_API_KEY="..."
```

## Python usage

```python
from imquest import ImQuestClient, Orientation, Size

client = ImQuestClient()

# keyword search across configured providers
resp = client.search(
    "mountain lake",
    orientation=Orientation.LANDSCAPE,
    size=Size.LARGE,
    per_page=5,
)

print(resp.total_results)
print(resp.results[0])

# location search (defaults to flickr)
geo = client.search_by_location(37.7749, -122.4194, per_page=5)
```

## CLI usage

Keyword search:

```bash
imquest "city skyline" --orientation landscape --size large --per-page 5
```

Limit to specific providers:

```bash
imquest "city skyline" --providers pexels flickr
```

Location search:

```bash
imquest --lat 40.7128 --lon -74.0060 --per-page 5
```

## Project scope and roadmap

### Current scope

- Unified search SDK and CLI
- Provider abstractions for easier extension
- Friendly errors for missing configuration
- Test suite covering orchestration and provider parsing

### Near-term possibilities

- Async HTTP mode for lower latency
- Pagination helpers and cursors
- Rate-limit awareness/retry middleware
- Result scoring/ranking and de-duplication across providers
- Optional metadata enrichments (licenses, EXIF, color palette)

## Development

Install dev tools:

```bash
pip install -e .[dev]
```

Run tests:

```bash
pytest
```
