"""OpenCode Console API (sign-in from `opencode auth login opencode`): Zen balance, budget, Go meters.

There is no API-key route for the balance (anomalyco/opencode#10448); the Console sign-in is the
only way. Amounts come in micro-cents: 1 USD = 100 000 000.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from common.http import HttpClient, HttpError
from stats import window

CONSOLE_URL = "https://opencode.ai/console"
UNITS_PER_USD = 100_000_000
GO_METERS = {"fiveHour": "rolling_5h", "week": "week", "month": "month"}
NO_SIGN_IN = ("Zen balance / Go extra usage need the OpenCode Console sign-in "
              "(`opencode auth login opencode`) — no API-key endpoint exists yet (opencode#10448)")


def _usd(value: Any) -> float | None:
    try:
        return round(float(value) / UNITS_PER_USD, 4)
    except (TypeError, ValueError):
        return None


class Console:
    def __init__(self, entry: dict[str, Any], source: str, http_env: dict[str, str]) -> None:
        self.source = source
        self.expires = entry.get("expires")
        headers = {"Authorization": f"Bearer {entry.get('access', '')}", "Accept": "application/json"}
        if entry.get("orgID"):
            headers["x-org-id"] = entry["orgID"]
        self.account_id = entry.get("accountID")
        self.client = HttpClient(str(entry.get("server") or CONSOLE_URL), environ=http_env,
                                 user_agent="ai-usage-skill/1.0", headers=headers, timeout=15)

    def expired(self) -> bool:
        return bool(self.expires) and self.expires / 1000 < time.time()

    def get(self, route: str) -> Any:
        # The Console answers an expired session with a redirect to an HTML login page.
        return self.client.get(f"api/{route}", expect_json=True)

    def go_status(self) -> dict[str, Any]:
        """Go meters for the signed-in member (works without a Go API key)."""
        try:
            data = self.get("go/status") or {}
        except HttpError as exc:
            note = "no Go subscription on this Console account" if exc.status == 404 else f"Console HTTP {exc.status}"
            return {"error": note}
        access = data.get("access") or {}
        meters = access.get("meters") or {}
        windows = []
        for key, name in GO_METERS.items():
            meter = meters.get(key) or {}
            limit, used = _usd(meter.get("limitMicroCents")), _usd(meter.get("usedMicroCents"))
            if limit is None or used is None:
                continue
            percent = (100.0 if used > 0 else 0.0) if limit == 0 else min(100.0, used / limit * 100)
            windows.append(window(name, percent, meter.get("resetsAt") or access.get("endsAt"),
                                  status="rate-limited" if percent >= 100 else "ok",
                                  used_usd=used, limit_usd=limit))
        if not access:
            return {"error": "OpenCode Go subscription is not active"}
        blocked = [w["window"] for w in windows if w.get("status") != "ok"]
        return {"windows": windows, "limit_reached": bool(blocked), "blocked_by": blocked or None,
                "credentials": f"{self.source} (Console sign-in)"}

    def billing(self) -> dict[str, Any]:
        """Zen pay-as-you-go balance (also what Go extra usage draws from), limit, auto-reload, month spend."""
        out: dict[str, Any] = {"source": f"{self.source} (Console sign-in)"}
        errors = []
        try:
            out["balance_usd"] = _usd((self.get("billing/status") or {}).get("balanceMicroCents"))
        except HttpError as exc:
            return {"error": f"Console billing/status HTTP {exc.status} — sign in again: `opencode auth login opencode`"}
        try:
            account = self.get("billing/account") or {}
            out["monthly_limit_usd"] = _usd(account.get("creditLimitMicroCents"))
        except HttpError as exc:
            errors.append(f"billing/account HTTP {exc.status}")
        try:
            reload = self.get("billing/auto-recharge") or {}
            out["auto_reload"] = {"enabled": reload.get("enabled"), "amount_usd": reload.get("rechargeAmountDollars"),
                                  "when_below_usd": reload.get("thresholdDollars")}
        except HttpError as exc:
            errors.append(f"billing/auto-recharge HTTP {exc.status}")
        try:
            month = datetime.now(timezone.utc).strftime("%Y-%m")
            days = self.get("usage/cost-by-day") or []
            spent = sum(float(d.get("totalCostMicroCents") or 0) for d in days
                        if str(d.get("date", "")).startswith(month))
            out["month_spent_usd"] = round(spent / UNITS_PER_USD, 4)
        except (HttpError, TypeError, ValueError) as exc:
            errors.append(f"usage/cost-by-day: {exc}"[:120])
        limit, spent = out.get("monthly_limit_usd"), out.get("month_spent_usd")
        if limit and spent is not None:
            out["month_used_percent"] = round(spent / limit * 100, 1)
            out["month_remaining_usd"] = round(max(0.0, limit - spent), 4)
        if errors:
            out["errors"] = errors
        return out
