"""Kibana dashboards."""

from __future__ import annotations

import argparse
from typing import Any

from base_kibana import BaseKibana
from model.dashboard import Dashboard


class KibanaDashboard(BaseKibana):
    def list_dashboards(self) -> dict:
        resp = self.client().search(
            index=".kibana*",
            query={"term": {"type": "dashboard"}},
            source=["dashboard.title", "dashboard.description", "updated_at"],
            size=10000,
            ignore_unavailable=True,
        )
        body = resp.body
        hits = (body.get("hits") or {}).get("hits") or []
        total = (body.get("hits") or {}).get("total") or {}
        count = total.get("value", len(hits)) if isinstance(total, dict) else total
        dashboards = []
        for hit in hits:
            src = hit.get("_source") or {}
            dash = src.get("dashboard") or {}
            raw_id = str(hit.get("_id") or "")
            so_id = (
                raw_id.split(":", 1)[-1]
                if raw_id.startswith("dashboard:")
                else raw_id
            )
            dashboards.append(
                {
                    "id": so_id,
                    "title": dash.get("title"),
                    "description": dash.get("description") or "",
                    "updated_at": src.get("updated_at"),
                }
            )
        return {"total": count, "dashboards": dashboards}

    def get_dashboard(self, dashboard_id: str) -> Any:
        return self._kibana_request("GET", f"/api/dashboards/{dashboard_id}")

    def create_dashboard(self, dashboard: Dashboard | dict) -> Any:
        body = self._dashboard_body(dashboard)
        return self._kibana_request("POST", "/api/dashboards", json_body=body)

    def update_dashboard(self, dashboard_id: str, dashboard: Dashboard | dict) -> Any:
        body = self._dashboard_body(dashboard)
        return self._kibana_request(
            "PUT", f"/api/dashboards/{dashboard_id}", json_body=body
        )

    @staticmethod
    def _dashboard_body(dashboard: Dashboard | dict) -> dict:
        if isinstance(dashboard, dict):
            dashboard = Dashboard.from_dict(dashboard)
        return dashboard.to_dict()

    def cmd_list(self, _: argparse.Namespace) -> None:
        self.dump(self.list_dashboards())
        return None

    def cmd_get(self, args: argparse.Namespace) -> None:
        self.dump(self.get_dashboard(args.id))
        return None

    def cmd_create(self, args: argparse.Namespace) -> None:
        self._dump_write(lambda: self.create_dashboard(self._parse_json(args.json)))
        return None

    def cmd_update(self, args: argparse.Namespace) -> None:
        self._dump_write(
            lambda: self.update_dashboard(args.id, self._parse_json(args.json))
        )
        return None

    @staticmethod
    def register_cmds(cmds: argparse._SubParsersAction) -> None:
        client = KibanaDashboard()
        dash = cmds.add_parser("dashboard", help="Dashboards")
        dash_cmds = dash.add_subparsers(required=True)
        dash_cmds.add_parser("list", help="List all dashboards").set_defaults(
            func=client.cmd_list
        )

        d_get = dash_cmds.add_parser("get", help="GET /api/dashboards/:id")
        d_get.add_argument("id", help="Dashboard id")
        d_get.set_defaults(func=client.cmd_get)

        d_create = dash_cmds.add_parser("create", help="POST /api/dashboards")
        d_create.add_argument("--json", required=True, help="Dashboard JSON body")
        d_create.set_defaults(func=client.cmd_create)

        d_update = dash_cmds.add_parser(
            "update", help="PUT /api/dashboards/:id (full replace)"
        )
        d_update.add_argument("id", help="Dashboard id")
        d_update.add_argument("--json", required=True, help="Dashboard JSON body")
        d_update.set_defaults(func=client.cmd_update)
