#!/usr/bin/env python3
"""Validate visible Source citations in Markdown against a repository tree."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


SOURCE_RE = re.compile(
    r"^\s*>\s*Source:\s*`(?P<path>[^`#]+)(?:#L(?P<start>\d+)(?:-L?(?P<end>\d+))?)?`",
    re.MULTILINE,
)


def markdown_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix.lower() in {".md", ".mdx"} else []
    return sorted(p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in {".md", ".mdx"})


def validate(repo: Path, docs: Path, require: bool) -> tuple[list[str], int]:
    errors: list[str] = []
    reference_count = 0

    for doc in markdown_files(docs):
        text = doc.read_text(encoding="utf-8", errors="replace")
        for match in SOURCE_RE.finditer(text):
            reference_count += 1
            raw_path = match.group("path").strip().replace("\\", "/")
            source_path = Path(raw_path)
            doc_line = text.count("\n", 0, match.start()) + 1
            location = f"{doc}:{doc_line}"

            if source_path.is_absolute() or ".." in source_path.parts:
                errors.append(f"{location}: source path must be repository-relative: {raw_path}")
                continue

            target = (repo / source_path).resolve()
            try:
                target.relative_to(repo)
            except ValueError:
                errors.append(f"{location}: source path escapes repository: {raw_path}")
                continue

            if not target.is_file():
                errors.append(f"{location}: source file does not exist: {raw_path}")
                continue

            start_text = match.group("start")
            end_text = match.group("end")
            if start_text:
                start = int(start_text)
                end = int(end_text) if end_text else start
                line_count = sum(1 for _ in target.open("r", encoding="utf-8", errors="replace"))
                if start < 1 or end < start or end > line_count:
                    errors.append(
                        f"{location}: invalid line range L{start}-L{end} for {raw_path} ({line_count} lines)"
                    )

    if require and reference_count == 0:
        errors.append(f"{docs}: no Source citations found")
    return errors, reference_count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", help="Repository root containing cited source files")
    parser.add_argument("docs", help="Markdown file or directory to validate")
    parser.add_argument("--require", action="store_true", help="Fail when no Source citations are found")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).expanduser().resolve()
    docs = Path(args.docs).expanduser().resolve()
    if not repo.is_dir():
        print(f"error: repository path is not a directory: {repo}", file=sys.stderr)
        return 2
    if not docs.exists():
        print(f"error: docs path does not exist: {docs}", file=sys.stderr)
        return 2

    errors, count = validate(repo, docs, args.require)
    if errors:
        for error in errors:
            print(f"ERROR {error}")
        print(f"Validated {count} source citation(s); {len(errors)} error(s).")
        return 1

    print(f"Validated {count} source citation(s); no errors.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
