"""Find each tool's credentials and data dirs: project first, then the computer."""

from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Scope:
    is_global: bool
    project: Path | None

    def roots(self) -> list[Path]:
        """Dirs searched for `.claude` / `.codex` / `.opencode`, in priority order."""
        home = Path.home()
        if self.is_global or self.project is None or self.project == home:
            return [home]
        return [self.project, home]

    def as_dict(self) -> dict[str, Any]:
        return {
            "is_global": self.is_global,
            "project": str(self.project) if self.project else None,
            "search_order": [str(root) for root in self.roots()],
        }


def resolve_scope(mode: str = "auto") -> Scope:
    """`auto` follows `$IS_GLOBAL` (registered skill); `project` / `global` force it."""
    if mode == "global":
        is_global = True
    elif mode == "project":
        is_global = False
    else:
        is_global = os.environ.get("IS_GLOBAL", "TRUE").strip().upper() not in {"FALSE", "0", "NO"}
    return Scope(is_global=is_global, project=None if is_global else _project_root())


def _project_root() -> Path:
    raw = os.environ.get("PROJECT_PATH", "").strip()
    if raw and "$(" not in raw and Path(raw).expanduser().is_dir():
        return Path(raw).expanduser().resolve()
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True, timeout=5,
        ).stdout.strip()
        if out:
            return Path(out).resolve()
    except (OSError, subprocess.SubprocessError):
        pass
    return Path.cwd().resolve()


def first_file(candidates: list[Path]) -> Path | None:
    for path in candidates:
        if path.is_file():
            return path.resolve()
    return None


def first_dir(candidates: list[Path]) -> Path | None:
    for path in candidates:
        if path.is_dir():
            return path.resolve()
    return None


def _home_env(var: str, default: Path) -> Path:
    raw = os.environ.get(var, "").strip()
    return Path(raw).expanduser() if raw else default


def claude_dirs(scope: Scope) -> list[Path]:
    home_dir = _home_env("CLAUDE_CONFIG_DIR", Path.home() / ".claude")
    return [home_dir if root == Path.home() else root / ".claude" for root in scope.roots()]


def codex_dirs(scope: Scope) -> list[Path]:
    home_dir = _home_env("CODEX_HOME", Path.home() / ".codex")
    return [home_dir if root == Path.home() else root / ".codex" for root in scope.roots()]


def opencode_data_dirs(scope: Scope) -> list[Path]:
    xdg = _home_env("XDG_DATA_HOME", Path.home() / ".local" / "share")
    dirs: list[Path] = []
    for root in scope.roots():
        if root == Path.home():
            dirs += [xdg / "opencode", Path.home() / ".opencode"]
        else:
            dirs += [root / ".opencode"]
    return dirs


def opencode_auth_files(scope: Scope) -> list[Path]:
    config = _home_env("OPENCODE_CONFIG_DIR", Path.home() / ".config" / "opencode")
    return [d / "auth.json" for d in opencode_data_dirs(scope)] + [config / "auth.json"]


def claude_keychain_credentials() -> dict[str, Any] | None:
    """macOS stores Claude Code OAuth in the login keychain, not in a file."""
    if sys.platform != "darwin":
        return None
    try:
        raw = subprocess.run(
            ["security", "find-generic-password", "-s", "Claude Code-credentials", "-w"],
            capture_output=True, text=True, check=True, timeout=10,
        ).stdout.strip()
        return json.loads(raw) if raw else None
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        return None


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def jwt_claims(token: str) -> dict[str, Any]:
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload))
    except (IndexError, ValueError):
        return {}
