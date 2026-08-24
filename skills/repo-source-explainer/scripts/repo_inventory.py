#!/usr/bin/env python3
"""Create a deterministic, language-agnostic repository inventory."""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path
import subprocess
import sys


EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
}

MANIFEST_NAMES = {
    "build.gradle",
    "build.gradle.kts",
    "cargo.toml",
    "cmakelists.txt",
    "composer.json",
    "deno.json",
    "deno.jsonc",
    "go.mod",
    "makefile",
    "mix.exs",
    "package.json",
    "pom.xml",
    "project.clj",
    "pyproject.toml",
    "requirements.txt",
    "setup.cfg",
    "setup.py",
}

SOURCE_SUFFIXES = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".cu",
    ".cuh",
    ".ex",
    ".exs",
    ".go",
    ".h",
    ".hpp",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".kts",
    ".lua",
    ".m",
    ".metal",
    ".mm",
    ".php",
    ".proto",
    ".py",
    ".rb",
    ".rs",
    ".scala",
    ".sh",
    ".sql",
    ".swift",
    ".ts",
    ".tsx",
    ".vue",
    ".zig",
}


def run_git(root: Path, *args: str) -> tuple[int, str]:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return result.returncode, result.stdout.strip()


def find_repo_root(path: Path) -> Path:
    code, output = run_git(path, "rev-parse", "--show-toplevel")
    return Path(output).resolve() if code == 0 and output else path.resolve()


def list_files(root: Path) -> list[Path]:
    code, output = run_git(root, "ls-files", "--cached", "--others", "--exclude-standard")
    if code == 0:
        return sorted(
            (root / line).resolve()
            for line in output.splitlines()
            if line and (root / line).is_file()
        )

    files: list[Path] = []
    for current, dirs, names in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED_DIRS)
        for name in sorted(names):
            files.append((Path(current) / name).resolve())
    return files


def relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def classify(files: list[Path], root: Path) -> dict[str, object]:
    extensions: Counter[str] = Counter()
    top_level: Counter[str] = Counter()
    manifests: list[str] = []
    tests: list[str] = []
    docs: list[str] = []
    entrypoints: list[str] = []
    source_sizes: list[tuple[int, str]] = []

    entrypoint_names = {
        "__main__.py",
        "app.py",
        "cli.py",
        "index.js",
        "index.ts",
        "main.c",
        "main.cc",
        "main.cpp",
        "main.go",
        "main.java",
        "main.py",
        "main.rs",
        "server.py",
    }

    for path in files:
        rel = relative(root, path)
        parts = Path(rel).parts
        top_level[parts[0] if len(parts) > 1 else "<root>"] += 1
        suffix = path.suffix.lower() or "<none>"
        extensions[suffix] += 1
        lower_name = path.name.lower()
        lower_parts = {part.lower() for part in parts}

        if lower_name in MANIFEST_NAMES or lower_name.endswith((".sln", ".csproj", ".xcodeproj")):
            manifests.append(rel)
        if lower_name in entrypoint_names:
            entrypoints.append(rel)
        if any(part in {"test", "tests", "spec", "specs"} for part in lower_parts) or lower_name.startswith("test_") or lower_name.endswith(("_test.go", ".spec.js", ".spec.ts", ".test.js", ".test.ts")):
            tests.append(rel)
        if any(part in {"doc", "docs", "documentation"} for part in lower_parts) or path.suffix.lower() in {".md", ".mdx", ".rst"}:
            docs.append(rel)
        if path.suffix.lower() in SOURCE_SUFFIXES:
            try:
                source_sizes.append((path.stat().st_size, rel))
            except OSError:
                pass

    return {
        "file_count": len(files),
        "extensions": dict(extensions.most_common()),
        "top_level": dict(top_level.most_common()),
        "manifests": sorted(manifests),
        "entrypoint_candidates": sorted(set(entrypoints))[:100],
        "test_files": sorted(set(tests))[:100],
        "documentation_files": sorted(set(docs))[:100],
        "largest_source_files": [
            {"path": path, "bytes": size}
            for size, path in sorted(source_sizes, reverse=True)[:20]
        ],
    }


def git_metadata(root: Path) -> dict[str, object]:
    code, revision = run_git(root, "rev-parse", "HEAD")
    if code != 0:
        return {"is_git_repository": False}
    _, branch = run_git(root, "branch", "--show-current")
    _, status = run_git(root, "status", "--porcelain")
    _, remote = run_git(root, "remote", "get-url", "origin")
    return {
        "is_git_repository": True,
        "revision": revision,
        "branch": branch or None,
        "dirty": bool(status),
        "remote_origin": remote or None,
    }


def to_markdown(data: dict[str, object]) -> str:
    repo = data["repository"]
    summary = data["summary"]
    lines = [
        "# Repository Inventory",
        "",
        f"- Root: `{repo['root']}`",
        f"- Git revision: `{repo.get('revision') or 'n/a'}`",
        f"- Branch: `{repo.get('branch') or 'n/a'}`",
        f"- Dirty: `{repo.get('dirty', False)}`",
        f"- Files: `{summary['file_count']}`",
        "",
        "## Top-Level Areas",
        "",
    ]
    for name, count in summary["top_level"].items():
        lines.append(f"- `{name}`: {count} files")
    lines.extend(["", "## Dominant Extensions", ""])
    for suffix, count in list(summary["extensions"].items())[:20]:
        lines.append(f"- `{suffix}`: {count}")
    for title, key in (
        ("Manifests", "manifests"),
        ("Entrypoint Candidates", "entrypoint_candidates"),
        ("Representative Test Files", "test_files"),
        ("Representative Documentation Files", "documentation_files"),
    ):
        lines.extend(["", f"## {title}", ""])
        values = summary[key]
        lines.extend(f"- `{value}`" for value in values) if values else lines.append("- None detected")
    lines.extend(["", "## Largest Source Files", ""])
    for item in summary["largest_source_files"]:
        lines.append(f"- `{item['path']}`: {item['bytes']} bytes")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", nargs="?", default=".", help="Repository path")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--output", help="Output file; stdout when omitted")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    requested = Path(args.repo).expanduser().resolve()
    if not requested.exists() or not requested.is_dir():
        print(f"error: repository path is not a directory: {requested}", file=sys.stderr)
        return 2

    root = find_repo_root(requested)
    files = list_files(root)
    data = {
        "repository": {"root": str(root), **git_metadata(root)},
        "summary": classify(files, root),
    }
    rendered = json.dumps(data, ensure_ascii=False, indent=2) + "\n" if args.format == "json" else to_markdown(data)

    if args.output:
        output = Path(args.output).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
