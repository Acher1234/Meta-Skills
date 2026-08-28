"""Kibana HTTP client — shared request helper for Kibana APIs."""

from __future__ import annotations

import json
import ssl
from base64 import b64encode
from collections.abc import Callable
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from client import ElasticClient
from skill_env import ENV

KIBANA_API_VERSION = "2023-10-31"


class BaseKibana(ElasticClient):
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
