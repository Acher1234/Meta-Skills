"""Every place a provider token can live: the tool's own files, Hermes, OpenClaw, process env.

Order: tool files (project first unless global) → Hermes → OpenClaw → environment.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from common.skill_env.skill_cred import display_path
from common.skill_env.skill_env_export import parse_env_file
from locate import (
    Scope,
    claude_dirs,
    claude_keychain_credentials,
    codex_dirs,
    jwt_claims,
    opencode_auth_files,
    read_json,
)
from stats import parse_ts

ORIGINS = ("tool", "hermes", "openclaw", "env")
CLAUDE_ENV_KEYS = ("CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_TOKEN", "ANTHROPIC_API_KEY")
OPENCODE_GO_ENV_KEYS = ("OPENCODE_GO_API_KEY", "OPENCODE_API_KEY")


@dataclass
class Cred:
    origin: str
    source: str
    token: str
    kind: str = "oauth"
    expires_at: float | None = None
    account: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)

    def expired(self) -> bool:
        return self.expires_at is not None and self.expires_at < time.time()

    def describe(self) -> dict[str, Any]:
        out: dict[str, Any] = {"origin": self.origin, "source": self.source, "kind": self.kind}
        if self.expired():
            out["expired"] = True
        return out


def _seconds(value: Any) -> float | None:
    if not value:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number / 1000 if number > 1e11 else number


def _jwt_exp(token: str) -> float | None:
    return _seconds(jwt_claims(token).get("exp"))


def _safe_json(path: Path) -> dict[str, Any]:
    try:
        return read_json(path) if path.is_file() else {}
    except (OSError, ValueError):
        return {}


def _label(path: Path, where: str = "") -> str:
    return f"{display_path(path)}{f' ({where})' if where else ''}"


def hermes_homes(scope: Scope) -> list[Path]:
    homes = []
    if os.environ.get("HERMES_HOME", "").strip():
        homes.append(Path(os.environ["HERMES_HOME"]).expanduser())
    homes += [root / ".hermes" for root in scope.roots()]
    return [h for h in dict.fromkeys(homes) if h.is_dir()]


def openclaw_homes(scope: Scope) -> list[Path]:
    homes = []
    if os.environ.get("OPENCLAW_STATE_DIR", "").strip():
        homes.append(Path(os.environ["OPENCLAW_STATE_DIR"]).expanduser())
    homes += [root / ".openclaw" for root in scope.roots()]
    return [h for h in dict.fromkeys(homes) if h.is_dir()]


def _hermes_pool(home: Path, provider: str) -> list[tuple[str, dict[str, Any]]]:
    path = home / "auth.json"
    entries = (_safe_json(path).get("credential_pool") or {}).get(provider) or []
    return [(_label(path, f"credential_pool.{provider}[{i}]"), e) for i, e in enumerate(entries) if isinstance(e, dict)]


def hermes_pool_status(scope: Scope, provider: str) -> list[dict[str, Any]]:
    """Hermes' last error per pooled key (e.g. 429 + reset) — no secret, only status."""
    keys = ("label", "source", "last_status", "last_error_code", "last_error_reason",
            "last_error_message", "last_error_reset_at", "secret_fingerprint")
    out = []
    for home in hermes_homes(scope):
        for label, entry in _hermes_pool(home, provider):
            status = {k: entry[k] for k in keys if entry.get(k) is not None}
            if status.get("last_status"):
                reset = parse_ts(status.get("last_error_reset_at"))
                if reset:
                    status["last_error_reset_at"] = reset.astimezone().isoformat()
                status["where"] = label
                out.append(status)
    return out


def _openclaw_profiles(home: Path) -> list[tuple[str, dict[str, Any]]]:
    agents = home / "agents"
    files = sorted(agents.glob("*/agent/auth-profiles.json"), key=lambda p: p.parts[-3] != "main") if agents.is_dir() else []
    out = []
    for path in files:
        for name, profile in (_safe_json(path).get("profiles") or {}).items():
            if isinstance(profile, dict):
                out.append((_label(path, name), {"_id": name, **profile}))
    return out


def _openclaw_token(profile: dict[str, Any]) -> str:
    return profile.get("access") or profile.get("token") or profile.get("key") or ""


def _env_files(homes: list[Path]) -> list[Path]:
    return [h / ".env" for h in homes if (h / ".env").is_file()]


def _from_env_files(origin: str, files: list[Path], keys: tuple[str, ...], kind_of) -> list[Cred]:
    out = []
    for path in files:
        values = parse_env_file(path)
        for key in keys:
            if values.get(key, "").strip():
                out.append(Cred(origin, _label(path, key), values[key].strip(), kind_of(values[key].strip())))
    return out


def _from_process_env(keys: tuple[str, ...], kind_of) -> list[Cred]:
    return [Cred("env", f"${key}", os.environ[key].strip(), kind_of(os.environ[key].strip()))
            for key in keys if os.environ.get(key, "").strip()]


def _anthropic_kind(token: str) -> str:
    return "api_key" if token.startswith("sk-ant-api") else "oauth"


def _provider_of(profile: dict[str, Any]) -> str:
    return str(profile.get("provider") or profile["_id"].split(":")[0])


