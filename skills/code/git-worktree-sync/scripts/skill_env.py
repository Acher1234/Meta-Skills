"""git-worktree-sync settings (optional `.env` next to the registered SKILL.md)."""

from __future__ import annotations

from pathlib import Path

from common.skill_env import SkillEnv, env_load_main


class WorktreeSyncSkillEnv(SkillEnv):
    """No required key: SYNC_EXTRA lists extra paths to copy besides .env files."""

    def __init__(self) -> None:
        super().__init__("git-worktree-sync", Path(__file__))

    def verify(self, values: dict[str, str]) -> dict[str, str]:
        return {"SYNC_EXTRA": values.get("SYNC_EXTRA", "").strip()}

    def extra_paths(self) -> list[str]:
        raw = self.env["SYNC_EXTRA"].replace(";", ",").replace("\n", ",")
        return [p.strip().strip("/\\") for p in raw.split(",") if p.strip()]


ENV = WorktreeSyncSkillEnv()

if __name__ == "__main__":
    raise SystemExit(env_load_main(ENV))
