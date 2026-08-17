"""ZIA URL categories — list, get, create, add/remove URLs, delete."""

from __future__ import annotations

import argparse
from typing import Any

from zia.client import ZiaClient


class UrlCategoriesClient(ZiaClient):
    @staticmethod
    def validate_urls(urls: list[str]) -> list[str]:
        cleaned: list[str] = []
        for raw in urls:
            value = (raw or "").strip()
            if not value:
                raise ValueError("URL must not be empty")
            cleaned.append(value)
        if not cleaned:
            raise ValueError("at least one URL is required")
        return cleaned

    def list_url_categories(
        self, *, cfg: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        with self.get_client(cfg) as client:
            categories, _, err = client.zia.url_categories.list_categories()
            if err:
                raise RuntimeError(f"Failed to list URL categories: {err}")
            return self.records(categories)

    def get_url_category(
        self,
        *,
        category_id: str | None = None,
        category_name: str | None = None,
        cfg: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not category_id and not category_name:
            raise ValueError("category_id or category_name is required")

        if category_id:
            with self.get_client(cfg) as client:
                cat, _, err = client.zia.url_categories.get_category(category_id)
                if err:
                    raise RuntimeError(
                        f"Failed to get URL category {category_id}: {err}"
                    )
                if cat is None:
                    raise RuntimeError(f"URL category not found: {category_id}")
                return cat.as_dict() if hasattr(cat, "as_dict") else dict(cat)

        needle = (category_name or "").strip().casefold()
        for cat in self.list_url_categories(cfg=cfg):
            configured = str(cat.get("configured_name") or "").casefold()
            cid = str(cat.get("id") or "").casefold()
            if configured == needle or cid == needle:
                return cat
        raise RuntimeError(f"URL category not found: {category_name!r}")

    def resolve_url_category_ids(
        self,
        *,
        category_ids: list[str] | None = None,
        category_names: list[str] | None = None,
        cfg: dict[str, Any] | None = None,
    ) -> list[str]:
        found: list[str] = []
        for cid in category_ids or []:
            value = str(cid).strip()
            if value:
                found.append(value)
        names = [str(n).strip() for n in (category_names or []) if str(n).strip()]
        for name in names:
            cat = self.get_url_category(category_name=name, cfg=cfg)
            found.append(str(cat["id"]))
        seen: set[str] = set()
        out: list[str] = []
        for cid in found:
            if cid not in seen:
                seen.add(cid)
                out.append(cid)
        return out

    def create_url_category(
        self,
        name: str,
        *,
        urls: list[str] | None = None,
        ip_ranges: list[str] | None = None,
        keywords: list[str] | None = None,
        super_category: str = "USER_DEFINED",
        description: str | None = None,
        cfg: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not name or not name.strip():
            raise ValueError("name is required to create a URL category")
        if not urls and not ip_ranges and not keywords:
            raise ValueError(
                "provide at least --url, --ip-range, or --keyword "
                "(required by the ZIA API)"
            )

        kwargs: dict[str, Any] = {
            "configured_name": name.strip(),
            "custom_category": True,
        }
        if urls:
            kwargs["urls"] = self.validate_urls(urls)
        if ip_ranges:
            kwargs["ip_ranges"] = ip_ranges
        if keywords:
            kwargs["keywords"] = keywords
        if description:
            kwargs["description"] = description

        with self.get_client(cfg) as client:
            created, _, err = client.zia.url_categories.add_url_category(
                super_category=super_category,
                **kwargs,
            )
            if err:
                raise RuntimeError(f"Failed to create URL category {name!r}: {err}")
            payload = (
                created.as_dict() if hasattr(created, "as_dict") else dict(created)
            )
        return self.with_activation(payload)

    def add_urls_to_category(
        self,
        urls: list[str],
        *,
        category_id: str | None = None,
        category_name: str | None = None,
        cfg: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not urls:
            raise ValueError("at least one URL is required")
        urls = self.validate_urls(urls)
        cat = self.get_url_category(
            category_id=category_id, category_name=category_name, cfg=cfg
        )
        cid = str(cat["id"])
        configured_name = cat.get("configured_name") or cat.get("id")

        with self.get_client(cfg) as client:
            updated, _, err = client.zia.url_categories.add_urls_to_category(
                category_id=cid,
                configured_name=configured_name,
                urls=urls,
            )
            if err:
                raise RuntimeError(f"Failed to add URLs to category {cid}: {err}")
            payload = (
                updated.as_dict() if hasattr(updated, "as_dict") else dict(updated)
            )
        return self.with_activation(payload)

    def remove_urls_from_category(
        self,
        urls: list[str],
        *,
        category_id: str | None = None,
        category_name: str | None = None,
        cfg: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not urls:
            raise ValueError("at least one URL is required")
        cat = self.get_url_category(
            category_id=category_id, category_name=category_name, cfg=cfg
        )
        cid = str(cat["id"])
        configured_name = cat.get("configured_name") or cat.get("id")

        with self.get_client(cfg) as client:
            updated, _, err = client.zia.url_categories.delete_urls_from_category(
                category_id=cid,
                configured_name=configured_name,
                urls=urls,
            )
            if err:
                raise RuntimeError(
                    f"Failed to remove URLs from category {cid}: {err}"
                )
            payload = (
                updated.as_dict() if hasattr(updated, "as_dict") else dict(updated)
            )
        return self.with_activation(payload)

    def delete_url_category(
        self,
        *,
        category_id: str | None = None,
        category_name: str | None = None,
        cfg: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        cat = self.get_url_category(
            category_id=category_id, category_name=category_name, cfg=cfg
        )
        cid = str(cat["id"])
        name = cat.get("configured_name") or cid

        with self.get_client(cfg) as client:
            _, _, err = client.zia.url_categories.delete_category(cid)
            if err:
                raise RuntimeError(f"Failed to delete URL category {cid}: {err}")
        return self.with_activation(
            {"deleted": True, "id": cid, "configured_name": name}
        )

    def cmd_list(self, args: argparse.Namespace) -> None:
        self.dump(self.list_url_categories(cfg=self.cfg_from_args(args)))
        return None

    def cmd_get(self, args: argparse.Namespace) -> None:
        self.dump(
            self.get_url_category(
                category_id=args.id or None,
                category_name=args.name or None,
                cfg=self.cfg_from_args(args),
            )
        )
        return None

    def cmd_create(self, args: argparse.Namespace) -> None:
        self.dump(
            self.create_url_category(
                args.name,
                urls=args.url,
                ip_ranges=args.ip_range,
                keywords=args.keyword,
                super_category=args.super_category,
                description=args.description or None,
                cfg=self.cfg_from_args(args),
            )
        )
        return None

    def cmd_add_urls(self, args: argparse.Namespace) -> None:
        self.dump(
            self.add_urls_to_category(
                args.url or [],
                category_id=args.id or None,
                category_name=args.name or None,
                cfg=self.cfg_from_args(args),
            )
        )
        return None

    def cmd_remove_urls(self, args: argparse.Namespace) -> None:
        self.dump(
            self.remove_urls_from_category(
                args.url or [],
                category_id=args.id or None,
                category_name=args.name or None,
                cfg=self.cfg_from_args(args),
            )
        )
        return None

    def cmd_delete(self, args: argparse.Namespace) -> None:
        self.dump(
            self.delete_url_category(
                category_id=args.id or None,
                category_name=args.name or None,
                cfg=self.cfg_from_args(args),
            )
        )
        return None

    @staticmethod
    def _add_category_ref(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--id", help="Category id (e.g. CUSTOM_01)")
        parser.add_argument("--name", help="configured_name")

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = UrlCategoriesClient()
        overrides = argparse.ArgumentParser(add_help=False)
        ZiaClient.add_overrides(overrides)

        p = sub.add_parser("url-categories", help="ZIA URL categories")
        cmds = p.add_subparsers(required=True)

        cmds.add_parser(
            "list", parents=[overrides], help="List URL categories"
        ).set_defaults(func=client.cmd_list)

        u_get = cmds.add_parser("get", parents=[overrides], help="Get a URL category")
        UrlCategoriesClient._add_category_ref(u_get)
        u_get.set_defaults(func=client.cmd_get)

        u_create = cmds.add_parser(
            "create", parents=[overrides], help="Create a custom URL category"
        )
        u_create.add_argument("name", help="configured_name")
        u_create.add_argument("--url", action="append", help="URL (repeatable)")
        u_create.add_argument(
            "--ip-range", action="append", help="IP range (repeatable)"
        )
        u_create.add_argument(
            "--keyword", action="append", help="Keyword (repeatable)"
        )
        u_create.add_argument("--super-category", default="USER_DEFINED")
        u_create.add_argument("--description", default="")
        u_create.set_defaults(func=client.cmd_create)

        u_add = cmds.add_parser(
            "add-urls", parents=[overrides], help="Add URLs to a category"
        )
        UrlCategoriesClient._add_category_ref(u_add)
        u_add.add_argument("--url", action="append", required=True)
        u_add.set_defaults(func=client.cmd_add_urls)

        u_rm = cmds.add_parser(
            "remove-urls", parents=[overrides], help="Remove URLs from a category"
        )
        UrlCategoriesClient._add_category_ref(u_rm)
        u_rm.add_argument("--url", action="append", required=True)
        u_rm.set_defaults(func=client.cmd_remove_urls)

        u_del = cmds.add_parser(
            "delete", parents=[overrides], help="Delete a custom URL category"
        )
        UrlCategoriesClient._add_category_ref(u_del)
        u_del.set_defaults(func=client.cmd_delete)
