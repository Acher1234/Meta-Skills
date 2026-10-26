"""OpenCode: limits of each logged-in provider (auth.json) + token/cost usage from local storage."""

from __future__ import annotations

import json
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import claude_usage
import codex_usage
from common.http import HttpClient, HttpError
from locate import Scope, jwt_claims, opencode_data_dirs
from opencode_console import NO_SIGN_IN, Console
from sources import Cred, hermes_pool_status, opencode_auth, opencode_go_creds, pick
from stats import Record, aggregate, parse_ts, window

GO_USAGE_URL = "https://opencode.ai/zen/go/v1/usage"
GO_WINDOWS = {"rolling": "rolling_5h", "weekly": "week", "monthly": "month"}
MAX_LOG_AGE = 31 * 86400


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
        note = "Console sign-in — see opencode_go / extra_usage" if kind == "oauth" else "see opencode_go"
        return {"type": kind, "limits": None, "note": note}
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


def local_spend(records: list[Record]) -> dict[str, float]:
    """This month's cost logged locally for Zen (`opencode/…`) and Go (`opencode-go/…`) models."""
    start = datetime.now().astimezone().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    spend = {"zen_usd": 0.0, "go_usd": 0.0}
    for rec in records:
        if rec.ts >= start:
            provider = rec.model.split("/", 1)[0]
            key = {"opencode": "zen_usd", "opencode-go": "go_usd"}.get(provider)
            if key:
                spend[key] = round(spend[key] + rec.cost, 6)
    return spend


def usage(scope: Scope, override: Path | None, http_env: dict[str, str], *,
          want_remote: bool = True, want_local: bool = True, origin: str = "auto",
          want_extra: bool = False) -> dict[str, Any]:
    auth = opencode_auth(scope, override) if origin in ("auto", "tool") else {}
    sources = sorted({label for _, label in auth.values()})
    _, go_found = pick(opencode_go_creds(scope, override), origin, kind="api_key")
    console_entry, console_label = auth.get("opencode", ({}, ""))
    console = Console(console_entry, console_label, http_env) if console_entry.get("type") == "oauth" else None
    out: dict[str, Any] = {"tool": "opencode", "credentials": ", ".join(sources) or None, "providers": sorted(auth)}
    if want_remote:
        out["limits"] = (
            {name: provider_limits(name, entry, label, http_env) for name, (entry, label) in auth.items()}
            if auth else {"error": "no OpenCode login found (auth.json / opencode.db) — run `opencode auth login`"}
        )
        if go_found or console or "opencode-go" in auth:
            go = go_limits(go_found, http_env)
            if "error" in go and console and not console.expired():
                go = {**console.go_status(), "key_error": go["error"]}
            go["sources_found"] = [c.describe() for c in go_found]
            hermes = hermes_pool_status(scope, "opencode-go")
            if hermes:
                go["hermes_last_status"] = hermes
            out["opencode_go"] = go
    records = local_records(scope) if (want_local or want_extra) else []
    if want_extra:
        if console is None:
            zen: dict[str, Any] = {"error": NO_SIGN_IN}
        elif console.expired():
            zen = {"error": "Console sign-in expired — run `opencode` once (or `opencode auth login opencode`)"}
        else:
            zen = console.billing()
        out["extra_usage"] = {
            "zen_balance": zen,
            "go_extra_usage": "when a Go window is blocked and Extra Usage is on (Go page), requests draw from this Zen balance",
            "local_spend_this_month": local_spend(records),
        }
    if want_local:
        out["local_usage"] = aggregate(records)
    return out
