"""Folder-crypt skill credentials (optional FOLDER + PASSWORD)."""

from __future__ import annotations

from pathlib import Path

from common.skill_env_export import SkillEnv

OPTIONAL_KEYS = ("FOLDER", "PASSWORD")


def split_folders(raw: str | None) -> list[str]:
    """Split a comma-separated FOLDER value. Drop empty segments."""
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


class FolderCryptSkillEnv(SkillEnv):
    required_keys = ()

    def __init__(self) -> None:
        super().__init__("folder-crypt", Path(__file__))

    def verify(self, values: dict[str, str]) -> dict[str, str]:
        # Both keys are optional — encrypt/decrypt prompt or take CLI args when absent.
        return {
            key: values[key].strip()
            for key in OPTIONAL_KEYS
            if values.get(key, "").strip()
        }

    def folders(self) -> list[str]:
        return split_folders(self.env.get("FOLDER", ""))

    def folder(self) -> str | None:
        items = self.folders()
        return items[0] if items else None

    def password(self) -> str | None:
        raw = self.env.get("PASSWORD", "").strip()
        return raw or None


ENV = FolderCryptSkillEnv()
