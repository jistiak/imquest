"""Minimal HTTP helpers using the Python standard library."""

from __future__ import annotations

import json
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
    with urlopen(request, timeout=timeout) as response:  # nosec B310
        status_code = response.getcode()
        content = response.read().decode("utf-8")
        payload = json.loads(content)
        return HttpResponse(status_code=status_code, payload=payload)
