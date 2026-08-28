"""Dealabs REST v2 client (OAuth1)."""

from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

import requests
from requests_oauthlib import OAuth1

API_BASE_URL = "https://www.dealabs.com/rest_api/v2/"
API_DEAL_SEARCH = urljoin(API_BASE_URL, "thread/search")
API_DEAL_THREAD = urljoin(API_BASE_URL, "thread")
API_THREAD_DETAIL = urljoin(API_BASE_URL, "thread/{thread_id}")
API_THREAD_COMMENTS = urljoin(API_BASE_URL, "thread/{thread_id}/comments")
API_MERCHANT = urljoin(API_BASE_URL, "merchant")
API_MERCHANT_SEARCH = urljoin(API_BASE_URL, "merchant/search")
API_MERCHANT_DETAIL = urljoin(API_BASE_URL, "merchant/{merchant_id}")


class DealabsError(RuntimeError):
    def __init__(self, status: int, body: Any):
        self.status = status
        self.body = body
        super().__init__(f"Dealabs API {status}: {body}")


class Deal:
    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    def to_dict(self) -> dict[str, Any]:
        return self._data

    def __getattr__(self, name: str) -> Any:
        try:
            return self._data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


class Dealabs:
    def __init__(self) -> None:
        self.client_key = "539f008401dbb"
        self.client_secret = "539f008401e9c"
        self.headers = {
            "User-Agent": "com.dealabs.apps.android ANDROID [v7.19.00] [22 | SM-G930K] [@2.0x]",
            "Pepper-Include-Counters": "unread_alerts",
            "Pepper-Include-Prev-And-Next-Ids": "true",
            "Pepper-JSON-Format": (
                "thread=list,group=ids,type=light,event=light,"
                "user=full,badge=user,formatted_text=html,message=with_code"
            ),
            "Pepper-Hardware-Id": "5bce296a65215d0bb3b9751bb77b0a1d",
            "Host": "www.dealabs.com",
        }
        self.oauth = OAuth1(self.client_key, client_secret=self.client_secret)

    def request(
        self,
        url: str,
        method: str = "GET",
        params: dict[str, Any] | None = None,
    ) -> Any:
        if not url.startswith("http"):
            url = urljoin(API_BASE_URL, url.lstrip("/"))
        clean: dict[str, Any] = {}
        for key, value in (params or {}).items():
            if value is None or value == "":
                continue
            clean[key] = value
        resp = requests.request(
            method=method,
            url=url,
            params=clean or None,
            headers=self.headers,
            auth=self.oauth,
            timeout=60,
        )
        try:
            body: Any = resp.json() if resp.content else None
        except ValueError as exc:
            raise DealabsError(resp.status_code, resp.text[:500]) from exc
        if resp.status_code >= 400:
            raise DealabsError(resp.status_code, body)
        return body

    def get_hot_deals(self, params: dict[str, Any] | None = None) -> Any:
        merged = {"order_by": "hot", "limit": "50", **(params or {})}
        return self.request(url=API_DEAL_THREAD, params=merged)

    def search_deals(self, params: dict[str, Any] | None = None) -> Any:
        merged = {"order_by": "hot", "limit": "50", **(params or {})}
        return self.request(url=API_DEAL_SEARCH, params=merged)

    def get_new_deals(self, params: dict[str, Any] | None = None) -> list[Deal]:
        merged = {"order_by": "new", "limit": "50", **(params or {})}
        req = self.request(url=API_DEAL_THREAD, params=merged)
        deals_data = req.get("data", []) if isinstance(req, dict) else []
        return [Deal(deal_data) for deal_data in deals_data]

    def list_merchants(self, params: dict[str, Any] | None = None) -> Any:
        return self.request(url=API_MERCHANT, params=params)

    def search_merchants(self, params: dict[str, Any] | None = None) -> Any:
        return self.request(url=API_MERCHANT_SEARCH, params=params)

    def get_merchant(self, merchant_id: str) -> Any:
        return self.request(url=API_MERCHANT_DETAIL.format(merchant_id=merchant_id))
