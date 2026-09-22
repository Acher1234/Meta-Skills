"""Kibana cases — get, create from alert, attach alert, delete with alerts."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from typing import Any

from alert import Alert
from base_kibana import BaseKibana

CASES_PATH = "/api/cases"
NONE_CONNECTOR = {
    "id": "none",
    "name": "none",
    "type": ".none",
    "fields": None,
}
SEVERITIES = {"low", "medium", "high", "critical"}


def _src_get(source: dict, *keys: str) -> Any:
    for key in keys:
        if key in source and source[key] is not None:
            return source[key]
        cur: Any = source
        ok = True
        for part in key.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                ok = False
                break
        if ok and cur is not None:
            return cur
    return None


class KibanaCase(BaseKibana):
    def get_case(self, case_id: str) -> Any:
        return self._kibana_request("GET", f"{CASES_PATH}/{case_id}")

    def get_case_alerts(self, case_id: str) -> list[dict]:
        data = self._kibana_request("GET", f"{CASES_PATH}/{case_id}/alerts")
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        if isinstance(data, dict):
            items = data.get("alerts") or data.get("items") or []
            if isinstance(items, list):
                return [item for item in items if isinstance(item, dict)]
        return []

    def create_case_from_alert(
        self, alert_id: str, extra: dict[str, Any] | None = None
    ) -> Any:
        hit = Alert().get_alert(alert_id)
        created = self._kibana_request(
            "POST", CASES_PATH, json_body=self._case_create_body(hit, extra or {})
        )
        case_id = created.get("id") if isinstance(created, dict) else None
        if not case_id:
            raise ValueError("case create did not return an id")
        owner = created.get("owner") if isinstance(created, dict) else None
        return self._attach_alert(str(case_id), hit, owner=owner)

    def add_alert(self, case_id: str, alert_id: str) -> Any:
        case = self.get_case(case_id)
        owner = case.get("owner") if isinstance(case, dict) else None
        return self._attach_alert(case_id, Alert().get_alert(alert_id), owner=owner)

    def delete_case(self, case_id: str) -> Any:
        attached = self.get_case_alerts(case_id)
        alerts = self._delete_attached_alerts(attached)
        deleted = self._kibana_request(
            "DELETE",
            CASES_PATH,
            params={"ids": json.dumps([case_id])},
        )
        return {"case": deleted, "alerts": alerts}

    def _attach_alert(
        self,
        case_id: str,
        hit: dict,
        *,
        owner: str | None,
    ) -> Any:
        src = hit.get("_source") if isinstance(hit.get("_source"), dict) else {}
        doc_id = hit.get("_id")
        index = hit.get("_index")
        if not doc_id or not index:
            raise ValueError("alert is missing _index/_id")
        rule_id = _src_get(
            src,
            "kibana.alert.rule.uuid",
            "kibana.alert.rule.rule_id",
            "signal.rule.id",
        )
        rule_name = _src_get(src, "kibana.alert.rule.name", "signal.rule.name")
        return self._kibana_request(
            "POST",
            f"{CASES_PATH}/{case_id}/comments",
            json_body={
                "type": "alert",
                "owner": owner or "securitySolution",
                "alertId": [str(doc_id)],
                "index": [str(index)],
                "rule": {
                    "id": str(rule_id) if rule_id else "unknown",
                    "name": str(rule_name) if rule_name else "unknown",
                },
            },
        )

    @staticmethod
    def _case_create_body(hit: dict, extra: dict[str, Any]) -> dict:
        src = hit.get("_source") if isinstance(hit.get("_source"), dict) else {}
        rule_name = _src_get(src, "kibana.alert.rule.name", "signal.rule.name")
        severity = extra.get("severity") or _src_get(
            src, "kibana.alert.severity", "signal.rule.severity"
        )
        if severity not in SEVERITIES:
            severity = "low"
        body = {
            "title": extra.get("title") or rule_name or f"Alert {hit.get('_id')}",
            "description": extra.get("description")
            or f"Created from alert {hit.get('_id')}",
            "tags": extra["tags"] if extra.get("tags") is not None else [],
            "severity": severity,
            "owner": extra.get("owner") or "securitySolution",
            "connector": extra.get("connector") or NONE_CONNECTOR,
            "settings": extra.get("settings") or {"syncAlerts": True},
            "assignees": extra["assignees"]
            if extra.get("assignees") is not None
            else [],
        }
        known = set(body)
        for key, value in extra.items():
            if key not in known:
                body[key] = value
        return body

    def _delete_attached_alerts(self, attached: list[dict]) -> list[dict]:
        by_index: dict[str, list[str]] = defaultdict(list)
        for item in attached:
            index = item.get("index")
            doc_id = item.get("id")
            if index and doc_id:
                by_index[str(index)].append(str(doc_id))
        results: list[dict] = []
        es = self.client()
        for index, ids in by_index.items():
            resp = es.delete_by_query(
                index=index,
                query={"ids": {"values": ids}},
                conflicts="proceed",
                refresh=True,
                ignore_unavailable=True,
            )
            results.append({"index": index, "ids": ids, "result": resp.body})
        return results

    def cmd_get(self, args: argparse.Namespace) -> None:
        self.dump(self.get_case(args.id))
        return None

    def cmd_create_from_alert(self, args: argparse.Namespace) -> None:
        extra = self._parse_json(args.json) if args.json else {}
        self._dump_write(
            lambda: self.create_case_from_alert(args.alert_id, extra)
        )
        return None

    def cmd_add_alert(self, args: argparse.Namespace) -> None:
        self._dump_write(lambda: self.add_alert(args.id, args.alert_id))
        return None

    def cmd_delete(self, args: argparse.Namespace) -> None:
        self._dump_write(lambda: self.delete_case(args.id))
        return None

    @staticmethod
    def register_cmds(cmds: argparse._SubParsersAction) -> None:
        client = KibanaCase()
        p = cmds.add_parser("case", help="Cases")
        case_cmds = p.add_subparsers(required=True)

        c_get = case_cmds.add_parser("get", help="GET /api/cases/:id")
        c_get.add_argument("id", help="Case id")
        c_get.set_defaults(func=client.cmd_get)

        c_create = case_cmds.add_parser(
            "create-from-alert",
            help="POST /api/cases then attach the alert",
        )
        c_create.add_argument("alert_id", help="Alert id (_id or kibana.alert.uuid)")
        c_create.add_argument(
            "--json",
            help="Optional case JSON (title, description, tags, severity, owner)",
        )
        c_create.set_defaults(func=client.cmd_create_from_alert)

        c_add = case_cmds.add_parser(
            "add-alert", help="POST /api/cases/:id/comments (type=alert)"
        )
        c_add.add_argument("id", help="Case id")
        c_add.add_argument("alert_id", help="Alert id (_id or kibana.alert.uuid)")
        c_add.set_defaults(func=client.cmd_add_alert)

        c_del = case_cmds.add_parser(
            "delete", help="Delete a case and its attached alerts"
        )
        c_del.add_argument("id", help="Case id")
        c_del.set_defaults(func=client.cmd_delete)
