"""ZIA URL cloud applications — get only."""

from __future__ import annotations

import argparse
from typing import Any

from zia.client import ZiaClient
from zia.url_categories import UrlCategoriesClient


class UrlCloudAppsClient(ZiaClient):
    @staticmethod
    def _cloud_apps_api(client: Any) -> Any:
        zia_svc = client.zia
        api = getattr(zia_svc, "shadow_it_report", None) or getattr(
            zia_svc, "cloud_apps", None
        )
        if api is None:
            raise RuntimeError("ZIA cloud applications API is not available on this client")
        return api

    @staticmethod
    def _matches(item: dict[str, Any], needle: str) -> bool:
        haystacks = (
            item.get("id"),
            item.get("name"),
            item.get("configured_name"),
            item.get("configuredName"),
            item.get("app"),
            item.get("app_name"),
            item.get("appName"),
            item.get("parent"),
            item.get("parent_name"),
            item.get("parentName"),
        )
        return any(needle in str(value or "").casefold() for value in haystacks)

    def list_cloud_apps(
        self,
        search: str | None = None,
    ) -> list[dict[str, Any]]:
        with self.get_client() as client:
            apps, _, err = self._cloud_apps_api(client).list_apps()
            if err:
                raise RuntimeError(f"Failed to list URL cloud applications: {err}")
            result = [self._to_dict(app) for app in (apps or [])]
        if search and search.strip():
            needle = search.strip().casefold()
            result = [app for app in result if self._matches(app, needle)]
        return result

    def get_cloud_app(
        self,
        *,
        app_id: int | str | None = None,
        app_name: str | None = None
    ) -> dict[str, Any]:
        apps = self.list_cloud_apps()
        if app_id is not None and str(app_id).strip():
            key = str(app_id).strip().casefold()
            for app in apps:
                if str(app.get("id") or "").casefold() == key:
                    return app
                if str(app.get("app") or "").casefold() == key:
                    return app
            raise RuntimeError(f"URL cloud application not found: {app_id}")

        if not app_name or not app_name.strip():
            raise ValueError("app_id or app_name is required")

        needle = app_name.strip().casefold()
        matches = [
            app
            for app in apps
            if str(app.get("name") or "").casefold() == needle
            or str(app.get("app_name") or app.get("appName") or "").casefold()
            == needle
        ]
        if not matches:
            raise RuntimeError(f"URL cloud application not found: {app_name!r}")
        if len(matches) > 1:
            ids = ", ".join(str(app.get("id") or app.get("app")) for app in matches)
            raise RuntimeError(
                f"multiple URL cloud applications named {app_name!r}: {ids}"
            )
        return matches[0]

    def cmd_list(self, args: argparse.Namespace) -> None:
        self.dump(
            self.list_cloud_apps(
                search=args.search or None
            )
        )
        return None

    def cmd_get(self, args: argparse.Namespace) -> None:
        self.dump(
            self.get_cloud_app(
                app_id=args.id or None,
                app_name=args.name or None
            )
        )
        return None

    def cmd_categories(self, args: argparse.Namespace) -> None:
        self.dump(
            UrlCategoriesClient().list_url_categories(
                search=args.search or None
            )
        )
        return None

    def cmd_category(self, args: argparse.Namespace) -> None:
        self.dump(
            UrlCategoriesClient().get_url_category(
                category_id=args.id or None,
                category_name=args.name or None
            )
        )
        return None

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = UrlCloudAppsClient()
        p = sub.add_parser(
            "url-cloud-apps", help="ZIA URL cloud apps and categories (get only)"
        )
        cmds = p.add_subparsers(required=True)

        u_list = cmds.add_parser(
            "list", help="List URL cloud applications"
        )
        u_list.add_argument("--search", default="", help="Filter by name or id")
        u_list.set_defaults(func=client.cmd_list)

        u_get = cmds.add_parser(
            "get", help="Get a URL cloud application"
        )
        u_get.add_argument("--id", help="Application id")
        u_get.add_argument("--name", help="Exact application name")
        u_get.set_defaults(func=client.cmd_get)

        u_cats = cmds.add_parser(
            "categories",
            help="List URL categories (via url-categories)",
        )
        u_cats.add_argument("--search", default="", help="Filter by name or id")
        u_cats.set_defaults(func=client.cmd_categories)

        u_cat = cmds.add_parser(
            "category",
            help="Get a URL category (via url-categories)",
        )
        u_cat.add_argument("--id", help="Category id")
        u_cat.add_argument("--name", help="Exact category name")
        u_cat.set_defaults(func=client.cmd_category)
