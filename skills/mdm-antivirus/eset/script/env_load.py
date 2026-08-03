"""Load ESET env from SkillCred-resolved `.env`."""

from __future__ import annotations

import os
import sys
import types
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
_COMMON_SRC = _ROOT / "meta-skill-common"
if _COMMON_SRC.is_dir() and "common" not in sys.modules:
    pkg = types.ModuleType("common")
    pkg.__path__ = [str(_COMMON_SRC)]
    sys.modules["common"] = pkg

from common.skill_cred import WORKSPACE_ENV, SkillCred, default_skill_dir  # noqa: E402
from common.skill_cred import display_path  # noqa: E402

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

SKILL_NAME = "eset"
_SKILL_DIR = default_skill_dir(__file__)
os.environ.setdefault(WORKSPACE_ENV, str(_SKILL_DIR))


def env_cred() -> SkillCred:
    return SkillCred(SKILL_NAME, [".env"])


def env_path() -> Path:
    return env_cred().file_path()


def display_env_path() -> str:
    return display_path(env_path())


def display_skill_home() -> str:
    return display_path(_SKILL_DIR)


def load_env(*, override: bool = False) -> Path:
    path = env_path()
    if path.is_file():
        if load_dotenv is not None:
            load_dotenv(path, override=override)
        else:
            for raw in path.read_text(encoding="utf-8").splitlines():
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip("'").strip('"')
                if key and (override or key not in os.environ):
                    os.environ[key] = value
    return path.resolve()


def upsert_env_vars(updates: dict[str, str]) -> Path:
    """Create or update keys in the SkillCred `.env` (preserves other lines)."""
    path = env_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    if path.is_file():
        lines = path.read_text(encoding="utf-8").splitlines()

    seen: set[str] = set()
    out: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in updates:
                out.append(f"{key}={updates[key]}")
                seen.add(key)
                continue
        out.append(line)

    for key, value in updates.items():
        if key not in seen:
            out.append(f"{key}={value}")

    text = "\n".join(out)
    if text and not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")
    for key, value in updates.items():
        os.environ[key] = value
    return path.resolve()
