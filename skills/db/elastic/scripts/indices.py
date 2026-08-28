"""List Elasticsearch indices, fields, and search documents."""

from __future__ import annotations

import argparse
import json
from typing import Any

from elasticsearch import NotFoundError

from client import ElasticClient

_DEFAULT_SIZE = 10
_ALL_BATCH = 100
_MAX_FROM = 10_000


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
    def query(args: argparse.Namespace) -> int:
        try:
            Indices.dump(
                Indices.search_index(
                    args.name,
                    args.esquery,
                    page=args.page,
                    skip=args.skip,
                    number_of_document=args.number_of_document,
                    fetch_all=args.all,
                )
            )
        except NotFoundError as exc:
            Indices.dump(
                {
                    "error": "index_not_found",
                    "index": args.name,
                    "detail": str(exc),
                }
            )
            return 1
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        return 0

    @staticmethod
    def search_index(
        index: str,
        esquery: str,
        *,
        page: int | None = None,
        skip: int | None = None,
        number_of_document: int | None = None,
        fetch_all: bool = False,
    ) -> dict:
        query, extra = Indices._esquery(esquery)
        size = number_of_document
        if size is None:
            size = _ALL_BATCH if fetch_all else _DEFAULT_SIZE
        if size < 1:
            raise ValueError("number-of-document must be >= 1")
        offset = skip or 0
        if offset < 0:
            raise ValueError("skip must be >= 0")
        if page is not None:
            if page < 1:
                raise ValueError("page must be >= 1")
            offset += (page - 1) * size
        if fetch_all:
            return Indices._search_all(index, query, extra, offset, size)
        return Indices._search_page(index, query, extra, offset, size)

    @staticmethod
    def _search_page(
        index: str,
        query: dict,
        extra: dict,
        offset: int,
        size: int,
    ) -> dict:
        data = Indices._search(index, query, extra, offset, size)
        hits_obj = data.get("hits") or {}
        hits = hits_obj.get("hits") or []
        return {
            "index": index,
            "from": offset,
            "size": size,
            "total": Indices._hit_total(hits_obj),
            "count": len(hits),
            "hits": hits,
        }

    @staticmethod
    def _search_all(
        index: str,
        query: dict,
        extra: dict,
        offset: int,
        size: int,
    ) -> dict:
        hits: list = []
        current = offset
        total = None
        while current < _MAX_FROM:
            batch = min(size, _MAX_FROM - current)
            data = Indices._search(index, query, extra, current, batch)
            hits_obj = data.get("hits") or {}
            chunk = hits_obj.get("hits") or []
            total = Indices._hit_total(hits_obj)
            hits.extend(chunk)
            if not chunk:
                break
            if total is not None and offset + len(hits) >= total:
                break
            current += len(chunk)
        return {
            "index": index,
            "from": offset,
            "size": size,
            "all": True,
            "total": total,
            "count": len(hits),
            "hits": hits,
        }

    @staticmethod
    def _search(
        index: str,
        query: dict,
        extra: dict,
        offset: int,
        size: int,
    ) -> dict:
        kwargs: dict[str, Any] = {
            "index": index,
            "query": query,
            "from_": offset,
            "size": size,
            "track_total_hits": True,
            "ignore_unavailable": True,
        }
        if "sort" in extra:
            kwargs["sort"] = extra["sort"]
        source = extra.get("_source", extra.get("source"))
        if source is not None:
            kwargs["source"] = source
        return dict(Indices.client().search(**kwargs).body)

    @staticmethod
    def _esquery(raw: str) -> tuple[dict, dict]:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return {"query_string": {"query": raw}}, {}
        if not isinstance(data, dict):
            raise ValueError("esquery must be a JSON object or a query string")
        if "query" in data:
            extra = {k: v for k, v in data.items() if k != "query"}
            return data["query"], extra
        return data, {}

    @staticmethod
    def _hit_total(hits_obj: dict) -> int | None:
        total = hits_obj.get("total")
        if isinstance(total, dict):
            return total.get("value")
        return total

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

        query = cmds.add_parser("query", help="Search documents in an index")
        query.add_argument("name", help="Index name")
        query.add_argument(
            "--esquery",
            required=True,
            help="Query DSL JSON object, search body, or query string",
        )
        query.add_argument("--page", type=int, help="Page index (1-based)")
        query.add_argument("--skip", type=int, help="Extra documents to skip")
        query.add_argument(
            "--number-of-document",
            type=int,
            help="Page size (batch size with --all)",
        )
        query.add_argument(
            "--all",
            action="store_true",
            help="Fetch all remaining hits from the offset",
        )
        query.set_defaults(func=Indices.query)
