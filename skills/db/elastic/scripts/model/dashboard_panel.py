from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from model._serialize import clean, extra_fields, require
from model.panel_grid import PanelGrid
from model.visualization import Visualization

_FIELDS = {"type", "grid", "config"}


@dataclass
class DashboardPanel:
    type: str
    grid: PanelGrid
    config: Visualization | dict[str, Any] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> DashboardPanel:
        require(data, "type")
        grid = data.get("grid") or {}
        return cls(
            type=data["type"],
            grid=PanelGrid.from_dict(grid) if isinstance(grid, dict) else grid,
            config=data.get("config") or {},
            extra=extra_fields(data, _FIELDS),
        )

    def to_dict(self) -> dict:
        return clean(
            {
                "type": self.type,
                "grid": self.grid,
                "config": self.config,
                **self.extra,
            }
        )
