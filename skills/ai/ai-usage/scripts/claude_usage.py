"""Claude Code: plan limits (OAuth usage API) + token usage from local session logs."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from common.http import HttpClient, HttpError
from locate import Scope, claude_dirs
from sources import Cred, claude_creds, pick
from stats import Record, aggregate, parse_ts, window

USAGE_URL = "https://api.anthropic.com/api/oauth/usage"
WINDOW_NAMES = {
    "five_hour": "session_5h",
    "seven_day": "week_7d",
    "seven_day_opus": "week_7d_opus",
    "seven_day_sonnet": "week_7d_sonnet",
    "seven_day_oauth_apps": "week_7d_oauth_apps",
}
MAX_LOG_AGE = 31 * 86400


def fetch_limits(access_token: str, http_env: dict[str, str]) -> dict[str, Any]:
    """Call the OAuth usage endpoint and normalize every limit window."""
    client = HttpClient(
        environ=http_env,
        user_agent="claude-code/2.0 (ai-usage skill)",
        headers={"Authorization": f"Bearer {access_token}", "anthropic-beta": "oauth-2025-04-20"},
        timeout=20,
    )
    data = client.get(USAGE_URL)
    windows: list[dict[str, Any]] = []
    for key, value in data.items():
        if isinstance(value, dict) and value.get("utilization") is not None and "resets_at" in value:
            windows.append(window(WINDOW_NAMES.get(key, key), value["utilization"], value.get("resets_at")))
    seen = {w["resets_at"] for w in windows}
    for limit in data.get("limits") or []:
        if limit.get("kind") == "session" and any(w["window"] == "session_5h" for w in windows):
            continue
        reset = parse_ts(limit.get("resets_at"))
        if reset and reset.astimezone().isoformat() in seen:
            continue
        model = ((limit.get("scope") or {}).get("model") or {}).get("display_name")
        name = "_".join(p for p in (limit.get("group") or limit.get("kind"), model) if p)
        windows.append(window(name, limit.get("percent"), limit.get("resets_at"), active=limit.get("is_active")))
    extra = data.get("extra_usage") or {}
    spend = data.get("spend") or {}
    used = (spend.get("used") or {})
    return {
        "windows": windows,
        "extra_usage": {
            "enabled": bool(extra.get("is_enabled")),
            "monthly_limit": extra.get("monthly_limit"),
            "used_credits": extra.get("used_credits"),
            "used_percent": extra.get("utilization"),
            "currency": extra.get("currency") or used.get("currency"),
            "spend_used": used.get("amount_minor") / 10 ** used.get("exponent", 2) if used.get("amount_minor") is not None else None,
            "spend_limit_reached": extra.get("spend_limit_reached"),
            "disabled_reason": extra.get("disabled_reason") or spend.get("disabled_reason"),
        },
    }


def remote(cred: Cred | None, http_env: dict[str, str], tool: str = "claude") -> dict[str, Any]:
    """Shared with OpenCode's `anthropic` OAuth entry."""
    if cred is None:
        return {"error": f"no Claude OAuth token found — log in with `{tool}` (Claude Code /login, Hermes or OpenClaw)"}
    if cred.expired():
        return {"error": f"OAuth token expired ({cred.source}) — run `{tool}` once to refresh it, then retry"}
    try:
        return fetch_limits(cred.token, http_env)
    except HttpError as exc:
        return {"error": f"usage API HTTP {exc.status}", "detail": str(exc)[:300]}
    except Exception as exc:  # network / proxy errors must not hide local stats
        return {"error": str(exc)[:300]}


def _log_files(scope: Scope) -> list[Path]:
    cutoff = time.time() - MAX_LOG_AGE
    files: list[Path] = []
    for base in dict.fromkeys(claude_dirs(Scope(True, None)) + claude_dirs(scope)):
        projects = base / "projects"
        if projects.is_dir():
            files += [p for p in projects.rglob("*.jsonl") if p.stat().st_mtime >= cutoff]
    return files


def local_records(scope: Scope) -> list[Record]:
    """Assistant messages from `projects/**/*.jsonl` (deduped; filtered to the project if not global)."""
    project = None if scope.is_global or scope.project is None else str(scope.project)
    seen: set[str] = set()
    records: list[Record] = []
    for path in _log_files(scope):
        with path.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if '"usage"' not in line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                msg = entry.get("message") or {}
                usage = msg.get("usage")
                if not usage or msg.get("model") == "<synthetic>":
                    continue
                if project and not str(entry.get("cwd", "")).startswith(project):
                    continue
                key = f"{msg.get('id')}:{entry.get('requestId')}"
                if key in seen:
                    continue
                seen.add(key)
                ts = parse_ts(entry.get("timestamp"))
                if ts is None:
                    continue
                records.append(Record(ts, msg.get("model", ""), {
                    "input": usage.get("input_tokens", 0),
                    "output": usage.get("output_tokens", 0),
                    "cache_read": usage.get("cache_read_input_tokens", 0),
                    "cache_write": usage.get("cache_creation_input_tokens", 0),
                    "reasoning": (usage.get("output_tokens_details") or {}).get("thinking_tokens", 0),
                }))
    return records


def usage(scope: Scope, override: Path | None, http_env: dict[str, str], *,
          want_remote: bool = True, want_local: bool = True, origin: str = "auto") -> dict[str, Any]:
    cred, found = pick(claude_creds(scope, override), origin)
    out: dict[str, Any] = {
        "tool": "claude",
        "credentials": cred.source if cred else None,
        "credentials_origin": cred.origin if cred else None,
        "plan": cred.meta.get("plan") if cred else None,
        "rate_limit_tier": cred.meta.get("rate_limit_tier") if cred else None,
        "sources_found": [c.describe() for c in found],
    }
    if want_remote:
        out["limits"] = remote(cred, http_env)
    if want_local:
        out["local_usage"] = aggregate(local_records(scope))
    return out
