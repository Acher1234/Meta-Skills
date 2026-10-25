"""OpenCode: limits of each logged-in provider (auth.json) + token/cost usage from local storage."""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any

import claude_usage
import codex_usage
from locate import Scope, first_file, opencode_auth_files, opencode_data_dirs, read_json
from stats import Record, aggregate, parse_ts

MAX_LOG_AGE = 31 * 86400


def load_auth(scope: Scope, override: Path | None) -> tuple[dict[str, Any], str | None]:
    candidates = [override] if override else []
    candidates += opencode_auth_files(scope)
    path = first_file(candidates)
    return (read_json(path), str(path)) if path else ({}, None)


def provider_limits(name: str, entry: dict[str, Any], http_env: dict[str, str]) -> dict[str, Any]:
    """Plan limits for OAuth providers we know how to query; others have none to report."""
    kind = entry.get("type")
    if kind != "oauth":
        return {"type": kind, "limits": None, "note": "API key — billed per token, no plan window"}
    expires = entry.get("expires")
    if expires and expires / 1000 < time.time():
        return {"type": kind, "limits": {"error": "OAuth token expired — run `opencode` once to refresh it"}}
    if name == "anthropic":
        limits = claude_usage.remote({"accessToken": entry.get("access")}, http_env)
    elif name == "openai":
        limits = codex_usage.remote({"access_token": entry.get("access")}, http_env, account=entry.get("accountId"))
    else:
        limits = None
    out: dict[str, Any] = {"type": kind, "limits": limits}
    if limits is None:
        out["note"] = "no public usage endpoint for this provider"
    return out


def _message_rows(data_dir: Path) -> list[dict[str, Any]]:
    """Assistant messages from `opencode.db` (v1+) or the legacy `storage/message/*/*.json` tree."""
    rows: list[dict[str, Any]] = []
    db = data_dir / "opencode.db"
    if db.is_file():
        try:
            with sqlite3.connect(f"file:{db}?mode=ro", uri=True) as conn:
                for (raw,) in conn.execute("SELECT data FROM message"):
                    try:
                        rows.append(json.loads(raw))
                    except (TypeError, json.JSONDecodeError):
                        continue
        except sqlite3.Error:
            pass
    storage = data_dir / "storage" / "message"
    if storage.is_dir():
        cutoff = time.time() - MAX_LOG_AGE
        for path in storage.glob("*/*.json"):
            if path.stat().st_mtime < cutoff:
                continue
            try:
                rows.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
    return rows


def local_records(scope: Scope) -> list[Record]:
    project = None if scope.is_global or scope.project is None else str(scope.project)
    records: list[Record] = []
    seen: set[str] = set()
    for data_dir in dict.fromkeys(d for d in opencode_data_dirs(scope) if d.is_dir()):
        for msg in _message_rows(data_dir):
            if msg.get("role") != "assistant" or not msg.get("tokens"):
                continue
            if msg.get("id") in seen:
                continue
            seen.add(msg.get("id"))
            where = msg.get("path") or {}
            if project and not str(where.get("root") or where.get("cwd") or "").startswith(project):
                continue
            ts = parse_ts((msg.get("time") or {}).get("created"))
            if ts is None:
                continue
            tokens = msg["tokens"]
            cache = tokens.get("cache") or {}
            model = "/".join(p for p in (msg.get("providerID"), msg.get("modelID")) if p)
            records.append(Record(ts, model, {
                "input": tokens.get("input", 0),
                "output": tokens.get("output", 0),
                "cache_read": cache.get("read", 0),
                "cache_write": cache.get("write", 0),
                "reasoning": tokens.get("reasoning", 0),
            }, cost=float(msg.get("cost") or 0)))
    return records


def usage(scope: Scope, override: Path | None, http_env: dict[str, str], *,
          want_remote: bool = True, want_local: bool = True) -> dict[str, Any]:
    auth, source = load_auth(scope, override)
    out: dict[str, Any] = {"tool": "opencode", "credentials": source, "providers": sorted(auth)}
    if want_remote:
        out["limits"] = (
            {name: provider_limits(name, entry, http_env) for name, entry in auth.items() if isinstance(entry, dict)}
            if auth else {"error": "no OpenCode auth.json found — log in with `opencode auth login`"}
        )
    if want_local:
        out["local_usage"] = aggregate(local_records(scope))
    return out
