"""Session, setup, and keychain commands."""

from __future__ import annotations

import argparse
import getpass
import sys
from typing import Any

import bw
from cli_io import emit
from bw import BitwardenError
from skill_env import ENV

SERVERS = {
    "1": "https://vault.bitwarden.com",
    "2": "https://vault.bitwarden.eu",
}


def cmd_env(_: argparse.Namespace) -> int:
    path = ENV.env_path()
    emit(
        {
            "env_path": str(path),
            "exists": path.is_file(),
            "CURRENT_SKILL_DIRECTORY": str(ENV.workspace()),
            "library_dir": str(bw.library_dir()),
            "bw_binary": bw.binary(),
            "server": ENV.server(),
            "auth_method": ENV.auth_method(),
            "missing_keys": ENV.missing_keys(),
            "session_ttl_minutes": ENV.session_ttl_minutes(),
            "session": bw.session_age() or {"cached": False},
            "session_storage": bw.session_location(),
            "keychain_cache": {
                "available": bw.keychain_available(),
                "enabled": bool(ENV.keychain_service()),
                "service": ENV.keychain_service() or None,
            },
        }
    )
    return 0


def cmd_status(_: argparse.Namespace) -> int:
    session = bw.read_cached_session()
    payload = bw.status(session=session)
    payload["cached_session"] = bw.session_age() or {"cached": False}
    if payload.get("status") != "unlocked":
        payload["unlock_command"] = bw.unlock_hint()
    emit(payload)
    return 0


def cmd_login(_: argparse.Namespace) -> int:
    payload = bw.ensure_login()
    payload["unlock_command"] = bw.unlock_hint()
    emit(payload)
    return 0


def cmd_unlock(args: argparse.Namespace) -> int:
    if args.stdin:
        password = sys.stdin.readline().rstrip("\n")
    elif sys.stdin.isatty():
        password = getpass.getpass("Bitwarden master password: ")
    else:
        raise BitwardenError(
            "no terminal available to prompt for the master password — run this "
            "command yourself in a shell, or pipe it with --stdin",
            code="no_tty",
        )
    if not password:
        raise BitwardenError("empty master password", code="bad_input")
    bw.unlock(password, code=args.code or "", method=args.method or "")
    emit(
        {
            "status": "unlocked",
            "auth_method": ENV.auth_method(),
            "session_cached_in": bw.session_location(),
            "session": bw.session_age(),
        }
    )
    return 0


def _say(text: str = "") -> None:
    sys.stderr.write(text + "\n")


def _ask(prompt: str, default: str = "") -> str:
    sys.stderr.write(f"{prompt}{f' [{default}]' if default else ''}: ")
    sys.stderr.flush()
    line = sys.stdin.readline()
    if not line:
        raise BitwardenError("setup aborted", code="aborted")
    return line.strip() or default


def _ask_yes(prompt: str, *, default: bool = False) -> bool:
    answer = _ask(f"{prompt} (y/n)", "y" if default else "n").lower()
    return answer.startswith("y") or answer.startswith("o")


def _setup_server() -> str:
    _say("\nServer")
    _say("  1) Bitwarden cloud — US   https://vault.bitwarden.com")
    _say("  2) Bitwarden cloud — EU   https://vault.bitwarden.eu")
    _say("  3) Self-hosted / Vaultwarden")
    choice = _ask("Choice", "1")
    if choice in SERVERS:
        return SERVERS[choice]
    return _ask("Server URL", ENV.server()).rstrip("/")


def _setup_auth() -> dict[str, str]:
    _say("\nAuthentication")
    _say("  1) Email + master password — nothing to copy, but prompts for a 2FA code")
    _say("  2) Personal API key        — immune to 2FA prompts; Web Vault >")
    _say("     Account settings > Security > Keys > View API Key")
    if _ask("Choice", "1") == "2":
        updates = {
            "BW_CLIENTID": _ask("client_id"),
            "BW_CLIENTSECRET": getpass.getpass("client_secret (hidden): ", stream=sys.stderr).strip(),
        }
        if not updates["BW_CLIENTID"] or not updates["BW_CLIENTSECRET"]:
            raise BitwardenError("both client_id and client_secret are required", code="bad_input")
        email = _ask("Account email (optional — used as the keychain account)", ENV.email())
        if email:
            updates["BW_EMAIL"] = email
        return updates
    email = _ask("Account email", ENV.email())
    if not email:
        raise BitwardenError("an email is required for password auth", code="bad_input")
    return {"BW_EMAIL": email, "BW_CLIENTID": "", "BW_CLIENTSECRET": ""}


