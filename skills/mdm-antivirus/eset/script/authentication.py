#!/usr/bin/env python3
"""ESET Connect OAuth — POST /oauth/token + persist tokens in SkillCred `.env`."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import requests

import _http
from skill_env import ConfigError, ENV

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
) -> tuple[Path, str]:
    updates = {"ESET_ACCESS_TOKEN": access_token}
    if refresh_token:
        updates["ESET_REFRESH_TOKEN"] = refresh_token
    if expires_in is not None:
        updates["ESET_TOKEN_EXPIRES_IN"] = str(expires_in)
    return ENV.upsert_env_vars(updates)


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
    Successful exchanges write ``ESET_ACCESS_TOKEN`` / ``ESET_REFRESH_TOKEN`` to `.env``.
    """
    env = ENV.read_env()
    cached = (access_token or env.get("ESET_ACCESS_TOKEN", "")).strip()
    if cached and not force:
        return {"ok": True, "access_token": cached, "source": "env"}

    refresh = (refresh_token or env.get("ESET_REFRESH_TOKEN", "")).strip() or None
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


def _dump(data: object) -> None:
    print(json.dumps(data, indent=2, default=str))


class Authentication:
    @staticmethod
    def cmd_env_check(_: argparse.Namespace) -> int | None:
        try:
            cfg = ENV.resolve(require_credentials=True)
        except ConfigError as exc:
            _dump(
                {
                    "ok": False,
                    "env": str(ENV.env_path()),
                    "library": ENV.display_skill_home(),
                    "error": str(exc),
                }
            )
            return 1
        _dump(
            {
                "ok": True,
                "env": str(ENV.env_path()),
                "library": ENV.display_skill_home(),
                "base_url": cfg["base_url"],
                "token_url": cfg["token_url"],
                "api_url": cfg["api_url"],
                "automation_url": cfg["automation_url"],
                "app_url": cfg["app_url"],
                "asset_url": cfg["asset_url"],
                "policy_url": cfg["policy_url"],
                "incident_url": cfg["incident_url"],
                "patch_url": cfg["patch_url"],
                "username": cfg["username"],
                "has_access_token": bool(os.getenv("ESET_ACCESS_TOKEN", "").strip()),
                "has_refresh_token": bool(os.getenv("ESET_REFRESH_TOKEN", "").strip()),
            }
        )
        return None

    @staticmethod
    def cmd_token(args: argparse.Namespace) -> int | None:
        cfg = ENV.resolve(require_credentials=True)
        if args.print_request:
            req = build_request(
                cfg["token_url"],
                username=cfg["username"],
                password=cfg["password"],
                refresh_token=args.refresh,
            )
            _dump(
                {
                    "method": req["method"],
                    "url": req["url"],
                    "headers": req["headers"],
                    "body": redact(req["data"]),
                }
            )
            return None

        try:
            result = ensure_access_token(
                cfg["token_url"],
                username=cfg["username"],
                password=cfg["password"],
                refresh_token=args.refresh
                or cfg["env_values"].get("ESET_REFRESH_TOKEN", "").strip()
                or None,
                force=True,
            )
        except AuthError as exc:
            _dump({"ok": False, "error": str(exc)})
            return 1

        if args.token_only and result.get("ok"):
            print(result["access_token"])
            return None

        safe = {
            k: v
            for k, v in result.items()
            if k not in ("access_token", "refresh_token")
        }
        safe["access_token"] = "***"
        if result.get("refresh_token"):
            safe["refresh_token"] = "***"
        safe["saved_to"] = str(ENV.env_path())
        _dump(safe)
        return None if result.get("ok") else 1

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        sub.add_parser(
            "env-check", help="Validate .env + resolved paths (no network)"
        ).set_defaults(func=Authentication.cmd_env_check)

        p_token = sub.add_parser("token", help="Get an OAuth Bearer token")
        p_token.add_argument(
            "--refresh",
            metavar="REFRESH_TOKEN",
            help="Use the refresh_token grant instead of password",
        )
        p_token.add_argument(
            "--print-request",
            action="store_true",
            help="Dry run: print the request (secrets masked) without calling the API",
        )
        p_token.add_argument(
            "--token-only",
            action="store_true",
            help="On success, print only the access_token",
        )
        p_token.set_defaults(func=Authentication.cmd_token)
