#!/usr/bin/env python3
"""Shared REST client base for ESET Connect services."""

from __future__ import annotations

from typing import Any

import requests

import _http


class ApiError(Exception):
    label = "ESET Connect API"

    def __init__(self, status: int, body: Any, request_id: str | None = None):
        self.status = status
        self.body = body
        self.request_id = request_id
        super().__init__(f"{self.label} error {status}: {body}")


class BaseClient:
    error_class: type[ApiError] = ApiError

    def __init__(
        self,
        base_url: str,
        token: str,
        *,
        timeout: int = 30,
        session: requests.Session | None = None,
    ):
        if not base_url:
            raise ValueError("base_url is required")
        if not token:
            raise ValueError("token is required")
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.session = session or requests.Session()

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        json_body: Any | None = None,
    ) -> Any:
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
        raise self.error_class(
            resp.status_code, _http.decode_body(resp), _http.request_id(resp)
        )

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
