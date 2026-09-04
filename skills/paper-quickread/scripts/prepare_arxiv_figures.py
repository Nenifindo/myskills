#!/usr/bin/env python3
"""Download arXiv LaTeX sources and prepare a manifest of Markdown-ready figures."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import gzip
from html.parser import HTMLParser
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import tarfile
import tempfile
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urljoin, urlparse
from urllib.request import Request, urlopen


USER_AGENT = "paper-quickread/1.0 (+https://arxiv.org)"
RENDERABLE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
GRAPHICS_EXTENSIONS = (".pdf", ".png", ".jpg", ".jpeg", ".eps", ".svg", ".gif", ".webp")
MODERN_ID_RE = re.compile(r"^(?P<base>\d{4}\.\d{4,5})(?P<version>v\d+)?$", re.I)
LEGACY_ID_RE = re.compile(
    r"^(?P<base>[a-z-]+(?:\.[A-Za-z-]+)?/\d{7})(?P<version>v\d+)?$",
    re.I,
)
INCLUDE_RE = re.compile(r"\\includegraphics\s*(?:\[[^\]]*\])?\s*\{([^{}]+)\}", re.S)
GRAPHICSPATH_RE = re.compile(r"\\graphicspath\s*\{((?:\s*\{[^{}]*\}\s*)+)\}", re.S)
INNER_PATH_RE = re.compile(r"\{([^{}]*)\}")
FIGURE_BEGIN_RE = re.compile(r"\\begin\{figure\*?\}")
FIGURE_END_RE = re.compile(r"\\end\{figure\*?\}")
VERSION_IN_FILENAME_RE = re.compile(
    r"arXiv-(?P<id>(?:\d{4}\.\d{4,5}|[A-Za-z.-]+_\d{7})v\d+)", re.I
)


class PreparationError(RuntimeError):
    """A user-facing preparation failure."""


@dataclass(frozen=True)
class ArxivIdentifier:
    base: str
    version: str | None = None

    @property
    def full(self) -> str:
        return self.base + (self.version or "")


@dataclass
class HtmlAsset:
    url: str
    caption: str = ""
    figure_id: str = ""

    @property
    def stem_key(self) -> str:
        return Path(unquote(urlparse(self.url).path)).stem.casefold()


@dataclass
class HtmlFigure:
    figure_id: str = ""
    caption_parts: list[str] = field(default_factory=list)
    assets: list[HtmlAsset] = field(default_factory=list)
    caption_depth: int = 0


class ArxivHtmlParser(HTMLParser):
    """Collect figure assets and captions from arXiv's LaTeXML HTML."""

    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.figure_stack: list[HtmlFigure] = []
        self.figures: list[HtmlFigure] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "figure":
            figure = HtmlFigure(figure_id=values.get("id", ""))
            self.figure_stack.append(figure)
            return
        if not self.figure_stack:
            return
        current = self.figure_stack[-1]
        if tag == "figcaption":
            current.caption_depth += 1
        if tag in {"img", "object"}:
            raw_url = values.get("src") if tag == "img" else values.get("data")
            if raw_url and not raw_url.startswith("data:"):
                current.assets.append(
                    HtmlAsset(url=urljoin(self.base_url, raw_url), figure_id=current.figure_id)
                )

    def handle_endtag(self, tag: str) -> None:
        if not self.figure_stack:
            return
        current = self.figure_stack[-1]
        if tag == "figcaption" and current.caption_depth:
            current.caption_depth -= 1
        elif tag == "figure":
            completed = self.figure_stack.pop()
            caption = normalize_space("".join(completed.caption_parts))
            for asset in completed.assets:
                asset.caption = caption
            self.figures.append(completed)

    def handle_data(self, data: str) -> None:
        if self.figure_stack and self.figure_stack[-1].caption_depth:
            self.figure_stack[-1].caption_parts.append(data)


def normalize_space(value: str) -> str:
    return " ".join(value.split())


