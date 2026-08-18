#!/usr/bin/env python3
"""Zscaler CLI — thin router."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from skill_env import ZscalerSkillEnv  # noqa: E402
from zia.client import ZiaClient  # noqa: E402
from zia.dedicated_ip_gateways import DedicatedIpGatewaysClient  # noqa: E402
from zia.forwarding_rule import ForwardingRuleClient  # noqa: E402
from zia.ip_fqdn_groups import IpFqdnGroupsClient  # noqa: E402
from zia.url_categories import UrlCategoriesClient  # noqa: E402
from zia.url_cloud_apps import UrlCloudAppsClient  # noqa: E402
from zia.url_filtering_policy import UrlFilteringPolicyClient  # noqa: E402
from zia.users import UsersClient  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Zscaler ZPA / ZIA / ZIdentity CLI")
    sub = parser.add_subparsers(required=True)
    ZscalerSkillEnv.register(sub)
    zia = sub.add_parser("zia", help="ZIA legacy API")
    zia_cmds = zia.add_subparsers(required=True)
    ZiaClient.register(zia_cmds)
    UsersClient.register(zia_cmds)
    UrlCategoriesClient.register(zia_cmds)
    UrlCloudAppsClient.register(zia_cmds)
    UrlFilteringPolicyClient.register(zia_cmds)
    IpFqdnGroupsClient.register(zia_cmds)
    DedicatedIpGatewaysClient.register(zia_cmds)
    ForwardingRuleClient.register(zia_cmds)
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except RuntimeError as exc:
        ZiaClient.dump({"ok": False, "error": str(exc)})
        return 1
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        ZiaClient.dump({"ok": False, "error": str(exc)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
