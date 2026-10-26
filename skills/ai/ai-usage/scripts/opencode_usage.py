"""OpenCode: limits of each logged-in provider (auth.json) + token/cost usage from local storage."""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any

import claude_usage
import codex_usage
from common.http import HttpClient, HttpError
from common.skill_env.skill_cred import display_path
from locate import Scope, first_file, jwt_claims, opencode_auth_files, opencode_data_dirs, read_json
from sources import Cred, hermes_pool_status, opencode_go_creds, pick
from stats import Record, aggregate, parse_ts, window

GO_USAGE_URL = "https://opencode.ai/zen/go/v1/usage"
GO_WINDOWS = {"rolling": "rolling_5h", "weekly": "week", "monthly": "month"}
MAX_LOG_AGE = 31 * 86400


def load_auth(scope: Scope, override: Path | None) -> tuple[dict[str, Any], Path | None]:
    candidates = [override] if override else []
    candidates += opencode_auth_files(scope)
    path = first_file(candidates)
    return (read_json(path), path) if path else ({}, None)


def go_limits(creds: list[Cred], http_env: dict[str, str]) -> dict[str, Any]:
    """First key the Go endpoint accepts (a Zen `opencode` key may not be a Go subscription)."""
    if not creds:
        return {"error": "no OpenCode Go key — set OPENCODE_GO_API_KEY (or log in OpenCode / Hermes / OpenClaw)"}
    result: dict[str, Any] = {}
    for cred in creds:
        result = {**_go_limits(cred, http_env), "credentials": cred.source}
        if "error" not in result:
            break
    return result


def _go_limits(cred: Cred, http_env: dict[str, str]) -> dict[str, Any]:
    """OpenCode Go plan: rolling 5h / weekly / monthly windows (percent = consumed)."""
    # Cloudflare rejects urllib's default User-Agent (error 1010): always send an explicit one.
    client = HttpClient(environ=http_env, user_agent="ai-usage-skill/1.0",
                        headers={"Authorization": f"Bearer {cred.token}"}, timeout=20)
    try:
        data = client.get(GO_USAGE_URL)
    except HttpError as exc:
        return {"error": f"OpenCode Go usage HTTP {exc.status}", "detail": str(exc)[:300]}
    except Exception as exc:
        return {"error": str(exc)[:300]}
    windows = [
        window(GO_WINDOWS.get(name, name), w.get("percent"), w.get("resetsAt"), status=w.get("status"))
        for name, w in ((data or {}).get("usage") or {}).items() if isinstance(w, dict)
    ]
    blocked = [w["window"] for w in windows if w.get("status") not in (None, "ok")]
    return {"windows": windows, "limit_reached": bool(blocked), "blocked_by": blocked or None}


def provider_limits(name: str, entry: dict[str, Any], label: str, http_env: dict[str, str]) -> dict[str, Any]:
    """Plan limits for OAuth providers we know how to query; others have none to report."""
    kind = entry.get("type")
    if name in {"opencode", "opencode-go"}:
        return {"type": kind, "limits": None, "note": "see opencode_go"}
    if kind != "oauth":
        return {"type": kind, "limits": None, "note": "API key — billed per token, no plan window"}
    access = entry.get("access") or ""
    expires = entry["expires"] / 1000 if entry.get("expires") else jwt_claims(access).get("exp")
    cred = Cred("tool", f"{label} ({name})", access, expires_at=expires, account=entry.get("accountId"))
    if name == "anthropic":
        return {"type": kind, "limits": claude_usage.remote(cred, http_env, tool="opencode")}
    if name == "openai":
        return {"type": kind, "limits": codex_usage.remote(cred, http_env, tool="opencode")}
    return {"type": kind, "limits": None, "note": "no public usage endpoint for this provider"}


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
          want_remote: bool = True, want_local: bool = True, origin: str = "auto") -> dict[str, Any]:
    auth, path = load_auth(scope, override) if origin in ("auto", "tool") else ({}, None)
    label = display_path(path) if path else ""
    _, go_found = pick(opencode_go_creds(scope, override), origin, kind="api_key")
    out: dict[str, Any] = {"tool": "opencode", "credentials": label or None, "providers": sorted(auth)}
    if want_remote:
        out["limits"] = (
            {name: provider_limits(name, entry, label, http_env) for name, entry in auth.items() if isinstance(entry, dict)}
            if auth else {"error": "no OpenCode auth.json found — log in with `opencode auth login`"}
        )
        if go_found or "opencode-go" in auth:
            go = go_limits(go_found, http_env)
            go["sources_found"] = [c.describe() for c in go_found]
            hermes = hermes_pool_status(scope, "opencode-go")
            if hermes:
                go["hermes_last_status"] = hermes
            out["opencode_go"] = go
    if want_local:
        out["local_usage"] = aggregate(local_records(scope))
    return out