def _setup_keychain() -> dict[str, str] | None:
    if not bw.keychain_available():
        return None
    _say("\nSession cache (macOS keychain)")
    _say("  Keeps the session key in the encrypted login keychain instead of a plaintext")
    _say("  file, and it stays valid until `lock`. The master password is never stored.")
    if not _ask_yes("Enable", default=True):
        return None
    account = ENV.keychain_account() or ENV.email() or _ask("Keychain account (your Bitwarden email)")
    if not account:
        return None
    service = bw.DEFAULT_KEYCHAIN_SERVICE
    ENV.upsert_env_vars({"BW_KEYCHAIN_SERVICE": service, "BW_KEYCHAIN_ACCOUNT": account})
    return {"service": service, "account": account}


def cmd_setup(_: argparse.Namespace) -> int:
    if not sys.stdin.isatty():
        raise BitwardenError(
            "setup is interactive — run it yourself in a terminal:\n  " + bw.setup_hint(),
            code="no_tty",
        )
    _say(f"Bitwarden skill setup — configuration goes to {ENV.env_path()}")

    server = _setup_server()
    current = bw.status()
    bound = (current.get("serverUrl") or "").rstrip("/")
    if current.get("status") != "unauthenticated" and bound and bound != server.rstrip("/"):
        _say(f"\nAlready logged in to {bound}; switching servers requires a logout.")
        if not _ask_yes("Log out now", default=True):
            raise BitwardenError("keep the current server, or log out and re-run setup", code="aborted")
        bw.logout()

    updates = {"BW_SERVER": server, **_setup_auth()}
    updates["BW_SESSION_TTL"] = _ask("\nSession TTL in minutes", str(ENV.session_ttl_minutes()))
    env_file, _unused = ENV.upsert_env_vars(updates)

    keychain = _setup_keychain()

    _say("\nVerifying…")
    password = getpass.getpass("Master password (hidden): ", stream=sys.stderr)
    if not password:
        raise BitwardenError("empty master password", code="bad_input")
    code = ""
    if ENV.auth_method() == "password":
        code = _ask("2FA code (leave empty if two-step login is off)")
    bw.unlock(password, code=code)

    state = bw.status(session=bw.read_cached_session())
    _say("")
    emit(
        {
            "setup": "complete",
            "env_file": str(env_file),
            "server": ENV.server(),
            "auth_method": ENV.auth_method(),
            "account": state.get("userEmail"),
            "keychain_cache": keychain or "disabled",
            "vault": state.get("status"),
            "session": bw.session_age(),
            "next": "python scripts/cli.py list items --search github",
        }
    )
    return 0


def _keychain_target(args: argparse.Namespace) -> tuple[str, str]:
    if not bw.keychain_available():
        raise BitwardenError(
            "the macOS keychain is only available on macOS with the `security` tool",
            code="keychain_unavailable",
        )
    service = args.service or ENV.keychain_service() or bw.DEFAULT_KEYCHAIN_SERVICE
    account = args.account or ENV.keychain_account()
    if not account:
        account = bw.ensure_login().get("userEmail") or ""
    if not account:
        raise BitwardenError("cannot determine the account — pass --account", code="bad_input")
    return service, account


def cmd_keychain_set(args: argparse.Namespace) -> int:
    service, account = _keychain_target(args)
    if not sys.stdin.isatty():
        raise BitwardenError(
            "reading the master password needs a terminal — run this command yourself",
            code="no_tty",
        )
    path, _ = ENV.upsert_env_vars(
        {"BW_KEYCHAIN_SERVICE": service, "BW_KEYCHAIN_ACCOUNT": account}
    )
    password = getpass.getpass("Bitwarden master password (used once, never stored): ")
    if not password:
        raise BitwardenError("empty master password", code="bad_input")
    bw.unlock(password, code=args.code or "", method=args.method or "")
    emit(
        {
            "keychain": {"service": service, "account": account},
            "stores": "session key — the master password is never written anywhere",
            "env_updated": str(path),
            "session": bw.session_age(),
        }
    )
    return 0


