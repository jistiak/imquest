"""Command line interface for imquest."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from imquest.client import ImQuestClient
from imquest.enums import Orientation, Size
from imquest.tui import run_tui


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="imquest",
        description="All-in-one image search, download, AI generation, and interactive TUI",
    )

    subparsers = parser.add_subparsers(dest="command")

    search = subparsers.add_parser("search", help="Search images")
    _add_common_search_args(search)
    search.add_argument("--json", action="store_true", help="Output full JSON")

    download = subparsers.add_parser("download", help="Search and download images")
    _add_common_search_args(download)
    download.add_argument("--dest", default="downloads", help="Output directory")
    download.add_argument("--limit", type=int, default=5, help="How many results to download")
    download.add_argument("--no-generate", action="store_true", help="Disable AI generation fallback")

    generate = subparsers.add_parser("generate", help="Generate an image with AI providers")
    generate.add_argument("prompt", help="Prompt to generate")
    generate.add_argument("--providers", nargs="*", help="Generation providers (openai google)")
    generate.add_argument("--size", default="1024x1024", help="Generation size")
    generate.add_argument("--dest", default="downloads", help="Output directory")

    subparsers.add_parser("tui", help="Launch interactive terminal UI")

    # Backward-compatible mode: `imquest "query" --per-page 5`
    parser.add_argument("legacy_query", nargs="?", help=argparse.SUPPRESS)
    parser.add_argument("--orientation", choices=[o.value for o in Orientation])
    parser.add_argument("--size", choices=[s.value for s in Size])
    parser.add_argument("--per-page", type=int, default=10)
    parser.add_argument("--providers", nargs="*")
    parser.add_argument("--lat", type=float)
    parser.add_argument("--lon", type=float)
    parser.add_argument("--location-provider", default="flickr")

    return parser


def _add_common_search_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("query", help="Search query")
    parser.add_argument("--orientation", choices=[o.value for o in Orientation])
    parser.add_argument("--size", choices=[s.value for s in Size])
    parser.add_argument("--per-page", type=int, default=10)
    parser.add_argument("--providers", nargs="*", help="Search provider subset")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "tui":
        run_tui()
        return

    client = ImQuestClient()

    if args.command == "generate":
        generated = client.generate_image(args.prompt, size=args.size, providers=args.providers)
        if not generated:
            raise SystemExit("No AI generator configured or generation failed.")

        from imquest.utils.download import save_generated_image

        path = save_generated_image(generated, args.dest)
        print(json.dumps({"provider": generated.provider, "saved_to": str(path), "prompt": generated.prompt}, indent=2))
        return

    if args.command == "download":
        result = client.download(
            args.query,
            dest_dir=args.dest,
            limit=args.limit,
            generate_if_empty=not args.no_generate,
        )
        print(json.dumps({
            "downloaded": [str(path) for path in result.file_paths],
            "generated": result.generated,
        }, indent=2))
        return

    if args.command == "search":
        response, generated = client.search_or_generate(
            args.query,
            orientation=Orientation(args.orientation) if args.orientation else None,
            size=Size(args.size) if args.size else None,
            per_page=args.per_page,
            providers=args.providers,
            generate_if_empty=True,
        )
        payload = {
            "query": response.query,
            "total_results": response.total_results,
            "results": [asdict(photo) for photo in response.results],
            "generated_fallback": bool(generated),
            "generated_provider": generated.provider if generated else None,
        }
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(f"Found {response.total_results} results")
            if generated:
                print(f"No results found. Generated fallback image using {generated.provider}.")
        return

    # Legacy mode
    if args.legacy_query:
        if args.lat is not None or args.lon is not None:
            if args.lat is None or args.lon is None:
                parser.error("--lat and --lon must be provided together")
            response = client.search_by_location(args.lat, args.lon, per_page=args.per_page, provider=args.location_provider)
        else:
            response = client.search(
                args.legacy_query,
                orientation=Orientation(args.orientation) if args.orientation else None,
                size=Size(args.size) if args.size else None,
                per_page=args.per_page,
                providers=args.providers,
            )
        print(json.dumps({
            "query": response.query,
            "total_results": response.total_results,
            "results": [asdict(photo) for photo in response.results],
        }, indent=2))
        return

    parser.print_help()


if __name__ == "__main__":
    main()
