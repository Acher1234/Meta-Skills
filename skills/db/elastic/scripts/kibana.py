"""Kibana dashboards (`.kibana` index) and visualizations HTTP API."""

from __future__ import annotations

import argparse
import json
import ssl
from base64 import b64encode
from collections.abc import Callable
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from client import ElasticClient
from model.dashboard import Dashboard
from model.visualization import Visualization
from skill_env import ENV

KIBANA_API_VERSION = "2023-10-31"


class Kibana(ElasticClient):
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

    def list_visualizations(
        self,
        query: str = "",
        page: int | None = None,
        per_page: int = 100,
    ) -> Any:
        if page is not None:
            return self._list_visualizations_page(query, page, per_page)
        items: list = []
        current = 1
        total = None
        while True:
            data = self._list_visualizations_page(query, current, per_page)
            chunk, total = self._visualization_page_items(data)
            if isinstance(data, list):
                return {"total": len(data), "visualizations": data}
            items.extend(chunk)
            if not chunk or (total is not None and len(items) >= total):
                break
            current += 1
        return {
            "total": total if total is not None else len(items),
            "visualizations": items,
        }

    def get_visualization(self, visualization_id: str) -> Any:
        return self._kibana_request("GET", f"/api/visualizations/{visualization_id}")

    def create_visualization(self, visualization: Visualization | dict) -> Any:
        body = self._visualization_body(visualization)
        return self._kibana_request("POST", "/api/visualizations", json_body=body)

    def update_visualization(
        self, visualization_id: str, visualization: Visualization | dict
    ) -> Any:
        body = self._visualization_body(visualization)
        return self._kibana_request(
            "PUT", f"/api/visualizations/{visualization_id}", json_body=body
        )

    def delete_visualization(self, visualization_id: str) -> Any:
        return self._kibana_request(
            "DELETE", f"/api/visualizations/{visualization_id}"
        )

    def _list_visualizations_page(
        self, query: str, page: int, per_page: int
    ) -> Any:
        params: dict[str, Any] = {"page": page, "per_page": per_page}
        if query:
            params["query"] = query
        return self._kibana_request("GET", "/api/visualizations", params=params)

    @staticmethod
    def _visualization_page_items(data: Any) -> tuple[list, int | None]:
        if isinstance(data, list):
            return data, len(data)
        if not isinstance(data, dict):
            return [], None
        chunk = (
            data.get("data")
            or data.get("items")
            or data.get("visualizations")
            or []
        )
        total = data.get("total")
        if isinstance(total, dict):
            total = total.get("value")
        return list(chunk), int(total) if total is not None else None

    @staticmethod
    def _visualization_body(visualization: Visualization | dict) -> dict:
        if isinstance(visualization, dict):
            visualization = Visualization.from_dict(visualization)
        return visualization.to_dict()

    @staticmethod
    def _dashboard_body(dashboard: Dashboard | dict) -> dict:
        if isinstance(dashboard, dict):
            dashboard = Dashboard.from_dict(dashboard)
        return dashboard.to_dict()

    def cmd_dashboard_list(self, _: argparse.Namespace) -> None:
        self.dump(self.list_dashboards())
        return None

    def cmd_dashboard_get(self, args: argparse.Namespace) -> None:
        self.dump(self.get_dashboard(args.id))
        return None

    def cmd_dashboard_create(self, args: argparse.Namespace) -> None:
        self._dump_write(lambda: self.create_dashboard(self._parse_json(args.json)))
        return None

    def cmd_dashboard_update(self, args: argparse.Namespace) -> None:
        self._dump_write(
            lambda: self.update_dashboard(args.id, self._parse_json(args.json))
        )
        return None

    def cmd_visualization_list(self, args: argparse.Namespace) -> None:
        self.dump(
            self.list_visualizations(
                query=args.query or "",
                page=args.page,
                per_page=args.per_page,
            )
        )
        return None

    def cmd_visualization_get(self, args: argparse.Namespace) -> None:
        self.dump(self.get_visualization(args.id))
        return None

    def cmd_visualization_create(self, args: argparse.Namespace) -> None:
        self._dump_write(
            lambda: self.create_visualization(self._parse_json(args.json))
        )
        return None

    def cmd_visualization_update(self, args: argparse.Namespace) -> None:
        self._dump_write(
            lambda: self.update_visualization(args.id, self._parse_json(args.json))
        )
        return None

    def cmd_visualization_delete(self, args: argparse.Namespace) -> None:
        self.dump(self.delete_visualization(args.id))
        return None

    def _dump_write(self, call: Callable[[], Any]) -> None:
        try:
            self.dump(call())
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc

    @staticmethod
    def _parse_json(raw: str) -> dict:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"invalid JSON: {exc}") from exc
        if not isinstance(data, dict):
            raise SystemExit("JSON body must be an object")
        return data

    def _kibana_request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> Any:
        base = ENV.url()
        url = f"{base}{path}"
        if params:
            url = f"{url}?{urlencode(params)}"
        token = b64encode(
            f"{ENV.username()}:{ENV.password()}".encode()
        ).decode()
        data = json.dumps(json_body).encode() if json_body is not None else None
        req = Request(url, data=data, method=method)
        req.add_header("Authorization", f"Basic {token}")
        req.add_header("kbn-xsrf", "true")
        req.add_header("Elastic-Api-Version", KIBANA_API_VERSION)
        req.add_header("Accept", "application/json")
        if json_body is not None:
            req.add_header("Content-Type", "application/json")
        ctx = ssl.create_default_context()
        if not self._verify_certs(base):
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        try:
            with urlopen(req, context=ctx, timeout=60) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else {"ok": True, "status": resp.status}
        except HTTPError as exc:
            raw = exc.read()
            try:
                body = json.loads(raw) if raw else {"error": str(exc)}
            except json.JSONDecodeError:
                body = {"error": raw.decode(errors="replace") or str(exc)}
            self.dump({"ok": False, "status": exc.code, "error": body})
            raise SystemExit(1) from exc

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = Kibana()
        p = sub.add_parser("kibana", help="Kibana saved objects")
        cmds = p.add_subparsers(required=True)

        dash = cmds.add_parser("dashboard", help="Dashboards")
        dash_cmds = dash.add_subparsers(required=True)
        dash_cmds.add_parser("list", help="List all dashboards").set_defaults(
            func=client.cmd_dashboard_list
        )

        d_get = dash_cmds.add_parser("get", help="GET /api/dashboards/:id")
        d_get.add_argument("id", help="Dashboard id")
        d_get.set_defaults(func=client.cmd_dashboard_get)

        d_create = dash_cmds.add_parser("create", help="POST /api/dashboards")
        d_create.add_argument("--json", required=True, help="Dashboard JSON body")
        d_create.set_defaults(func=client.cmd_dashboard_create)

        d_update = dash_cmds.add_parser(
            "update", help="PUT /api/dashboards/:id (full replace)"
        )
        d_update.add_argument("id", help="Dashboard id")
        d_update.add_argument("--json", required=True, help="Dashboard JSON body")
        d_update.set_defaults(func=client.cmd_dashboard_update)

        vis = cmds.add_parser("visualization", help="Visualizations")
        vis_cmds = vis.add_subparsers(required=True)

        v_list = vis_cmds.add_parser("list", help="GET /api/visualizations")
        v_list.add_argument("--query", default="", help="Optional search query")
        v_list.add_argument("--page", type=int, help="Page index (omit to fetch all)")
        v_list.add_argument("--per-page", type=int, default=100)
        v_list.set_defaults(func=client.cmd_visualization_list)

        v_get = vis_cmds.add_parser("get", help="GET /api/visualizations/:id")
        v_get.add_argument("id", help="Visualization id")
        v_get.set_defaults(func=client.cmd_visualization_get)

        v_create = vis_cmds.add_parser("create", help="POST /api/visualizations")
        v_create.add_argument("--json", required=True, help="Visualization JSON body")
        v_create.set_defaults(func=client.cmd_visualization_create)

        v_update = vis_cmds.add_parser(
            "update", help="PUT /api/visualizations/:id (full replace)"
        )
        v_update.add_argument("id", help="Visualization id")
        v_update.add_argument("--json", required=True, help="Visualization JSON body")
        v_update.set_defaults(func=client.cmd_visualization_update)

        v_del = vis_cmds.add_parser("delete", help="DELETE /api/visualizations/:id")
        v_del.add_argument("id", help="Visualization id")
        v_del.set_defaults(func=client.cmd_visualization_delete)
