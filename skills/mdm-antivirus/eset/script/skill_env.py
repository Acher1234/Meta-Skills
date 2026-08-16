"""ESET skill credentials and regional gateway URLs."""

from __future__ import annotations

import sys
from pathlib import Path

from common.skill_env_export import SkillEnv

TOKEN_PATH = "/oauth/token"

KNOWN_REGIONS = {
    "eu": "https://eu.business-account.iam.eset.systems",
    "de": "https://de.business-account.iam.eset.systems",
    "us": "https://us.business-account.iam.eset.systems",
    "ca": "https://ca.business-account.iam.eset.systems",
    "jpn": "https://jpn.business-account.iam.eset.systems",
}


class ConfigError(Exception):
    pass


class EsetSkillEnv(SkillEnv):
    required_keys = ("ESET_URL", "ESET_USERNAME", "ESET_PASSWORD")

    def __init__(self) -> None:
        super().__init__("eset", Path(__file__))

    def verify(self, values: dict[str, str]) -> dict[str, str]:
        return self.verify_required_keys(values)

    def sav_env(self) -> None:
        self.env = self.read_env()
        self._config: dict | None = None
        self.access_token_override: str | None = None

    def config(self) -> dict:
        if self._config is None:
            self._config = self.resolve(require_credentials=False)
        return self._config

    def resolve(self, *, require_credentials: bool = True) -> dict:
        return _resolve_config(self.read_env(), require_credentials)

    def gateway_url(self, key: str) -> str:
        return self.config()[key]

    def token_url(self) -> str:
        return self.config()["token_url"]

    def username(self) -> str | None:
        return self.config().get("username") or None

    def password(self) -> str | None:
        return self.config().get("password") or None


def normalize_base_url(raw: str) -> str:
    if not raw:
        raise ConfigError("ESET_URL is not set")
    value = raw.strip()
    if value.lower() in KNOWN_REGIONS:
        return KNOWN_REGIONS[value.lower()]
    value = value.rstrip("/")
    if value.endswith(TOKEN_PATH):
        value = value[: -len(TOKEN_PATH)].rstrip("/")
    return value


def _region_from_base(base_url: str) -> str:
    host = base_url.split("://", 1)[-1]
    return host.split(".", 1)[0] if host else ""


def _service_url(
    base_url: str, service_host: str, override_key: str, values: dict[str, str]
) -> str:
    override = values.get(override_key, "").strip()
    if override:
        return override.rstrip("/")
    region = _region_from_base(base_url)
    if not region:
        raise ConfigError(f"Cannot resolve {service_host} URL; set {override_key}")
    return f"https://{region}.{service_host}.eset.systems"


def _resolve_config(values: dict[str, str], require_credentials: bool = True) -> dict:
    base = normalize_base_url(values.get("ESET_URL", ""))
    username = values.get("ESET_USERNAME", "").strip()
    password = values.get("ESET_PASSWORD", "")

    required = [("ESET_URL", base)]
    if require_credentials:
        required += [("ESET_USERNAME", username), ("ESET_PASSWORD", password)]
    missing = [name for name, val in required if not val]
    if missing:
        raise ConfigError(
            f"Missing in {ENV.display_env_path()}: {', '.join(missing)}. "
            f"Copy .env.example there and fill it in."
        )

    return {
        "base_url": base,
        "token_url": base.rstrip("/") + TOKEN_PATH,
        "api_url": _service_url(base, "automation", "ESET_API_URL", values),
        "automation_url": _service_url(base, "automation", "ESET_AUTOMATION_URL", values),
        "app_url": _service_url(
            base, "application-management", "ESET_APP_URL", values
        ),
        "asset_url": _service_url(base, "automation", "ESET_ASSET_URL", values),
        "policy_url": _service_url(base, "automation", "ESET_POLICY_URL", values),
        "incident_url": _service_url(
            base, "incident-management", "ESET_INCIDENT_URL", values
        ),
        "patch_url": _service_url(base, "patch-management", "ESET_PATCH_URL", values),
        "username": username,
        "password": password,
        "env_path": str(ENV.env_path()),
        "env_values": values,
    }


ENV = EsetSkillEnv()


if __name__ == "__main__":
    from common.skill_env_export import env_load_main

    raise SystemExit(env_load_main(ENV, sys.argv[1:]))
