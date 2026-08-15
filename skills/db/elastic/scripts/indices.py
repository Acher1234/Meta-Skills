"""List Elasticsearch indices and fields."""

from __future__ import annotations

import argparse

from elasticsearch import NotFoundError

from client import ElasticClient


class Indices(ElasticClient):
    @staticmethod
    def list_indices(_: argparse.Namespace) -> int:
        Indices.dump(Indices.client().cat.indices(format="json").body)
        return 0

    @staticmethod
    def list_fields(args: argparse.Namespace) -> int:
        try:
            mapping = dict(Indices.client().indices.get_mapping(index=args.name).body)
        except NotFoundError as exc:
            Indices.dump(
                {"error": "index_not_found", "index": args.name, "detail": str(exc)}
            )
            return 1
        out = {}
        for index_name, payload in mapping.items():
            mappings = payload.get("mappings") or {}
            fields = Indices._flatten_fields(mappings.get("properties") or {})
            for runtime_name, spec in (mappings.get("runtime") or {}).items():
                fields[runtime_name] = spec.get("type", "runtime")
            out[index_name] = fields
        Indices.dump(out)
        return 0

    @staticmethod
    def _flatten_fields(properties: dict, prefix: str = "") -> dict[str, str]:
        fields: dict[str, str] = {}
        for name, spec in properties.items():
            path = f"{prefix}.{name}" if prefix else name
            nested = spec.get("properties")
            if nested:
                fields.update(Indices._flatten_fields(nested, path))
            for sub_name, sub_spec in (spec.get("fields") or {}).items():
                fields[f"{path}.{sub_name}"] = sub_spec.get("type", "unknown")
            field_type = spec.get("type")
            if field_type:
                fields[path] = field_type
            elif nested:
                fields.setdefault(path, "object")
        return fields

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        p = sub.add_parser("indices", help="List indices or fields")
        cmds = p.add_subparsers(required=True)
        cmds.add_parser("list", help="List indices").set_defaults(
            func=Indices.list_indices
        )
        fields = cmds.add_parser("fields", help="List fields of an index")
        fields.add_argument("name", help="Index name")
        fields.set_defaults(func=Indices.list_fields)
