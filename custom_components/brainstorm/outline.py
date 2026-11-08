"""Read an outline from Markdown, indented text, OPML or FreeMind.

The result is a flat list of nodes in document order, each with its depth,
so the store can build the tree of notes from it.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any
from xml.etree import ElementTree as ET

from .const import DESCRIPTION_MAX_LENGTH

OUTLINE_FORMATS = ("auto", "markdown", "opml", "freemind")
OUTLINE_MAX_NODES = 300
OUTLINE_MAX_LENGTH = 200_000
NODE_TEXT_MAX_LENGTH = 500

_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_ITEM = re.compile(r"^([-*+]|\d{1,3}[.)])\s+(?:\[([ xX])\]\s+)?(.*)$")
_RULE = re.compile(r"^(?:[-*_]\s*){3,}$")


class OutlineError(ValueError):
    """The outline cannot be read."""


@dataclass
class OutlineNode:
    """One line of an outline."""

    text: str
    depth: int
    description: str | None = None
    done: bool = False


def _clean(text: Any, limit: int = NODE_TEXT_MAX_LENGTH) -> str:
    return " ".join(str(text or "").split())[:limit]


def _indent(line: str) -> int:
    width = 0
    for char in line:
        if char == " ":
            width += 1
        elif char == "\t":
            width += 4
        else:
            break
    return width


def parse_markdown(text: str) -> list[OutlineNode]:
    """Read headings, list items and indented lines as a tree."""
    lines = text.splitlines()
    levels = [len(m.group(1)) for line in lines if (m := _HEADING.match(line.strip()))]
    top = min(levels, default=1)
    nodes: list[OutlineNode] = []
    base = 0
    stack: list[tuple[int, int]] = []
    in_code = False
    for raw in lines:
        stripped = raw.strip()
        if stripped.startswith(("```", "~~~")):
            in_code = not in_code
            continue
        if in_code or not stripped or _RULE.match(stripped):
            continue
        # A quote below a note is its description, as the cards export it
        if stripped.startswith(">") and nodes:
            quote = stripped.lstrip("> ").strip()
            if quote:
                note = nodes[-1].description
                nodes[-1].description = f"{note} {quote}" if note else quote
                nodes[-1].description = nodes[-1].description[:DESCRIPTION_MAX_LENGTH]
            continue
        if heading := _HEADING.match(stripped):
            depth = len(heading.group(1)) - top
            if text_ := _clean(heading.group(2)):
                nodes.append(OutlineNode(text_, depth))
            base = depth + 1
            stack = []
            continue
        indent = _indent(raw)
        while stack and stack[-1][0] > indent:
            stack.pop()
        if stack and stack[-1][0] == indent:
            depth = stack.pop()[1]
        elif stack:
            depth = stack[-1][1] + 1
        else:
            depth = base
        stack.append((indent, depth))
        done = False
        content = stripped
        if item := _ITEM.match(stripped):
            done = (item.group(2) or "").lower() == "x"
            content = item.group(3)
        if text_ := _clean(content):
            nodes.append(OutlineNode(text_, depth, done=done))
    return nodes


def _xml_root(text: str) -> ET.Element:
    # Entities could blow up the parser or read files, an outline needs none
    lowered = text.lower()
    if "<!doctype" in lowered or "<!entity" in lowered:
        raise OutlineError("doctype")
    try:
        return ET.fromstring(text)
    except ET.ParseError as err:
        raise OutlineError(str(err)) from err


def parse_opml(text: str) -> list[OutlineNode]:
    """Read the outline elements of an OPML file."""
    root = _xml_root(text)
    body = root.find("body")
    if root.tag != "opml" or body is None:
        raise OutlineError("no opml")
    nodes: list[OutlineNode] = []

    def walk(element: ET.Element, depth: int) -> None:
        for child in element.findall("outline"):
            label = _clean(child.get("text") or child.get("title"))
            if label:
                note = (child.get("_note") or "").strip()[:DESCRIPTION_MAX_LENGTH]
                done = (child.get("_complete") or "").lower() == "true"
                nodes.append(OutlineNode(label, depth, note or None, done))
                walk(child, depth + 1)
            else:
                walk(child, depth)

    walk(body, 0)
    return nodes


def parse_freemind(text: str) -> list[OutlineNode]:
    """Read the nodes of a FreeMind or Freeplane map, the root node included."""
    root = _xml_root(text)
    if root.tag != "map":
        raise OutlineError("no freemind map")
    nodes: list[OutlineNode] = []

    def note_of(element: ET.Element) -> str | None:
        for rich in element.findall("richcontent"):
            if (rich.get("TYPE") or "").upper() in ("NOTE", "DETAILS"):
                content = " ".join("".join(rich.itertext()).split())
                return content[:DESCRIPTION_MAX_LENGTH] or None
        return None

    def label_of(element: ET.Element) -> str:
        if label := element.get("TEXT"):
            return _clean(label)
        for rich in element.findall("richcontent"):
            if (rich.get("TYPE") or "NODE").upper() == "NODE":
                return _clean("".join(rich.itertext()))
        return ""

    def walk(element: ET.Element, depth: int) -> None:
        for child in element.findall("node"):
            label = label_of(child)
            if label:
                nodes.append(OutlineNode(label, depth, note_of(child)))
                walk(child, depth + 1)
            else:
                walk(child, depth)

    walk(root, 0)
    return nodes


def parse_outline(text: str, fmt: str = "auto") -> list[OutlineNode]:
    """Read an outline; auto tells XML formats apart by their root element."""
    text = (text or "").lstrip("﻿")
    if len(text) > OUTLINE_MAX_LENGTH:
        raise OutlineError("too long")
    if fmt == "auto":
        head = text.lstrip()[:400].lower()
        if head.startswith("<"):
            fmt = "freemind" if "<map" in head else "opml"
        else:
            fmt = "markdown"
    if fmt == "opml":
        nodes = parse_opml(text)
    elif fmt == "freemind":
        nodes = parse_freemind(text)
    else:
        nodes = parse_markdown(text)
    if len(nodes) > OUTLINE_MAX_NODES:
        raise OutlineError("too many")
    # A jump of more than one level hangs below the last note before it
    depth = -1
    for node in nodes:
        node.depth = max(0, min(node.depth, depth + 1))
        depth = node.depth
    return nodes
