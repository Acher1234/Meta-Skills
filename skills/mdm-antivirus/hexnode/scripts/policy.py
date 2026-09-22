"""Hexnode Policies API — https://www.hexnode.com/mobile-device-management/developers/policies/

GET    /policy/                 list_policies
POST   /policy/                 create_policy
GET    /policy/{id}/            get_policy
PUT    /policy/{id}/            edit_policy
DELETE /policy/{id}/            archive_policy

Platform payload keys (ios / android / macos / windows) are documented at:
https://www.hexnode.com/mobile-device-management/developers/policies/ios-policies/
https://www.hexnode.com/mobile-device-management/developers/policies/android-policies/
https://www.hexnode.com/mobile-device-management/developers/policies/macos-policies/
https://www.hexnode.com/mobile-device-management/developers/policies/windows-policies/
"""

from __future__ import annotations

from typing import Any

from client import HexnodeClient


class PolicyClient(HexnodeClient):
    def list_policies(
        self, *, page: int | None = None, per_page: int | None = None
    ) -> Any:
        """GET /policy/ — list all policies."""
        return self.request(
            "GET", "/policy/", params=self._page_params(page, per_page)
        )

    def create_policy(self, body: dict[str, Any]) -> Any:
        """POST /policy/ — create a policy (full JSON body)."""
        return self.request("POST", "/policy/", json=body)

    def get_policy(self, policy_id: int | str) -> Any:
        """GET /policy/{id}/ — policy details."""
        return self.request("GET", f"/policy/{policy_id}/")

    def edit_policy(self, policy_id: int | str, body: dict[str, Any]) -> Any:
        """PUT /policy/{id}/ — edit an existing policy."""
        return self.request("PUT", f"/policy/{policy_id}/", json=body)

    def archive_policy(self, policy_id: int | str) -> Any:
        """DELETE /policy/{id}/ — archive policy (dissociates from all devices)."""
        return self.request("DELETE", f"/policy/{policy_id}/")
