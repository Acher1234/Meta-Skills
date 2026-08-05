"""Vault read/write commands: list, get, generate, create, edit, delete, restore."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import bw
from cli_io import (
    add_item_content_flags,
    add_secret_output_flags,
    deliver_secret,
    emit,
    parse_fields,
    resolve_password,
)
from bw import BitwardenError

ITEM_TYPES = {"login": 1, "note": 2, "card": 3, "identity": 4}
SCALAR_GETS = {"username", "password", "uri", "totp", "notes", "exposed", "fingerprint"}
SECRET_GETS = {"password", "totp", "notes"}


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
    emit(bw.redact(data, reveal=args.reveal))
    return 0


def cmd_get(args: argparse.Namespace) -> int:
    session = bw.ensure_session()
    command = ["get", args.object, args.id]
    if args.organizationid:
        command += ["--organizationid", args.organizationid]
    if args.object in SCALAR_GETS:
        value = bw.run(command, session=session)
        if args.object in SECRET_GETS:
            emit(deliver_secret(value, args, args.object))
        else:
            emit({"object": args.object, "value": value})
        return 0
    reveal = args.reveal or args.object == "template"
    emit(bw.redact(bw.run_json(command, session=session), reveal=reveal))
    return 0


def cmd_get_attachment(args: argparse.Namespace) -> int:
    session = bw.ensure_session()
    output = str(Path(args.output).expanduser())
    message = bw.run(
        ["get", "attachment", args.filename, "--itemid", args.itemid, "--output", output],
        session=session,
        timeout=300,
    )
    emit({"downloaded": args.filename, "itemid": args.itemid, "output": output, "message": message})
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
    emit(deliver_secret(value, args, "generated"))
    return 0


def _build_item(
    args: argparse.Namespace, session: str, base: dict[str, Any] | None
) -> dict[str, Any]:
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
    password = resolve_password(args)

    if item_type == ITEM_TYPES["login"]:
        login = item.get("login") or {
            "uris": [],
            "username": None,
            "password": None,
            "totp": None,
        }
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

    fields = parse_fields(args.field, 0) + parse_fields(args.hidden_field, 1)
    if fields:
        item["fields"] = (item.get("fields") or []) + fields
    return item


def cmd_create_item(args: argparse.Namespace) -> int:
    session = bw.ensure_session()
    item = _build_item(args, session, None)
    created = bw.run_json(["create", "item"], session=session, stdin=bw.encode(item))
    emit(bw.redact(created, reveal=args.reveal))
    return 0


def cmd_create_folder(args: argparse.Namespace) -> int:
    session = bw.ensure_session()
    template = bw.run_json(["get", "template", "folder"], session=session)
    template["name"] = args.name
    emit(bw.run_json(["create", "folder"], session=session, stdin=bw.encode(template)))
    return 0


def cmd_create_org_collection(args: argparse.Namespace) -> int:
    session = bw.ensure_session()
    template = bw.run_json(["get", "template", "org-collection"], session=session)
    template["organizationId"] = args.organizationid
    template["name"] = args.name
    template["externalId"] = args.external_id or None
    template["groups"] = []
    template["users"] = [
        {"id": user, "readOnly": False, "hidePasswords": False, "manage": True}
        for user in args.manage_user or []
    ]
    created = bw.run_json(
        ["create", "org-collection", "--organizationid", args.organizationid],
        session=session,
        stdin=bw.encode(template),
    )
    emit(created)
    return 0


def cmd_create_attachment(args: argparse.Namespace) -> int:
    session = bw.ensure_session()
    path = str(Path(args.file).expanduser().resolve())
    created = bw.run_json(
        ["create", "attachment", "--file", path, "--itemid", args.itemid],
        session=session,
        timeout=300,
    )
    emit(bw.redact(created, reveal=args.reveal))
    return 0


def cmd_edit_item(args: argparse.Namespace) -> int:
    session = bw.ensure_session()
    current = bw.run_json(["get", "item", args.id], session=session)
    item = _build_item(args, session, current)
    updated = bw.run_json(["edit", "item", args.id], session=session, stdin=bw.encode(item))
    emit(bw.redact(updated, reveal=args.reveal))
    return 0


def cmd_edit_folder(args: argparse.Namespace) -> int:
    session = bw.ensure_session()
    folder = bw.run_json(["get", "folder", args.id], session=session)
    folder["name"] = args.name
    emit(bw.run_json(["edit", "folder", args.id], session=session, stdin=bw.encode(folder)))
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
    emit({"deleted": args.id, "object": args.object, "permanent": bool(args.permanent)})
    return 0


def cmd_restore(args: argparse.Namespace) -> int:
    session = bw.ensure_session()
    bw.run(["restore", "item", args.id], session=session)
    emit({"restored": args.id})
    return 0


def register(sub: argparse._SubParsersAction) -> None:
    lst = sub.add_parser("list", help="List vault objects")
    lst.add_argument(
        "object",
        choices=(
            "items",
            "folders",
            "collections",
            "organizations",
            "org-collections",
            "org-members",
        ),
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
            "item",
            "username",
            "password",
            "uri",
            "totp",
            "notes",
            "exposed",
            "folder",
            "collection",
            "organization",
            "org-collection",
            "template",
            "fingerprint",
        ),
    )
    get.add_argument("id", help="Exact id or unique search term")
    get.add_argument("--organizationid")
    add_secret_output_flags(get)
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
    add_secret_output_flags(gen)
    gen.set_defaults(func=cmd_generate)

    create = sub.add_parser("create", help="Create an item, folder, collection, or attachment")
    create_sub = create.add_subparsers(dest="create_command", required=True)

    create_item = create_sub.add_parser("item", help="Create a login, note, card, or identity")
    create_item.add_argument("--name", required=True)
    create_item.add_argument("--type", choices=tuple(ITEM_TYPES), default="login")
    create_item.add_argument("--favorite", action="store_true", default=None)
    add_item_content_flags(create_item)
    create_item.set_defaults(func=cmd_create_item)

    create_folder = create_sub.add_parser("folder", help="Create a folder")
    create_folder.add_argument("--name", required=True)
    create_folder.set_defaults(func=cmd_create_folder)

    create_collection = create_sub.add_parser(
        "org-collection", help="Create a collection in an organization (shared)"
    )
    create_collection.add_argument("--name", required=True)
    create_collection.add_argument("--organizationid", required=True)
    create_collection.add_argument("--external-id", help="Your own identifier for sync tooling")
    create_collection.add_argument(
        "--manage-user",
        action="append",
        metavar="ORG_MEMBER_ID",
        help="Grant manage access to an org member (repeatable; see `list org-members`)",
    )
    create_collection.set_defaults(func=cmd_create_org_collection)

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
    add_item_content_flags(edit_item)
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
