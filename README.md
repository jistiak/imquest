# imquest

`imquest` is an all-in-one image toolkit for:

- searching images across multiple providers,
- downloading top matches quickly,
- generating AI images when search quality is poor,
- running an interactive smart terminal UI (TUI),
- and using everything from Python scripts.

## Quick start

Install:

```bash
pip install imquest
```

Search:

```bash
imquest search "cyberpunk city skyline" --per-page 8
```

Download top matches:

```bash
imquest download "japanese tea house" --limit 5 --dest downloads/
```

Generate with AI directly:

```bash
imquest generate "ultra detailed product photo of a matte black watch" --dest downloads/
```

Launch smart TUI:

```bash
imquest tui
```

## Provider matrix

### Search providers

- `openverse` (no key)
- `wikimedia` (no key)
- `pexels` (key)
- `unsplash` (key)
- `flickr` (key)
- `pixabay` (key)
- `google_cse` (Google Programmable Search JSON API: key + CSE ID)

### AI generation providers

- `openai` (OPENAI_API_KEY)
- `google` (GOOGLE_GENAI_API_KEY)

---

## Authentication setup guide (folded sections)

> Tip: You only need to configure the providers you want. `openverse` and `wikimedia` work without any API keys.

<details>
<summary><strong>Global setup (recommended first step)</strong></summary>

### 1) Put keys in your shell profile

```bash
# ~/.bashrc or ~/.zshrc
export PEXELS_API_KEY="..."
export UNSPLASH_ACCESS_KEY="..."
export FLICKR_API_KEY="..."
export PIXABAY_API_KEY="..."
export GOOGLE_API_KEY="..."
export GOOGLE_CSE_ID="..."
export OPENAI_API_KEY="..."
export GOOGLE_GENAI_API_KEY="..."
```

Then reload:

```bash
source ~/.bashrc
# or source ~/.zshrc
```

### 2) Verify keys loaded

```bash
env | grep -E 'PEXELS|UNSPLASH|FLICKR|PIXABAY|GOOGLE_API_KEY|GOOGLE_CSE_ID|OPENAI|GOOGLE_GENAI'
```

### 3) Test one query quickly

```bash
imquest search "studio portrait" --per-page 3 --json
```

</details>

<details>
<summary><strong>Pexels (PEXELS_API_KEY)</strong></summary>

1. Create/sign in to your Pexels account.
2. Go to the Pexels API dashboard and create an API key.
3. Add to environment:

```bash
export PEXELS_API_KEY="your_pexels_key"
```

4. Test only pexels:

```bash
imquest search "landscape" --providers pexels --json
```

</details>

<details>
<summary><strong>Unsplash (UNSPLASH_ACCESS_KEY)</strong></summary>

1. Create an Unsplash developer app.
2. Copy the **Access Key**.
3. Add to environment:

```bash
export UNSPLASH_ACCESS_KEY="your_unsplash_access_key"
```

4. Test:

```bash
imquest search "architecture" --providers unsplash --json
```

</details>

<details>
<summary><strong>Flickr (FLICKR_API_KEY)</strong></summary>

1. Create/get a Flickr API key from your app settings.
2. Add to environment:

```bash
export FLICKR_API_KEY="your_flickr_api_key"
```

3. Test keyword search:

```bash
imquest search "sunset" --providers flickr --json
```

4. Test location search:

```bash
imquest --lat 40.7128 --lon -74.0060 --location-provider flickr
```

</details>

<details>
<summary><strong>Pixabay (PIXABAY_API_KEY)</strong></summary>

1. Register and get your Pixabay API key.
2. Add to environment:

```bash
export PIXABAY_API_KEY="your_pixabay_api_key"
```

3. Test:

```bash
imquest search "nature" --providers pixabay --json
```

</details>

<details>
<summary><strong>Google CSE image search (GOOGLE_API_KEY + GOOGLE_CSE_ID)</strong></summary>

1. Enable Programmable Search JSON API in Google Cloud.
2. Create an API key (`GOOGLE_API_KEY`).
3. Create a Programmable Search Engine and copy its CX id (`GOOGLE_CSE_ID`).
4. Add both:

```bash
export GOOGLE_API_KEY="your_google_api_key"
export GOOGLE_CSE_ID="your_custom_search_engine_id"
```

5. Test:

```bash
imquest search "electric car" --providers google_cse --json
```

</details>

<details>
<summary><strong>OpenAI image generation (OPENAI_API_KEY)</strong></summary>

1. Create an OpenAI API key.
2. Add to environment:

```bash
export OPENAI_API_KEY="your_openai_api_key"
```

3. Test generation:

```bash
imquest generate "photoreal cozy coffee shop interior" --providers openai --dest downloads/
```

</details>

<details>
<summary><strong>Google AI generation (GOOGLE_GENAI_API_KEY)</strong></summary>

1. Create a Google GenAI API key.
2. Add to environment:

```bash
export GOOGLE_GENAI_API_KEY="your_google_genai_key"
```

3. Test generation:

```bash
imquest generate "futuristic city at sunrise" --providers google --dest downloads/
```

</details>

<details>
<summary><strong>No-key providers: Openverse + Wikimedia</strong></summary>

You can use these immediately with no setup:

```bash
imquest search "public domain vintage map" --providers openverse wikimedia --json
```

</details>

---

## AI fallback behavior

When you use `search` (via Python `search_or_generate`) or `download`, `imquest` can auto-generate an image if search results are empty.

This makes it useful for “always return something” workflows.

## Python API examples

```python
from imquest import ImQuestClient

client = ImQuestClient()

# 1) Search only
search = client.search("minimalist interior", per_page=10)
print(search.total_results)

# 2) Search with generation fallback
search, generated = client.search_or_generate("concept art floating city")
if generated:
    print("Fallback generated by", generated.provider)

# 3) Generate explicitly
image = client.generate_image("cinematic portrait of a robot violinist")

# 4) Download search hits (or generated fallback)
out = client.download("nature wallpaper 4k", dest_dir="downloads", limit=3)
print(out.file_paths)
```

## TUI controls

In `imquest tui`:

- `/` search
- `g` AI generate
- `d` download selected result (or generated image)
- `r` show selected result data
- `j/k` or arrows move selection
- `q` quit

## PyPI release guide (maintainers)

<details>
<summary><strong>Build and upload to PyPI</strong></summary>

### 1) Clean previous build artifacts

```bash
rm -rf dist build *.egg-info
```

### 2) Build wheel + sdist

Recommended:

```bash
python -m build
```

Fallback if `build` is unavailable:

```bash
python -m pip wheel --no-build-isolation . -w dist
```

### 3) Install twine

```bash
python -m pip install twine
```

### 4) Upload (token-based)

```bash
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="pypi-..."
python -m twine upload dist/*
```

### 5) Verify install from PyPI

```bash
python -m pip install -U imquest
```

</details>

## Important note on Google Images

`imquest` does **not** scrape Google Images pages. It supports official Programmable Search API integration (`google_cse`) where configured.
