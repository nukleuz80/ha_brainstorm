"""Tests for the wiki pages in wiki/, which a workflow publishes to GitHub."""

from __future__ import annotations

from pathlib import Path
import re

import pytest

WIKI = Path(__file__).parent.parent / "wiki"
SPECIAL = {"Home", "_Sidebar", "_Footer"}
LINK = re.compile(r"\[(?:[^\]\[]|\[[^\]]*\])*\]\(([^)\s]+)\)")


def _pages() -> dict[str, str]:
    return {path.stem: path.read_text("utf-8") for path in WIKI.glob("*.md")}


def _slug(heading: str) -> str:
    """Return the anchor GitHub gives a heading."""
    text = re.sub(r"[^\w\- ️]", "", heading.strip().lower())
    return text.replace(" ", "-")


def _anchors(text: str) -> set[str]:
    anchors: set[str] = set()
    seen: dict[str, int] = {}
    in_code = False
    for line in text.splitlines():
        if line.startswith("```"):
            in_code = not in_code
        match = re.match(r"^#{1,6} (.*)$", line)
        if match and not in_code:
            slug = _slug(match.group(1))
            count = seen.get(slug, 0)
            seen[slug] = count + 1
            anchors.add(slug if count == 0 else f"{slug}-{count}")
    return anchors


def _content_pages() -> list[str]:
    return sorted(set(_pages()) - SPECIAL)


def test_every_page_is_reachable() -> None:
    """Home and the sidebar list each page, and both languages have 14."""
    pages = _pages()
    content = _content_pages()
    assert len(content) == 28
    for name in content:
        assert f"]({name})" in pages["Home"], name
        assert f"]({name})" in pages["_Sidebar"], name


@pytest.mark.parametrize("name", _content_pages())
def test_page_links_its_other_language(name: str) -> None:
    """The first line of a page links Home and its twin, which links back."""
    pages = _pages()
    first = pages[name].splitlines()[0]
    assert "](Home)" in first
    twin = re.findall(r"\]\(([^)#]+)\)", first)[-1]
    assert twin in pages and twin != name
    assert f"]({name})" in pages[twin].splitlines()[0]


@pytest.mark.parametrize("name", sorted(_pages()))
def test_links_lead_somewhere(name: str) -> None:
    """Wiki links name a page and heading that exist, files are absolute."""
    pages = _pages()
    for url in LINK.findall(pages[name]):
        if re.match(r"^(https?:|mailto:)", url):
            continue
        page, _, anchor = url.partition("#")
        page = page or name
        assert page in pages, (name, url)
        if anchor:
            assert anchor in _anchors(pages[page]), (name, url)
