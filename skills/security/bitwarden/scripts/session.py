#!/usr/bin/env python3
"""Load .env, login --apikey if unauthenticated, unlock, print shell exports.

Usage:
  eval "$(python3 scripts/session.py)"
  eval "$(CURRENT_SKILL_DIRECTORY=/path/to/registered python3 scripts/session.py)"
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent


def die(msg: str, code: int = 1) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key:
            values[key] = value
    return values


def require(env: dict[str, str], key: str) -> str:
    value = env.get(key, "").strip()
    if not value:
        die(f"{key} required in .env")
    return value


def find_bw() -> str:
    local = SKILL_DIR / "node_modules" / ".bin" / "bw"
    if local.is_file() and os.access(local, os.X_OK):
        return str(local)
    found = shutil.which("bw")
    if found:
        return found
    die(f"bw not found — run: cd {SKILL_DIR} && ~/.meta-skills/install.sh npm init .")


def shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


def main() -> int:
    workspace = Path(
        os.environ.get("CURRENT_SKILL_DIRECTORY", "").strip() or SKILL_DIR
    ).expanduser().resolve()
    env_file = workspace / ".env"
    if not env_file.is_file():
        die(
            f"missing {env_file} — copy .env.example and fill "
            "BW_SERVER / API key / BW_PASSWORD"
        )

    file_env = parse_env(env_file)
    server = require(file_env, "BW_SERVER").rstrip("/")
    client_id = require(file_env, "BW_CLIENTID")
    client_secret = require(file_env, "BW_CLIENTSECRET")
    password = require(file_env, "BW_PASSWORD")

    appdata = workspace / ".bw-appdata"
    appdata.mkdir(parents=True, exist_ok=True)

    bw_bin = find_bw()
    run_env = dict(os.environ)
    run_env["BITWARDENCLI_APPDATA_DIR"] = str(appdata)
    run_env.pop("BW_SESSION", None)
    ca = file_env.get("NODE_EXTRA_CA_CERTS", "").strip()
    if ca:
        run_env["NODE_EXTRA_CA_CERTS"] = ca

    def bw(*args: str, extra: dict[str, str] | None = None, timeout: int = 120) -> str:
        env = dict(run_env)
        if extra:
            env.update(extra)
        cmd = [bw_bin, *args]
        if "--nointeraction" not in args:
            cmd.append("--nointeraction")
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            cwd=str(SKILL_DIR),
            timeout=timeout,
        )
        if proc.returncode != 0:
            msg = (proc.stderr or proc.stdout or "").strip() or f"bw {args[0]} failed"
            die(msg)
        return proc.stdout.strip()

    def status_payload() -> dict:
        raw = bw("status")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            die(f"bw status: unparseable output: {raw[:200]}")

    state = status_payload()
    configured = (state.get("serverUrl") or "").rstrip("/")
    if configured != server:
        if state.get("status") != "unauthenticated" and configured:
            die(
                f"CLI bound to {configured} but BW_SERVER={server} — run: bw logout"
            )
        bw("config", "server", server)
        state = status_payload()

    if state.get("status") == "unauthenticated":
        bw(
            "login",
            "--apikey",
            extra={"BW_CLIENTID": client_id, "BW_CLIENTSECRET": client_secret},
        )

    session = bw(
        "unlock",
        "--passwordenv",
        "BW_PASSWORD",
        "--raw",
        extra={"BW_PASSWORD": password},
    ).strip()
    if not session:
        die("unlock returned empty session")

    print(f"export BITWARDENCLI_APPDATA_DIR={shell_quote(str(appdata))}")
    print(f"export BW_SESSION={shell_quote(session)}")
    if ca:
        print(f"export NODE_EXTRA_CA_CERTS={shell_quote(ca)}")
    print(f"export BW={shell_quote(bw_bin)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
