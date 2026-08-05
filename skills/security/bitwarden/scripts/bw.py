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

# Allowlist, not denylist: any string whose key is absent here is masked. A denylist
# has to predict every field Bitwarden will ever add — it already missed `keyValue`,
# the FIDO2 passkey private key. Getting this wrong must fail closed.
SAFE_KEYS = frozenset(
    {
        # Identity and structure
        "id", "object", "type", "name", "folderId", "organizationId", "collectionIds",
        "externalId", "favorite", "reprompt", "edit", "viewPassword", "deletedDate",
        "creationDate", "revisionDate", "passwordRevisionDate", "lastUsedDate",
        # Login — the username and the site are what make an item recognisable
        "username", "uri", "uris", "match",
        # Attachment metadata
        "fileName", "size", "sizeName", "url",
        # Card: the number and the CVC stay masked, the rest identifies the card
        "brand", "cardholderName", "expMonth", "expYear",
        # FIDO2 metadata — `keyValue` is the private key and is deliberately absent
        "keyType", "keyAlgorithm", "keyCurve", "rpId", "rpName", "userName",
        "userDisplayName", "discoverable", "counter",
        # SSH: the public half only
        "publicKey", "keyFingerprint",
        # Session and account state
        "status", "serverUrl", "lastSync", "userEmail", "userId",
        # Send: `accessUrl`, `key` and the payload stay masked
        "accessId", "accessCount", "maxAccessCount", "expirationDate", "deletionDate",
        "disabled", "hideEmail", "hidden",
        # Organisation and collection membership
        "readOnly", "hidePasswords", "manage", "permissions", "email",
    }
)

AMBIGUOUS_MATCH = "More than one result was found"


class BitwardenError(RuntimeError):
    def __init__(self, message: str, *, code: str = "bw_error", detail: Any = None):
        self.code = code
        self.detail = detail
        super().__init__(message)


def library_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def pinned_binary() -> str | None:
    local = library_dir() / "node_modules" / ".bin" / "bw"
    return str(local) if local.is_file() and os.access(local, os.X_OK) else None


def binary(*, trusted: bool = False) -> str:
    """Path to `bw`. With trusted=True, refuse a PATH lookup we cannot vouch for."""
    local = pinned_binary()
    if local:
        return local
    if trusted and not ENV.trust_path_binary():
        raise BitwardenError(
            "Refusing to hand the master password to a `bw` resolved from PATH — "
            "anything earlier in PATH could impersonate it and capture the password. "
            f"Install the pinned CLI (cd {library_dir()} && "
            "~/.meta-skills/install.sh npm init .), or set BW_TRUST_PATH_BINARY=true "
            "in the .env if you installed bw yourself and trust it.",
            code="untrusted_binary",
        )
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
    trusted: bool = False,
) -> str:
    """Run `bw` and return stdout. Raises BitwardenError on a non-zero exit."""
    command = [binary(trusted=trusted), *args]
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
        if AMBIGUOUS_MATCH in message:
            # bw dumps every matching id — dozens of bare UUIDs, useless without names.
            matches = sum(1 for line in message.splitlines()[1:] if line.strip())
            raise BitwardenError(
                f"{matches} objects match that search term. Narrow it, or run "
                "`list items --search <term>` to pick an id from names.",
                code="ambiguous",
                detail={"command": args[0], "matches": matches},
            )
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
#
# The cached value is a session key, never the master password. A stolen session key
# decrypts the vault until `lock` revokes it; a stolen master password is a permanent
# account takeover. Two backends, and the storage decides the expiry policy: the
# keychain is encrypted at rest and holds the key until `lock`, while the file cache
# is plaintext and therefore expires after BW_SESSION_TTL.


def session_path() -> Path:
    return ENV.workspace() / SESSION_FILE


def _session_store() -> tuple[str, str] | None:
    """Keychain (service, account) when configured, or None for the file cache."""
    return keychain_target()


def clear_session() -> None:
    store = _session_store()
    if store:
        keychain_delete(*store)
    session_path().unlink(missing_ok=True)


def session_location() -> str:
    store = _session_store()
    return f"macOS keychain ({store[0]})" if store else str(session_path())


def write_session(key: str) -> str:
    """Cache the session key; returns a human-readable description of where."""
    store = _session_store()
    payload = json.dumps(
        {
            "session": key,
            "created_at": time.time(),
            # None = revoked by `lock`, not by the clock. Only the plaintext file expires.
            "ttl_minutes": None if store else ENV.session_ttl_minutes(),
        }
    )
    if store:
        keychain_write(*store, payload)
        return session_location()
    path = session_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(payload)
    os.chmod(path, 0o600)
    return str(path)