def parse_arxiv_identifier(value: str) -> ArxivIdentifier:
    raw = value.strip()
    if not raw:
        raise PreparationError("arXiv URL or identifier is empty")

    if "://" in raw:
        parsed = urlparse(raw)
        host = (parsed.hostname or "").casefold()
        if host not in {"arxiv.org", "www.arxiv.org", "export.arxiv.org"}:
            raise PreparationError(f"not an arXiv URL: {value}")
        path = unquote(parsed.path).strip("/")
        for prefix in ("abs/", "pdf/", "html/", "format/", "src/", "e-print/"):
            if path.startswith(prefix):
                path = path[len(prefix) :]
                break
        if path.endswith(".pdf"):
            path = path[:-4]
        raw = path.strip("/")
    elif raw.casefold().startswith("arxiv:"):
        raw = raw.split(":", 1)[1].strip()

    match = MODERN_ID_RE.fullmatch(raw) or LEGACY_ID_RE.fullmatch(raw)
    if not match:
        raise PreparationError(f"unsupported arXiv URL or identifier: {value}")
    version = match.group("version")
    return ArxivIdentifier(match.group("base"), version.casefold() if version else None)


def request_bytes(url: str, timeout: float) -> tuple[bytes, dict[str, str], str]:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.read(), dict(response.headers.items()), response.geturl()
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise PreparationError(f"download failed for {url}: {exc}") from exc


def resolved_identifier(requested: ArxivIdentifier, headers: dict[str, str]) -> ArxivIdentifier:
    if requested.version:
        return requested
    disposition = next(
        (value for key, value in headers.items() if key.casefold() == "content-disposition"),
        "",
    )
    match = VERSION_IN_FILENAME_RE.search(disposition)
    if not match:
        return requested
    full = match.group("id").replace("_", "/", 1) if "/" in requested.base else match.group("id")
    try:
        candidate = parse_arxiv_identifier(full)
    except PreparationError:
        return requested
    return candidate if candidate.base.casefold() == requested.base.casefold() else requested


def reset_known_outputs(output_dir: Path, overwrite: bool) -> None:
    known = (output_dir / "source", output_dir / "figures", output_dir / "figures-manifest.json")
    existing = [path for path in known if path.exists() or path.is_symlink()]
    if existing and not overwrite:
        names = ", ".join(path.name for path in existing)
        raise PreparationError(f"output already exists ({names}); pass --overwrite to replace it")
    if not overwrite:
        return
    for path in existing:
        if path.is_symlink() or path.is_file():
            path.unlink()
        else:
            shutil.rmtree(path)


def safe_extract_tar(archive: Path, destination: Path) -> None:
    destination = destination.resolve()
    with tarfile.open(archive, mode="r:*") as bundle:
        for member in bundle.getmembers():
            member_path = PurePosixPath(member.name)
            if member_path.is_absolute() or ".." in member_path.parts:
                raise PreparationError(f"unsafe path in source archive: {member.name}")
            if member.issym() or member.islnk() or member.isdev() or member.isfifo():
                raise PreparationError(f"unsupported archive member: {member.name}")
            target = destination.joinpath(*member_path.parts)
            if os.path.commonpath((str(destination), str(target.resolve()))) != str(destination):
                raise PreparationError(f"unsafe path in source archive: {member.name}")
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                target.parent.mkdir(parents=True, exist_ok=True)
                source = bundle.extractfile(member)
                if source is None:
                    raise PreparationError(f"could not read archive member: {member.name}")
                with source, target.open("wb") as output:
                    shutil.copyfileobj(source, output)


def unpack_source(payload: bytes, destination: Path) -> str:
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="paper-quickread-") as temp_name:
        temp = Path(temp_name)
        archive = temp / "source-download"
        archive.write_bytes(payload)
        if payload.startswith(b"\x1f\x8b"):
            try:
                decompressed = gzip.decompress(payload)
            except OSError as exc:
                raise PreparationError(f"invalid gzip source archive: {exc}") from exc
            inner = temp / "source-uncompressed"
            inner.write_bytes(decompressed)
            if tarfile.is_tarfile(inner):
                safe_extract_tar(inner, destination)
                return "tar.gz"
            (destination / "main.tex").write_bytes(decompressed)
            return "tex.gz"
        if tarfile.is_tarfile(archive):
            safe_extract_tar(archive, destination)
            return "tar"
        if b"\\document" in payload or b"\\begin{" in payload:
            (destination / "main.tex").write_bytes(payload)
            return "tex"
    raise PreparationError("downloaded arXiv source is not a supported tar or TeX payload")