def claude_creds(scope: Scope, override: Path | None) -> list[Cred]:
    creds: list[Cred] = []
    for path in ([override] if override else []) + [d / ".credentials.json" for d in claude_dirs(scope)]:
        oauth = _safe_json(path).get("claudeAiOauth") or {}
        if oauth.get("accessToken"):
            creds.append(Cred("tool", _label(path), oauth["accessToken"], expires_at=_seconds(oauth.get("expiresAt")),
                              meta={"plan": oauth.get("subscriptionType"), "rate_limit_tier": oauth.get("rateLimitTier")}))
    oauth = (claude_keychain_credentials() or {}).get("claudeAiOauth") or {}
    if oauth.get("accessToken"):
        creds.append(Cred("tool", "macOS keychain (Claude Code-credentials)", oauth["accessToken"],
                          expires_at=_seconds(oauth.get("expiresAt")), meta={"plan": oauth.get("subscriptionType")}))
    homes = hermes_homes(scope)
    for home in homes:
        for label, entry in _hermes_pool(home, "anthropic"):
            if entry.get("access_token") and entry.get("last_status") != "dead":
                creds.append(Cred("hermes", label, entry["access_token"], entry.get("auth_type") or _anthropic_kind(entry["access_token"]),
                                  expires_at=_seconds(entry.get("expires_at_ms") or entry.get("expires_at"))))
    creds += _from_env_files("hermes", _env_files(homes), CLAUDE_ENV_KEYS, _anthropic_kind)
    claw = openclaw_homes(scope)
    for home in claw:
        for label, profile in _openclaw_profiles(home):
            if _provider_of(profile) == "anthropic" and _openclaw_token(profile):
                token = _openclaw_token(profile)
                kind = "api_key" if profile.get("type") == "api_key" else _anthropic_kind(token)
                creds.append(Cred("openclaw", label, token, kind, expires_at=_seconds(profile.get("expires"))))
    creds += _from_env_files("openclaw", _env_files(claw), CLAUDE_ENV_KEYS, _anthropic_kind)
    creds += _from_process_env(CLAUDE_ENV_KEYS, _anthropic_kind)
    return creds


def codex_creds(scope: Scope, override: Path | None) -> list[Cred]:
    creds: list[Cred] = []
    for path in ([override] if override else []) + [d / "auth.json" for d in codex_dirs(scope)]:
        auth = _safe_json(path)
        tokens = auth.get("tokens") or {}
        if tokens.get("access_token"):
            creds.append(Cred("tool", _label(path), tokens["access_token"], expires_at=_jwt_exp(tokens["access_token"]),
                              account=tokens.get("account_id"), meta={"id_token": tokens.get("id_token")}))
        elif auth.get("OPENAI_API_KEY"):
            creds.append(Cred("tool", _label(path, "OPENAI_API_KEY"), auth["OPENAI_API_KEY"], "api_key"))
    for home in hermes_homes(scope):
        path = home / "auth.json"
        tokens = ((_safe_json(path).get("providers") or {}).get("openai-codex") or {}).get("tokens") or {}
        if tokens.get("access_token"):
            creds.append(Cred("hermes", _label(path, "providers.openai-codex"), tokens["access_token"],
                              expires_at=_jwt_exp(tokens["access_token"]), account=tokens.get("account_id")))
        for label, entry in _hermes_pool(home, "openai-codex"):
            if entry.get("access_token") and entry.get("last_status") != "dead":
                creds.append(Cred("hermes", label, entry["access_token"], expires_at=_jwt_exp(entry["access_token"])))
    for home in openclaw_homes(scope):
        for label, profile in _openclaw_profiles(home):
            if _provider_of(profile) in {"openai-codex", "codex"} and _openclaw_token(profile):
                creds.append(Cred("openclaw", label, _openclaw_token(profile), expires_at=_seconds(profile.get("expires")),
                                  account=profile.get("accountId")))
    return creds


def opencode_go_creds(scope: Scope, override: Path | None) -> list[Cred]:
    """OpenCode Go keys (`opencode-go`, or the shared Zen `opencode` key)."""
    creds: list[Cred] = []
    for path in ([override] if override else []) + opencode_auth_files(scope):
        auth = _safe_json(path)
        for provider in ("opencode-go", "opencode"):
            entry = auth.get(provider) or {}
            token = entry.get("key") or entry.get("access")
            if token:
                creds.append(Cred("tool", _label(path, provider), token, "api_key"))
    homes = hermes_homes(scope)
    for home in homes:
        for label, entry in _hermes_pool(home, "opencode-go"):
            if entry.get("access_token"):
                creds.append(Cred("hermes", label, entry["access_token"], "api_key"))
    creds += _from_env_files("hermes", _env_files(homes), OPENCODE_GO_ENV_KEYS, lambda _: "api_key")
    claw = openclaw_homes(scope)
    for home in claw:
        for label, profile in _openclaw_profiles(home):
            if _provider_of(profile) in {"opencode-go", "opencode"} and _openclaw_token(profile):
                creds.append(Cred("openclaw", label, _openclaw_token(profile), "api_key"))
    creds += _from_env_files("openclaw", _env_files(claw), OPENCODE_GO_ENV_KEYS, lambda _: "api_key")
    creds += _from_process_env(OPENCODE_GO_ENV_KEYS, lambda _: "api_key")
    return _dedupe(creds)


def _dedupe(creds: list[Cred]) -> list[Cred]:
    seen: set[str] = set()
    out = []
    for cred in creds:
        if cred.token not in seen:
            seen.add(cred.token)
            out.append(cred)
    return out


def pick(creds: list[Cred], origin: str = "auto", kind: str = "oauth") -> tuple[Cred | None, list[Cred]]:
    """First usable credential of *kind* (non-expired preferred), filtered by origin; plus all candidates."""
    pool = _dedupe([c for c in creds if origin in ("auto", c.origin)])
    usable = [c for c in pool if c.kind == kind]
    fresh = [c for c in usable if not c.expired()]
    return (fresh or usable or [None])[0], pool