def _read_session_payload() -> dict[str, Any] | None:
    store = _session_store()
    if store:
        # The keychain is authoritative. Any plaintext cache is residue from a version
        # that wrote one, or from a run before the keychain was enabled: shred it.
        session_path().unlink(missing_ok=True)
        raw = keychain_read(*store)
    else:
        raw = session_path().read_text(encoding="utf-8") if session_path().is_file() else None
    if not raw:
        return None
    try:
        payload = json.loads(raw)
    except ValueError:
        return None
    return payload if isinstance(payload, dict) else None


def session_age() -> dict[str, Any] | None:
    payload = _read_session_payload()
    if payload is None:
        return None
    ttl_minutes = payload.get("ttl_minutes")
    where = "keychain" if _session_store() else "file"
    if ttl_minutes is None:
        return {"cached": True, "storage": where, "expired": False, "expires": "on `lock`"}
    remaining = float(payload.get("created_at", 0)) + float(ttl_minutes) * 60 - time.time()
    return {
        "cached": True,
        "storage": where,
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
    payload = _read_session_payload() or {}
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


def keychain_target() -> tuple[str, str] | None:
    """(service, account) to use, or None when the keychain is not configured."""
    service = ENV.keychain_service()
    if not service or not keychain_available():
        return None
    account = ENV.keychain_account() or ENV.email()
    if not account:
        return None
    return service, account


def _run_security(
    args: list[str], stdin: str | None = None
) -> subprocess.CompletedProcess[str] | None:
    """None when `security` is absent or the keychain dialog went unanswered."""
    try:
        return subprocess.run(
            ["security", *args], input=stdin, capture_output=True, text=True, timeout=30
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


def keychain_write(service: str, account: str, secret: str) -> None:
    # `security -w` with no value opens /dev/tty and ignores piped stdin whenever a
    # controlling terminal exists — exactly the case for interactive `unlock`.
    # Passing -w on argv is unavoidable here; the session key already travels in
    # BW_SESSION for every later bw call, so this is the same exposure class.
    proc = _run_security(
        [
            "add-generic-password",
            "-s", service,
            "-a", account,
            "-l", f"{service} ({account})",
            "-U",
            "-w", secret,
        ],
    )
    if proc is None or proc.returncode != 0:
        detail = (proc.stderr.strip() if proc else "security unavailable") or "unknown error"
        raise BitwardenError(f"could not write to the keychain: {detail}", code="keychain_error")


TWOFA_METHODS = {"authenticator": "0", "email": "1", "yubikey": "3"}


def _login_password(email: str, master_password: str, code: str, method: str) -> str:
    """`bw login <email>` already returns a session key: no separate unlock needed."""
    args = ["login", email, "--passwordenv", "BW_MASTER_PASSWORD", "--raw"]
    if code:
        args += ["--method", TWOFA_METHODS.get(method, method or "0"), "--code", code]
    try:
        return run(
            args, env_extra={"BW_MASTER_PASSWORD": master_password}, trusted=True
        ).strip()
    except BitwardenError as exc:
        if "two-step" in str(exc).lower() or "two-factor" in str(exc).lower():
            raise BitwardenError(
                "This account has two-step login enabled. Pass `--code 123456` "
                "(add `--method email|yubikey` if not an authenticator app), or switch "
                "to a personal API key, which bypasses 2FA entirely.",
                code="twofa_required",
            ) from exc
        raise


def unlock(master_password: str, *, code: str = "", method: str = "") -> str:
    """Exchange the master password for a session key and cache it."""
    state = ensure_server()
    if state.get("status") == "unauthenticated" and ENV.auth_method() == "password":
        key = _login_password(ENV.email(), master_password, code, method)
    else:
        ensure_login()
        key = run(
            ["unlock", "--passwordenv", "BW_MASTER_PASSWORD", "--raw"],
            env_extra={"BW_MASTER_PASSWORD": master_password},
            trusted=True,
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


def _carries_secret(key: str, value: Any) -> bool:
    """Only a non-empty string can hold secret material; ints, bools and null cannot."""
    return isinstance(value, str) and value != "" and key not in SAFE_KEYS


def redact(data: Any, *, reveal: bool = False) -> Any:
    """Mask every string that is not explicitly allowlisted as structure or metadata."""
    if reveal:
        return data
    if isinstance(data, list):
        return [redact(item) for item in data]
    if not isinstance(data, dict):
        return data
    return {
        key: mask(value) if _carries_secret(key, value) else redact(value)
        for key, value in data.items()
    }