def strip_comments(text: str) -> str:
    output: list[str] = []
    for line in text.splitlines(keepends=True):
        comment_at = None
        for index, char in enumerate(line):
            if char != "%":
                continue
            backslashes = 0
            cursor = index - 1
            while cursor >= 0 and line[cursor] == "\\":
                backslashes += 1
                cursor -= 1
            if backslashes % 2 == 0:
                comment_at = index
                break
        if comment_at is None:
            output.append(line)
        else:
            suffix = "\n" if line.endswith("\n") else ""
            output.append(line[:comment_at] + " " * (len(line) - comment_at - len(suffix)) + suffix)
    return "".join(output)


def command_arguments(text: str, command: str) -> list[str]:
    results: list[str] = []
    pattern = re.compile(r"\\" + re.escape(command) + r"\s*(?:\[[^\]]*\]\s*)?\{")
    for match in pattern.finditer(text):
        start = match.end() - 1
        depth = 0
        for index in range(start, len(text)):
            if text[index] == "{" and (index == 0 or text[index - 1] != "\\"):
                depth += 1
            elif text[index] == "}" and (index == 0 or text[index - 1] != "\\"):
                depth -= 1
                if depth == 0:
                    results.append(text[start + 1 : index])
                    break
    return results


def tex_to_text(value: str) -> str:
    value = re.sub(r"\\(?:textit|textbf|emph|textrm|texttt)\s*\{([^{}]*)\}", r"\1", value)
    value = value.replace("\\&", "&").replace("~", " ")
    value = re.sub(r"\\[A-Za-z@]+\*?", "", value)
    value = value.replace("{", "").replace("}", "")
    return normalize_space(value)


def containing_figure(text: str, position: int) -> str:
    begins = [match for match in FIGURE_BEGIN_RE.finditer(text, 0, position)]
    if not begins:
        return ""
    begin = begins[-1]
    previous_end = list(FIGURE_END_RE.finditer(text, 0, position))
    if previous_end and previous_end[-1].start() > begin.start():
        return ""
    end = FIGURE_END_RE.search(text, position)
    return text[begin.start() : end.end()] if end else ""


def collect_graphics_paths(tex_files: Iterable[Path], source_root: Path) -> list[Path]:
    paths: list[Path] = []
    for tex_file in tex_files:
        text = strip_comments(tex_file.read_text(encoding="utf-8", errors="replace"))
        for match in GRAPHICSPATH_RE.finditer(text):
            for raw in INNER_PATH_RE.findall(match.group(1)):
                if not raw or "\\" in raw:
                    continue
                for base in (tex_file.parent, source_root):
                    candidate = (base / raw).resolve()
                    if candidate not in paths and candidate.is_relative_to(source_root.resolve()):
                        paths.append(candidate)
    return paths


def resolve_graphic(
    declared: str,
    tex_file: Path,
    source_root: Path,
    graphics_paths: Iterable[Path],
) -> Path | None:
    if not declared.strip() or "\\" in declared or "#" in declared:
        return None
    declared_path = Path(declared.strip())
    bases = [tex_file.parent, source_root, *graphics_paths]
    candidates: list[Path] = []
    for base in bases:
        direct = base / declared_path
        candidates.append(direct)
        if not declared_path.suffix:
            candidates.extend(Path(str(direct) + extension) for extension in GRAPHICS_EXTENSIONS)
    root = source_root.resolve()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved.is_relative_to(root) and resolved.is_file():
            return resolved
    return None


