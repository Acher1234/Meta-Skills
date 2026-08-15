"""Hexnode Applications API — https://www.hexnode.com/mobile-device-management/developers/applications/

GET  /applications/                 list_apps
GET  /applications/searchapp/       search_apps
POST /applications/                 add_app
GET  /applications/{id}/            get_app
"""

from __future__ import annotations

import argparse
from typing import Any

from client import ConfigError, HexnodeClient


class ApplicationClient(HexnodeClient):
    def list_apps(
        self,
        *,
        order_by: str | None = None,
        app_type: str | None = None,
        platform: str | None = None,
        page: int | None = None,
        per_page: int | None = None,
    ) -> Any:
        """GET /applications/ — list apps in the portal catalog."""
        return self.request(
            "GET",
            "/applications/",
            params={
                "order_by": order_by,
                "app_type": app_type,
                "platform": platform,
                **self._page_params(page, per_page),
            },
        )

    def search_apps(
        self,
        *,
        keyword: str,
        platform: str,
        country: str | None = None,
    ) -> Any:
        """GET /applications/searchapp/ — search App Store / Play Store."""
        return self.request(
            "GET",
            "/applications/searchapp/",
            params={
                "keyword": keyword,
                "platform": platform,
                "country": country,
            },
        )

    def add_app(self, body: dict[str, Any] | list[dict[str, Any]]) -> Any:
        """POST /applications/ — add app(s) to the catalog.

        Hexnode sample post data is a list of app objects; the shell example
        also accepts a single object. Pass either.
        """
        return self.request("POST", "/applications/", json=body)

    def get_app(self, app_id: int | str) -> Any:
        """GET /applications/{id}/ — retrieve app details."""
        return self.request("GET", f"/applications/{app_id}/")

    def cmd_list(self, args: argparse.Namespace) -> int:
        self.dump(
            self.list_apps(
                order_by=args.order_by,
                app_type=args.app_type,
                platform=args.platform,
                page=args.page,
                per_page=args.per_page,
            )
        )
        return 0

    def cmd_search(self, args: argparse.Namespace) -> int:
        self.dump(
            self.search_apps(
                keyword=args.keyword,
                platform=args.platform,
                country=args.country,
            )
        )
        return 0

    def cmd_add(self, args: argparse.Namespace) -> int:
        if args.file:
            body = self.load_json_file(args.file)
        else:
            missing = [
                name
                for name, val in (
                    ("--name", args.name),
                    ("--app-type", args.app_type),
                    ("--platform", args.platform),
                    ("--category", args.category),
                    ("--icon", args.icon),
                )
                if not val
            ]
            if missing:
                raise ConfigError(
                    "apps add requires --file JSON or flags: " + ", ".join(missing)
                )
            body = {
                "name": args.name,
                "app_type": args.app_type,
                "platform": args.platform,
                "category": args.category,
                "icon": args.icon,
            }
            optional = {
                "identifier": args.identifier,
                "version": args.version,
                "price": args.price,
                "vendor": args.vendor,
                "webapp_url": args.webapp_url,
                "appstore_id": args.appstore_id,
                "bundle_size": args.bundle_size,
                "description": args.description,
                "appstore_url": args.appstore_url,
                "average_user_rating": args.average_user_rating,
                "content_rating": args.content_rating,
            }
            for key, value in optional.items():
                if value is not None:
                    body[key] = value
            if args.remove_with_mdm is not None:
                body["remove_with_mdm"] = args.remove_with_mdm
            if args.prevent_backup is not None:
                body["prevent_backup"] = args.prevent_backup
            body = [body]
        return self.dump_result(self.add_app(body), empty_status=201)

    def cmd_get(self, args: argparse.Namespace) -> int:
        self.dump(self.get_app(args.app_id))
        return 0

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = ApplicationClient()
        p = sub.add_parser("apps", help="Applications API (portal catalog)")
        cmds = p.add_subparsers(required=True)

        a_list = cmds.add_parser("list", help="GET /applications/")
        a_list.add_argument("--order-by", choices=["asc", "desc"])
        a_list.add_argument("--app-type", choices=["store", "web", "enterprise"])
        a_list.add_argument("--platform", choices=["ios", "android"])
        HexnodeClient.add_paging(a_list)
        a_list.set_defaults(func=client.cmd_list)

        a_search = cmds.add_parser("search", help="GET /applications/searchapp/")
        a_search.add_argument("--keyword", required=True, help="App name to search")
        a_search.add_argument(
            "--platform", required=True, choices=["ios", "android"]
        )
        a_search.add_argument("--country", help="ISO alpha-2 country code (e.g. us)")
        a_search.set_defaults(func=client.cmd_search)

        a_add = cmds.add_parser(
            "add",
            help="POST /applications/ — add app to catalog (--file or flags)",
        )
        a_add.add_argument(
            "--file",
            metavar="JSON",
            help="Raw JSON body (object or list); overrides individual flags",
        )
        a_add.add_argument("--name", help="App display name (required without --file)")
        a_add.add_argument("--app-type", choices=["store", "web"])
        a_add.add_argument("--platform", choices=["ios", "android"])
        a_add.add_argument("--category", help="App category")
        a_add.add_argument("--icon", help="Icon URL or base64")
        a_add.add_argument("--identifier", help="Bundle / package id")
        a_add.add_argument("--version")
        a_add.add_argument("--price")
        a_add.add_argument("--vendor")
        a_add.add_argument("--webapp-url", dest="webapp_url")
        a_add.add_argument("--appstore-id", dest="appstore_id", type=int)
        a_add.add_argument("--bundle-size", dest="bundle_size", type=float)
        a_add.add_argument("--description")
        a_add.add_argument("--appstore-url", dest="appstore_url")
        a_add.add_argument("--average-user-rating", dest="average_user_rating")
        a_add.add_argument("--content-rating", dest="content_rating")
        a_add.add_argument(
            "--remove-with-mdm",
            dest="remove_with_mdm",
            action=argparse.BooleanOptionalAction,
            default=None,
        )
        a_add.add_argument(
            "--prevent-backup",
            dest="prevent_backup",
            action=argparse.BooleanOptionalAction,
            default=None,
        )
        a_add.set_defaults(func=client.cmd_add)

        a_get = cmds.add_parser("get", help="GET /applications/{id}/")
        a_get.add_argument("app_id", help="Hexnode application id")
        a_get.set_defaults(func=client.cmd_get)
