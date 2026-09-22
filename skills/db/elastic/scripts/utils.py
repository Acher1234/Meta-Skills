"""Elasticsearch helpers — cluster ping and health."""

from __future__ import annotations

import argparse

from client import ElasticClient


class Utils(ElasticClient):
    @staticmethod
    def ping(_: argparse.Namespace) -> int:
        Utils.dump(dict(Utils.client().info().body))
        return 0

    @staticmethod
    def health(_: argparse.Namespace) -> int:
        Utils.dump(dict(Utils.client().cluster.health().body))
        return 0

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        sub.add_parser("ping", help="GET / cluster info").set_defaults(func=Utils.ping)
        sub.add_parser("health", help="Cluster health").set_defaults(func=Utils.health)
