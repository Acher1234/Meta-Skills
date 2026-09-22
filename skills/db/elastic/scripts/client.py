"""Elasticsearch client — connection + JSON output."""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlparse

from elasticsearch import Elasticsearch

from skill_env import ENV


class ElasticClient:
    @classmethod
    def client(cls) -> Elasticsearch:
        url = ENV.url()
        verify = cls._verify_certs(url)
        return Elasticsearch(
            url,
            basic_auth=(ENV.username(), ENV.password()),
            verify_certs=verify,
            ssl_show_warn=verify,
        )

    @staticmethod
    def _verify_certs(url: str) -> bool:
        host = (urlparse(url).hostname or "").lower()
        return host not in {"localhost", "127.0.0.1", "::1"}

    @staticmethod
    def dump(data: Any) -> None:
        print(json.dumps(data, indent=2, default=str))