def scan_latex_figures(source_root: Path) -> list[dict[str, object]]:
    tex_files = sorted(source_root.rglob("*.tex"))
    graphics_paths = collect_graphics_paths(tex_files, source_root)
    figures: list[dict[str, object]] = []
    for tex_file in tex_files:
        raw_text = tex_file.read_text(encoding="utf-8", errors="replace")
        text = strip_comments(raw_text)
        for match in INCLUDE_RE.finditer(text):
            declared = normalize_space(match.group(1))
            resolved = resolve_graphic(declared, tex_file, source_root, graphics_paths)
            environment = containing_figure(text, match.start())
            captions = [tex_to_text(value) for value in command_arguments(environment, "caption")]
            labels = [normalize_space(value) for value in command_arguments(environment, "label")]
            figures.append(
                {
                    "index": len(figures) + 1,
                    "tex_file": tex_file.relative_to(source_root).as_posix(),
                    "line": text.count("\n", 0, match.start()) + 1,
                    "declared_path": declared,
                    "source_path": resolved.relative_to(source_root).as_posix() if resolved else None,
                    "caption": captions[-1] if captions else "",
                    "label": labels[-1] if labels else "",
                    "captions": captions,
                    "labels": labels,
                    "renderable_path": None,
                    "renderable_source": None,
                    "status": "pending" if resolved else "missing-source",
                    "warnings": [] if resolved else ["LaTeX image reference could not be resolved"],
                }
            )
    return figures


def parse_html_assets(html: str, base_url: str) -> list[HtmlAsset]:
    parser = ArxivHtmlParser(base_url)
    parser.feed(html)
    return [asset for figure in parser.figures for asset in figure.assets]


def safe_asset_name(index: int, source_path: str, extension: str) -> str:
    stem = Path(source_path).stem
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip("-._") or "figure"
    return f"figure-{index:03d}-{slug}{extension.casefold()}"


def copy_source_asset(source: Path, figures_dir: Path, index: int, source_path: str) -> str:
    name = safe_asset_name(index, source_path, source.suffix)
    target = figures_dir / name
    shutil.copyfile(source, target)
    return target.relative_to(figures_dir.parent).as_posix()


def download_html_asset(
    asset: HtmlAsset,
    figures_dir: Path,
    index: int,
    source_path: str,
    timeout: float,
) -> str:
    extension = Path(unquote(urlparse(asset.url).path)).suffix.casefold()
    if extension not in RENDERABLE_EXTENSIONS:
        raise PreparationError(f"arXiv HTML asset is not Markdown-renderable: {asset.url}")
    last_error: PreparationError | None = None
    for attempt in range(2):
        try:
            payload, _, _ = request_bytes(asset.url, timeout)
            break
        except PreparationError as exc:
            last_error = exc
            if attempt == 1:
                raise
    else:
        raise last_error or PreparationError(f"could not download {asset.url}")
    prefix = payload[:256].lstrip().lower()
    if prefix.startswith(b"<!doctype html") or prefix.startswith(b"<html"):
        raise PreparationError(f"arXiv HTML asset returned an HTML page: {asset.url}")
    name = safe_asset_name(index, source_path, extension)
    target = figures_dir / name
    target.write_bytes(payload)
    return target.relative_to(figures_dir.parent).as_posix()


def prepare_renderable_figures(
    figures: list[dict[str, object]],
    source_root: Path,
    figures_dir: Path,
    html_assets: list[HtmlAsset],
    timeout: float,
) -> None:
    by_stem: dict[str, list[HtmlAsset]] = {}
    for asset in html_assets:
        candidates = by_stem.setdefault(asset.stem_key, [])
        if all(existing.url != asset.url for existing in candidates):
            candidates.append(asset)
    copied: dict[tuple[str, str], str] = {}
    figures_dir.mkdir(parents=True, exist_ok=True)

    for figure in figures:
        source_path = figure["source_path"]
        if not isinstance(source_path, str):
            continue
        source = source_root / source_path
        source_key = source_path.casefold()
        if source.suffix.casefold() in RENDERABLE_EXTENSIONS:
            cache_key = (source_key, "source")
            if cache_key not in copied:
                copied[cache_key] = copy_source_asset(
                    source, figures_dir, int(figure["index"]), source_path
                )
            figure["renderable_path"] = copied[cache_key]
            figure["renderable_source"] = "latex-source"
            figure["status"] = "ready"
            continue

        candidates = by_stem.get(source.stem.casefold(), [])
        if not candidates:
            figure["status"] = "unresolved"
            figure["warnings"].append("no matching SVG/PNG asset found in arXiv HTML")
            continue
        if len(candidates) > 1:
            figure["status"] = "unresolved"
            figure["warnings"].append(
                "multiple arXiv HTML assets share this basename; refusing an ambiguous match"
            )
            continue
        asset = candidates[0]
        cache_key = (source_key, asset.url)
        try:
            if cache_key not in copied:
                copied[cache_key] = download_html_asset(
                    asset, figures_dir, int(figure["index"]), source_path, timeout
                )
            figure["renderable_path"] = copied[cache_key]
            figure["renderable_source"] = "arxiv-html"
            figure["html_asset_url"] = asset.url
            figure["html_caption"] = asset.caption
            figure["html_figure_id"] = asset.figure_id
            figure["status"] = "ready"
        except PreparationError as exc:
            figure["status"] = "unresolved"
            figure["warnings"].append(str(exc))


