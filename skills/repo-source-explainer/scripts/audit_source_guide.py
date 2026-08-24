#!/usr/bin/env python3
"""Audit a chaptered source guide for repeatable evidence and report hygiene."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys


SOURCE_RE = re.compile(
    r"^\s*>\s*Source:\s*`(?P<path>[^`#]+)(?:#L(?P<start>\d+)(?:-L?(?P<end>\d+))?)?`",
    re.MULTILINE,
)
PATH_RE = re.compile(
    r"`(?P<path>(?:[A-Za-z0-9_.-]+/)+(?:[A-Za-z0-9_.-]+\.(?:ts|tsx|js|mjs|py|rs|go|c|cc|cpp|cu|cuh|h|hpp|md|yml|yaml|json)))`"
)
PLACEHOLDER_RE = re.compile(r"待运行|待验证|TODO|TBD|to be run|not yet run", re.I)
STATE_RE = re.compile(r"\b(planned|executed|passed|failed|blocked|not run)\b|计划|已执行|通过|失败|阻断|未执行|未运行", re.I)


def git(root: Path, *args: str) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def metadata(root: Path) -> dict[str, object]:
    revision = git(root, "rev-parse", "HEAD")
    date = git(root, "show", "-s", "--format=%cs", "HEAD")
    branch = git(root, "branch", "--show-current") if revision else None
    status = git(root, "status", "--porcelain") if revision else None
    return {
        "root": str(root),
        "revision": revision,
        "date": date,
        "branch": branch or None,
        "dirty": bool(status),
    }


def markdown_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.md") if p.is_file())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path)
    parser.add_argument("docs", type=Path)
    parser.add_argument("--revision")
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--strict", action="store_true", help="return non-zero for warnings")
    args = parser.parse_args()

    repo = args.repo.expanduser().resolve()
    docs = args.docs.expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []
    required = {name: (docs / name).is_file() for name in ("index.md", "contents.md", "evidence-map.md", "verification.md")}
    errors.extend(f"missing required file: {name}" for name, present in required.items() if not present)

    files = markdown_files(docs) if docs.exists() else []
    chapters = sorted((docs / "chapters").glob("*.md")) if (docs / "chapters").is_dir() else []
    all_text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in files)
    citations = list(SOURCE_RE.finditer(all_text))
    cited_paths = sorted({m.group("path").strip().replace("\\", "/") for m in citations})
    per_chapter = {
        str(path.relative_to(docs)).replace("\\", "/"): len(SOURCE_RE.findall(path.read_text(encoding="utf-8", errors="replace")))
        for path in chapters
    }
    uncovered = [name for name, count in per_chapter.items() if count == 0]
    if uncovered:
        warnings.append("chapters without Source citations: " + ", ".join(uncovered))
    if not citations:
        errors.append("no Source citations found")

    target_meta = metadata(repo) if repo.is_dir() else {"root": str(repo), "revision": None}
    if args.revision and target_meta.get("revision") != args.revision:
        errors.append(f"revision mismatch: expected {args.revision}, observed {target_meta.get('revision')}")
    if args.revision and args.revision not in all_text:
        errors.append("expected revision is not recorded in the guide")

    verification = docs / "verification.md"
    verification_text = verification.read_text(encoding="utf-8", errors="replace") if verification.is_file() else ""
    if PLACEHOLDER_RE.search(verification_text):
        errors.append("verification report contains an unfinished placeholder")
    if verification.is_file() and not STATE_RE.search(verification_text):
        warnings.append("verification report does not use recognizable execution states")

    reference_meta = None
    if args.reference:
        reference = args.reference.expanduser().resolve()
        reference_meta = metadata(reference) if reference.is_dir() else {"root": str(reference), "revision": None}
        reference_text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in markdown_files(reference)) if reference.is_dir() else ""
        reference_paths = sorted({m.group("path").replace("\\", "/") for m in PATH_RE.finditer(reference_text)})
        missing = [path for path in reference_paths if not (repo / path).is_file()]
        if missing:
            warnings.append(f"reference mentions {len(missing)} path(s) missing at target revision")
        if target_meta.get("date") and reference_meta.get("date") and target_meta["date"] > reference_meta["date"]:
            warnings.append("reference commit is older than the analyzed source; inspect version drift")
        reference_meta["path_candidates"] = len(reference_paths)
        reference_meta["missing_paths"] = missing

    result = {
        "repository": target_meta,
        "guide": str(docs),
        "required_files": required,
        "chapters": len(chapters),
        "citations": len(citations),
        "unique_cited_paths": len(cited_paths),
        "citations_per_chapter": per_chapter,
        "errors": errors,
        "warnings": warnings,
        "reference": reference_meta,
    }
    output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.json_output:
        args.json_output.expanduser().resolve().write_text(output, encoding="utf-8")
    print(output, end="")
    return 1 if errors or (args.strict and warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
