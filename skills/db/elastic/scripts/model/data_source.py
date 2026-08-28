from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from model._serialize import clean, extra_fields, require

_FIELDS = {"type", "index_pattern", "time_field", "ref_id", "query"}


@dataclass
class DataSource:
    type: str
    index_pattern: str | None = None
    time_field: str | None = None
    ref_id: str | None = None
    query: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> DataSource:
        require(data, "type")
        return cls(
            type=data["type"],
            index_pattern=data.get("index_pattern"),
            time_field=data.get("time_field"),
            ref_id=data.get("ref_id"),
            query=data.get("query"),
            extra=extra_fields(data, _FIELDS),
        )

    def to_dict(self) -> dict:
        return clean(
            {
                "type": self.type,
                "index_pattern": self.index_pattern,
                "time_field": self.time_field,
                "ref_id": self.ref_id,
                "query": self.query,
                **self.extra,
            }
        )
