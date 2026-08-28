from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from model._serialize import clean, extra_fields, require
from model.data_source import DataSource

_FIELDS = {"type", "data_source", "x", "y"}


@dataclass
class VisualizationLayer:
    type: str
    data_source: DataSource | None = None
    x: dict[str, Any] | None = None
    y: list[dict[str, Any]] | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> VisualizationLayer:
        require(data, "type")
        ds = data.get("data_source")
        return cls(
            type=data["type"],
            data_source=DataSource.from_dict(ds) if isinstance(ds, dict) else ds,
            x=data.get("x"),
            y=data.get("y"),
            extra=extra_fields(data, _FIELDS),
        )

    def to_dict(self) -> dict:
        return clean(
            {
                "type": self.type,
                "data_source": self.data_source,
                "x": self.x,
                "y": self.y,
                **self.extra,
            }
        )
