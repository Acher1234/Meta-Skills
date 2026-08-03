"""Resolve Hexnode SkillCred `.env` and portal / API base URL."""

from __future__ import annotations

import os
import sys
import types
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

SKILL_NAME = "hexnode"


def _repo_root(start: Path) -> Path:
    for path in [start, *start.parents]:
        if (path / "meta-skill-common").is_dir():
            return path
    return start.parents[4]


_ROOT = _repo_root(Path(__file__).resolve())
_COMMON_SRC = _ROOT / "meta-skill-common"
if _COMMON_SRC.is_dir() and "common" not in sys.modules:
    pkg = types.ModuleType("common")
    pkg.__path__ = [str(_COMMON_SRC)]
    sys.modules["common"] = pkg

from common.skill_cred import WORKSPACE_ENV, SkillCred, default_skill_dir  # noqa: E402
from common.skill_cred import display_path  # noqa: E402

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


def load_env(*, override: bool = True) -> Path:
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


class ConfigError(Exception):
    pass


def require_api_key() -> str:
    load_env()
    key = os.environ.get("HEXNODE_API_KEY", "").strip()
    if not key:
        raise ConfigError(
            f"HEXNODE_API_KEY not set — edit {env_path()} "
            f"(CURRENT_SKILL_DIRECTORY={os.environ.get(WORKSPACE_ENV, '')!r})"
        )
    return key


def base_url() -> str:
    """Return API root ending with /api/v1 (no trailing slash beyond that)."""
    load_env()
    explicit = os.environ.get("HEXNODE_BASE_URL", "").strip().rstrip("/")
    if explicit:
        return explicit
    portal = os.environ.get("HEXNODE_PORTAL", "").strip().strip("/")
    if not portal:
        raise ConfigError(
            f"Set HEXNODE_PORTAL or HEXNODE_BASE_URL in {env_path()}"
        )
    if portal.startswith("http://") or portal.startswith("https://"):
        return portal.rstrip("/")
    return f"https://{portal}.hexnodemdm.com/api/v1"
