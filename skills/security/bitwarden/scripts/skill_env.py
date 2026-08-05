"""Bitwarden skill credentials."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from common.skill_env_export import SkillEnv


class BitwardenSkillEnv(SkillEnv):
    DEFAULT_SERVER = "https://vault.bitwarden.com"
    DEFAULT_SESSION_TTL = "15"
    required_keys = ("BW_CLIENTID", "BW_CLIENTSECRET")

    def __init__(self) -> None:
        super().__init__("bitwarden", Path(__file__))

    def apply_defaults(self, values: Mapping[str, str]) -> dict[str, str]:
        out = dict(values)
        out.setdefault("BW_SERVER", self.DEFAULT_SERVER)
        out.setdefault("BW_SESSION_TTL", self.DEFAULT_SESSION_TTL)
        return out

    def verify(self, values: dict[str, str]) -> dict[str, str]:
        # Deliberately non-fatal: `env` and `status` must stay usable while the
        # .env is still empty. Missing keys are reported by missing_keys().
        verified = dict(values)
        verified["BW_SERVER"] = values.get("BW_SERVER", self.DEFAULT_SERVER).rstrip("/")
        verified["BW_SESSION_TTL"] = values.get("BW_SESSION_TTL", self.DEFAULT_SESSION_TTL)
        return verified

    def missing_keys(self) -> list[str]:
        """Keys still needed by the configured auth method (empty when email-only)."""
        if self.email() and not (self.client_id() or self.client_secret()):
            return []
        return [key for key in self.required_keys if not self.env.get(key, "").strip()]

    def client_id(self) -> str:
        return self.env.get("BW_CLIENTID", "").strip()

    def client_secret(self) -> str:
        return self.env.get("BW_CLIENTSECRET", "").strip()

    def has_api_key(self) -> bool:
        return bool(self.client_id() and self.client_secret())

    def email(self) -> str:
        return self.env.get("BW_EMAIL", "").strip()

    def auth_method(self) -> str:
        """`apikey` (2FA-proof), `password` (email + master password), or `none`."""
        if self.has_api_key():
            return "apikey"
        if self.email():
            return "password"
        return "none"

    def upsert_env_vars(self, updates: Mapping[str, str], **kwargs: Any) -> tuple[Path, str]:
        # The shared helper writes with the default umask; this file holds secrets.
        path, exports = super().upsert_env_vars(updates, **kwargs)
        path.chmod(0o600)
        self.sav_env()
        return path, exports

    def server(self) -> str:
        return self.env["BW_SERVER"]

    def node_extra_ca_certs(self) -> str:
        return self.env.get("NODE_EXTRA_CA_CERTS", "").strip()

    def keychain_service(self) -> str:
        # Legacy name kept readable: it used to hold the master password, not a session.
        return (
            self.env.get("BW_KEYCHAIN_SERVICE")
            or self.env.get("BW_PASSWORD_KEYCHAIN_SERVICE", "")
        ).strip()

    def keychain_account(self) -> str:
        return (
            self.env.get("BW_KEYCHAIN_ACCOUNT")
            or self.env.get("BW_PASSWORD_KEYCHAIN_ACCOUNT", "")
        ).strip()

    def trust_path_binary(self) -> bool:
        return self.env.get("BW_TRUST_PATH_BINARY", "").strip().lower() in {"1", "true", "yes"}

    def session_ttl_minutes(self) -> int:
        try:
            return max(1, int(self.env["BW_SESSION_TTL"]))
        except (TypeError, ValueError):
            return int(self.DEFAULT_SESSION_TTL)

    def workspace(self) -> Path:
        return self.env_cred().workspace


ENV = BitwardenSkillEnv()
