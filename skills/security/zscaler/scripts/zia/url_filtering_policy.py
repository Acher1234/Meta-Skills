"""ZIA URL Filtering Policy — list, get, create, update, delete."""

from __future__ import annotations

import argparse
from typing import Any

from zia.client import ZiaClient
from zia.url_categories import UrlCategoriesClient
from zia.users import UsersClient

URL_FILTERING_ACTIONS = frozenset(
    {"ANY", "NONE", "BLOCK", "CAUTION", "ALLOW", "ICAP_RESPONSE"}
)
URL_FILTERING_REQUEST_METHODS = (
    "CONNECT",
    "DELETE",
    "GET",
    "HEAD",
    "OPTIONS",
    "OTHER",
    "POST",
    "PUT",
    "TRACE",
)
URL_FILTERING_DEFAULT_PROTOCOLS = ("ANY_RULE",)
URL_FILTERING_DEFAULT_DEVICE_TRUST_LEVELS = (
    "UNKNOWN_DEVICETRUSTLEVEL",
    "LOW_TRUST",
    "MEDIUM_TRUST",
    "HIGH_TRUST",
)
URL_FILTERING_DEFAULT_USER_AGENT_TYPES = (
    "OPERA",
    "FIREFOX",
    "MSIE",
    "MSEDGE",
    "CHROME",
    "SAFARI",
    "MSCHREDGE",
    "OTHER",
)


