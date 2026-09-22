from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from model._serialize import clean, extra_fields, require
from model.data_source import DataSource
from model.visualization_layer import VisualizationLayer

_FIELDS = {
    "type",
    "title",
    "description",
    "data_source",
    "layers",
    "metrics",
    "query",
    "filters",
}


@dataclass
class Visualization:
    type: str
    title: str
    description: str | None = None
    data_source: DataSource | None = None
    layers: list[VisualizationLayer] | None = None
    metrics: list[dict[str, Any]] | None = None
    query: dict[str, Any] | None = None
    filters: list[dict[str, Any]] | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> Visualization:
        require(data, "type", "title")
        ds = data.get("data_source")
        layers = data.get("layers")
        return cls(
            type=data["type"],
            title=data["title"],
            description=data.get("description"),
            data_source=DataSource.from_dict(ds) if isinstance(ds, dict) else ds,
            layers=(
                [
                    VisualizationLayer.from_dict(layer)
                    if isinstance(layer, dict)
                    else layer
                    for layer in layers
                ]
                if layers is not None
                else None
            ),
            metrics=data.get("metrics"),
            query=data.get("query"),
            filters=data.get("filters"),
            extra=extra_fields(data, _FIELDS),
        )

    def to_dict(self) -> dict:
        return clean(
            {
                "type": self.type,
                "title": self.title,
                "description": self.description,
                "data_source": self.data_source,
                "layers": self.layers,
                "metrics": self.metrics,
                "query": self.query,
                "filters": self.filters,
                **self.extra,
            }
        )
