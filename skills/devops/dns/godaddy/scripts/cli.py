#!/usr/bin/env python3
"""GoDaddy Domains v3 CLI — discovery + owned domains + DNS."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from client import GoDaddyClient, GoDaddyError  # noqa: E402
from skill_env import ENV  # noqa: E402


def _print(data: Any) -> None:
    print(json.dumps(data, indent=2, default=str))


def _split_csv(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [part.strip() for part in value.split(",") if part.strip()]


def cmd_env(_: argparse.Namespace) -> int:
    path = ENV.env_path()
    _print(
        {
            "env_path": str(path),
            "exists": path.is_file(),
            "CURRENT_SKILL_DIRECTORY": str(ENV.env_cred().workspace),
        }
    )
    return 0


def cmd_suggest(args: argparse.Namespace) -> int:
    client = GoDaddyClient()
    _print(
        client.suggest(
            query=args.query,
            tlds=_split_csv(args.tlds),
            length_min=args.length_min,
            length_max=args.length_max,
            page_size=args.page_size,
            sources=_split_csv(args.sources),
        )
    )
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    client = GoDaddyClient()
    _print(
        client.check_availability(
            args.domain,
            optimize_for=args.optimize_for,
            isc_code=args.isc_code,
        )
    )
    return 0


def cmd_domain_list(args: argparse.Namespace) -> int:
    client = GoDaddyClient()
    _print(
        client.list_domains(
            statuses=_split_csv(args.statuses),
            status_groups=_split_csv(args.status_groups),
            limit=args.limit,
            marker=args.marker,
            includes=_split_csv(args.includes),
            modified_date=args.modified_date,
            shopper_id=args.shopper_id,
        )
    )
    return 0


def cmd_domain_get(args: argparse.Namespace) -> int:
    client = GoDaddyClient()
    _print(client.get_domain(args.domain))
    return 0


def cmd_dns_list(args: argparse.Namespace) -> int:
    client = GoDaddyClient()
    _print(
        client.dns_list(
            args.zone,
            record_type=args.type,
            name=args.name,
            page=args.page,
            page_size=args.page_size,
            total_required=args.total_required,
        )
    )
    return 0


def cmd_dns_add(args: argparse.Namespace) -> int:
    record: dict[str, Any] = {
        "type": args.type,
        "name": args.name,
        "data": args.data,
        "ttl": args.ttl,
    }
    if args.priority is not None:
        record["priority"] = args.priority
    if args.service:
        record["service"] = args.service
    if args.port is not None:
        record["port"] = args.port
    if args.weight is not None:
        record["weight"] = args.weight
    if args.protocol:
        record["protocol"] = args.protocol
    if args.flag is not None:
        record["flag"] = args.flag
    if args.tag:
        record["tag"] = args.tag
    client = GoDaddyClient()
    _print(client.dns_add(args.zone, record))
    return 0


def cmd_dns_delete(args: argparse.Namespace) -> int:
    client = GoDaddyClient()
    result = client.dns_delete(args.zone, args.record_id)
    _print(result if result is not None else {"ok": True, "deleted": args.record_id})
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="GoDaddy Domains CLI (v1 list + v3 discovery/domains/DNS)"
    )
    sub = p.add_subparsers(dest="command", required=True)

    env = sub.add_parser("env", help="Print SkillCred-resolved .env path")
    env.set_defaults(func=cmd_env)

    domain = sub.add_parser("domain", help="Owned domain records")
    domain_sub = domain.add_subparsers(dest="domain_command", required=True)

    domain_list = domain_sub.add_parser(
        "list",
        help="GET /v1/domains — list all domains for the shopper",
    )
    domain_list.add_argument(
        "--statuses",
        help="Comma-separated status filter, e.g. ACTIVE,CANCELLED_REDEEMABLE",
    )
    domain_list.add_argument(
        "--status-groups",
        help="Comma-separated status groups filter",
    )
    domain_list.add_argument("--limit", type=int, help="Max domains to return")
    domain_list.add_argument(
        "--marker",
        help="Marker domain used as offset for pagination",
    )
    domain_list.add_argument(
        "--includes",
        help="Comma-separated extras: authCode,contacts,nameServers",
    )
    domain_list.add_argument(
        "--modified-date",
        help="ISO datetime — only domains modified since this date",
    )
    domain_list.add_argument(
        "--shopper-id",
        help="X-Shopper-Id (reseller managing domains outside own account)",
    )
    domain_list.set_defaults(func=cmd_domain_list)

    domain_get = domain_sub.add_parser(
        "get",
        help="GET /v3/domains/domain-names/{domain-name} — status, NS, privacy, expiry",
    )
    domain_get.add_argument("domain", help="Domain in punycode A-label form")
    domain_get.set_defaults(func=cmd_domain_get)

    suggest = sub.add_parser(
        "suggest",
        help="GET /v3/domains/suggestions — available domain suggestions",
    )
    suggest.add_argument("--query", help='Natural-language query, e.g. "sunrise bakery"')
    suggest.add_argument("--tlds", help="Comma-separated TLDs, e.g. com,net,shop")
    suggest.add_argument("--length-min", type=int)
    suggest.add_argument("--length-max", type=int)
    suggest.add_argument("--page-size", type=int, default=10)
    suggest.add_argument(
        "--sources",
        help="Comma-separated: EXTENSION,KEYWORD_SPIN,CC_TLD,PREMIUM",
    )
    suggest.set_defaults(func=cmd_suggest)

    check = sub.add_parser(
        "check",
        help="GET /v3/domains/check-availability — indicative availability + pricing",
    )
    check.add_argument("domain", help="Domain in punycode A-label form")
    check.add_argument(
        "--optimize-for",
        choices=("SPEED", "ACCURACY"),
        help="Default SPEED when omitted",
    )
    check.add_argument("--isc-code", help="ISC pricing context")
    check.set_defaults(func=cmd_check)

    dns = sub.add_parser("dns", help="DNS zone records (list / add / delete)")
    dns_sub = dns.add_subparsers(dest="dns_command", required=True)

    dns_list = dns_sub.add_parser("list", help="GET /v3/domains/zones/{zone}/dns-records")
    dns_list.add_argument("zone", help="Zone / domain, e.g. example.com")
    dns_list.add_argument("--type", help="Filter by record type (A, CNAME, MX, …)")
    dns_list.add_argument("--name", help="Filter by host name (@ for apex)")
    dns_list.add_argument("--page", type=int)
    dns_list.add_argument("--page-size", type=int)
    dns_list.add_argument(
        "--total-required",
        action="store_true",
        help="Include totalItems / totalPages when matches exist",
    )
    dns_list.set_defaults(func=cmd_dns_list)

    dns_add = dns_sub.add_parser("add", help="POST /v3/domains/zones/{zone}/dns-records")
    dns_add.add_argument("zone")
    dns_add.add_argument("--type", required=True, help="A, AAAA, CNAME, MX, TXT, …")
    dns_add.add_argument("--name", required=True, help="@ for zone apex")
    dns_add.add_argument("--data", required=True, help="Record value")
    dns_add.add_argument("--ttl", type=int, default=600)
    dns_add.add_argument("--priority", type=int, help="Required for MX / SRV")
    dns_add.add_argument("--service", help="SRV service label")
    dns_add.add_argument("--port", type=int, help="SRV port")
    dns_add.add_argument("--weight", type=int, help="SRV weight")
    dns_add.add_argument("--protocol", help="SRV protocol (_tcp / _udp)")
    dns_add.add_argument("--flag", type=int, help="CAA flag")
    dns_add.add_argument("--tag", help="CAA tag")
    dns_add.set_defaults(func=cmd_dns_add)

    dns_del = dns_sub.add_parser(
        "delete", help="DELETE /v3/domains/zones/{zone}/dns-records/{recordId}"
    )
    dns_del.add_argument("zone")
    dns_del.add_argument("record_id", help="Server-assigned recordId from dns list")
    dns_del.set_defaults(func=cmd_dns_delete)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except GoDaddyError as exc:
        _print({"error": True, "status": exc.status, "body": exc.body})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
