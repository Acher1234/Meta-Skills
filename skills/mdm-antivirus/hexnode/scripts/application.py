"""Hexnode Applications API — https://www.hexnode.com/mobile-device-management/developers/applications/

GET  /applications/                 list_apps
GET  /applications/searchapp/       search_apps
POST /applications/                 add_app
GET  /applications/{id}/            get_app
"""

from __future__ import annotations

from typing import Any

from client import HexnodeClient


class ApplicationClient(HexnodeClient):
    def list_apps(
        self,
        *,
        order_by: str | None = None,
        app_type: str | None = None,
        platform: str | None = None,
        page: int | None = None,
        per_page: int | None = None,
    ) -> Any:
        """GET /applications/ — list apps in the portal catalog."""
        return self.request(
            "GET",
            "/applications/",
            params={
                "order_by": order_by,
                "app_type": app_type,
                "platform": platform,
                **self._page_params(page, per_page),
            },
        )

    def search_apps(
        self,
        *,
        keyword: str,
        platform: str,
        country: str | None = None,
    ) -> Any:
        """GET /applications/searchapp/ — search App Store / Play Store."""
        return self.request(
            "GET",
            "/applications/searchapp/",
            params={
                "keyword": keyword,
                "platform": platform,
                "country": country,
            },
        )

    def add_app(self, body: dict[str, Any] | list[dict[str, Any]]) -> Any:
        """POST /applications/ — add app(s) to the catalog.

        Hexnode sample post data is a list of app objects; the shell example
        also accepts a single object. Pass either.
        """
        return self.request("POST", "/applications/", json=body)

    def get_app(self, app_id: int | str) -> Any:
        """GET /applications/{id}/ — retrieve app details."""
        return self.request("GET", f"/applications/{app_id}/")
