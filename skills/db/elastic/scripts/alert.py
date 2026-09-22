"""Elastic Security detection alerts (signals)."""

from __future__ import annotations

import argparse
from typing import Any

from base_kibana import BaseKibana
from security_rule import SecurityRule

SEARCH_PATH = "/api/detection_engine/signals/search"


class Alert(BaseKibana):
    def get_alert(self, alert_id: str) -> Any:
        hit = self._find_alert(alert_id)
        if hit is None:
            raise ValueError(f"alert not found: {alert_id}")
        return hit

    def delete_alert(self, alert_id: str) -> Any:
        hit = self.get_alert(alert_id)
        index = hit.get("_index")
        doc_id = hit.get("_id")
        if not index or not doc_id:
            raise ValueError(f"alert is missing _index/_id: {alert_id}")
        resp = self.client().delete_by_query(
            index=index,
            query={"ids": {"values": [doc_id]}},
            conflicts="proceed",
            refresh=True,
        )
        body = resp.body
        if not body.get("deleted"):
            raise ValueError(f"alert not deleted: {alert_id}")
        return body

    def _find_alert(self, alert_id: str) -> Any | None:
        data = self._kibana_request(
            "POST",
            SEARCH_PATH,
            json_body={
                "query": {
                    "bool": {
                        "should": [
                            {"ids": {"values": [alert_id]}},
                            {"term": {"kibana.alert.uuid": alert_id}},
                        ],
                        "minimum_should_match": 1,
                    }
                },
                "size": 1,
            },
        )
        hits = ((data.get("hits") or {}).get("hits") or [])
        return hits[0] if hits else None

    def cmd_get(self, args: argparse.Namespace) -> None:
        self._dump_write(lambda: self.get_alert(args.id))
        return None

    def cmd_delete(self, args: argparse.Namespace) -> None:
        self._dump_write(lambda: self.delete_alert(args.id))
        return None

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = Alert()
        p = sub.add_parser("alert", help="Elastic Security alerts")
        cmds = p.add_subparsers(required=True)

        g = cmds.add_parser("get", help="Get a detection alert by id")
        g.add_argument("id", help="Alert id (_id or kibana.alert.uuid)")
        g.set_defaults(func=client.cmd_get)

        d = cmds.add_parser("delete", help="Delete a detection alert by id")
        d.add_argument("id", help="Alert id (_id or kibana.alert.uuid)")
        d.set_defaults(func=client.cmd_delete)

        SecurityRule.register_cmds(cmds)