def cmd_keychain_status(args: argparse.Namespace) -> int:
    service = args.service or ENV.keychain_service()
    account = args.account or ENV.keychain_account() or ENV.email()
    payload: dict[str, Any] = {
        "available": bw.keychain_available(),
        "enabled_in_env": bool(ENV.keychain_service()),
        "service": service or None,
        "account": account or None,
        "stores": "session key — never the master password",
    }
    if service and account and bw.keychain_available():
        payload["entry_found"] = bw.keychain_read(service, account) is not None
        payload["session"] = bw.session_age() or {"cached": False}
    emit(payload)
    return 0


def cmd_keychain_clear(args: argparse.Namespace) -> int:
    service, account = _keychain_target(args)
    emit({"deleted": bw.keychain_delete(service, account), "service": service, "account": account})
    return 0


def cmd_lock(_: argparse.Namespace) -> int:
    bw.lock()
    emit({"status": "locked", "session_cache_cleared": True})
    return 0


def cmd_logout(_: argparse.Namespace) -> int:
    bw.logout()
    emit({"status": "unauthenticated", "session_cache_cleared": True})
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    session = bw.ensure_session()
    if args.last:
        emit({"last_sync": bw.run(["sync", "--last"], session=session, timeout=300)})
        return 0
    bw.run(["sync", "--force"] if args.force else ["sync"], session=session, timeout=300)
    emit({"synced": True, "last_sync": bw.run(["sync", "--last"], session=session)})
    return 0


def register(sub: argparse._SubParsersAction) -> None:
    sub.add_parser("setup", help="Guided first-run configuration (writes .env)").set_defaults(
        func=cmd_setup
    )
    sub.add_parser("env", help="Resolved .env, binary, server, session state").set_defaults(
        func=cmd_env
    )
    sub.add_parser("status", help="bw status + cached session state").set_defaults(func=cmd_status)
    sub.add_parser("login", help="Log in with the API key (does not unlock)").set_defaults(
        func=cmd_login
    )
    sub.add_parser("lock", help="Lock the vault and drop the cached session").set_defaults(
        func=cmd_lock
    )
    sub.add_parser("logout", help="Log out and drop the cached session").set_defaults(
        func=cmd_logout
    )

    unlock = sub.add_parser("unlock", help="Prompt for the master password and cache a session key")
    unlock.add_argument("--stdin", action="store_true", help="Read the master password from stdin")
    unlock.add_argument("--code", help="Two-step login code (email auth only)")
    unlock.add_argument(
        "--method",
        choices=tuple(bw.TWOFA_METHODS),
        help="Two-step method for --code (default authenticator)",
    )
    unlock.set_defaults(func=cmd_unlock)

    keychain = sub.add_parser(
        "keychain",
        help="Cache the session key in the macOS keychain (never the master password)",
    )
    keychain_sub = keychain.add_subparsers(dest="keychain_command", required=True)
    for name, help_text, func in (
        ("set", "Unlock once and store the session key in the keychain", cmd_keychain_set),
        ("status", "Report whether an entry exists", cmd_keychain_status),
        ("clear", "Delete the stored entry", cmd_keychain_clear),
    ):
        parser = keychain_sub.add_parser(name, help=help_text)
        parser.add_argument(
            "--service", help=f"Keychain service (default {bw.DEFAULT_KEYCHAIN_SERVICE})"
        )
        parser.add_argument("--account", help="Keychain account (default: the Bitwarden user email)")
        if name == "set":
            parser.add_argument("--code", help="Two-step login code")
            parser.add_argument("--method", help=f"2FA method: {', '.join(bw.TWOFA_METHODS)}")
        parser.set_defaults(func=func)

    sync = sub.add_parser("sync", help="Pull the vault from the server")
    sync.add_argument("--last", action="store_true", help="Only report the last sync timestamp")
    sync.add_argument("--force", action="store_true", help="Force a full sync")
    sync.set_defaults(func=cmd_sync)
