from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from model._serialize import clean, extra_fields, require
from model.dashboard_panel import DashboardPanel

_FIELDS = {
    "title",
    "description",
    "panels",
    "pinned_panels",
    "time_range",
    "query",
    "filters",
    "tags",
}


@dataclass
class Dashboard:
    title: str
    description: str | None = None
    panels: list[DashboardPanel] = field(default_factory=list)
    pinned_panels: list[DashboardPanel] | None = None
    time_range: dict[str, Any] | None = None
    query: dict[str, Any] | None = None
    filters: list[dict[str, Any]] | None = None
    tags: list[str] | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> Dashboard:
        require(data, "title")
        panels = data.get("panels") or []
        pinned = data.get("pinned_panels")
        return cls(
            title=data["title"],
            description=data.get("description"),
            panels=[
                DashboardPanel.from_dict(panel) if isinstance(panel, dict) else panel
                for panel in panels
            ],
            pinned_panels=(
                [
                    DashboardPanel.from_dict(panel)
                    if isinstance(panel, dict)
                    else panel
                    for panel in pinned
                ]
                if pinned is not None
                else None
            ),
            time_range=data.get("time_range"),
            query=data.get("query"),
            filters=data.get("filters"),
            tags=data.get("tags"),
            extra=extra_fields(data, _FIELDS),
        )

    def to_dict(self) -> dict:
        return clean(
            {
                "title": self.title,
                "description": self.description,
                "panels": self.panels,
                "pinned_panels": self.pinned_panels,
                "time_range": self.time_range,
                "query": self.query,
                "filters": self.filters,
                "tags": self.tags,
                **self.extra,
            }
        )
