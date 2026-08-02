"""Load Namecheap env vars from SkillCred-resolved `.env`."""

from __future__ import annotations

import os
import shutil
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

SKILL_NAME = "namecheap"
ENV_KEYS = (
    "NAMECHEAP_API_KEY",
    "NAMECHEAP_USERNAME",
    "NAMECHEAP_API_USER",
    "NAMECHEAP_CLIENT_IP",
    "NAMECHEAP_SANDBOX",
)

_SKILL_DIR = default_skill_dir(__file__)
os.environ.setdefault(WORKSPACE_ENV, str(_SKILL_DIR))


def env_cred() -> SkillCred:
    return SkillCred(SKILL_NAME, [".env"])


def parse_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key:
            values[key] = value
    return values


def load_env(*, override: bool = True) -> Path:
    """Load `.env` into ``os.environ``. Returns the resolved path."""
    cred = env_cred()
    path = cred.file_path()
    if not path.is_file():
        raise FileNotFoundError(
            f"missing {path} — run: python scripts/init.py  "
            f"(CURRENT_SKILL_DIRECTORY={os.environ.get(WORKSPACE_ENV, '')!r})"
        )
    for key, value in parse_dotenv(path).items():
        if override or key not in os.environ:
            os.environ[key] = value
    username = os.environ.get("NAMECHEAP_USERNAME", "").strip()
    api_user = os.environ.get("NAMECHEAP_API_USER", "").strip()
    if username and not api_user:
        os.environ["NAMECHEAP_API_USER"] = username
    return path.resolve()


def ensure_env_file() -> tuple[Path, bool]:
    """Create `.env` from `.env.example` if missing. Returns (path, created)."""
    cred = env_cred()
    path = cred.file_path()
    if path.is_file():
        return path.resolve(), False
    example = _SKILL_DIR / ".env.example"
    path.parent.mkdir(parents=True, exist_ok=True)
    if example.is_file():
        shutil.copyfile(example, path)
    else:
        path.write_text(
            "\n".join(f"{k}=" for k in ENV_KEYS) + "\n",
            encoding="utf-8",
        )
    return path.resolve(), True


def env_status() -> dict[str, object]:
    path = env_cred().file_path()
    present = path.is_file()
    loaded = parse_dotenv(path) if present else {}
    return {
        "env_path": str(path.resolve()),
        "exists": present,
        "CURRENT_SKILL_DIRECTORY": os.environ.get(WORKSPACE_ENV, ""),
        "keys": {
            k: bool(str(loaded.get(k, os.environ.get(k, ""))).strip()) for k in ENV_KEYS
        },
    }