def build_manifest(
    requested: ArxivIdentifier,
    resolved: ArxivIdentifier,
    source_url: str,
    html_url: str,
    source_format: str,
    html_status: str,
    figures: list[dict[str, object]],
    warnings: list[str],
) -> dict[str, object]:
    ready = sum(figure["status"] == "ready" for figure in figures)
    return {
        "schema_version": 1,
        "arxiv": {
            "requested": requested.full,
            "id": resolved.base,
            "version": resolved.version,
            "resolved_id": resolved.full,
            "source_url": source_url,
            "html_url": html_url,
            "source_format": source_format,
            "html_status": html_status,
        },
        "summary": {
            "latex_references": len(figures),
            "ready": ready,
            "unresolved": len(figures) - ready,
        },
        "figures": figures,
        "warnings": warnings,
    }


def prepare(value: str, output_dir: Path, overwrite: bool, timeout: float) -> dict[str, object]:
    requested = parse_arxiv_identifier(value)
    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    reset_known_outputs(output_dir, overwrite)

    source_url = f"https://export.arxiv.org/e-print/{quote(requested.full, safe='/')}"
    source_payload, source_headers, _ = request_bytes(source_url, timeout)
    resolved = resolved_identifier(requested, source_headers)
    source_root = output_dir / "source"
    source_format = unpack_source(source_payload, source_root)
    figures = scan_latex_figures(source_root)

    html_url = f"https://arxiv.org/html/{quote(resolved.full, safe='/')}"
    warnings: list[str] = []
    html_assets: list[HtmlAsset] = []
    try:
        html_payload, _, final_html_url = request_bytes(html_url, timeout)
        html_assets = parse_html_assets(html_payload.decode("utf-8", errors="replace"), final_html_url)
        html_status = "available"
        if not html_assets:
            html_status = "available-without-figure-assets"
            warnings.append("arXiv HTML was available but exposed no figure assets")
    except PreparationError as exc:
        html_status = "unavailable"
        warnings.append(str(exc))

    figures_dir = output_dir / "figures"
    prepare_renderable_figures(figures, source_root, figures_dir, html_assets, timeout)
    manifest = build_manifest(
        requested,
        resolved,
        source_url,
        html_url,
        source_format,
        html_status,
        figures,
        warnings,
    )
    (output_dir / "figures-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("arxiv", help="arXiv abs/pdf/html URL, arXiv: identifier, or bare ID")
    parser.add_argument("--output-dir", required=True, type=Path, help="directory for source, figures, and manifest")
    parser.add_argument("--overwrite", action="store_true", help="replace this script's existing outputs")
    parser.add_argument("--timeout", type=float, default=60.0, help="network timeout in seconds (default: 60)")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    try:
        manifest = prepare(args.arxiv, args.output_dir, args.overwrite, args.timeout)
    except PreparationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    summary = manifest["summary"]
    arxiv = manifest["arxiv"]
    print(
        f"Prepared arXiv {arxiv['resolved_id']}: "
        f"{summary['ready']}/{summary['latex_references']} referenced images are Markdown-ready."
    )
    print(args.output_dir.expanduser().resolve() / "figures-manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
