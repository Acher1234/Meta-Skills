"""Skill credential loading, verification, and shell export (cross-platform)."""

from __future__ import annotations

import argparse
import os
import sys
from abc import ABC, abstractmethod
from collections.abc import Mapping
from pathlib import Path

from common.skill_cred import WORKSPACE_ENV, SkillCred, default_skill_dir, display_path

ShellName = str


def detect_shell() -> ShellName:
    shell = os.environ.get("SHELL", "").lower()
    if any(name in shell for name in ("bash", "zsh", "fish")):
        return "bash"
    if sys.platform == "win32":
        if os.environ.get("PSModulePath"):
            return "powershell"
        return "cmd"
    return "bash"


def _bash_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


def _powershell_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def format_exports(variables: Mapping[str, str], shell: ShellName) -> str:
    lines: list[str] = []
    if shell == "bash":
        for key, value in variables.items():
            lines.append(f"export {key}={_bash_quote(value)}")
    elif shell == "powershell":
        for key, value in variables.items():
            lines.append(f"$env:{key} = {_powershell_quote(value)}")
    elif shell == "cmd":
        for key, value in variables.items():
            safe = value.replace('"', "")
            lines.append(f'set "{key}={safe}"')
    else:
        raise ValueError(f"unsupported shell: {shell!r}")
    return "\n".join(lines)


def emit_env_load(
    variables: Mapping[str, str],
    *,
    shell: ShellName = "auto",
) -> str:
    resolved = detect_shell() if shell == "auto" else shell
    if resolved not in {"bash", "powershell", "cmd"}:
        raise SystemExit(
            f"env-load: unsupported shell {resolved!r} (use bash, powershell, cmd, auto)"
        )
    return format_exports(variables, resolved)


def _parse_env_line(raw: str) -> tuple[str, str] | None:
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        return None
    if line.startswith("export "):
        line = line[len("export ") :].strip()
    key, _, value = line.partition("=")
    key = key.strip()
    value = value.strip().strip("'").strip('"')
    if not key:
        return None
    return key, value


def parse_env_file(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        parsed = _parse_env_line(raw)
        if parsed is None:
            continue
        key, value = parsed
        values[key] = value
    return values


class SkillEnv(ABC):
    """Read and verify a skill `.env` via SkillCred.
    """

    required_keys: tuple[str, ...] = ()

    def __init__(
        self,
        skill_name: str,
        caller_file: str | Path,
        *,
        env_files: tuple[str, ...] = (".env",),
    ):
        self.skill_name = skill_name
        self._caller_file = Path(caller_file).resolve()
        self._skill_dir = default_skill_dir(self._caller_file)
        self._env_files = env_files
        self._cred = SkillCred(skill_name, list(env_files))
        os.environ.setdefault(WORKSPACE_ENV, str(self._skill_dir))
        self.env = {}
        self.sav_env()

    def env_cred(self) -> SkillCred:
        return self._cred

    def env_path(self) -> Path:
        return self._cred.file_path()

    def display_env_path(self) -> str:
        return display_path(self.env_path())

    def display_skill_home(self) -> str:
        return display_path(self._skill_dir)

    def read_env(self) -> dict[str, str]:
        """Parse `.env` into a dict (no ``os.environ`` side effects)."""
        return self.apply_defaults(parse_env_file(self.env_path()))

    def set_env(self, values: Mapping[str, str]) -> None:
        for key, value in values.items():
            os.environ[key] = value

    def apply_defaults(self, values: Mapping[str, str]) -> dict[str, str]:
        """Hook to add derived/default keys after parsing the file."""
        return dict(values)

    @abstractmethod
    def verify(self, values: dict[str, str]) -> dict[str, str]:
        """Validate *values* and return verified key/value pairs."""

    def get_secured_env(self) -> dict[str, str]:
        return self.verify(self.read_env())

    def sav_env(self) -> None:
        self.env = self.get_secured_env()

    def verify_required_keys(
        self,
        values: Mapping[str, str],
        keys: tuple[str, ...] | None = None,
    ) -> dict[str, str]:
        names = keys if keys is not None else self.required_keys
        if not names:
            raise NotImplementedError(f"{type(self).__name__}.verify() must be implemented")
        missing = [key for key in names if not values.get(key, "").strip()]
        if missing:
            raise SystemExit(
                f"Missing {', '.join(missing)} — edit {self.env_path()} "
                f"(CURRENT_SKILL_DIRECTORY={os.environ.get(WORKSPACE_ENV, '')!r})"
            )
        return {key: values[key].strip() for key in names}

    def emit_shell_exports(self, *, shell: ShellName = "auto") -> str:
        variables = dict(self.get_secured_env())
        variables["CURRENT_SKILL_DIRECTORY"] = str(self.env_cred().workspace)
        return emit_env_load(variables, shell=shell)

    def upsert_env_vars(
        self,
        updates: Mapping[str, str],
        *,
        shell: ShellName = "auto",
    ) -> tuple[Path, str]:
        """Persist *updates* to `.env` and return shell commands to export them."""
        path = self.env_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = []
        if path.is_file():
            lines = path.read_text(encoding="utf-8").splitlines()

        seen: set[str] = set()
        out: list[str] = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and "=" in stripped:
                key = stripped.split("=", 1)[0].strip()
                if key in updates:
                    out.append(f"{key}={updates[key]}")
                    seen.add(key)
                    continue
            out.append(line)

        for key, value in updates.items():
            if key not in seen:
                out.append(f"{key}={value}")

        text = "\n".join(out)
        if text and not text.endswith("\n"):
            text += "\n"
        path.write_text(text, encoding="utf-8")
        return path.resolve(), emit_env_load(updates, shell=shell)


def env_load_main(env: SkillEnv, argv: list[str] | None = None) -> int:
    """CLI entrypoint for ``python skill_env.py`` (shell export commands)."""
    parser = argparse.ArgumentParser(
        description=(
            "Resolve .env via SkillCred and print export statements for the current "
            "shell. Eval the output before calling external CLIs."
        ),
    )
    parser.add_argument(
        "--shell",
        choices=("auto", "bash", "powershell", "cmd"),
        default="auto",
        help="Target shell (default: auto-detect)",
    )
    args = parser.parse_args(argv)
    print(env.emit_shell_exports(shell=args.shell))
    return 0
