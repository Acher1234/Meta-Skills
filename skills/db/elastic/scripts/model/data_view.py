from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from model._serialize import clean, extra_fields

_FIELDS = {
    "title",
    "name",
    "timeFieldName",
    "id",
    "allowNoIndex",
    "sourceFilters",
    "fieldFormats",
    "runtimeFieldMap",
    "namespaces",
}


@dataclass
class DataView:
    title: str | None = None
    name: str | None = None
    timeFieldName: str | None = None
    id: str | None = None
    allowNoIndex: bool | None = None
    sourceFilters: list | None = None
    fieldFormats: dict[str, Any] | None = None
    runtimeFieldMap: dict[str, Any] | None = None
    namespaces: list[str] | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> DataView:
        return cls(
            title=data.get("title"),
            name=data.get("name"),
            timeFieldName=data.get("timeFieldName") or data.get("time_field"),
            id=data.get("id"),
            allowNoIndex=data.get("allowNoIndex"),
            sourceFilters=data.get("sourceFilters"),
            fieldFormats=data.get("fieldFormats"),
            runtimeFieldMap=data.get("runtimeFieldMap"),
            namespaces=data.get("namespaces"),
            extra=extra_fields(data, _FIELDS | {"time_field"}),
        )

    def to_dict(self) -> dict:
        return clean(
            {
                "title": self.title,
                "name": self.name,
                "timeFieldName": self.timeFieldName,
                "id": self.id,
                "allowNoIndex": self.allowNoIndex,
                "sourceFilters": self.sourceFilters,
                "fieldFormats": self.fieldFormats,
                "runtimeFieldMap": self.runtimeFieldMap,
                "namespaces": self.namespaces,
                **self.extra,
            }
        )
