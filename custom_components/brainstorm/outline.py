"""Read an outline from Markdown, indented text, OPML, FreeMind, Trello or CSV.

The result is a flat list of nodes in document order, each with its depth,
so the store can build the tree of notes from it.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
import io
import json
import re
from typing import Any
from xml.etree import ElementTree as ET

from .const import DESCRIPTION_MAX_LENGTH

OUTLINE_FORMATS = ("auto", "markdown", "opml", "freemind", "trello", "csv")
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
    due: str | None = None
    priority: str | None = None


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


def _desc(text: Any) -> str | None:
    return str(text or "").strip()[:DESCRIPTION_MAX_LENGTH] or None


def _pos(item: dict[str, Any]) -> float:
    try:
        return float(item.get("pos") or 0)
    except (TypeError, ValueError):
        return 0.0


def parse_trello(text: str) -> list[OutlineNode]:
    """Read the lists, cards and checklists of a Trello board export.

    Lists become main notes, their cards notes below them and checklist items
    subtasks of the cards. Archived lists and cards stay out.
    """
    try:
        board = json.loads(text)
    except ValueError as err:
        raise OutlineError(str(err)) from err
    if not isinstance(board, dict) or not isinstance(board.get("cards"), list):
        raise OutlineError("no trello board")
    lists = [
        item
        for item in board.get("lists") or []
        if isinstance(item, dict) and not item.get("closed")
    ]
    cards = [
        card
        for card in board["cards"]
        if isinstance(card, dict) and not card.get("closed")
    ]
    checklists: dict[str, list[dict[str, Any]]] = {}
    for checklist in board.get("checklists") or []:
        if isinstance(checklist, dict) and checklist.get("idCard"):
            checklists.setdefault(str(checklist["idCard"]), []).append(checklist)
    nodes: list[OutlineNode] = []

    def add_card(card: dict[str, Any], depth: int) -> None:
        label = _clean(card.get("name"))
        if not label:
            return
        due = card.get("due")
        nodes.append(
            OutlineNode(
                label,
                depth,
                _desc(card.get("desc")),
                bool(card.get("dueComplete")),
                due=str(due) if isinstance(due, str) and due else None,
            )
        )
        for checklist in sorted(checklists.get(str(card.get("id")), []), key=_pos):
            items = [
                i for i in checklist.get("checkItems") or [] if isinstance(i, dict)
            ]
            for item in sorted(items, key=_pos):
                if name := _clean(item.get("name")):
                    done = item.get("state") == "complete"
                    nodes.append(OutlineNode(name, depth + 1, done=done))

    known = {str(item.get("id")) for item in lists}
    for item in sorted(lists, key=_pos):
        label = _clean(item.get("name"))
        if not label:
            continue
        nodes.append(OutlineNode(label, 0))
        for card in sorted(
            (c for c in cards if str(c.get("idList")) == str(item.get("id"))), key=_pos
        ):
            add_card(card, 1)
    # Cards whose list is missing from a trimmed export still come in
    orphans = (c for c in cards if str(c.get("idList")) not in known)
    for card in sorted(orphans, key=_pos):
        add_card(card, 0)
    return nodes


# Todoist writes priority 1 for p1, the most urgent one, and 4 for none
_TODOIST_PRIORITY = {"1": "urgent", "2": "high", "3": "medium"}
_TRUE = {"x", "yes", "true", "1", "ja", "done", "completed", "complete", "erledigt"}
_COLUMNS = {
    "text": (
        "content", "text", "title", "name", "task", "card name", "card", "item",
        "aufgabe", "inhalt", "titel", "notiz", "idee", "sticky note",
    ),
    "description": ("description", "desc", "notes", "note", "beschreibung", "details"),
    "due": ("due", "due date", "date", "deadline", "fällig", "fälligkeit", "datum"),
    "priority": ("priority", "priorität"),
    "depth": ("indent", "level", "depth", "ebene"),
    "done": ("done", "completed", "complete", "status", "erledigt"),
    "group": (
        "list", "list name", "column", "group", "section", "liste", "spalte",
        "frame", "gruppe", "abschnitt",
    ),
}
_PRIORITY_WORDS = {
    "urgent": "urgent", "dringend": "urgent", "p1": "urgent", "highest": "urgent",
    "high": "high", "hoch": "high", "p2": "high",
    "medium": "medium", "mittel": "medium", "normal": "medium", "p3": "medium",
    "low": "low", "niedrig": "low", "lowest": "low", "p4": "low",
}


def _csv_rows(text: str) -> list[list[str]]:
    sample = text[:4000]
    try:
        dialect: Any = csv.Sniffer().sniff(sample, delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    try:
        rows = list(csv.reader(io.StringIO(text), dialect))
    except csv.Error as err:
        raise OutlineError(str(err)) from err
    return [
        [cell.strip() for cell in row] for row in rows if any(c.strip() for c in row)
    ]


def _date(value: str) -> str | None:
    """Keep a date only when it is one, Todoist also writes "every day"."""
    value = value.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}([ T]\d{2}:\d{2}(:\d{2})?.*)?", value):
        return value
    return None


def parse_todoist(rows: list[list[str]]) -> list[OutlineNode]:
    """Read a Todoist CSV export: sections, indented tasks and comments."""
    head = [cell.upper() for cell in rows[0]]
    col = {name: head.index(name) for name in head}

    def cell(row: list[str], name: str) -> str:
        index = col.get(name)
        return row[index] if index is not None and index < len(row) else ""

    nodes: list[OutlineNode] = []
    base = 0
    for row in rows[1:]:
        kind = cell(row, "TYPE").lower()
        content = _clean(cell(row, "CONTENT"))
        if kind == "section" and content:
            nodes.append(OutlineNode(content, 0))
            base = 1
        elif kind == "task" and content:
            try:
                indent = max(1, int(cell(row, "INDENT") or 1))
            except ValueError:
                indent = 1
            nodes.append(
                OutlineNode(
                    content,
                    base + indent - 1,
                    _desc(cell(row, "DESCRIPTION")),
                    due=_date(cell(row, "DATE")),
                    priority=_TODOIST_PRIORITY.get(cell(row, "PRIORITY")),
                )
            )
        elif kind == "note" and content and nodes:
            note = nodes[-1].description
            nodes[-1].description = _desc(f"{note}\n{content}" if note else content)
    return nodes


def parse_csv(text: str) -> list[OutlineNode]:
    """Read a table: Todoist, a list with known columns, or one group per column.

    With columns such as Title, Description and List (Trello, Miro, Excel)
    each row is a note, grouped below its list. Without them, as in a Miro
    board exported to CSV, each column is a main note with its cells below.
    """
    rows = _csv_rows(text)
    if not rows:
        return []
    head = [cell.lower().lstrip("\ufeff") for cell in rows[0]]
    if head[:2] == ["type", "content"]:
        return parse_todoist(rows)
    col: dict[str, int] = {}
    for key, names in _COLUMNS.items():
        for name in names:
            if name in head and head.index(name) not in col.values():
                col[key] = head.index(name)
                break
    if "text" not in col:
        if len(head) == 1:
            return [OutlineNode(t, 0) for row in rows if (t := _clean(row[0]))]
        nodes: list[OutlineNode] = []
        for index, title in enumerate(rows[0]):
            cells = [_clean(r[index]) for r in rows[1:] if index < len(r)]
            cells = [c for c in cells if c]
            if label := _clean(title):
                nodes.append(OutlineNode(label, 0))
                nodes.extend(OutlineNode(c, 1) for c in cells)
            else:
                nodes.extend(OutlineNode(c, 0) for c in cells)
        return nodes

    def cell(row: list[str], key: str) -> str:
        index = col.get(key)
        return row[index] if index is not None and index < len(row) else ""

    groups: dict[str, list[OutlineNode]] = {}
    for row in rows[1:]:
        label = _clean(cell(row, "text"))
        if not label:
            continue
        try:
            depth = max(0, int(cell(row, "depth") or 1) - 1)
        except ValueError:
            depth = 0
        node = OutlineNode(
            label,
            depth,
            _desc(cell(row, "description")),
            cell(row, "done").lower() in _TRUE,
            due=_date(cell(row, "due")),
            priority=_PRIORITY_WORDS.get(cell(row, "priority").lower()),
        )
        groups.setdefault(_clean(cell(row, "group")), []).append(node)
    nodes = []
    for group, members in groups.items():
        if group:
            nodes.append(OutlineNode(group, 0))
            for node in members:
                node.depth += 1
        nodes.extend(members)
    return nodes


def parse_outline(text: str, fmt: str = "auto") -> list[OutlineNode]:
    """Read an outline; auto tells the formats apart by how they start."""
    text = (text or "").lstrip("﻿")
    if len(text) > OUTLINE_MAX_LENGTH:
        raise OutlineError("too long")
    if fmt == "auto":
        head = text.lstrip()[:400].lower()
        if head.startswith("<"):
            fmt = "freemind" if "<map" in head else "opml"
        elif head.startswith("{"):
            fmt = "trello"
        elif re.match(r'"?type"?[,;\t]"?content"?', head):
            fmt = "csv"
        else:
            fmt = "markdown"
    if fmt == "opml":
        nodes = parse_opml(text)
    elif fmt == "freemind":
        nodes = parse_freemind(text)
    elif fmt == "trello":
        nodes = parse_trello(text)
    elif fmt == "csv":
        nodes = parse_csv(text)
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
