"""Kibana visualizations."""

from __future__ import annotations

import argparse
from typing import Any

from base_kibana import BaseKibana
from model.visualization import Visualization


class KibanaVisualization(BaseKibana):
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

    def cmd_list(self, args: argparse.Namespace) -> None:
        self.dump(
            self.list_visualizations(
                query=args.query or "",
                page=args.page,
                per_page=args.per_page,
            )
        )
        return None

    def cmd_get(self, args: argparse.Namespace) -> None:
        self.dump(self.get_visualization(args.id))
        return None

    def cmd_create(self, args: argparse.Namespace) -> None:
        self._dump_write(
            lambda: self.create_visualization(self._parse_json(args.json))
        )
        return None

    def cmd_update(self, args: argparse.Namespace) -> None:
        self._dump_write(
            lambda: self.update_visualization(args.id, self._parse_json(args.json))
        )
        return None

    def cmd_delete(self, args: argparse.Namespace) -> None:
        self.dump(self.delete_visualization(args.id))
        return None

    @staticmethod
    def register_cmds(cmds: argparse._SubParsersAction) -> None:
        client = KibanaVisualization()
        vis = cmds.add_parser("visualization", help="Visualizations")
        vis_cmds = vis.add_subparsers(required=True)

        v_list = vis_cmds.add_parser("list", help="GET /api/visualizations")
        v_list.add_argument("--query", default="", help="Optional search query")
        v_list.add_argument("--page", type=int, help="Page index (omit to fetch all)")
        v_list.add_argument("--per-page", type=int, default=100)
        v_list.set_defaults(func=client.cmd_list)

        v_get = vis_cmds.add_parser("get", help="GET /api/visualizations/:id")
        v_get.add_argument("id", help="Visualization id")
        v_get.set_defaults(func=client.cmd_get)

        v_create = vis_cmds.add_parser("create", help="POST /api/visualizations")
        v_create.add_argument("--json", required=True, help="Visualization JSON body")
        v_create.set_defaults(func=client.cmd_create)

        v_update = vis_cmds.add_parser(
            "update", help="PUT /api/visualizations/:id (full replace)"
        )
        v_update.add_argument("id", help="Visualization id")
        v_update.add_argument("--json", required=True, help="Visualization JSON body")
        v_update.set_defaults(func=client.cmd_update)

        v_del = vis_cmds.add_parser("delete", help="DELETE /api/visualizations/:id")
        v_del.add_argument("id", help="Visualization id")
        v_del.set_defaults(func=client.cmd_delete)
