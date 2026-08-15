#!/usr/bin/env python3
"""Shared REST client base for ESET Connect services."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import requests

import _http
import authentication as auth
from skill_env import ConfigError, ENV

TOKEN_PARENT = argparse.ArgumentParser(add_help=False)
TOKEN_PARENT.add_argument(
    "--token",
    metavar="ACCESS_TOKEN",
    help="Bearer access token to use (skip the password grant)",
)


class ApiError(Exception):
    label = "ESET Connect API"

    def __init__(self, status: int, body: Any, request_id: str | None = None):
        self.status = status
        self.body = body
        self.request_id = request_id
        super().__init__(f"{self.label} error {status}: {body}")


class BaseClient:
    error_class: type[ApiError] = ApiError
    url_key: str = ""

    def __init__(self) -> None:
        self.timeout = 30
        self.session = requests.Session()
        self._token: str | None = None
        try:
            self.base_url = ENV.gateway_url(self.url_key).rstrip("/")
            self.token_url = ENV.token_url()
            self.username = ENV.username()
            self.password = ENV.password()
        except ConfigError:
            self.base_url = ""
            self.token_url = ""
            self.username = None
            self.password = None

    def _ensure_token(self, *, force: bool = False) -> str:
        if force:
            self._token = None
            ENV.access_token_override = None
        result = auth.ensure_access_token(
            self.token_url,
            username=self.username,
            password=self.password,
            access_token=ENV.access_token_override or self._token,
            force=force,
        )
        token = result.get("access_token")
        if not token:
            raise auth.AuthError(f"No access token obtained: {result}")
        self._token = token
        return token

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._ensure_token()}",
            "Accept": "application/json",
        }

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        json_body: Any | None = None,
        _retried: bool = False,
    ) -> Any:
        if not self.base_url:
            raise ConfigError("ESET_URL is not set")
        resp = _http.send(
            method,
            f"{self.base_url}{path}",
            headers=self._headers(),
            params=params,
            json_body=json_body,
            timeout=self.timeout,
            session=self.session,
        )
        if 200 <= resp.status_code < 300:
            return _http.decode_body(resp)

        if resp.status_code == 401 and not _retried:
            self._ensure_token(force=True)
            return self._request(
                method,
                path,
                params=params,
                json_body=json_body,
                _retried=True,
            )

        raise self.error_class(
            resp.status_code, _http.decode_body(resp), _http.request_id(resp)
        )

    @staticmethod
    def dump(data: Any) -> None:
        print(json.dumps(data, indent=2, default=str))

    @staticmethod
    def add_paging(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--page-size", type=int, default=None, help="Page size")
        parser.add_argument("--page-token", default=None, help="Pagination token")

    @staticmethod
    def load_json_file(path: str) -> Any:
        text = sys.stdin.read() if path == "-" else Path(path).read_text()
        return json.loads(text)

    @staticmethod
    def _page_params(
        page_size: int | None, page_token: str | None, extra: dict | None = None
    ) -> dict:
        params: dict = dict(extra or {})
        if page_size is not None:
            params["pageSize"] = page_size
        if page_token:
            params["pageToken"] = page_token
        return params
