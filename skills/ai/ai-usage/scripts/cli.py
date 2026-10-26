#!/usr/bin/env python3
"""AI usage CLI — plan limits left + token usage per period for Claude Code, Codex and OpenCode."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import claude_usage  # noqa: E402
import codex_usage  # noqa: E402
import opencode_usage  # noqa: E402
from locate import resolve_scope  # noqa: E402
from skill_env import ENV  # noqa: E402

TOOLS = {
    "claude": (claude_usage, "CLAUDE_CREDENTIALS_FILE"),
    "codex": (codex_usage, "CODEX_AUTH_FILE"),
    "opencode": (opencode_usage, "OPENCODE_AUTH_FILE"),
}


def run_tool(name: str, args: argparse.Namespace) -> dict[str, Any]:
    module, override_key = TOOLS[name]
    try:
        return module.usage(
            resolve_scope(args.scope),
            ENV.override(override_key),
            ENV.http_values(),
            want_remote=not args.no_remote,
            want_local=not args.no_local,
            origin=args.source,
        )
    except Exception as exc:  # one broken tool must not hide the others in `all`
        return {"tool": name, "error": f"{type(exc).__name__}: {exc}"}


def strip_extra(node: Any) -> Any:
    """Drop every `extra_usage` block unless --extra was asked."""
    if isinstance(node, dict):
        return {k: strip_extra(v) for k, v in node.items() if k != "extra_usage"}
    if isinstance(node, list):
        return [strip_extra(v) for v in node]
    return node


def _fmt_int(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def _text_windows(limits: Any, indent: str = "  ") -> list[str]:
    if not isinstance(limits, dict):
        return []
    if limits.get("error"):
        return [f"{indent}limits: {limits['error']}"]
    lines = []
    for w in limits.get("windows", []):
        reset = f" · resets in {w['resets_in']}" if w.get("resets_in") else ""
        status = f" [{w['status']}]" if w.get("status") not in (None, "ok") else ""
        lines.append(f"{indent}{w['window']:<22} {w['used_percent']:>5}% used · {w['remaining_percent']:>5}% left{reset}{status}")
    extra = limits.get("extra_usage")
    if extra:
        if extra.get("enabled") is False:
            spent = f" · spent {extra['spend_used']} {extra.get('currency') or ''}" if extra.get("spend_used") is not None else ""
            lines.append(f"{indent}extra usage: disabled{spent}")
        else:
            shown = {k: v for k, v in extra.items() if v not in (None, False)}
            lines.append(f"{indent}extra usage: {shown or 'none'}")
    return lines


def render_text(report: dict[str, Any]) -> str:
    lines = [f"== {report['tool']} =="]
    if report.get("error"):
        return "\n".join(lines + [f"  error: {report['error']}"])
    lines.append(f"  credentials: {report.get('credentials') or 'not found'}")
    if report.get("plan"):
        lines.append(f"  plan: {report['plan']} ({report.get('rate_limit_tier') or '-'})")
    limits = report.get("limits")
    if report["tool"] == "opencode" and isinstance(limits, dict) and "error" not in limits:
        for provider, info in limits.items():
            lines.append(f"  [{provider}] {info.get('type')}{' — ' + info['note'] if info.get('note') else ''}")
            lines += _text_windows(info.get("limits"), "    ")
    else:
        lines += _text_windows(limits)
    go = report.get("opencode_go")
    if go:
        lines.append(f"  [opencode-go] {go.get('credentials') or 'no key'}")
        lines += _text_windows(go, "    ")
        for status in go.get("hermes_last_status") or []:
            lines.append(f"    hermes: {status.get('last_status')} {status.get('last_error_code') or ''} "
                         f"{status.get('last_error_reason') or ''} reset {status.get('last_error_reset_at') or '-'}")
    if report.get("last_logged_limits"):
        snap = report["last_logged_limits"]
        lines.append(f"  last logged limits (as of {snap['as_of']}{', stale' if snap['stale'] else ''}):")
        lines += _text_windows(snap, "    ")
    local = report.get("local_usage")
    if local:
        lines.append(f"  local usage (last activity {local['last_activity'] or '-'}):")
        lines.append(f"    {'period':<11}{'msgs':>7}{'input':>14}{'output':>12}{'cache read':>15}{'total':>15}{'cost $':>10}")
        for period, b in local["periods"].items():
            lines.append(
                f"    {period:<11}{b['messages']:>7}{_fmt_int(b['input']):>14}{_fmt_int(b['output']):>12}"
                f"{_fmt_int(b['cache_read']):>15}{_fmt_int(b['total']):>15}{b['cost_usd']:>10.2f}"
            )
    return "\n".join(lines)


def emit(reports: list[dict[str, Any]], text: bool) -> None:
    if text:
        print("\n\n".join(render_text(r) for r in reports))
    elif len(reports) == 1:
        print(json.dumps(reports[0], indent=2, default=str))
    else:
        print(json.dumps({r["tool"]: r for r in reports}, indent=2, default=str))


def cmd_tool(args: argparse.Namespace) -> int:
    names = list(TOOLS) if args.command == "all" else [args.command]
    reports = [run_tool(name, args) for name in names]
    emit(reports if args.extra else [strip_extra(r) for r in reports], args.text)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--scope", choices=("auto", "project", "global"), default="auto",
                        help="auto: follow $IS_GLOBAL (project .<tool>/ first, then ~); project / global: force")
    common.add_argument("--no-remote", action="store_true", help="skip the plan-limits API call")
    common.add_argument("--no-local", action="store_true", help="skip scanning local session logs")
    common.add_argument("--extra", action="store_true",
                        help="also show extra usage: Claude pay-as-you-go credits / monthly cap, Codex credits")
    common.add_argument("--source", choices=("auto", "tool", "hermes", "openclaw", "env"), default="auto",
                        help="where to take the token: auto (tool → Hermes → OpenClaw → env) or one origin only")
    common.add_argument("--text", action="store_true", help="human-readable output instead of JSON")
    sub = parser.add_subparsers(dest="command", required=True)
    helps = {
        "claude": "Claude Code — 5h session / weekly limits left + local token usage",
        "codex": "Codex CLI — 5h / weekly ChatGPT limits left + local token usage",
        "opencode": "OpenCode — limits of each logged-in provider, OpenCode Go quota + local token/cost usage",
        "all": "All three tools",
    }
    for name, text in helps.items():
        sub.add_parser(name, parents=[common], help=text, description=text).set_defaults(func=cmd_tool)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
