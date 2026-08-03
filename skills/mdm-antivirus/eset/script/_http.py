#!/usr/bin/env python3
"""Shared HTTP helpers for ESET Connect (named ``_http`` to avoid stdlib ``http``)."""

from __future__ import annotations

from typing import Any

import requests

DEFAULT_TIMEOUT = 30


def request_id(resp: requests.Response) -> str | None:
    return resp.headers.get("request-id")


def decode_body(resp: requests.Response) -> Any:
    if not resp.content:
        return {}
    try:
        return resp.json()
    except ValueError:
        return resp.text


def send(
    method: str,
    url: str,
    *,
    headers: dict | None = None,
    params: dict | None = None,
    json_body: Any | None = None,
    data: Any | None = None,
    timeout: int = DEFAULT_TIMEOUT,
    session: requests.Session | None = None,
) -> requests.Response:
    caller = session or requests
    return caller.request(
        method,
        url,
        headers=headers,
        params=params,
        json=json_body,
        data=data,
        timeout=timeout,
    )