class UrlFilteringPolicyClient(ZiaClient):
    @staticmethod
    def _to_dict(item: Any) -> dict[str, Any]:
        if item is None:
            return {}
        if hasattr(item, "as_dict"):
            return item.as_dict()
        return dict(item)

    @staticmethod
    def _url_filtering_api(client: Any) -> Any:
        api = getattr(client.zia, "url_filtering", None) or getattr(
            client.zia, "url_filtering_rules", None
        )
        if api is None:
            raise RuntimeError("ZIA URL filtering API is not available on this client")
        return api

    @staticmethod
    def _entity_ids(value: Any) -> list:
        ids: list = []
        for item in value or []:
            if isinstance(item, dict):
                eid = item.get("id")
                if eid is not None:
                    ids.append(eid)
            elif item is not None:
                ids.append(item)
        return ids

    @staticmethod
    def _normalize_url_filtering_action(action: str) -> str:
        value = (action or "").strip().upper().replace(" ", "_")
        aliases = {"ALLOW_AND_SCAN": "ALLOW", "ALLOWANDSCAN": "ALLOW"}
        value = aliases.get(value, value)
        if value not in URL_FILTERING_ACTIONS:
            raise ValueError(
                f"invalid action {action!r}; expected one of {sorted(URL_FILTERING_ACTIONS)}"
            )
        return value

    @staticmethod
    def _normalize_request_methods(methods: list[str] | None) -> list[str]:
        if not methods:
            return list(URL_FILTERING_REQUEST_METHODS)
        allowed = set(URL_FILTERING_REQUEST_METHODS)
        out: list[str] = []
        for raw in methods:
            value = str(raw).strip().upper()
            if value not in allowed:
                raise ValueError(f"invalid request method: {raw!r}")
            out.append(value)
        return out

    def list_url_filtering_rules(
        self,
        search: str | None = None,
    ) -> list[dict[str, Any]]:
        with self.get_client() as client:
            rules, _, err = self._url_filtering_api(client).list_rules()
            if err:
                raise RuntimeError(f"Failed to list URL filtering rules: {err}")
            result = [self._to_dict(rule) for rule in (rules or [])]
        if search and search.strip():
            needle = search.strip().casefold()
            result = [
                rule
                for rule in result
                if needle in str(rule.get("name") or "").casefold()
                or needle == str(rule.get("id") or "").casefold()
            ]
        return result

    def get_url_filtering_rule(
        self,
        *,
        rule_id: int | str | None = None,
        rule_name: str | None = None
    ) -> dict[str, Any]:
        if rule_id is not None and str(rule_id).strip():
            with self.get_client() as client:
                rule, _, err = self._url_filtering_api(client).get_rule(int(rule_id))
                if err:
                    raise RuntimeError(
                        f"Failed to get URL filtering rule {rule_id}: {err}"
                    )
                if rule is None:
                    raise RuntimeError(f"URL filtering rule not found: {rule_id}")
                return self._to_dict(rule)

        if not rule_name or not rule_name.strip():
            raise ValueError("rule_id or rule_name is required")

        needle = rule_name.strip().casefold()
        matches = [
            rule
            for rule in self.list_url_filtering_rules(rule_name)
            if str(rule.get("name") or "").casefold() == needle
        ]
        if not matches:
            matches = [
                rule
                for rule in self.list_url_filtering_rules()
                if str(rule.get("name") or "").casefold() == needle
            ]
        if not matches:
            raise RuntimeError(f"URL filtering rule not found: {rule_name!r}")
        if len(matches) > 1:
            ids = ", ".join(str(rule.get("id")) for rule in matches)
            raise RuntimeError(
                f"multiple URL filtering rules named {rule_name!r}: {ids}"
            )
        return matches[0]

    def _url_filtering_payload_from_current(
        self, current: dict[str, Any]
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": current.get("name"),
            "order": current.get("order"),
            "rank": current.get("rank") if current.get("rank") is not None else 7,
            "state": current.get("state") or "ENABLED",
            "action": current.get("action"),
            "protocols": current.get("protocols")
            or list(URL_FILTERING_DEFAULT_PROTOCOLS),
            "url_categories": current.get("url_categories") or [],
            "request_methods": current.get("request_methods")
            or list(URL_FILTERING_REQUEST_METHODS),
        }
        if current.get("description") is not None:
            payload["description"] = current.get("description")
        if current.get("url_categories2"):
            payload["url_categories2"] = current.get("url_categories2")
        if current.get("device_trust_levels"):
            payload["device_trust_levels"] = current.get("device_trust_levels")
        if current.get("user_agent_types"):
            payload["user_agent_types"] = current.get("user_agent_types")
        if "block_override" in current:
            payload["block_override"] = bool(current.get("block_override"))
        if "ciparule" in current:
            payload["ciparule"] = bool(current.get("ciparule"))
        groups = self._entity_ids(current.get("groups"))
        if groups:
            payload["groups"] = groups
        users = self._entity_ids(current.get("users"))
        if users:
            payload["users"] = users
        departments = self._entity_ids(current.get("departments"))
        if departments:
            payload["departments"] = departments
        return payload

    def create_url_filtering_rule(
        self,
        name: str,
        *,
        action: str,
        url_category_ids: list[str] | None = None,
        url_category_names: list[str] | None = None,
        request_methods: list[str] | None = None,
        group_ids: list[int | str] | None = None,
        group_names: list[str] | None = None,
        user_ids: list[int | str] | None = None,
        usernames: list[str] | None = None,
        order: int | None = None,
        rank: int = 7,
        state: str = "ENABLED",
        description: str | None = None,
        protocols: list[str] | None = None
    ) -> dict[str, Any]:
        name = (name or "").strip()
        if not name:
            raise ValueError("name is required")
        state_norm = (state or "ENABLED").strip().upper()
        if state_norm not in ("ENABLED", "DISABLED"):
            raise ValueError("state must be ENABLED or DISABLED")
        categories = UrlCategoriesClient().resolve_url_category_ids(
            category_ids=url_category_ids,
            category_names=url_category_names,
        )
        if not categories:
            raise ValueError(
                "at least one URL category is required (--category-id / --category-name)"
            )
        kwargs: dict[str, Any] = {
            "name": name,
            "action": self._normalize_url_filtering_action(action),
            "state": state_norm,
            "rank": int(rank),
            "url_categories": categories,
            "request_methods": self._normalize_request_methods(request_methods),
            "protocols": [
                str(proto).strip().upper()
                for proto in (protocols or list(URL_FILTERING_DEFAULT_PROTOCOLS))
                if str(proto).strip()
            ]
            or list(URL_FILTERING_DEFAULT_PROTOCOLS),
            "device_trust_levels": list(URL_FILTERING_DEFAULT_DEVICE_TRUST_LEVELS),
            "user_agent_types": list(URL_FILTERING_DEFAULT_USER_AGENT_TYPES),
        }
        if description:
            kwargs["description"] = description
        if order is not None:
            kwargs["order"] = int(order)
        if group_ids or group_names:
            groups = UsersClient().resolve_group_ids(
                group_ids=group_ids, group_names=group_names
            )
            kwargs["groups"] = [group["id"] for group in groups]
        if user_ids or usernames:
            users = UsersClient().resolve_user_ids(
                user_ids=user_ids, usernames=usernames
            )
            if users:
                kwargs["users"] = users
        with self.get_client() as client:
            created, _, err = self._url_filtering_api(client).add_rule(**kwargs)
            if err:
                raise RuntimeError(
                    f"Failed to create URL filtering rule {name!r}: {err}"
                )
            payload = self._to_dict(created)
        return self.with_activation(payload)

    def update_url_filtering_rule(
        self,
        *,
        rule_id: int | str | None = None,
        rule_name: str | None = None,
        name: str | None = None,
        action: str | None = None,
        url_category_ids: list[str] | None = None,
        url_category_names: list[str] | None = None,
        request_methods: list[str] | None = None,
        group_ids: list[int | str] | None = None,
        group_names: list[str] | None = None,
        user_ids: list[int | str] | None = None,
        usernames: list[str] | None = None,
        order: int | None = None,
        rank: int | None = None,
        state: str | None = None,
        description: str | None = None
    ) -> dict[str, Any]:
        current = self.get_url_filtering_rule(
            rule_id=rule_id, rule_name=rule_name
        )
        rid = current["id"]
        kwargs = self._url_filtering_payload_from_current(current)
        if name is not None and str(name).strip():
            kwargs["name"] = str(name).strip()
        if action is not None:
            kwargs["action"] = self._normalize_url_filtering_action(action)
        if order is not None:
            kwargs["order"] = int(order)
        if rank is not None:
            kwargs["rank"] = int(rank)
        if state is not None:
            state_norm = state.strip().upper()
            if state_norm not in ("ENABLED", "DISABLED"):
                raise ValueError("state must be ENABLED or DISABLED")
            kwargs["state"] = state_norm
        if description is not None:
            kwargs["description"] = description
        if request_methods is not None:
            kwargs["request_methods"] = self._normalize_request_methods(
                request_methods
            )
        if url_category_ids is not None or url_category_names is not None:
            categories = UrlCategoriesClient().resolve_url_category_ids(
                category_ids=url_category_ids,
                category_names=url_category_names,
            )
            if not categories:
                raise ValueError(
                    "at least one URL category is required to replace url_categories"
                )
            kwargs["url_categories"] = categories
        if group_ids is not None or group_names is not None:
            if not group_ids and not group_names:
                kwargs.pop("groups", None)
            else:
                groups = UsersClient().resolve_group_ids(
                    group_ids=group_ids or [],
                    group_names=group_names or [],
                )
                kwargs["groups"] = [group["id"] for group in groups]
        if user_ids is not None or usernames is not None:
            users = UsersClient().resolve_user_ids(
                user_ids=user_ids or [], usernames=usernames or []
            )
            if users:
                kwargs["users"] = users
            else:
                kwargs.pop("users", None)
        with self.get_client() as client:
            updated, _, err = self._url_filtering_api(client).update_rule(
                str(rid), **kwargs
            )
            if err:
                raise RuntimeError(f"Failed to update URL filtering rule {rid}: {err}")
            payload = self._to_dict(updated)
        return self.with_activation(payload)

    def delete_url_filtering_rule(
        self,
        *,
        rule_id: int | str | None = None,
        rule_name: str | None = None
    ) -> dict[str, Any]:
        current = self.get_url_filtering_rule(
            rule_id=rule_id, rule_name=rule_name
        )
        rid = current["id"]
        with self.get_client() as client:
            _, _, err = self._url_filtering_api(client).delete_rule(str(rid))
            if err:
                raise RuntimeError(f"Failed to delete URL filtering rule {rid}: {err}")
        return self.with_activation(
            {"deleted": True, "id": rid, "name": current.get("name")},
        )

    def cmd_list(self, args: argparse.Namespace) -> None:
        self.dump(
            self.list_url_filtering_rules(
                search=args.search or None
            )
        )
        return None

    def cmd_get(self, args: argparse.Namespace) -> None:
        self.dump(
            self.get_url_filtering_rule(
                rule_id=args.id or None,
                rule_name=args.name or None
            )
        )
        return None

    def cmd_create(self, args: argparse.Namespace) -> None:
        self.dump(
            self.create_url_filtering_rule(
                args.name,
                action=args.action,
                url_category_ids=args.category_id,
                url_category_names=args.category_name,
                request_methods=args.request_method,
                group_ids=args.group_id,
                group_names=args.group_name,
                user_ids=args.user_id,
                usernames=args.user_name,
                order=args.order,
                rank=args.rank,
                state=args.state,
                description=args.description or None,
                protocols=args.protocol
            )
        )
        return None

    def cmd_update(self, args: argparse.Namespace) -> None:
        self.dump(
            self.update_url_filtering_rule(
                rule_id=args.id or None,
                rule_name=args.name or None,
                name=args.new_name or None,
                action=args.action,
                url_category_ids=args.category_id,
                url_category_names=args.category_name,
                request_methods=args.request_method,
                group_ids=args.group_id,
                group_names=args.group_name,
                user_ids=args.user_id,
                usernames=args.user_name,
                order=args.order,
                rank=args.rank,
                state=args.state,
                description=args.description
            )
        )
        return None

    def cmd_delete(self, args: argparse.Namespace) -> None:
        self.dump(
            self.delete_url_filtering_rule(
                rule_id=args.id or None,
                rule_name=args.name or None
            )
        )
        return None

    @staticmethod
    def _add_rule_ref(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--id", help="Rule id")
        parser.add_argument("--name", help="Exact rule name")

    @staticmethod
    def _add_rule_fields(
        parser: argparse.ArgumentParser, *, create: bool
    ) -> None:
        if create:
            parser.add_argument("--action", required=True, help="ALLOW, BLOCK, …")
        else:
            parser.add_argument("--action", help="ALLOW, BLOCK, …")
            parser.add_argument("--new-name", help="Rename the rule")
        parser.add_argument("--category-id", action="append")
        parser.add_argument("--category-name", action="append")
        parser.add_argument("--request-method", action="append")
        parser.add_argument("--group-id", action="append")
        parser.add_argument("--group-name", action="append")
        parser.add_argument("--user-id", action="append")
        parser.add_argument(
            "--user-name",
            action="append",
            help="Directory user name/email (not ZIA__USERNAME)",
        )
        parser.add_argument("--order", type=int)
        parser.add_argument("--rank", type=int, default=7 if create else None)
        parser.add_argument("--state", default="ENABLED" if create else None)
        parser.add_argument("--description")
        if create:
            parser.add_argument("--protocol", action="append")

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = UrlFilteringPolicyClient()
        p = sub.add_parser("url-filtering-policy", help="ZIA URL Filtering Policy")
        cmds = p.add_subparsers(required=True)

        u_list = cmds.add_parser("list", help="List rules")
        u_list.add_argument("--search", default="", help="Filter by name or id")
        u_list.set_defaults(func=client.cmd_list)

        u_get = cmds.add_parser("get", help="Get a rule")
        UrlFilteringPolicyClient._add_rule_ref(u_get)
        u_get.set_defaults(func=client.cmd_get)

        u_create = cmds.add_parser("create", help="Create a rule")
        u_create.add_argument("name", help="Rule name")
        UrlFilteringPolicyClient._add_rule_fields(u_create, create=True)
        u_create.set_defaults(func=client.cmd_create)

        u_update = cmds.add_parser("update", help="Update a rule")
        UrlFilteringPolicyClient._add_rule_ref(u_update)
        UrlFilteringPolicyClient._add_rule_fields(u_update, create=False)
        u_update.set_defaults(func=client.cmd_update)

        u_del = cmds.add_parser("delete", help="Delete a rule")
        UrlFilteringPolicyClient._add_rule_ref(u_del)
        u_del.set_defaults(func=client.cmd_delete)
