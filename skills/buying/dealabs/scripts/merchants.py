"""Dealabs merchants — search, list, get."""

from __future__ import annotations

import argparse
import json
from typing import Any

from dealabs import Dealabs


def dump(data: Any) -> None:
    print(json.dumps(data, indent=2, default=str, ensure_ascii=False))


class Merchants:
    def __init__(self, api: Dealabs | None = None) -> None:
        self.api = api or Dealabs()

    def search(self, query: str, *, page: int = 0, limit: int = 25) -> Any:
        return self.api.search_merchants(
            {"query": query, "page": page, "limit": limit}
        )

    def list_merchants(self, *, page: int = 0, limit: int = 25) -> Any:
        return self.api.list_merchants({"page": page, "limit": limit})

    def get(self, merchant_id: str) -> Any:
        return self.api.get_merchant(merchant_id)

    def cmd_search(self, args: argparse.Namespace) -> None:
        dump(self.search(args.query, page=args.page, limit=args.limit))

    def cmd_list(self, args: argparse.Namespace) -> None:
        dump(self.list_merchants(page=args.page, limit=args.limit))

    def cmd_get(self, args: argparse.Namespace) -> None:
        dump(self.get(args.merchant_id))

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = Merchants()
        p = sub.add_parser("merchants", help="Search, list, and get Dealabs merchants")
        inner = p.add_subparsers(required=True)

        search = inner.add_parser("search", help="GET merchant/search")
        search.add_argument("--query", required=True, help="Merchant name")
        search.add_argument("--page", type=int, default=0)
        search.add_argument("--limit", type=int, default=25)
        search.set_defaults(func=client.cmd_search)

        listing = inner.add_parser("list", help="GET merchant")
        listing.add_argument("--page", type=int, default=0)
        listing.add_argument("--limit", type=int, default=25)
        listing.set_defaults(func=client.cmd_list)

        get = inner.add_parser("get", help="GET merchant/{merchant_id}")
        get.add_argument("merchant_id", help="Merchant id")
        get.set_defaults(func=client.cmd_get)
