"""Hexnode Users API — https://www.hexnode.com/mobile-device-management/developers/users/

GET    /users/                              list_users
POST   /users/                              create_user
GET    /users/{id}/                         get_user
PUT    /users/{id}/                         edit_user
DELETE /users/{id}/                         delete_user
POST   /users/{id}/send_request/            send_enrollment_request
"""

from __future__ import annotations

from typing import Any

from client import HexnodeClient


class UsersClient(HexnodeClient):
    def list_users(
        self,
        *,
        order_by: str | None = None,
        user_type: str | None = None,
        enrollment_status: str | None = None,
        page: int | None = None,
        per_page: int | None = None,
    ) -> Any:
        """GET /users/ — list enrolled users."""
        return self.request(
            "GET",
            "/users/",
            params={
                "order_by": order_by,
                "user_type": user_type,
                "enrollment_status": enrollment_status,
                **self._page_params(page, per_page),
            },
        )

    def create_user(
        self,
        *,
        name: str,
        email: str,
        phoneno: str | int | None = None,
        password: str | None = None,
    ) -> Any:
        """POST /users/ — create a user (API expects a one-element list body)."""
        user: dict[str, Any] = {"name": name, "email": email}
        if phoneno is not None:
            user["phoneno"] = phoneno
        if password is not None:
            user["password"] = password
        return self.request("POST", "/users/", json=[user])

    def get_user(self, user_id: int | str) -> Any:
        """GET /users/{id}/ — retrieve user details."""
        return self.request("GET", f"/users/{user_id}/")

    def edit_user(
        self,
        user_id: int | str,
        *,
        name: str,
        email: str,
        phoneno: str | int | None = None,
        password: str | None = None,
    ) -> Any:
        """PUT /users/{id}/ — edit user details."""
        body: dict[str, Any] = {"name": name, "email": email}
        if phoneno is not None:
            body["phoneno"] = phoneno
        if password is not None:
            body["password"] = password
        return self.request("PUT", f"/users/{user_id}/", json=body)

    def delete_user(self, user_id: int | str) -> Any:
        """DELETE /users/{id}/ — deletes user and disenrolls their devices."""
        return self.request("DELETE", f"/users/{user_id}/")

    def send_enrollment_request(
        self, user_id: int | str, *, ownership: str
    ) -> Any:
        """POST /users/{id}/send_request/ — send enrollment request."""
        return self.request(
            "POST",
            f"/users/{user_id}/send_request/",
            json={"ownership": ownership},
        )
