#!/usr/bin/env python3
"""Hexnode MDM CLI — thin router."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from application import ApplicationClient  # noqa: E402
from client import ConfigError, HexnodeClient, HexnodeError  # noqa: E402
from device_groups import DeviceGroupsClient  # noqa: E402
from devices import DevicesClient  # noqa: E402
from policy import PolicyClient  # noqa: E402
from skill_env import HexnodeSkillEnv  # noqa: E402
from users import UsersClient  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description=(
            "Hexnode MDM API CLI — Devices + Users + Apps + Policies + "
            "Device groups."
        ),
    )
    sub = parser.add_subparsers(required=True)
    HexnodeSkillEnv.register(sub)
    DevicesClient.register(sub)
    UsersClient.register(sub)
    ApplicationClient.register(sub)
    PolicyClient.register(sub)
    DeviceGroupsClient.register(sub)
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ConfigError as exc:
        HexnodeClient.dump({"ok": False, "error": str(exc)})
        return 1
    except HexnodeError as exc:
        HexnodeClient.dump({"ok": False, "status": exc.status, "error": exc.body})
        return 1
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        HexnodeClient.dump({"ok": False, "error": str(exc)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
