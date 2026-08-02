"""Resolve local skill-directory config files for a Meta-Skills skill.

``$CURRENT_SKILL_DIRECTORY`` must already point at the directory that contains
``SKILL.md`` (project install *or* the tool's global skill dir). This module
does **not** enumerate ``.cursor`` / ``.claude`` / Hermes paths — the caller
sets the env (see each skill's Working directory section).

Usage::

    from common.skill_cred import SkillCred

    token = SkillCred("google-workspace", ["google_token.json"])
    path = token.file_path()
"""

from __future__ import annotations

import os
from pathlib import Path

WORKSPACE_ENV = "CURRENT_SKILL_DIRECTORY"


def default_skill_dir(library_file: str | Path) -> Path:
    """Skill package dir from a file under ``<skill>/scripts/``."""
    return Path(library_file).resolve().parent.parent


class SkillCred:
    """Locate config files under the directory given by ``$CURRENT_SKILL_DIRECTORY``."""

    def __init__(self, name: str, file_search: list[str] | tuple[str, ...]):
        self.name = name.strip().strip("/")
        if not self.name:
            raise ValueError("skill name required")
        names = tuple(n for n in file_search if n and str(n).strip())
        if not names:
            raise ValueError("file_search required")
        self.file_search = names
        self.workspace = self._workspace_from_env()

    def _workspace_from_env(self) -> Path:
        raw = os.environ.get(WORKSPACE_ENV, "").strip()
        if raw:
            candidate = Path(raw).expanduser()
            if candidate.is_dir():
                return candidate.resolve()
        return Path.cwd().resolve()

    def find_file(self) -> Path | None:
        """First existing ``workspace / <name>`` for names in ``file_search``."""
        for filename in self.file_search:
            path = self.workspace / filename
            if path.is_file():
                return path.resolve()
        return None

    def file_path(self, filename: str | None = None) -> Path:
        """Existing match, or create-path under workspace (default: first search name)."""
        if filename is not None:
            return (self.workspace / filename).resolve()
        found = self.find_file()
        if found is not None:
            return found
        return (self.workspace / self.file_search[0]).resolve()

    def __fspath__(self) -> str:
        return str(self.file_path())

    def __str__(self) -> str:
        return str(self.file_path())

    def __repr__(self) -> str:
        return f"SkillCred({self.name!r}, {list(self.file_search)!r})"

    def exists(self) -> bool:
        return self.file_path().is_file()

    def read_text(self, encoding: str = "utf-8") -> str:
        return self.file_path().read_text(encoding=encoding)

    def write_text(self, data: str, encoding: str = "utf-8") -> int:
        path = self.file_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        return path.write_text(data, encoding=encoding)

    def unlink(self, missing_ok: bool = False) -> None:
        self.file_path().unlink(missing_ok=missing_ok)


def display_path(path: Path | SkillCred) -> str:
    """Return a user-friendly ``~/``-shortened path."""
    resolved = path.file_path() if isinstance(path, SkillCred) else path.resolve()
    try:
        return "~/" + str(resolved.relative_to(Path.home()))
    except ValueError:
        return str(resolved)
