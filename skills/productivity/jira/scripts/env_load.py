"""Load Jira env vars from SkillCred-resolved `.env`."""

from __future__ import annotations

import os
import sys
import types
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = next(
    (p for p in [_HERE, *_HERE.parents] if (p / "meta-skill-common").is_dir()),
    _HERE.parents[4],
)
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

SKILL_NAME = "meta-jira"
REQUIRED_KEYS = ("JIRA_SITE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN")

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


def _parse_env_line(raw: str) -> tuple[str, str] | None:
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        return None
    if line.startswith("export "):
        line = line[len("export ") :].strip()
    key, _, value = line.partition("=")
    key = key.strip()
    value = value.strip().strip("'").strip('"')
    if not key:
        return None
    return key, value


def load_env(*, override: bool = False) -> Path:
    """Load `.env` into ``os.environ``. Returns the resolved path."""
    path = env_path()
    if path.is_file():
        if load_dotenv is not None:
            load_dotenv(path, override=override)
        else:
            for raw in path.read_text(encoding="utf-8").splitlines():
                parsed = _parse_env_line(raw)
                if parsed is None:
                    continue
                key, value = parsed
                if override or key not in os.environ:
                    os.environ[key] = value
    return path.resolve()


def require_env() -> dict[str, str]:
    load_env()
    missing = [k for k in REQUIRED_KEYS if not os.environ.get(k, "").strip()]
    if missing:
        raise SystemExit(
            f"Missing {', '.join(missing)} — edit {env_path()} "
            f"(CURRENT_SKILL_DIRECTORY={os.environ.get(WORKSPACE_ENV, '')!r})"
        )
    return {k: os.environ[k].strip() for k in REQUIRED_KEYS}
