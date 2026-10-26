"""Token usage records from local logs, aggregated per period, and limit-window helpers."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

TOKEN_KEYS = ("input", "output", "cache_read", "cache_write", "reasoning")


@dataclass
class Record:
    ts: datetime
    model: str
    tokens: dict[str, int] = field(default_factory=dict)
    cost: float = 0.0


def parse_ts(value: Any) -> datetime | None:
    """ISO string, epoch seconds or epoch milliseconds → aware UTC datetime."""
    if value is None or value == "":
        return None
    try:
        if isinstance(value, (int, float)):
            seconds = value / 1000 if value > 1e11 else value
            return datetime.fromtimestamp(seconds, tz=timezone.utc)
        text = str(value).replace("Z", "+00:00")
        dt = datetime.fromisoformat(text)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except (ValueError, OSError, OverflowError):
        return None


def _periods(now: datetime) -> dict[str, datetime]:
    local = now.astimezone()
    day = local.replace(hour=0, minute=0, second=0, microsecond=0)
    return {
        "last_5h": now - timedelta(hours=5),
        "today": day,
        "last_7d": now - timedelta(days=7),
        "this_week": day - timedelta(days=local.weekday()),
        "this_month": day.replace(day=1),
        "last_30d": now - timedelta(days=30),
    }


def _empty() -> dict[str, Any]:
    return {"messages": 0, **{key: 0 for key in TOKEN_KEYS}, "total": 0, "cost_usd": 0.0}


def _add(bucket: dict[str, Any], rec: Record) -> None:
    bucket["messages"] += 1
    for key in TOKEN_KEYS:
        value = int(rec.tokens.get(key, 0) or 0)
        bucket[key] += value
        if key != "reasoning":
            bucket["total"] += value
    bucket["cost_usd"] = round(bucket["cost_usd"] + (rec.cost or 0.0), 6)


def aggregate(records: list[Record], now: datetime | None = None) -> dict[str, Any]:
    """Totals per period plus a per-model split for the current month."""
    now = now or datetime.now(timezone.utc)
    starts = _periods(now)
    totals = {name: _empty() for name in starts}
    by_model: dict[str, dict[str, Any]] = defaultdict(_empty)
    for rec in records:
        for name, start in starts.items():
            if rec.ts >= start:
                _add(totals[name], rec)
        if rec.ts >= starts["this_month"]:
            _add(by_model[rec.model or "unknown"], rec)
    last = max((rec.ts for rec in records), default=None)
    return {
        "periods": totals,
        "this_month_by_model": dict(sorted(by_model.items(), key=lambda kv: -kv[1]["total"])),
        "last_activity": last.isoformat() if last else None,
    }


def humanize(seconds: float) -> str:
    seconds = max(0, int(seconds))
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes = rem // 60
    parts = [f"{days}d"] if days else []
    if hours or days:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    return " ".join(parts)


def window(name: str, used_percent: Any, resets_at: Any, **extra: Any) -> dict[str, Any]:
    """Normalized limit window: used / remaining percent and time until reset."""
    used = float(used_percent or 0)
    reset = parse_ts(resets_at)
    out: dict[str, Any] = {
        "window": name,
        "used_percent": round(used, 1),
        "remaining_percent": round(max(0.0, 100.0 - used), 1),
        "resets_at": reset.astimezone().isoformat() if reset else None,
        "resets_in": humanize((reset - datetime.now(timezone.utc)).total_seconds()) if reset else None,
    }
    out.update({key: value for key, value in extra.items() if value is not None})
    return out
