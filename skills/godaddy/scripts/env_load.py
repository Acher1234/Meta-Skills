"""Load GoDaddy env vars from SkillCred-resolved `.env`."""

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

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

SKILL_NAME = "godaddy"
DEFAULT_BASE_URL = "https://api.godaddy.com"

_SKILL_DIR = default_skill_dir(__file__)
os.environ.setdefault(WORKSPACE_ENV, str(_SKILL_DIR))


def env_cred() -> SkillCred:
    return SkillCred(SKILL_NAME, [".env"])


def load_env(*, override: bool = True) -> Path:
    """Load `.env` into ``os.environ``. Returns the resolved path."""
    path = env_cred().file_path()
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
    os.environ.setdefault("BASE_URL", DEFAULT_BASE_URL)
    return path.resolve()


def require_pat() -> str:
    load_env()
    pat = os.environ.get("GODADDY_PAT", "").strip()
    if not pat:
        path = env_cred().file_path()
        raise SystemExit(
            f"GODADDY_PAT not set — edit {path} (CURRENT_SKILL_DIRECTORY="
            f"{os.environ.get(WORKSPACE_ENV, '')!r})"
        )
    return pat


def base_url() -> str:
    load_env()
    return os.environ.get("BASE_URL", DEFAULT_BASE_URL).rstrip("/")
