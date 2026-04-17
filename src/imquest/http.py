"""Minimal HTTP helpers using the Python standard library."""

from __future__ import annotations

import json
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class HttpResponse:
    def __init__(self, status_code: int, payload: dict) -> None:
        self.status_code = status_code
        self._payload = payload

    def json(self) -> dict:
        return self._payload


def get_json(
    url: str,
    *,
    params: dict[str, str | int | float] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 10.0,
) -> HttpResponse:
    final_url = url
    if params:
        final_url = f"{url}?{urlencode(params)}"

    request = Request(final_url, headers=headers or {}, method="GET")
    return _read_json_response(request, timeout=timeout)


def post_json(
    url: str,
    *,
    payload: dict,
    headers: dict[str, str] | None = None,
    timeout: float = 30.0,
) -> HttpResponse:
    req_headers = {"Content-Type": "application/json", **(headers or {})}
    body = json.dumps(payload).encode("utf-8")
    request = Request(url, headers=req_headers, data=body, method="POST")
    return _read_json_response(request, timeout=timeout)


def download_bytes(url: str, *, timeout: float = 20.0) -> bytes:
    request = Request(url, method="GET")
    with urlopen(request, timeout=timeout) as response:  # nosec B310
        return response.read()


def _read_json_response(request: Request, *, timeout: float) -> HttpResponse:
    try:
        with urlopen(request, timeout=timeout) as response:  # nosec B310
            status_code = response.getcode()
            content = response.read().decode("utf-8")
            payload = json.loads(content)
            return HttpResponse(status_code=status_code, payload=payload)
    except HTTPError as exc:
        content = exc.read().decode("utf-8") if exc.fp else "{}"
        try:
            payload = json.loads(content) if content else {}
        except json.JSONDecodeError:
            payload = {"error": {"message": content}}
        return HttpResponse(status_code=exc.code, payload=payload)
