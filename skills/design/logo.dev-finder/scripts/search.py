"""Search logo.dev and download each logo into a folder."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from skill_env import ENV

SEARCH_URL = "https://api.logo.dev/search"
_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")
_CONTENT_EXT = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/webp": ".webp",
    "image/svg+xml": ".svg",
    "image/gif": ".gif",
}


class Search:
    def search(self, query: str) -> list[dict[str, Any]]:
        q = query.strip()
        if not q:
            raise SystemExit("query is required (search term or domain)")
        url = f"{SEARCH_URL}?{urlencode({'q': q})}"
        req = Request(url, method="GET")
        req.add_header("Authorization", f"Bearer {ENV.api_key()}")
        req.add_header("Accept", "application/json")
        try:
            with urlopen(req, timeout=60) as resp:
                raw = resp.read()
        except HTTPError as exc:
            body = exc.read().decode(errors="replace")
            try:
                parsed = json.loads(body) if body else {"error": str(exc)}
            except json.JSONDecodeError:
                parsed = {"error": body or str(exc)}
            self.dump({"ok": False, "status": exc.code, "error": parsed})
            raise SystemExit(1) from exc
        except URLError as exc:
            raise SystemExit(f"request failed: {exc}") from exc
        data = json.loads(raw) if raw else []
        if not isinstance(data, list):
            raise SystemExit("unexpected search response (expected a list)")
        return data

    def download_logos(
        self,
        query: str,
        folder: Path,
        *,
        force: bool = False,
    ) -> dict[str, Any]:
        dest = folder.expanduser().resolve()
        dest.mkdir(parents=True, exist_ok=True)
        hits = self.search(query)
        saved: list[dict[str, Any]] = []
        skipped: list[dict[str, Any]] = []
        failed: list[dict[str, Any]] = []
        for hit in hits:
            if not isinstance(hit, dict):
                continue
            name = str(hit.get("name") or "")
            domain = str(hit.get("domain") or "")
            logo_url = str(hit.get("logo_url") or "")
            row = {"name": name, "domain": domain, "logo_url": logo_url}
            if not logo_url or not domain:
                failed.append({**row, "error": "missing domain or logo_url"})
                continue
            try:
                path, existed = self._download(logo_url, dest, domain, force=force)
            except SystemExit:
                raise
            except Exception as exc:
                failed.append({**row, "error": str(exc)})
                continue
            if existed:
                skipped.append({**row, "path": str(path)})
            else:
                saved.append({**row, "path": str(path)})
        return {
            "ok": True,
            "query": query,
            "folder": str(dest),
            "total": len(hits),
            "saved": saved,
            "skipped": skipped,
            "failed": failed,
        }

    def _download(
        self, logo_url: str, folder: Path, domain: str, *, force: bool
    ) -> tuple[Path, bool]:
        req = Request(logo_url, method="GET")
        try:
            with urlopen(req, timeout=60) as resp:
                payload = resp.read()
                ctype = (resp.headers.get_content_type() or "").lower()
        except HTTPError as exc:
            raise RuntimeError(f"download HTTP {exc.code}") from exc
        except URLError as exc:
            raise RuntimeError(f"download failed: {exc}") from exc
        suffix = _CONTENT_EXT.get(ctype, ".png")
        path = folder / f"{self._safe_stem(domain)}{suffix}"
        if path.exists() and not force:
            return path, True
        path.write_bytes(payload)
        return path, False

    @staticmethod
    def _safe_stem(domain: str) -> str:
        stem = _SAFE_NAME.sub("_", domain.strip().lower()).strip("._")
        return stem or "logo"

    @staticmethod
    def dump(data: Any) -> None:
        print(json.dumps(data, indent=2, default=str))

    def cmd_search(self, args: argparse.Namespace) -> None:
        self.dump(
            self.download_logos(
                args.query, Path(args.folder), force=args.force
            )
        )
        return None

    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        client = Search()
        p = sub.add_parser(
            "search",
            help="Search logo.dev by term or domain and download logos",
        )
        p.add_argument("query", help="Search term or domain")
        p.add_argument(
            "--folder",
            required=True,
            help="Folder to save downloaded logos",
        )
        p.add_argument("--force", action="store_true", help="Overwrite existing files")
        p.set_defaults(func=client.cmd_search)
