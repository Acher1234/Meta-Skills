"""ai-usage skill settings (all keys optional)."""

from __future__ import annotations

import os
from pathlib import Path

from common.http.skill_env import HttpSkillEnv

OPTIONAL_KEYS = ("CLAUDE_CREDENTIALS_FILE", "CODEX_AUTH_FILE", "OPENCODE_AUTH_FILE")


class AiUsageSkillEnv(HttpSkillEnv):
    def __init__(self) -> None:
        super().__init__("ai-usage", Path(__file__))

    def verify(self, values: dict[str, str]) -> dict[str, str]:
        own = {key: values[key].strip() for key in OPTIONAL_KEYS if values.get(key, "").strip()}
        return {**super().verify(values), **own}

    def override(self, key: str) -> Path | None:
        raw = self.env.get(key) or os.environ.get(key, "").strip()
        return Path(raw).expanduser() if raw else None


ENV = AiUsageSkillEnv()

