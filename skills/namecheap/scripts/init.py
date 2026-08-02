#!/usr/bin/env python3
"""Install namecheap-cli via pip and ensure SkillCred `.env` exists."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from env_load import ENV_KEYS, ensure_env_file, env_status, load_env  # noqa: E402

PIP_PKG = "namecheap-python[cli]"


def _meta_skills_home() -> Path:
    return Path(os.environ.get("META_SKILLS_HOME", Path.home() / ".meta-skills")).expanduser()


def _shared_venv_python() -> Path | None:
    py = _meta_skills_home() / ".venv" / "bin" / "python"
    return py if py.is_file() else None


def _cli_path_for(python: Path | str) -> Path:
    return Path(python).resolve().parent / "namecheap-cli"


def _resolve_cli() -> str | None:
    shared = _shared_venv_python()
    if shared is not None:
        candidate = _cli_path_for(shared)
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return shutil.which("namecheap-cli")


def _pip_python() -> str:
    shared = _shared_venv_python()
    return str(shared) if shared is not None else sys.executable


def _install_cli() -> dict[str, object]:
    existing = _resolve_cli()
    if existing:
        return {"installed": True, "action": "already_present", "cli_path": existing}

    python = _pip_python()
    cmd = [python, "-m", "pip", "install", PIP_PKG]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    cli = _resolve_cli()
    return {
        "installed": proc.returncode == 0 and cli is not None,
        "action": "pip install",
        "command": " ".join(cmd),
        "cli_path": cli,
        "returncode": proc.returncode,
        "stdout": (proc.stdout or "").strip(),
        "stderr": (proc.stderr or "").strip(),
    }


def main() -> int:
    env_path, created = ensure_env_file()
    install = _install_cli()
    status = env_status()
    loaded_ok = False
    load_error = None
    try:
        load_env()
        loaded_ok = True
    except FileNotFoundError as exc:
        load_error = str(exc)

    missing = [
        k
        for k, ok in status["keys"].items()
        if k in ("NAMECHEAP_API_KEY", "NAMECHEAP_USERNAME") and not ok
    ]

    cli = install.get("cli_path") or _resolve_cli() or "namecheap-cli"
    out = {
        "ok": bool(install.get("installed")) and not missing,
        "env_path": str(env_path),
        "env_created": created,
        "env_loaded": loaded_ok,
        "env_load_error": load_error,
        "env_keys_set": status["keys"],
        "CURRENT_SKILL_DIRECTORY": os.environ.get("CURRENT_SKILL_DIRECTORY", ""),
        "cli": install,
        "next": (
            f"Edit {env_path} and set at least NAMECHEAP_API_KEY + NAMECHEAP_USERNAME. "
            "NAMECHEAP_API_USER defaults to username if empty; NAMECHEAP_CLIENT_IP is "
            f"auto-detected if empty. Then source the .env and run: {cli} -o json domain list"
            if missing
            else f"Ready — source the SkillCred .env, then: {cli} -o json domain list"
        ),
        "required_keys": list(ENV_KEYS),
    }
    print(json.dumps(out, indent=2))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
