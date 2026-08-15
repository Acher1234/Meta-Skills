#!/usr/bin/env python3
"""ESET Connect CLI — thin router."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import requests

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from _client import ApiError, BaseClient  # noqa: E402
from application_management import ApplicationManagementClient  # noqa: E402
from asset_management import AssetManagementClient  # noqa: E402
from authentication import AuthError, Authentication  # noqa: E402
from automation import AutomationClient  # noqa: E402
from device_management import DeviceManagementClient  # noqa: E402
from incident_detections import DetectionsClient  # noqa: E402
from incident_edr import EdrClient  # noqa: E402
from incident_incidents import IncidentsClient  # noqa: E402
from patch_management import PatchManagementClient  # noqa: E402
from policy_management import PolicyManagementClient  # noqa: E402
from skill_env import ENV, ConfigError  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description=(
            "ESET Connect CLI: OAuth token (/oauth/token), Device / Application / "
            "Asset / Policy Management, Automation (Device tasks), Incident "
            "Management, and Patch Management APIs "
            "(resolves .env + regional gateway URLs)."
        ),
    )
    sub = parser.add_subparsers(required=True)
    Authentication.register(sub)
    DeviceManagementClient.register(sub)
    AssetManagementClient.register(sub)
    PolicyManagementClient.register(sub)
    ApplicationManagementClient.register(sub)
    DetectionsClient.register(sub)
    EdrClient.register(sub)
    IncidentsClient.register(sub)
    AutomationClient.register(sub)
    PatchManagementClient.register(sub)
    args = parser.parse_args(argv)
    token = getattr(args, "token", None)
    if token:
        ENV.access_token_override = token.strip() or None
    try:
        code = args.func(args)
        return 0 if code is None else code
    except (ConfigError, AuthError) as exc:
        BaseClient.dump({"ok": False, "error": str(exc)})
        return 1
    except ApiError as exc:
        BaseClient.dump(
            {
                "ok": False,
                "status": exc.status,
                "request_id": exc.request_id,
                "error": exc.body,
            }
        )
        return 1
    except requests.RequestException as exc:
        BaseClient.dump({"ok": False, "error": f"HTTP request failed: {exc}"})
        return 1
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        BaseClient.dump({"ok": False, "error": str(exc)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
