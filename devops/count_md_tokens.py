#!/usr/bin/env python3
"""Count tokens in every Markdown file under a path."""

import argparse
import sys
from pathlib import Path
import tiktoken

def count_tokens(text: str, encoding_name: str) -> int:
    return len(tiktoken.get_encoding(encoding_name).encode(text))


def iter_markdown_files(root: Path) -> list[Path]:
    if root.is_file():
        if root.suffix.lower() != ".md":
            raise SystemExit(f"not a Markdown file: {root}")
        return [root]
    if not root.is_dir():
        raise SystemExit(f"path not found: {root}")
    return sorted(file for file in root.rglob("*.md") if file.is_file())


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Count tokens in Markdown files under a path."
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Directory (recursive) or a single .md file",
    )
    parser.add_argument(
        "--encoding",
        default="cl100k_base",
        help="tiktoken encoding (default: cl100k_base)",
    )
    parser.add_argument(
        "--sort",
        choices=("path", "tokens"),
        default="tokens",
        help="Sort output by path or token count (default: path)",
    )
    args = parser.parse_args()

    root = args.path.expanduser().resolve()
    files = iter_markdown_files(root)
    if not files:
        print(f"no .md files under {root}", file=sys.stderr)
        return 1

    rows: list[tuple[Path, int]] = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        rows.append((path, count_tokens(text, args.encoding)))

    if args.sort == "tokens":
        rows.sort(key=lambda row: (-row[1], str(row[0])))

    print(f"# files: {len(rows)}  encoding: {args.encoding}", file=sys.stderr)
    for path, tokens in rows:
        print(f"{path} -> {tokens}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
