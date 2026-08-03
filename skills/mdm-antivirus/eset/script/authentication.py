#!/usr/bin/env python3
"""ESET Connect OAuth — POST /oauth/token + persist tokens in SkillCred `.env`."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests

import _http
from env_load import upsert_env_vars

TOKEN_PATH = "/oauth/token"


class AuthError(Exception):
    pass


def token_url(base_url: str) -> str:
    return base_url.rstrip("/") + TOKEN_PATH


def build_request(
    url: str,
    *,
    username: str | None = None,
    password: str | None = None,
    refresh_token: str | None = None,
) -> dict:
    if refresh_token:
        body = {"grant_type": "refresh_token", "refresh_token": refresh_token}
    else:
        if not username or not password:
            raise AuthError("username and password required for password grant")
        body = {
            "grant_type": "password",
            "username": username,
            "password": password,
        }
    return {
        "method": "POST",
        "url": url,
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
        "data": body,
    }


def redact(body: dict) -> dict:
    masked = dict(body)
    for key in ("password", "refresh_token"):
        if masked.get(key):
            masked[key] = "***"
    return masked


def parse_response(resp: requests.Response) -> dict:
    request_id = _http.request_id(resp)
    if resp.status_code == 200:
        payload = resp.json()
        return {
            "ok": True,
            "status": 200,
            "request_id": request_id,
            "access_token": payload.get("access_token"),
            "refresh_token": payload.get("refresh_token"),
            "token_type": payload.get("token_type", "Bearer"),
            "expires_in": payload.get("expires_in"),
        }
    if resp.status_code == 202:
        return {
            "ok": False,
            "status": 202,
            "cached": True,
            "response_id": resp.headers.get("response-id"),
            "request_id": request_id,
            "message": "Request cached (202); retry / poll with the response-id.",
        }
    return {
        "ok": False,
        "status": resp.status_code,
        "request_id": request_id,
        "error": _http.decode_body(resp),
    }


def request_token(
    url: str,
    *,
    username: str | None = None,
    password: str | None = None,
    refresh_token: str | None = None,
    timeout: int = 30,
) -> dict:
    req = build_request(
        url,
        username=username,
        password=password,
        refresh_token=refresh_token,
    )
    resp = _http.send(
        req["method"],
        req["url"],
        headers=req["headers"],
        data=req["data"],
        timeout=timeout,
    )
    return parse_response(resp)


def save_tokens(
    *,
    access_token: str,
    refresh_token: str | None = None,
    expires_in: Any = None,
) -> Path:
    updates = {"ESET_ACCESS_TOKEN": access_token}
    if refresh_token:
        updates["ESET_REFRESH_TOKEN"] = refresh_token
    if expires_in is not None:
        updates["ESET_TOKEN_EXPIRES_IN"] = str(expires_in)
    return upsert_env_vars(updates)


def ensure_access_token(
    url: str,
    *,
    username: str | None = None,
    password: str | None = None,
    access_token: str | None = None,
    refresh_token: str | None = None,
    force: bool = False,
) -> dict:
    """Return a usable token; reload from `.env` or fetch and persist.

    Order: existing access_token (unless force) → refresh_token grant → password grant.
    Successful exchanges write ``ESET_ACCESS_TOKEN`` / ``ESET_REFRESH_TOKEN`` to `.env`.
    """
    cached = (access_token or os.getenv("ESET_ACCESS_TOKEN", "")).strip()
    if cached and not force:
        return {"ok": True, "access_token": cached, "source": "env"}

    refresh = (refresh_token or os.getenv("ESET_REFRESH_TOKEN", "")).strip() or None
    if refresh:
        result = request_token(url, refresh_token=refresh)
        if result.get("ok") and result.get("access_token"):
            save_tokens(
                access_token=result["access_token"],
                refresh_token=result.get("refresh_token") or refresh,
                expires_in=result.get("expires_in"),
            )
            result["source"] = "refresh"
            return result

    if not username or not password:
        raise AuthError(
            "No ESET_ACCESS_TOKEN and cannot refresh/login — "
            "set ESET_USERNAME/ESET_PASSWORD or run: python cli.py token"
        )

    result = request_token(url, username=username, password=password)
    if not result.get("ok") or not result.get("access_token"):
        raise AuthError(f"Failed to obtain access token: {result}")

    save_tokens(
        access_token=result["access_token"],
        refresh_token=result.get("refresh_token"),
        expires_in=result.get("expires_in"),
    )
    result["source"] = "password"
    return result
