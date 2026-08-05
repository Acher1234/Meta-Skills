"""Thin wrapper around the Bitwarden `bw` CLI.

Owns the three things the raw CLI makes awkward for an agent: locating the pinned
binary, keeping a short-lived session key, and masking secrets before they reach
stdout.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from skill_env import ENV

SESSION_FILE = ".bw_session"
APPDATA_DIR = ".bw-appdata"
DEFAULT_TIMEOUT = 120

# Values never printed unless the caller passes --reveal.
SENSITIVE_KEYS = frozenset(
    {
        "password",
        "totp",
        "code",
        "number",
        "ssn",
        "passportNumber",
        "licenseNumber",
        "privateKey",
        "notes",
        "key",
    }
)

HIDDEN_FIELD_TYPE = 1


class BitwardenError(RuntimeError):
    def __init__(self, message: str, *, code: str = "bw_error", detail: Any = None):
        self.code = code
        self.detail = detail
        super().__init__(message)


def library_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def binary() -> str:
    local = library_dir() / "node_modules" / ".bin" / "bw"
    if local.is_file() and os.access(local, os.X_OK):
        return str(local)
    found = shutil.which("bw")
    if found:
        return found
    raise BitwardenError(
        f"bw CLI not found. Install it once: cd {library_dir()} "
        "&& ~/.meta-skills/install.sh npm init .",
        code="binary_missing",
    )


def appdata_dir() -> Path:
    path = ENV.workspace() / APPDATA_DIR
    path.mkdir(parents=True, exist_ok=True)
    return path


def _subprocess_env(
    session: str | None = None,
    extra: Mapping[str, str] | None = None,
) -> dict[str, str]:
    env = dict(os.environ)
    # Isolate login state per registered skill dir so each workspace can hold a
    # different Bitwarden account, and ignore any ambient credentials.
    env["BITWARDENCLI_APPDATA_DIR"] = str(appdata_dir())
    for key in ("BW_SESSION", "BW_CLIENTID", "BW_CLIENTSECRET"):
        env.pop(key, None)
    # Node only trusts a TLS-inspecting proxy or self-signed server through this.
    ca_certs = ENV.node_extra_ca_certs()
    if ca_certs:
        env["NODE_EXTRA_CA_CERTS"] = ca_certs
    if session:
        env["BW_SESSION"] = session
    if extra:
        env.update(extra)
    return env


def run(
    args: list[str],
    *,
    session: str | None = None,
    env_extra: Mapping[str, str] | None = None,
    stdin: str | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> str:
    """Run `bw` and return stdout. Raises BitwardenError on a non-zero exit."""
    command = [binary(), *args]
    if "--nointeraction" not in args:
        command.append("--nointeraction")
    try:
        proc = subprocess.run(
            command,
            input=stdin,
            capture_output=True,
            text=True,
            env=_subprocess_env(session, env_extra),
            cwd=str(library_dir()),
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise BitwardenError(f"bw {args[0]} timed out after {timeout}s", code="timeout") from exc
    if proc.returncode != 0:
        message = (proc.stderr or proc.stdout or "").strip() or f"bw {args[0]} failed"
        code = "locked" if "locked" in message.lower() else "bw_error"
        # Only the subcommand is echoed back: argv can carry secrets.
        raise BitwardenError(message, code=code, detail={"command": args[0]})
    return proc.stdout.strip()


def _loads(raw: str) -> Any:
    text = raw.strip()
    try:
        return json.loads(text)
    except ValueError:
        pass
    for opener, closer in (("{", "}"), ("[", "]")):
        start, end = text.find(opener), text.rfind(closer)
        if start != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except ValueError:
                continue
    raise BitwardenError("bw returned unparseable output", code="parse_error")


def run_json(args: list[str], **kwargs: Any) -> Any:
    return _loads(run(args, **kwargs))


def encode(payload: Any) -> str:
    """Base64-encode JSON the way `bw encode` does, without a second subprocess."""
    return base64.b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")


# --- Session -----------------------------------------------------------------


def session_path() -> Path:
    return ENV.workspace() / SESSION_FILE


def clear_session() -> None:
    session_path().unlink(missing_ok=True)


def write_session(key: str) -> Path:
    path = session_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        {
            "session": key,
            "created_at": time.time(),
            "ttl_minutes": ENV.session_ttl_minutes(),
        }
    )
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(payload)
    os.chmod(path, 0o600)
    return path


def session_age() -> dict[str, Any] | None:
    path = session_path()
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return None
    created = float(payload.get("created_at", 0))
    ttl_minutes = float(payload.get("ttl_minutes") or ENV.session_ttl_minutes())
    remaining = created + ttl_minutes * 60 - time.time()
    return {
        "cached": True,
        "expires_in_seconds": max(0, int(remaining)),
        "expired": remaining <= 0,
    }


def read_cached_session() -> str | None:
    info = session_age()
    if info is None:
        return None
    if info["expired"]:
        clear_session()
        return None
    payload = json.loads(session_path().read_text(encoding="utf-8"))
    return payload.get("session") or None


def status(session: str | None = None) -> dict[str, Any]:
    return run_json(["status"], session=session)


def ensure_server() -> dict[str, Any]:
    current = status()
    configured = (current.get("serverUrl") or ENV.DEFAULT_SERVER).rstrip("/")
    wanted = ENV.server().rstrip("/")
    if configured == wanted:
        return current
    if current.get("status") != "unauthenticated":
        raise BitwardenError(
            f"CLI is bound to {configured} but BW_SERVER is {wanted}. "
            "Run `cli.py logout` before switching servers.",
            code="server_mismatch",
        )
    run(["config", "server", wanted])
    return status()


def setup_hint() -> str:
    return (
        f'CURRENT_SKILL_DIRECTORY="{ENV.workspace()}" '
        f"{sys.executable} {library_dir()}/scripts/cli.py setup"
    )


def ensure_login() -> dict[str, Any]:
    """Authenticate if possible. Email auth cannot: it needs the master password."""
    current = ensure_server()
    if current.get("status") != "unauthenticated":
        return current
    missing = ENV.missing_keys()
    if missing:
        raise BitwardenError(
            f"No usable credentials in {ENV.env_path()} (missing {', '.join(missing)}). "
            "Set BW_EMAIL, or a personal API key — the guided setup does it for you:"
            f"\n  {setup_hint()}",
            code="missing_credentials",
        )
    if ENV.auth_method() == "password":
        raise BitwardenError(
            "Not logged in. With email auth, logging in and unlocking are the same "
            f"step and need the master password:\n  {unlock_hint()}",
            code="locked",
        )
    run(
        ["login", "--apikey"],
        env_extra={
            "BW_CLIENTID": ENV.client_id(),
            "BW_CLIENTSECRET": ENV.client_secret(),
        },
    )
    return status()


DEFAULT_KEYCHAIN_SERVICE = "meta-skills-bitwarden"


def keychain_available() -> bool:
    return sys.platform == "darwin" and shutil.which("security") is not None


def keychain_target(user_email: str = "") -> tuple[str, str] | None:
    """(service, account) to use, or None when the keychain is not configured."""
    service = ENV.keychain_service()
    if not service or not keychain_available():
        return None
    account = ENV.keychain_account() or user_email or ENV.email()
    if not account:
        return None
    return service, account


def _run_security(args: list[str]) -> subprocess.CompletedProcess[str] | None:
    """None when `security` is absent or the keychain dialog went unanswered."""
    try:
        return subprocess.run(
            ["security", *args], capture_output=True, text=True, timeout=30
        )
    except (OSError, subprocess.SubprocessError):
        return None


def keychain_read(service: str, account: str) -> str | None:
    proc = _run_security(["find-generic-password", "-s", service, "-a", account, "-w"])
    if proc is None or proc.returncode != 0:
        return None
    return proc.stdout.rstrip("\n") or None


def keychain_delete(service: str, account: str) -> bool:
    proc = _run_security(["delete-generic-password", "-s", service, "-a", account])
    return proc is not None and proc.returncode == 0


def keychain_store(service: str, account: str) -> None:
    """Let `security` prompt for the password itself, so it never enters Python."""
    try:
        proc = subprocess.run(
            [
                "security", "add-generic-password",
                "-s", service,
                "-a", account,
                "-l", f"{service} ({account})",
                "-U", "-w",
            ]
        )
    except OSError as exc:
        raise BitwardenError("could not run `security`", code="keychain_error") from exc
    if proc.returncode != 0:
        raise BitwardenError("security add-generic-password failed", code="keychain_error")


TWOFA_METHODS = {"authenticator": "0", "email": "1", "yubikey": "3"}


def _login_password(email: str, master_password: str, code: str, method: str) -> str:
    """`bw login <email>` already returns a session key: no separate unlock needed."""
    args = ["login", email, "--passwordenv", "BW_MASTER_PASSWORD", "--raw"]
    if code:
        args += ["--method", TWOFA_METHODS.get(method, method or "0"), "--code", code]
    try:
        return run(args, env_extra={"BW_MASTER_PASSWORD": master_password}).strip()
    except BitwardenError as exc:
        if "two-step" in str(exc).lower() or "two-factor" in str(exc).lower():
            raise BitwardenError(
                "This account has two-step login enabled. Pass `--code 123456` "
                "(add `--method email|yubikey` if not an authenticator app), or switch "
                "to a personal API key, which bypasses 2FA entirely.",
                code="twofa_required",
            ) from exc
        raise


def unlock(
    master_password: str,
    *,
    login_first: bool = True,
    code: str = "",
    method: str = "",
) -> str:
    """Exchange the master password for a session key and cache it."""
    state = ensure_server() if login_first else {"status": "locked"}
    if state.get("status") == "unauthenticated" and ENV.auth_method() == "password":
        key = _login_password(ENV.email(), master_password, code, method)
    else:
        if login_first:
            ensure_login()
        key = run(
            ["unlock", "--passwordenv", "BW_MASTER_PASSWORD", "--raw"],
            env_extra={"BW_MASTER_PASSWORD": master_password},
        ).strip()
    if not key:
        raise BitwardenError("unlock returned an empty session key", code="unlock_failed")
    write_session(key)
    return key


def unlock_hint() -> str:
    """Copy-pastable unlock command, built from the interpreter actually in use."""
    return (
        f'CURRENT_SKILL_DIRECTORY="{ENV.workspace()}" '
        f"{sys.executable} {library_dir()}/scripts/cli.py unlock"
    )


def ensure_session() -> str:
    """Session key for vault commands, or a BitwardenError telling the user to unlock."""
    key = read_cached_session()
    if key:
        return key
    # Tried before ensure_login(): under email auth, logging in already consumes the
    # very master password the keychain holds.
    target = keychain_target(status().get("userEmail") or "")
    if target:
        password = keychain_read(*target)
        if password:
            try:
                return unlock(password)
            except BitwardenError as exc:
                raise BitwardenError(
                    "The master password stored in the macOS keychain was rejected. "
                    f"Refresh it with `cli.py keychain set`, or unlock manually:\n  {unlock_hint()}",
                    code="locked",
                ) from exc
    ensure_login()
    raise BitwardenError(
        "Vault is locked (no valid cached session). The master password can only be "
        "typed by the user, so run this in your own terminal:\n  " + unlock_hint(),
        code="locked",
    )


def lock() -> None:
    clear_session()
    try:
        run(["lock"])
    except BitwardenError:
        # Already locked or logged out: the cache is cleared either way.
        pass


def logout() -> None:
    clear_session()
    try:
        run(["logout"])
    except BitwardenError:
        pass


# --- Redaction ---------------------------------------------------------------


def fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:8]


def mask(value: Any) -> Any:
    if value is None or value == "":
        return value
    text = str(value)
    return {"masked": True, "length": len(text), "sha256_8": fingerprint(text)}


def _is_hidden_field(node: Mapping[str, Any]) -> bool:
    return "value" in node and node.get("type") == HIDDEN_FIELD_TYPE


def redact(data: Any, *, reveal: bool = False) -> Any:
    """Replace secret values with a length + fingerprint stub."""
    if reveal:
        return data
    if isinstance(data, list):
        return [redact(item) for item in data]
    if not isinstance(data, dict):
        return data
    hidden_field = _is_hidden_field(data)
    out: dict[str, Any] = {}
    for key, value in data.items():
        if key in SENSITIVE_KEYS and not isinstance(value, (dict, list)):
            out[key] = mask(value)
        elif hidden_field and key == "value":
            out[key] = mask(value)
        else:
            out[key] = redact(value)
    return out
