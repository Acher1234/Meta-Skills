#!/usr/bin/env python3
"""Bitwarden CLI — vault read/write and Send, with masked output by default."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import bw  # noqa: E402
from bw import BitwardenError  # noqa: E402
from skill_env import ENV  # noqa: E402

ITEM_TYPES = {"login": 1, "note": 2, "card": 3, "identity": 4}
SCALAR_GETS = {"username", "password", "uri", "totp", "notes", "exposed", "fingerprint"}
SECRET_GETS = {"password", "totp", "notes"}


def _print(data: Any) -> None:
    print(json.dumps(data, indent=2, default=str))


def _write_secret_file(path: Path, value: str) -> Path:
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(value)
    os.chmod(path, 0o600)
    return path


def _clipboard_command() -> list[str] | None:
    if sys.platform == "darwin":
        return ["pbcopy"]
    if sys.platform == "win32":
        return ["clip"]
    for candidate in (["wl-copy"], ["xclip", "-selection", "clipboard"], ["xsel", "-bi"]):
        if shutil.which(candidate[0]):
            return candidate
    return None


def _copy_to_clipboard(value: str) -> bool:
    command = _clipboard_command()
    if not command:
        return False
    try:
        subprocess.run(command, input=value, text=True, check=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return False
    return True


def _deliver_secret(value: str, args: argparse.Namespace, label: str) -> dict[str, Any]:
    """Return a payload for a secret: file, clipboard, revealed, or masked."""
    result: dict[str, Any] = {"object": label}
    if getattr(args, "output", None):
        path = _write_secret_file(Path(args.output), value)
        result["written_to"] = str(path)
        result["value"] = bw.mask(value)
        return result
    if getattr(args, "clipboard", False):
        if _copy_to_clipboard(value):
            result["copied_to_clipboard"] = True
            result["value"] = bw.mask(value)
            return result
        result["copied_to_clipboard"] = False
        result["warning"] = "no clipboard tool found"
    result["value"] = value if args.reveal else bw.mask(value)
    if not args.reveal:
        result["hint"] = "add --reveal, --clipboard or --output to obtain the value"
    return result


def _resolve_password(args: argparse.Namespace, session: str) -> str | None:
    """Password from --generate, --password-stdin, or --password (in that order)."""
    if getattr(args, "generate", False):
        return bw.run(["generate", "--length", str(args.generate_length), "-uln", "-s"])
    if getattr(args, "password_stdin", False):
        value = sys.stdin.readline().rstrip("\n")
        if not value:
            raise BitwardenError("no password received on stdin", code="bad_input")
        return value
    return getattr(args, "password", None)


def _parse_fields(pairs: list[str] | None, field_type: int) -> list[dict[str, Any]]:
    fields: list[dict[str, Any]] = []
    for raw in pairs or []:
        name, sep, value = raw.partition("=")
        if not sep:
            raise BitwardenError(f"field must be name=value, got {name!r}", code="bad_input")
        fields.append({"name": name, "value": value, "type": field_type})
    return fields


# --- Session -----------------------------------------------------------------


def cmd_env(_: argparse.Namespace) -> int:
    path = ENV.env_path()
    _print(
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
            "keychain_unlock": {
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
    _print(payload)
    return 0


def cmd_login(_: argparse.Namespace) -> int:
    payload = bw.ensure_login()
    payload["unlock_command"] = bw.unlock_hint()
    _print(payload)
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
    _print(
        {
            "status": "unlocked",
            "auth_method": ENV.auth_method(),
            "session_cached_at": str(bw.session_path()),
            "session": bw.session_age(),
        }
    )
    return 0


# --- Guided setup ------------------------------------------------------------

SERVERS = {
    "1": "https://vault.bitwarden.com",
    "2": "https://vault.bitwarden.eu",
}


def _say(text: str = "") -> None:
    """Prompts go to stderr so stdout stays parseable JSON."""
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
    _say("\nSilent unlock (macOS keychain)")
    _say("  Stores the master password in the login keychain so the agent can unlock")
    _say("  on its own. `security` prompts for it — it never passes through Python.")
    if not _ask_yes("Enable", default=True):
        return None
    account = ENV.keychain_account() or ENV.email() or _ask("Keychain account (your Bitwarden email)")
    if not account:
        return None
    service = bw.DEFAULT_KEYCHAIN_SERVICE
    bw.keychain_store(service, account)
    ENV.upsert_env_vars(
        {"BW_PASSWORD_KEYCHAIN_SERVICE": service, "BW_PASSWORD_KEYCHAIN_ACCOUNT": account}
    )
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
    if keychain:
        bw.ensure_session()
    else:
        password = getpass.getpass("Master password (hidden): ", stream=sys.stderr)
        if not password:
            raise BitwardenError("empty master password", code="bad_input")
        code = ""
        if ENV.auth_method() == "password":
            code = _ask("2FA code (leave empty if two-step login is off)")
        bw.unlock(password, code=code)

    state = bw.status(session=bw.read_cached_session())
    _say("")
    _print(
        {
            "setup": "complete",
            "env_file": str(env_file),
            "server": ENV.server(),
            "auth_method": ENV.auth_method(),
            "account": state.get("userEmail"),
            "keychain_unlock": keychain or "disabled",
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
            "`security` prompts for the password on a terminal — run this command yourself",
            code="no_tty",
        )
    bw.keychain_store(service, account)
    path, _ = ENV.upsert_env_vars({"BW_PASSWORD_KEYCHAIN_SERVICE": service})
    stored = bw.keychain_read(service, account)
    if not stored:
        raise BitwardenError("stored the entry but could not read it back", code="keychain_error")
    bw.unlock(stored)
    _print(
        {
            "keychain": {"service": service, "account": account},
            "env_updated": str(path),
            "verified": "unlock succeeded with the stored password",
            "session": bw.session_age(),
        }
    )
    return 0


def cmd_keychain_status(args: argparse.Namespace) -> int:
    service = args.service or ENV.keychain_service()
    account = args.account or ENV.keychain_account()
    if not account:
        account = bw.status().get("userEmail") or ""
    payload: dict[str, Any] = {
        "available": bw.keychain_available(),
        "enabled_in_env": bool(ENV.keychain_service()),
        "service": service or None,
        "account": account or None,
    }
    if service and account and bw.keychain_available():
        stored = bw.keychain_read(service, account)
        payload["entry_found"] = stored is not None
        if stored:
            payload["value"] = bw.mask(stored)
    _print(payload)
    return 0


def cmd_keychain_clear(args: argparse.Namespace) -> int:
    service, account = _keychain_target(args)
    _print({"deleted": bw.keychain_delete(service, account), "service": service, "account": account})
    return 0


def cmd_lock(_: argparse.Namespace) -> int:
    bw.lock()
    _print({"status": "locked", "session_cache_cleared": True})
    return 0


def cmd_logout(_: argparse.Namespace) -> int:
    bw.logout()
    _print({"status": "unauthenticated", "session_cache_cleared": True})
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    session = bw.ensure_session()
    if args.last:
        _print({"last_sync": bw.run(["sync", "--last"], session=session, timeout=300)})
        return 0
    bw.run(["sync", "--force"] if args.force else ["sync"], session=session, timeout=300)
    _print({"synced": True, "last_sync": bw.run(["sync", "--last"], session=session)})
    return 0


# --- Read --------------------------------------------------------------------


def cmd_list(args: argparse.Namespace) -> int:
    session = bw.ensure_session()
    command = ["list", args.object]
    for flag, value in (
        ("--search", args.search),
        ("--folderid", args.folderid),
        ("--collectionid", args.collectionid),
        ("--organizationid", args.organizationid),
        ("--url", args.url),
    ):
        if value:
            command += [flag, value]
    if args.trash:
        command.append("--trash")
    if args.archived:
        command.append("--archived")
    data = bw.run_json(command, session=session)
    if isinstance(data, list) and args.limit:
        data = data[: args.limit]
    _print(bw.redact(data, reveal=args.reveal))
    return 0


def cmd_get(args: argparse.Namespace) -> int:
    session = bw.ensure_session()
    command = ["get", args.object, args.id]
    if args.organizationid:
        command += ["--organizationid", args.organizationid]
    if args.object in SCALAR_GETS:
        value = bw.run(command, session=session)
        if args.object in SECRET_GETS:
            _print(_deliver_secret(value, args, args.object))
        else:
            _print({"object": args.object, "value": value})
        return 0
    # Templates only carry placeholder text, so masking them is pure noise.
    reveal = args.reveal or args.object == "template"
    _print(bw.redact(bw.run_json(command, session=session), reveal=reveal))
    return 0


def cmd_get_attachment(args: argparse.Namespace) -> int:
    session = bw.ensure_session()
    output = str(Path(args.output).expanduser())
    message = bw.run(
        ["get", "attachment", args.filename, "--itemid", args.itemid, "--output", output],
        session=session,
        timeout=300,
    )
    _print({"downloaded": args.filename, "itemid": args.itemid, "output": output, "message": message})
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    command = ["generate"]
    if args.passphrase:
        command.append("--passphrase")
        command += ["--words", str(args.words), "--separator", args.separator]
        if args.capitalize:
            command.append("--capitalize")
        if args.include_number:
            command.append("--includeNumber")
    else:
        flags = "".join(
            char
            for char, enabled in (
                ("u", args.uppercase),
                ("l", args.lowercase),
                ("n", args.number),
                ("s", args.special),
            )
            if enabled
        )
        command.append(f"-{flags or 'uln'}")
        command += ["--length", str(args.length)]
    value = bw.run(command)
    _print(_deliver_secret(value, args, "generated"))
    return 0


# --- Write -------------------------------------------------------------------


def _build_item(args: argparse.Namespace, session: str, base: dict[str, Any] | None) -> dict[str, Any]:
    item = base if base is not None else bw.run_json(["get", "template", "item"], session=session)
    if base is None:
        item["type"] = ITEM_TYPES[args.type]
        item["name"] = args.name
        item["notes"] = args.notes
        for key in ("login", "secureNote", "card", "identity"):
            item[key] = None
    elif args.name:
        item["name"] = args.name
    if args.notes is not None:
        item["notes"] = args.notes
    if args.folderid is not None:
        item["folderId"] = args.folderid or None
    if getattr(args, "favorite", None) is not None:
        item["favorite"] = args.favorite

    item_type = item.get("type", 1)
    password = _resolve_password(args, session)

    if item_type == ITEM_TYPES["login"]:
        login = item.get("login") or {"uris": [], "username": None, "password": None, "totp": None}
        if args.username is not None:
            login["username"] = args.username
        if password is not None:
            login["password"] = password
        if args.totp is not None:
            login["totp"] = args.totp or None
        if args.uri:
            login["uris"] = [{"match": None, "uri": uri} for uri in args.uri]
        item["login"] = login
    elif item_type == ITEM_TYPES["note"]:
        item["secureNote"] = item.get("secureNote") or {"type": 0}
    elif item_type == ITEM_TYPES["card"]:
        card = item.get("card") or {}
        for key, value in (
            ("cardholderName", args.card_holder),
            ("brand", args.card_brand),
            ("number", args.card_number),
            ("expMonth", args.card_exp_month),
            ("expYear", args.card_exp_year),
            ("code", args.card_code),
        ):
            if value is not None:
                card[key] = value
        item["card"] = card
    elif item_type == ITEM_TYPES["identity"]:
        identity = item.get("identity") or {}
        for key, value in (
            ("firstName", args.identity_first_name),
            ("lastName", args.identity_last_name),
            ("email", args.identity_email),
            ("phone", args.identity_phone),
        ):
            if value is not None:
                identity[key] = value
        item["identity"] = identity

    fields = _parse_fields(args.field, 0) + _parse_fields(args.hidden_field, 1)
    if fields:
        item["fields"] = (item.get("fields") or []) + fields
    return item


def cmd_create_item(args: argparse.Namespace) -> int:
    session = bw.ensure_session()
    item = _build_item(args, session, None)
    # Payload goes through stdin, not argv: it carries the password in clear text.
    created = bw.run_json(["create", "item"], session=session, stdin=bw.encode(item))
    _print(bw.redact(created, reveal=args.reveal))
    return 0


def cmd_create_folder(args: argparse.Namespace) -> int:
    session = bw.ensure_session()
    template = bw.run_json(["get", "template", "folder"], session=session)
    template["name"] = args.name
    _print(bw.run_json(["create", "folder"], session=session, stdin=bw.encode(template)))
    return 0


def cmd_create_attachment(args: argparse.Namespace) -> int:
    session = bw.ensure_session()
    path = str(Path(args.file).expanduser().resolve())
    created = bw.run_json(
        ["create", "attachment", "--file", path, "--itemid", args.itemid],
        session=session,
        timeout=300,
    )
    _print(bw.redact(created, reveal=args.reveal))
    return 0


def cmd_edit_item(args: argparse.Namespace) -> int:
    session = bw.ensure_session()
    current = bw.run_json(["get", "item", args.id], session=session)
    item = _build_item(args, session, current)
    updated = bw.run_json(["edit", "item", args.id], session=session, stdin=bw.encode(item))
    _print(bw.redact(updated, reveal=args.reveal))
    return 0


def cmd_edit_folder(args: argparse.Namespace) -> int:
    session = bw.ensure_session()
    folder = bw.run_json(["get", "folder", args.id], session=session)
    folder["name"] = args.name
    _print(bw.run_json(["edit", "folder", args.id], session=session, stdin=bw.encode(folder)))
    return 0


def cmd_delete(args: argparse.Namespace) -> int:
    if not args.yes:
        raise BitwardenError(
            "refusing to delete without --yes (confirm with the user first)",
            code="confirmation_required",
        )
    if args.permanent and not args.i_understand_this_is_irreversible:
        raise BitwardenError(
            "--permanent bypasses the trash and cannot be undone; add "
            "--i-understand-this-is-irreversible to proceed",
            code="confirmation_required",
        )
    session = bw.ensure_session()
    command = ["delete", args.object, args.id]
    if args.object == "attachment":
        if not args.itemid:
            raise BitwardenError("--itemid is required to delete an attachment", code="bad_input")
        command += ["--itemid", args.itemid]
    if args.object == "org-collection":
        if not args.organizationid:
            raise BitwardenError(
                "--organizationid is required to delete an org-collection", code="bad_input"
            )
        command += ["--organizationid", args.organizationid]
    if args.permanent:
        command.append("--permanent")
    bw.run(command, session=session)
    _print({"deleted": args.id, "object": args.object, "permanent": bool(args.permanent)})
    return 0


def cmd_restore(args: argparse.Namespace) -> int:
    session = bw.ensure_session()
    bw.run(["restore", "item", args.id], session=session)
    _print({"restored": args.id})
    return 0


# --- Send --------------------------------------------------------------------


def cmd_send_create(args: argparse.Namespace) -> int:
    if not args.file and args.text is None:
        raise BitwardenError("provide --text or --file", code="bad_input")
    session = bw.ensure_session()
    kind = "send.file" if args.file else "send.text"
    send = bw.run_json(["send", "template", kind], session=session)
    send["name"] = args.name
    send["notes"] = args.notes or None
    send["maxAccessCount"] = args.max_access
    send["deletionDate"] = (
        datetime.now(timezone.utc) + timedelta(days=args.days)
    ).isoformat().replace("+00:00", "Z")

    password = args.password
    if args.password_stdin:
        password = sys.stdin.readline().rstrip("\n")
    send["password"] = password or None

    command = ["send", "create"]
    if args.file:
        path = Path(args.file).expanduser().resolve()
        send["file"] = {"fileName": path.name}
        command += ["--file", str(path)]
    else:
        send["text"] = {"text": args.text, "hidden": bool(args.hidden)}

    # The whole payload, password included, travels on stdin rather than argv.
    raw = bw.run(command, session=session, stdin=bw.encode(send), timeout=300)
    try:
        created = json.loads(raw)
    except ValueError:
        created = None
    if not isinstance(created, dict):
        # Without --fullObject the CLI answers with the bare access URL.
        _print({"accessUrl": raw, "passwordProtected": bool(password)})
        return 0
    _print(
        {
            "id": created.get("id"),
            "accessUrl": created.get("accessUrl"),
            "deletionDate": created.get("deletionDate"),
            "maxAccessCount": created.get("maxAccessCount"),
            "passwordProtected": bool(password),
        }
    )
    return 0


def cmd_send_list(args: argparse.Namespace) -> int:
    session = bw.ensure_session()
    _print(bw.redact(bw.run_json(["send", "list"], session=session), reveal=args.reveal))
    return 0


def cmd_send_get(args: argparse.Namespace) -> int:
    session = bw.ensure_session()
    _print(bw.redact(bw.run_json(["send", "get", args.id], session=session), reveal=args.reveal))
    return 0


def cmd_send_delete(args: argparse.Namespace) -> int:
    if not args.yes:
        raise BitwardenError(
            "refusing to delete a Send without --yes", code="confirmation_required"
        )
    session = bw.ensure_session()
    bw.run(["send", "delete", args.id], session=session)
    _print({"deleted": args.id, "object": "send"})
    return 0


def cmd_receive(args: argparse.Namespace) -> int:
    session = bw.ensure_session()
    command = ["send", "receive", args.url]
    password = args.password
    if args.password_stdin:
        password = sys.stdin.readline().rstrip("\n")
    env_extra = None
    if password:
        command += ["--passwordenv", "BW_SEND_PASSWORD"]
        env_extra = {"BW_SEND_PASSWORD": password}
    if args.output:
        output = str(Path(args.output).expanduser())
        command += ["--output", output]
        message = bw.run(command, session=session, env_extra=env_extra, timeout=300)
        _print({"received": args.url, "output": output, "message": message})
        return 0
    content = bw.run(command, session=session, env_extra=env_extra, timeout=300)
    _print(_deliver_secret(content, args, "send"))
    return 0


# --- Parser ------------------------------------------------------------------


def _add_secret_output_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--reveal", action="store_true", help="Print the secret in clear text")
    parser.add_argument("--clipboard", action="store_true", help="Copy the secret to the clipboard")
    parser.add_argument("--output", help="Write the secret to a file (chmod 600)")


def _add_password_source_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--password", help="Visible in the process list — prefer --generate")
    parser.add_argument("--password-stdin", action="store_true", help="Read the password from stdin")
    parser.add_argument("--generate", action="store_true", help="Generate a strong password")
    parser.add_argument("--generate-length", type=int, default=20)


def _add_item_content_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--notes")
    parser.add_argument("--folderid")
    parser.add_argument("--username")
    parser.add_argument("--totp", help="TOTP secret / otpauth URI")
    parser.add_argument("--uri", action="append", help="Login URI (repeatable)")
    parser.add_argument("--field", action="append", metavar="NAME=VALUE", help="Text field")
    parser.add_argument("--hidden-field", action="append", metavar="NAME=VALUE", help="Hidden field")
    parser.add_argument("--card-holder")
    parser.add_argument("--card-brand")
    parser.add_argument("--card-number")
    parser.add_argument("--card-exp-month")
    parser.add_argument("--card-exp-year")
    parser.add_argument("--card-code")
    parser.add_argument("--identity-first-name")
    parser.add_argument("--identity-last-name")
    parser.add_argument("--identity-email")
    parser.add_argument("--identity-phone")
    _add_password_source_flags(parser)
    parser.add_argument("--reveal", action="store_true", help="Do not mask secrets in the response")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Bitwarden vault CLI (read, write, Send)")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("setup", help="Guided first-run configuration (writes .env)").set_defaults(func=cmd_setup)
    sub.add_parser("env", help="Resolved .env, binary, server, session state").set_defaults(func=cmd_env)
    sub.add_parser("status", help="bw status + cached session state").set_defaults(func=cmd_status)
    sub.add_parser("login", help="Log in with the API key (does not unlock)").set_defaults(func=cmd_login)
    sub.add_parser("lock", help="Lock the vault and drop the cached session").set_defaults(func=cmd_lock)
    sub.add_parser("logout", help="Log out and drop the cached session").set_defaults(func=cmd_logout)

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
        "keychain", help="Store the master password in the macOS keychain for silent unlocks"
    )
    keychain_sub = keychain.add_subparsers(dest="keychain_command", required=True)
    for name, help_text, func in (
        ("set", "Store or replace the master password (prompts via `security`)", cmd_keychain_set),
        ("status", "Report whether an entry exists", cmd_keychain_status),
        ("clear", "Delete the stored entry", cmd_keychain_clear),
    ):
        parser = keychain_sub.add_parser(name, help=help_text)
        parser.add_argument("--service", help=f"Keychain service (default {bw.DEFAULT_KEYCHAIN_SERVICE})")
        parser.add_argument("--account", help="Keychain account (default: the Bitwarden user email)")
        parser.set_defaults(func=func)

    sync = sub.add_parser("sync", help="Pull the vault from the server")
    sync.add_argument("--last", action="store_true", help="Only report the last sync timestamp")
    sync.add_argument("--force", action="store_true", help="Force a full sync")
    sync.set_defaults(func=cmd_sync)

    lst = sub.add_parser("list", help="List vault objects")
    lst.add_argument(
        "object",
        choices=("items", "folders", "collections", "organizations", "org-collections", "org-members"),
    )
    lst.add_argument("--search")
    lst.add_argument("--folderid")
    lst.add_argument("--collectionid")
    lst.add_argument("--organizationid")
    lst.add_argument("--url")
    lst.add_argument("--trash", action="store_true")
    lst.add_argument("--archived", action="store_true")
    lst.add_argument("--limit", type=int, help="Truncate the response client-side")
    lst.add_argument("--reveal", action="store_true")
    lst.set_defaults(func=cmd_list)

    get = sub.add_parser("get", help="Get one object or field (search term or exact id)")
    get.add_argument(
        "object",
        choices=(
            "item", "username", "password", "uri", "totp", "notes", "exposed",
            "folder", "collection", "organization", "org-collection", "template", "fingerprint",
        ),
    )
    get.add_argument("id", help="Exact id or unique search term")
    get.add_argument("--organizationid")
    _add_secret_output_flags(get)
    get.set_defaults(func=cmd_get)

    attachment = sub.add_parser("get-attachment", help="Download a file attachment")
    attachment.add_argument("filename")
    attachment.add_argument("--itemid", required=True)
    attachment.add_argument("--output", required=True, help="Directory (trailing /) or file path")
    attachment.set_defaults(func=cmd_get_attachment)

    gen = sub.add_parser("generate", help="Generate a password or passphrase")
    gen.add_argument("--length", type=int, default=14)
    gen.add_argument("--uppercase", "-u", action="store_true")
    gen.add_argument("--lowercase", "-l", action="store_true")
    gen.add_argument("--number", "-n", action="store_true")
    gen.add_argument("--special", "-s", action="store_true")
    gen.add_argument("--passphrase", action="store_true")
    gen.add_argument("--words", type=int, default=3)
    gen.add_argument("--separator", default="-")
    gen.add_argument("--capitalize", action="store_true")
    gen.add_argument("--include-number", action="store_true")
    _add_secret_output_flags(gen)
    gen.set_defaults(func=cmd_generate)

    create = sub.add_parser("create", help="Create an item, folder, or attachment")
    create_sub = create.add_subparsers(dest="create_command", required=True)

    create_item = create_sub.add_parser("item", help="Create a login, note, card, or identity")
    create_item.add_argument("--name", required=True)
    create_item.add_argument("--type", choices=tuple(ITEM_TYPES), default="login")
    create_item.add_argument("--favorite", action="store_true", default=None)
    _add_item_content_flags(create_item)
    create_item.set_defaults(func=cmd_create_item)

    create_folder = create_sub.add_parser("folder", help="Create a folder")
    create_folder.add_argument("--name", required=True)
    create_folder.set_defaults(func=cmd_create_folder)

    create_attachment = create_sub.add_parser("attachment", help="Attach a file to an item")
    create_attachment.add_argument("--file", required=True)
    create_attachment.add_argument("--itemid", required=True)
    create_attachment.add_argument("--reveal", action="store_true")
    create_attachment.set_defaults(func=cmd_create_attachment)

    edit = sub.add_parser("edit", help="Edit an item or folder")
    edit_sub = edit.add_subparsers(dest="edit_command", required=True)

    edit_item = edit_sub.add_parser("item", help="Update fields of an existing item")
    edit_item.add_argument("id")
    edit_item.add_argument("--name")
    edit_item.add_argument("--favorite", action="store_true", default=None)
    _add_item_content_flags(edit_item)
    edit_item.set_defaults(func=cmd_edit_item)

    edit_folder = edit_sub.add_parser("folder", help="Rename a folder")
    edit_folder.add_argument("id")
    edit_folder.add_argument("--name", required=True)
    edit_folder.set_defaults(func=cmd_edit_folder)

    delete = sub.add_parser("delete", help="Send an object to the trash (or destroy it)")
    delete.add_argument("object", choices=("item", "attachment", "folder", "org-collection"))
    delete.add_argument("id")
    delete.add_argument("--itemid", help="Required for attachments")
    delete.add_argument("--organizationid", help="Required for org-collections")
    delete.add_argument("--permanent", action="store_true", help="Bypass the trash — irreversible")
    delete.add_argument("--yes", action="store_true", help="Confirm the deletion")
    delete.add_argument(
        "--i-understand-this-is-irreversible",
        action="store_true",
        help="Second confirmation, required with --permanent",
    )
    delete.set_defaults(func=cmd_delete)

    restore = sub.add_parser("restore", help="Restore an item from the trash")
    restore.add_argument("id")
    restore.set_defaults(func=cmd_restore)

    send = sub.add_parser("send", help="Bitwarden Send — ephemeral sharing")
    send_sub = send.add_subparsers(dest="send_command", required=True)

    send_create = send_sub.add_parser("create", help="Create a text or file Send")
    send_create.add_argument("--name", required=True)
    send_create.add_argument("--text")
    send_create.add_argument("--file")
    send_create.add_argument("--hidden", action="store_true", help="Hide the text by default")
    send_create.add_argument("--days", type=int, default=7, help="Delete after N days")
    send_create.add_argument("--max-access", type=int)
    send_create.add_argument("--notes")
    send_create.add_argument("--password")
    send_create.add_argument("--password-stdin", action="store_true")
    send_create.set_defaults(func=cmd_send_create)

    send_list = send_sub.add_parser("list", help="List your Sends")
    send_list.add_argument("--reveal", action="store_true")
    send_list.set_defaults(func=cmd_send_list)

    send_get = send_sub.add_parser("get", help="Get one Send")
    send_get.add_argument("id")
    send_get.add_argument("--reveal", action="store_true")
    send_get.set_defaults(func=cmd_send_get)

    send_delete = send_sub.add_parser("delete", help="Delete a Send")
    send_delete.add_argument("id")
    send_delete.add_argument("--yes", action="store_true")
    send_delete.set_defaults(func=cmd_send_delete)

    receive = sub.add_parser("receive", help="Access a Send from its URL")
    receive.add_argument("url")
    receive.add_argument("--password")
    receive.add_argument("--password-stdin", action="store_true")
    _add_secret_output_flags(receive)
    receive.set_defaults(func=cmd_receive)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except BitwardenError as exc:
        payload: dict[str, Any] = {"error": True, "code": exc.code, "message": str(exc)}
        if exc.detail is not None:
            payload["detail"] = exc.detail
        if exc.code == "locked":
            payload["unlock_command"] = bw.unlock_hint()
        _print(payload)
        return 1
    except Exception as exc:  # noqa: BLE001 — stdout must stay JSON for the agent
        if os.environ.get("BITWARDEN_SKILL_DEBUG"):
            raise
        # Exception text can embed argv, and argv can embed secrets: report the type only.
        _print(
            {
                "error": True,
                "code": "internal_error",
                "exception": type(exc).__name__,
                "hint": "re-run with BITWARDEN_SKILL_DEBUG=1 to get the traceback",
            }
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
