from __future__ import annotations

from typing import Any


def clean(value: Any) -> Any:
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if isinstance(value, dict):
        return {k: clean(v) for k, v in value.items() if v is not None}
    if isinstance(value, list):
        return [clean(v) for v in value]
    return value


def require(data: dict, *keys: str) -> None:
    missing = [key for key in keys if key not in data or data[key] is None]
    if missing:
        raise ValueError(f"missing required field(s): {', '.join(missing)}")


def extra_fields(data: dict, known: set[str]) -> dict:
    return {k: v for k, v in data.items() if k not in known}
