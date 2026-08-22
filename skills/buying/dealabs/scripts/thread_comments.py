"""Dealabs thread comments."""

from __future__ import annotations

import argparse
import json
from typing import Any

from dealabs import API_THREAD_COMMENTS, Dealabs


def dump(data: Any) -> None:
    print(json.dumps(data, indent=2, default=str, ensure_ascii=False))


class ThreadComments:
    def __init__(self, api: Dealabs | None = None) -> None:
        self.api = api or Dealabs()

    def list_comments(
        self,
        thread_id: str,
        *,
        page: int = 0,
        limit: int = 50,
        order: str | None = None,
    ) -> Any:
        return self.api.request(
            API_THREAD_COMMENTS.format(thread_id=thread_id),
            params={"page": page, "limit": limit, "order": order},
        )

    def cmd_list(self, args: argparse.Namespace) -> None:
        dump(
            self.list_comments(
                args.thread_id,
                page=args.page,
                limit=args.limit,
                order=args.order,
            )
        )

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = ThreadComments()
        p = sub.add_parser("thread-comments", help="List comments on a Dealabs thread")
        inner = p.add_subparsers(required=True)

        listing = inner.add_parser("list", help="GET thread/{thread_id}/comments")
        listing.add_argument("thread_id", help="Thread id")
        listing.add_argument("--page", type=int, default=0)
        listing.add_argument("--limit", type=int, default=50)
        listing.add_argument("--order", help="Comment sort (e.g. new)")
        listing.set_defaults(func=client.cmd_list)
