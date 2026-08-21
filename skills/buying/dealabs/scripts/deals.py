"""Dealabs deals — search, list, get, hot, new."""

from __future__ import annotations

import argparse
import json
from typing import Any

from dealabs import Deal, Dealabs


def dump(data: Any) -> None:
    print(json.dumps(data, indent=2, default=_json_default, ensure_ascii=False))


def _json_default(obj: Any) -> Any:
    if isinstance(obj, Deal):
        return obj.to_dict()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


class Deals:
    def __init__(self, api: Dealabs | None = None) -> None:
        self.api = api or Dealabs()

    def search(self, params: dict[str, Any]) -> Any:
        return self.api.search_deals(params)

    def list_deals(
        self,
        *,
        deal_ids: str | None = None,
        page: int = 0,
        limit: int = 25,
    ) -> Any:
        return self.api.request(
            "thread",
            params={"thread_ids": deal_ids, "page": page, "limit": limit},
        )

    def get(self, deal_id: str) -> Any:
        return self.api.request(f"thread/{deal_id}")

    def hot(self, params: dict[str, Any]) -> Any:
        return self.api.get_hot_deals(params)

    def new(self, params: dict[str, Any]) -> list[Deal]:
        return self.api.get_new_deals(params)

    def cmd_search(self, args: argparse.Namespace) -> None:
        dump(self.search(_search_params(args)))

    def cmd_list(self, args: argparse.Namespace) -> None:
        dump(
            self.list_deals(
                deal_ids=args.deal_ids,
                page=args.page,
                limit=args.limit,
            )
        )

    def cmd_get(self, args: argparse.Namespace) -> None:
        dump(self.get(args.deal_id))

    def cmd_hot(self, args: argparse.Namespace) -> None:
        dump(self.hot(_page_params(args, extra={"days": args.days})))

    def cmd_new(self, args: argparse.Namespace) -> None:
        dump(self.new(_page_params(args)))

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = Deals()
        p = sub.add_parser("deals", help="Search, list, and get Dealabs deals")
        inner = p.add_subparsers(required=True)

        search = inner.add_parser("search", help="GET thread/search")
        search.add_argument("--query", help="Search text")
        search.add_argument(
            "--order-by",
            dest="order_by",
            default="hot",
            choices=("new", "hot", "discussed", "featured"),
        )
        search.add_argument("--type-id", dest="type_id")
        search.add_argument("--group-id", dest="group_id")
        search.add_argument("--merchant-id", dest="merchant_id")
        search.add_argument("--expired")
        search.add_argument("--local")
        search.add_argument("--clearance")
        search.add_argument("--page", type=int, default=0)
        search.add_argument("--limit", type=int, default=50)
        search.set_defaults(func=client.cmd_search)

        listing = inner.add_parser("list", help="GET thread")
        listing.add_argument("--deal-ids", help="Comma-separated deal ids")
        listing.add_argument("--page", type=int, default=0)
        listing.add_argument("--limit", type=int, default=25)
        listing.set_defaults(func=client.cmd_list)

        get = inner.add_parser("get", help="GET thread/{deal_id}")
        get.add_argument("deal_id", help="Deal id")
        get.set_defaults(func=client.cmd_get)

        hot = inner.add_parser("hot", help="GET thread?order_by=hot")
        hot.add_argument("--days", type=int, default=1, help="Window in days (e.g. 1, 7, 30)")
        hot.add_argument("--page", type=int, default=0)
        hot.add_argument("--limit", type=int, default=50)
        hot.set_defaults(func=client.cmd_hot)

        newest = inner.add_parser("new", help="GET thread?order_by=new")
        newest.add_argument("--page", type=int, default=0)
        newest.add_argument("--limit", type=int, default=50)
        newest.set_defaults(func=client.cmd_new)


def _page_params(args: argparse.Namespace, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    params: dict[str, Any] = {"page": args.page, "limit": args.limit}
    if extra:
        params.update(extra)
    return params


def _search_params(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "query": args.query,
        "order_by": args.order_by,
        "type_id": args.type_id,
        "group_id": args.group_id,
        "merchant_id": args.merchant_id,
        "expired": args.expired,
        "local": args.local,
        "clearance": args.clearance,
        "page": args.page,
        "limit": args.limit,
    }
