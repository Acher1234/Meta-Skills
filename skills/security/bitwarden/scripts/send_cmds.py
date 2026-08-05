"""Bitwarden Send — ephemeral sharing and receive."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import bw
from cli_io import add_secret_output_flags, deliver_secret, emit
from bw import BitwardenError


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

    raw = bw.run(command, session=session, stdin=bw.encode(send), timeout=300)
    try:
        created = json.loads(raw)
    except ValueError:
        created = None
    if not isinstance(created, dict):
        emit({"accessUrl": raw, "passwordProtected": bool(password)})
        return 0
    emit(
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
    emit(bw.redact(bw.run_json(["send", "list"], session=session), reveal=args.reveal))
    return 0


def cmd_send_get(args: argparse.Namespace) -> int:
    session = bw.ensure_session()
    emit(bw.redact(bw.run_json(["send", "get", args.id], session=session), reveal=args.reveal))
    return 0


def cmd_send_delete(args: argparse.Namespace) -> int:
    if not args.yes:
        raise BitwardenError(
            "refusing to delete a Send without --yes", code="confirmation_required"
        )
    session = bw.ensure_session()
    bw.run(["send", "delete", args.id], session=session)
    emit({"deleted": args.id, "object": "send"})
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
        emit({"received": args.url, "output": output, "message": message})
        return 0
    content = bw.run(command, session=session, env_extra=env_extra, timeout=300)
    emit(deliver_secret(content, args, "send"))
    return 0


def register(sub: argparse._SubParsersAction) -> None:
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
    add_secret_output_flags(receive)
    receive.set_defaults(func=cmd_receive)
