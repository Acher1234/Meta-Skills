"""Kibana data views."""

from __future__ import annotations

import argparse
from typing import Any

from base_kibana import BaseKibana
from model.data_view import DataView

DATA_VIEW_PATH = "/api/data_views/data_view"


class KibanaDataView(BaseKibana):
    def get_data_view(self, view_id: str) -> Any:
        return self._kibana_request("GET", f"{DATA_VIEW_PATH}/{view_id}")

    def create_data_view(self, data_view: DataView | dict) -> Any:
        body = self._data_view_body(data_view)
        if not (body.get("data_view") or {}).get("title"):
            raise ValueError("missing required field(s): title")
        return self._kibana_request("POST", DATA_VIEW_PATH, json_body=body)

    def update_data_view(self, view_id: str, data_view: DataView | dict) -> Any:
        body = self._data_view_body(data_view)
        return self._kibana_request(
            "POST", f"{DATA_VIEW_PATH}/{view_id}", json_body=body
        )

    def delete_data_view(self, view_id: str) -> Any:
        return self._kibana_request("DELETE", f"{DATA_VIEW_PATH}/{view_id}")

    @staticmethod
    def _data_view_body(data_view: DataView | dict) -> dict:
        if isinstance(data_view, dict) and isinstance(
            data_view.get("data_view"), dict
        ):
            view = DataView.from_dict(data_view["data_view"])
            extra = {k: v for k, v in data_view.items() if k != "data_view"}
            return {"data_view": view.to_dict(), **extra}
        if isinstance(data_view, dict):
            data_view = DataView.from_dict(data_view)
        return {"data_view": data_view.to_dict()}

    def cmd_get(self, args: argparse.Namespace) -> None:
        self.dump(self.get_data_view(args.id))
        return None

    def cmd_create(self, args: argparse.Namespace) -> None:
        self._dump_write(lambda: self.create_data_view(self._parse_json(args.json)))
        return None

    def cmd_update(self, args: argparse.Namespace) -> None:
        self._dump_write(
            lambda: self.update_data_view(args.id, self._parse_json(args.json))
        )
        return None

    def cmd_delete(self, args: argparse.Namespace) -> None:
        self.dump(self.delete_data_view(args.id))
        return None

    @staticmethod
    def register_cmds(cmds: argparse._SubParsersAction) -> None:
        client = KibanaDataView()
        p = cmds.add_parser("data-view", help="Data views")
        view_cmds = p.add_subparsers(required=True)

        v_get = view_cmds.add_parser("get", help="GET /api/data_views/data_view/:id")
        v_get.add_argument("id", help="Data view id")
        v_get.set_defaults(func=client.cmd_get)

        v_create = view_cmds.add_parser(
            "create", help="POST /api/data_views/data_view"
        )
        v_create.add_argument("--json", required=True, help="Data view JSON body")
        v_create.set_defaults(func=client.cmd_create)

        v_update = view_cmds.add_parser(
            "update", help="POST /api/data_views/data_view/:id (partial)"
        )
        v_update.add_argument("id", help="Data view id")
        v_update.add_argument("--json", required=True, help="Data view JSON body")
        v_update.set_defaults(func=client.cmd_update)

        v_del = view_cmds.add_parser(
            "delete", help="DELETE /api/data_views/data_view/:id"
        )
        v_del.add_argument("id", help="Data view id")
        v_del.set_defaults(func=client.cmd_delete)
