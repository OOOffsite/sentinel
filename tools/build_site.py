"""Build the public static site from explicit sources using markdown-it-py."""
from __future__ import annotations

import argparse
import html
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit, urlunsplit

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "_site"
MARKER = ".sentinel-site-build"


def relative(target: Path, page: Path) -> str:
    return Path(os.path.relpath(target, page.parent)).as_posix()


def walk(tokens):
    for token in tokens:
        yield token
        yield from walk(token.children or [])


def build() -> None:
    subprocess.run([sys.executable, str(ROOT / "tools/build_product_preview.py"), "--check"], check=True)
    # Refuse to erase a directory we did not create.
    if OUTPUT.is_symlink():
        raise ValueError("_site must not be a symlink")
    if OUTPUT.exists():
        if not (OUTPUT / MARKER).is_file():
            raise ValueError("_site exists without the build marker; inspect it first")
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()
    (OUTPUT / MARKER).write_text("Generated public documentation.\n")
    (OUTPUT / ".nojekyll").touch()
    mapping = {}

    def copy(source: Path, target: Path):
        if source.is_symlink():
            raise ValueError(f"Public source must not be a symlink: {source.relative_to(ROOT)}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        mapping[source.resolve()] = target

    copy(ROOT / "site/index.html", OUTPUT / "index.html")
    fragment = (ROOT / "site/assets/product-preview.html").read_text()
    homepage = (OUTPUT / "index.html").read_text()
    if homepage.count("<!-- PRODUCT_PREVIEW -->") != 1:
        raise ValueError("Homepage needs exactly one product preview slot")
    (OUTPUT / "index.html").write_text(homepage.replace("<!-- PRODUCT_PREVIEW -->", fragment))
    for source in sorted((ROOT / "site/assets").rglob("*")):
        if source.is_file() and source.suffix.lower() in {".css", ".js", ".svg", ".png", ".webp", ".ico", ".html", ".json", ".woff2"}:
            copy(source, OUTPUT / source.relative_to(ROOT / "site"))
    for directory in ("contracts", "examples"):
        for source in sorted((ROOT / directory).glob("*")):
            if source.is_file() and source.suffix in {".json", ".ts"}:
                copy(source, OUTPUT / "references" / source.relative_to(ROOT))
    for name in ("LICENSE", "NOTICE", "module.json", "pyproject.toml", "README.md", "README.pypi.md", "CHANGELOG.md", "requirements-docs.txt"):
        source = ROOT / name
        if source.is_file():
            copy(source, OUTPUT / "references" / name)

    for source in sorted((ROOT / "docs").rglob("*.json")):
        copy(source, OUTPUT / source.relative_to(ROOT))

    sources = sorted((ROOT / "docs").rglob("*.md"))
    for source in sources:
        mapping[source.resolve()] = OUTPUT / source.relative_to(ROOT).with_suffix(".html")
    template = (ROOT / "site/docs-template.html").read_text()
    for key in ("TITLE", "CONTENT", "TOC", "ROOT"):
        if "{{" + key + "}}" not in template:
            raise ValueError(f"Missing template placeholder: {key}")
    parser = MarkdownIt("commonmark", {"html": False}).enable("table")
    for source in sources:
        page = mapping[source.resolve()]
        tokens = parser.parse(source.read_text())
        title = source.stem
        toc = []
        ids = set()
        for index, token in enumerate(tokens):
            if token.type != "heading_open":
                continue
            label = tokens[index + 1].content
            slug = re.sub(r"[^\w\s-]", "", label.lower()).strip().replace(" ", "-") or "section"
            base, counter = slug, 0
            while slug in ids:
                counter += 1
                slug = f"{base}-{counter}"
            ids.add(slug)
            token.attrSet("id", slug)
            if token.tag == "h1":
                title = label
            if token.tag in {"h2", "h3"}:
                toc.append(f'<li><a href="#{html.escape(slug)}">{html.escape(label)}</a></li>')
        for token in walk(tokens):
            for attr in ("href", "src"):
                value = token.attrGet(attr)
                if not value:
                    continue
                url = urlsplit(value)
                if url.scheme or url.netloc or not url.path:
                    continue
                target = (source.parent / unquote(url.path)).resolve()
                if target not in mapping:
                    raise ValueError(f"Unpublished link in {source.relative_to(ROOT)}: {value}")
                token.attrSet(attr, urlunsplit(("", "", relative(mapping[target], page), url.query, url.fragment)))
        content = parser.renderer.render(tokens, parser.options, {})
        values = {"TITLE": html.escape(title), "CONTENT": content, "TOC": "<ul>" + "".join(toc) + "</ul>", "ROOT": relative(OUTPUT, page) + "/"}
        rendered = re.sub(r"\{\{(TITLE|CONTENT|TOC|ROOT)\}\}", lambda match: values[match[1]], template)
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(rendered)
    print(f"Built {len(sources)} documentation pages into _site/")


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()
        self.duplicates = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            if attrs["id"] in self.ids:
                self.duplicates.append(attrs["id"])
            self.ids.add(attrs["id"])
        for attr in ("href", "src"):
            if attrs.get(attr):
                self.links.append(attrs[attr])


def check() -> None:
    pages = {}
    failures = []
    for path in sorted(OUTPUT.rglob("*.html")):
        reader = References()
        reader.feed(path.read_text())
        pages[path] = reader
        if reader.duplicates:
            failures.append(f"{path.relative_to(OUTPUT)}: duplicate IDs {reader.duplicates}")
    for path, reader in pages.items():
        for value in reader.links:
            url = urlsplit(value)
            if url.scheme or url.netloc:
                continue
            if url.path.startswith("/"):
                failures.append(f"{path.relative_to(OUTPUT)}: nonportable absolute path {value}")
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            if target.is_dir():
                target /= "index.html"
            if not target.is_relative_to(OUTPUT) or not target.is_file():
                failures.append(f"{path.relative_to(OUTPUT)}: missing local target {value}")
            elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                failures.append(f"{path.relative_to(OUTPUT)}: missing anchor {value}")
    for path in OUTPUT.rglob("*.css"):
        for value in re.findall(r"url\(['\"]?([^)'\"]+)", path.read_text()):
            if not urlsplit(value).scheme and not (path.parent / value).is_file():
                failures.append(f"{path.relative_to(OUTPUT)}: missing CSS asset {value}")
    if failures:
        raise ValueError("\n".join(failures))
    print(f"Checked {len(pages)} HTML pages: local links, anchors, assets, duplicate IDs, repository-subpath paths")


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--check", action="store_true", help="Validate generated pages and local references")
    args = cli.parse_args()
    try:
        build()
        if args.check:
            check()
    except (OSError, ValueError) as error:
        cli.exit(1, f"Site build failed: {error}\n")
