# imquest

`imquest` is an all-in-one Python package for discovering images from multiple APIs with a single interface.

## Supported services

### Works without account/API key

- **Openverse** (`openverse`) — open licensed image search endpoint.
- **Wikimedia Commons** (`wikimedia`) — MediaWiki API based file search and geosearch.

### Requires account/API key

- **Pexels** (`pexels`) — free API key.
- **Unsplash** (`unsplash`) — access key.
- **Flickr** (`flickr`) — API key.
- **Pixabay** (`pixabay`) — API key.
- **Google Programmable Search JSON API** (`google_cse`) — API key + CSE ID (legacy product; closed to new customers per Google docs).

By default, `imquest` searches across every configured provider (including no-key providers).

## Install

```bash
pip install .
```

Build wheel:

```bash
python -m pip wheel --no-build-isolation . -w dist
```

Install wheel:

```bash
pip install dist/imquest-0.1.0-py3-none-any.whl
```

## Environment variables

```bash
export PEXELS_API_KEY="..."
export UNSPLASH_ACCESS_KEY="..."
export FLICKR_API_KEY="..."
export PIXABAY_API_KEY="..."
export GOOGLE_API_KEY="..."
export GOOGLE_CSE_ID="..."
```

## Python usage

```python
from imquest import ImQuestClient, Orientation, Size

client = ImQuestClient()

# All configured providers (Openverse and Wikimedia always available)
resp = client.search(
    "autumn forest",
    orientation=Orientation.LANDSCAPE,
    size=Size.LARGE,
    per_page=5,
)

# Only certain providers
resp2 = client.search("city skyline", providers=["openverse", "pixabay"])

# Location search with Flickr (default) or Wikimedia
geo = client.search_by_location(40.7128, -74.0060, provider="wikimedia", per_page=10)
```

## CLI usage

```bash
imquest "northern lights" --providers openverse wikimedia pixabay --per-page 5
```

Location search:

```bash
imquest --lat 37.7749 --lon -122.4194 --location-provider wikimedia
```

## Notes about Google Images

`imquest` supports Google image search only through **Programmable Search JSON API** (`google_cse`). It is not browser scraping.

Google’s official docs state this API is closed to new customers and existing users must transition by **January 1, 2027**. Treat it as optional/legacy support.

## Scope / possibilities

Current package scope includes:

- Multi-provider keyword search
- Optional location search (Flickr + Wikimedia)
- Unified normalized output model
- Provider-level extensibility for adding more backends

Future upgrades can add:

- Async execution and parallel provider fan-out
- Deduplication and ranking across provider results
- License-aware filtering and attribution exporters
- Local caching and retry/rate-limit middleware

## Development

```bash
pytest
```
