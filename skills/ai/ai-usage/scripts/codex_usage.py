"""Codex CLI: ChatGPT plan limits (wham usage API) + token usage from local rollout logs."""

from __future__ import annotations

import json
import time
from datetime import timedelta
from pathlib import Path
from typing import Any

from common.http import HttpClient, HttpError
from locate import Scope, codex_dirs, jwt_claims
from sources import Cred, codex_creds, pick
from stats import Record, aggregate, parse_ts, window

USAGE_URL = "https://chatgpt.com/backend-api/wham/usage"
MAX_LOG_AGE = 31 * 86400


def window_name(seconds: Any) -> str:
    seconds = int(seconds or 0)
    if seconds == 5 * 3600:
        return "session_5h"
    if seconds == 7 * 86400:
        return "week_7d"
    if seconds and seconds % 86400 == 0:
        return f"{seconds // 86400}d"
    return f"{round(seconds / 3600)}h" if seconds else "window"


def account_id(cred: Cred) -> str | None:
    if cred.account:
        return cred.account
    for token in (cred.meta.get("id_token") or "", cred.token):
        found = (jwt_claims(token).get("https://api.openai.com/auth") or {}).get("chatgpt_account_id")
        if found:
            return found
    return None


def fetch_limits(access_token: str, account: str | None, http_env: dict[str, str]) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {access_token}"}
    if account:
        headers["ChatGPT-Account-Id"] = account
    client = HttpClient(environ=http_env, user_agent="codex_cli_rs (ai-usage skill)", headers=headers, timeout=20)
    data = client.get(USAGE_URL)
    limits = data.get("rate_limit") or {}
    windows = []
    for key in ("primary_window", "secondary_window"):
        w = limits.get(key)
        if not w:
            continue
        reset = w.get("reset_at") or (time.time() + w["reset_after_seconds"] if w.get("reset_after_seconds") is not None else None)
        windows.append(window(window_name(w.get("limit_window_seconds")), w.get("used_percent"), reset))
    return {
        "plan": data.get("plan_type"),
        "allowed": limits.get("allowed"),
        "limit_reached": limits.get("limit_reached"),
        "windows": windows,
        "extra_usage": {"credits": data.get("credits")},
    }


def remote(cred: Cred | None, http_env: dict[str, str], tool: str = "codex") -> dict[str, Any]:
    """Shared with OpenCode's `openai` OAuth entry."""
    if cred is None:
        return {"error": "no ChatGPT OAuth token — log in with `codex login`, Hermes or OpenClaw (API keys have no plan limits)"}
    if cred.expired():
        return {"error": f"OAuth token expired ({cred.source}) — run `{tool}` once to refresh it, then retry"}
    try:
        return fetch_limits(cred.token, account_id(cred), http_env)
    except HttpError as exc:
        return {"error": f"usage API HTTP {exc.status}", "detail": str(exc)[:300]}
    except Exception as exc:  # network / proxy errors must not hide local stats
        return {"error": str(exc)[:300]}


def _log_files(scope: Scope) -> list[Path]:
    cutoff = time.time() - MAX_LOG_AGE
    files: list[Path] = []
    for base in dict.fromkeys(codex_dirs(Scope(True, None)) + codex_dirs(scope)):
        for sub in ("sessions", "archived_sessions"):
            root = base / sub
            if root.is_dir():
                files += [p for p in root.rglob("*.jsonl") if p.stat().st_mtime >= cutoff]
    return files


def _snapshot_window(raw: dict[str, Any], at: float) -> dict[str, Any]:
    reset = raw.get("resets_at")
    if reset is None and raw.get("resets_in_seconds") is not None:
        reset = at + raw["resets_in_seconds"]
    return window(window_name((raw.get("window_minutes") or 0) * 60), raw.get("used_percent"), reset)


def local_scan(scope: Scope) -> tuple[list[Record], dict[str, Any] | None]:
    """Token records + the newest rate-limit snapshot logged by Codex (offline fallback)."""
    project = None if scope.is_global or scope.project is None else str(scope.project)
    records: list[Record] = []
    snapshot: tuple[float, dict[str, Any]] | None = None
    for path in _log_files(scope):
        cwd, model, prev_total = "", "", None
        with path.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                payload = entry.get("payload") or {}
                kind = entry.get("type")
                if kind == "session_meta":
                    cwd = payload.get("cwd", "")
                elif kind == "turn_context":
                    model = payload.get("model", model)
                    cwd = payload.get("cwd", cwd)
                if kind != "event_msg" or payload.get("type") != "token_count":
                    continue
                ts = parse_ts(entry.get("timestamp"))
                if ts is None or (project and not cwd.startswith(project)):
                    continue
                if payload.get("rate_limits") and (snapshot is None or ts.timestamp() > snapshot[0]):
                    snapshot = (ts.timestamp(), payload["rate_limits"])
                info = payload.get("info") or {}
                total, last = info.get("total_token_usage"), info.get("last_token_usage")
                if not last or total == prev_total:
                    continue
                prev_total = total
                cached = last.get("cached_input_tokens", 0) or 0
                records.append(Record(ts, model, {
                    "input": (last.get("input_tokens", 0) or 0) - cached,
                    "output": last.get("output_tokens", 0),
                    "cache_read": cached,
                    "reasoning": last.get("reasoning_output_tokens", 0),
                }))
    if snapshot is None:
        return records, None
    at, raw = snapshot
    windows = [_snapshot_window(raw[k], at) for k in ("primary", "secondary") if raw.get(k)]
    as_of = parse_ts(at)
    return records, {"as_of": as_of.astimezone().isoformat() if as_of else None,
                     "stale": time.time() - at > timedelta(hours=1).total_seconds(),
                     "windows": windows}


def usage(scope: Scope, override: Path | None, http_env: dict[str, str], *,
          want_remote: bool = True, want_local: bool = True, origin: str = "auto",
          want_extra: bool = False) -> dict[str, Any]:
    cred, found = pick(codex_creds(scope, override), origin)
    out: dict[str, Any] = {
        "tool": "codex",
        "credentials": cred.source if cred else None,
        "credentials_origin": cred.origin if cred else None,
        "auth_mode": "chatgpt" if cred else ("api_key" if found else None),
        "sources_found": [c.describe() for c in found],
    }
    if want_remote:
        out["limits"] = remote(cred, http_env)
    if want_local:
        records, snapshot = local_scan(scope)
        out["local_usage"] = aggregate(records)
        if snapshot:
            out["last_logged_limits"] = snapshot
    return out
