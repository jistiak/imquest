"""Command line interface for imquest."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from imquest.client import ImQuestClient
from imquest.enums import Orientation, Size


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Search photos across Openverse, Wikimedia, Pexels, Unsplash, Flickr, Pixabay, and Google CSE")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("--orientation", choices=[o.value for o in Orientation])
    parser.add_argument("--size", choices=[s.value for s in Size])
    parser.add_argument("--per-page", type=int, default=10)
    parser.add_argument("--providers", nargs="*", help="Subset of providers (openverse wikimedia pexels unsplash flickr pixabay google_cse)")
    parser.add_argument("--lat", type=float, help="Latitude for location search")
    parser.add_argument("--lon", type=float, help="Longitude for location search")
    parser.add_argument("--location-provider", default="flickr", help="Provider for location search")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    client = ImQuestClient()
    if args.lat is not None or args.lon is not None:
        if args.lat is None or args.lon is None:
            parser.error("--lat and --lon must be provided together")
        response = client.search_by_location(
            args.lat,
            args.lon,
            per_page=args.per_page,
            provider=args.location_provider,
        )
    else:
        if not args.query:
            parser.error("query is required for keyword search")
        response = client.search(
            args.query,
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


if __name__ == "__main__":
    main()
