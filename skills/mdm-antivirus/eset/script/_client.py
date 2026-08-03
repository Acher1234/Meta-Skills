#!/usr/bin/env python3
"""Shared REST client base for ESET Connect services."""

from __future__ import annotations

from typing import Any

import requests

import _http
import authentication as auth


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
        *,
        token_url: str,
        username: str | None = None,
        password: str | None = None,
        access_token: str | None = None,
        timeout: int = 30,
        session: requests.Session | None = None,
    ):
        if not base_url:
            raise ValueError("base_url is required")
        if not token_url:
            raise ValueError("token_url is required")
        self.base_url = base_url.rstrip("/")
        self.token_url = token_url
        self.username = username
        self.password = password
        self._token_override = (access_token or "").strip() or None
        self._token: str | None = None
        self.timeout = timeout
        self.session = session or requests.Session()

    def _ensure_token(self, *, force: bool = False) -> str:
        if force:
            self._token = None
            self._token_override = None
        result = auth.ensure_access_token(
            self.token_url,
            username=self.username,
            password=self.password,
            access_token=self._token_override or self._token,
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
    def _page_params(
        page_size: int | None, page_token: str | None, extra: dict | None = None
    ) -> dict:
        params: dict = dict(extra or {})
        if page_size is not None:
            params["pageSize"] = page_size
        if page_token:
            params["pageToken"] = page_token
        return params
