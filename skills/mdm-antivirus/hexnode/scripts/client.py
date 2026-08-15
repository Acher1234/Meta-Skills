"""Hexnode MDM REST client — API key in Authorization (Authentication field)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import requests

from skill_env import ENV


class ConfigError(Exception):
    pass


class HexnodeError(RuntimeError):
    def __init__(self, status: int, body: Any):
        self.status = status
        self.body = body
        super().__init__(f"Hexnode API {status}: {body}")


class HexnodeClient:
    """Base HTTP client for https://<portal>.hexnodemdm.com/api/v1/…

    Endpoint examples use ``Authorization: <api_key>`` (raw key, no Bearer /
    Basic prefix).
    """

    def __init__(self):
        self.api_key = ENV.api_key()
        self.api_base = ENV.base_url()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": self.api_key,
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
    ) -> Any:
        url = f"{self.api_base}{path}"
        clean: dict[str, Any] | None = None
        if params:
            clean = {
                key: value
                for key, value in params.items()
                if value is not None and value != ""
            }
        resp = self.session.request(
            method, url, params=clean, json=json, timeout=60
        )
        if resp.status_code == 204:
            return None
        try:
            body: Any = resp.json() if resp.content else None
        except ValueError:
            body = resp.text
        if resp.status_code >= 400:
            raise HexnodeError(resp.status_code, body)
        return body

    @staticmethod
    def dump(data: Any) -> None:
        print(json.dumps(data, indent=2, default=str))

    @staticmethod
    def add_paging(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--page", type=int)
        parser.add_argument("--per-page", type=int)

    @staticmethod
    def load_json_file(path: str) -> Any:
        return json.loads(Path(path).read_text(encoding="utf-8"))

    def dump_result(self, result: Any, *, empty_status: int = 204) -> int:
        self.dump(result if result is not None else {"ok": True, "status": empty_status})
        return 0

    @staticmethod
    def _page_params(
        page: int | None = None, per_page: int | None = None
    ) -> dict[str, Any]:
        return {"page": page, "per_page": per_page}
