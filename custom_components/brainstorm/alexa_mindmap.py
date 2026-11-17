"""The mind map of a category as a vector graphic for an Echo with a screen.

An Echo draws Alexa Vector Graphics (AVG) itself, so the map needs no picture
address the Echo would have to reach. The category sits in the middle, its
main tasks branch out to both sides and their subtasks further out. The Echo
scales the graphic to its screen.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any

from .const import ATTR_ID, ATTR_PARENT_ID, ATTR_PRIORITY, ATTR_TEXT

# Levels below the category, deeper subtasks are counted on a "+ n" node
MAX_DEPTH = 3
MAX_CHILDREN = 7
# Nodes of one map, so that the text stays readable once it is scaled down
MAX_NODES = 36
# Font size, padding and longest text per level, the category first
FONT_SIZES = (34, 24, 20, 17)
PADDING_X = (26, 18, 14, 12)
PADDING_Y = (16, 11, 9, 8)
MAX_LABELS = (24, 26, 24, 22)
STROKES = (5, 4, 3, 2)
# Width of an average letter compared to the font size
LETTER_WIDTH = 0.56
ROW_GAP = 14
COLUMN_GAP = 54
MARGIN = 24
# A small map is not blown up to fill the whole screen
MIN_WIDTH = 960
MIN_HEIGHT = 540

TEXT_COLOR = "#ffffff"
MUTED_COLOR = "#b8b5c9"
NODE_COLOR = "#ffffff14"


@dataclass
class _Node:
    """One box of the map."""

    label: str
    depth: int
    accent: str | None = None
    more: bool = False
    children: list[_Node] = field(default_factory=list)
    width: float = 0
    height: float = 0
    x: float = 0
    y: float = 0
    span: float = 0


def _plain(text: Any, limit: int) -> str:
    """Return a label the graphic shows as it is, shortened for the box.

    Strings in an APL document are evaluated, so "${" must not get through.
    """
    cleaned = " ".join(str(text or "").split())
    if len(cleaned) > limit:
        cleaned = f"{cleaned[: limit - 1].rstrip()}…"
    return cleaned.replace("${", "$ {").replace("#{", "# {")


def _measure(node: _Node) -> None:
    """Give a node the size of its text."""
    level = min(node.depth, len(FONT_SIZES) - 1)
    size = FONT_SIZES[level]
    node.width = len(node.label) * size * LETTER_WIDTH + 2 * PADDING_X[level]
    node.height = size + 2 * PADDING_Y[level]


def _build_tree(
    category: str, ideas: list[dict[str, Any]], priority_colors: dict[str, str]
) -> tuple[_Node, int]:
    """Return the category with its tasks, and how many tasks are not drawn.

    Nodes are taken level by level, so a long branch cannot crowd out the
    main tasks.
    """
    ids = {idea.get(ATTR_ID) for idea in ideas}
    children: dict[Any, list[dict[str, Any]]] = {}
    tops: list[dict[str, Any]] = []
    for idea in ideas:
        if idea.get(ATTR_PARENT_ID) in ids and idea.get(ATTR_PARENT_ID) != idea.get(
            ATTR_ID
        ):
            children.setdefault(idea.get(ATTR_PARENT_ID), []).append(idea)
        else:
            tops.append(idea)

    root = _Node(_plain(category, MAX_LABELS[0]), 0)
    budget = MAX_NODES
    drawn = 0
    seen: set[Any] = set()
    queue: deque[tuple[_Node, list[dict[str, Any]]]] = deque([(root, tops)])
    while queue:
        parent, members = queue.popleft()
        members = [idea for idea in members if idea.get(ATTR_ID) not in seen]
        depth = parent.depth + 1
        allowed = 0 if depth > MAX_DEPTH else min(len(members), MAX_CHILDREN, budget)
        if allowed < len(members) and allowed == budget and allowed:
            # Room for the "+ n" node
            allowed -= 1
        for idea in members[:allowed]:
            seen.add(idea.get(ATTR_ID))
            level = min(depth, len(MAX_LABELS) - 1)
            node = _Node(
                _plain(idea.get(ATTR_TEXT), MAX_LABELS[level]),
                depth,
                accent=priority_colors.get(str(idea.get(ATTR_PRIORITY))),
            )
            parent.children.append(node)
            queue.append((node, children.get(idea.get(ATTR_ID), [])))
        budget -= allowed
        drawn += allowed
        if hidden := len(members) - allowed:
            parent.children.append(_Node(f"+ {hidden}", depth, more=True))
            budget = max(0, budget - 1)
    return root, len(ideas) - drawn


def _span(node: _Node) -> float:
    """Return the height a node needs with everything below it."""
    _measure(node)
    below = sum(_span(child) for child in node.children)
    below += ROW_GAP * max(0, len(node.children) - 1)
    node.span = max(node.height, below)
    return node.span


def _place(node: _Node, edge: float, center: float, side: int) -> None:
    """Put a node next to its parent and its children next to it."""
    node.x = edge + side * node.width / 2
    node.y = center
    block = sum(child.span for child in node.children)
    block += ROW_GAP * max(0, len(node.children) - 1)
    top = center - block / 2
    outer = edge + side * (node.width + COLUMN_GAP)
    for child in node.children:
        _place(child, outer, top + child.span / 2, side)
        top += child.span + ROW_GAP


def _layout(root: _Node) -> list[tuple[_Node, int]]:
    """Place the map, main tasks shared between both sides."""
    _span(root)
    sides: dict[int, list[_Node]] = {1: [], -1: []}
    heights = {1: 0.0, -1: 0.0}
    # The largest branches first, each to the lower side, then in their order
    chosen: dict[int, int] = {}
    for index in sorted(
        range(len(root.children)), key=lambda i: -root.children[i].span
    ):
        side = 1 if heights[1] <= heights[-1] else -1
        chosen[index] = side
        heights[side] += root.children[index].span + ROW_GAP
    for index, child in enumerate(root.children):
        sides[chosen[index]].append(child)
    placed: list[tuple[_Node, int]] = []
    for side, members in sides.items():
        block = sum(child.span for child in members)
        block += ROW_GAP * max(0, len(members) - 1)
        top = -block / 2
        edge = side * (root.width / 2 + COLUMN_GAP)
        for child in members:
            _place(child, edge, top + child.span / 2, side)
            top += child.span + ROW_GAP
            placed.append((child, side))
    return placed


def _walk(node: _Node) -> list[_Node]:
    """Return a node and everything below it."""
    nodes = [node]
    for child in node.children:
        nodes.extend(_walk(child))
    return nodes


def _number(value: float) -> int:
    return round(value)


def _box(node: _Node, dx: float, dy: float) -> str:
    """Return the path of a rounded box."""
    left = _number(node.x - node.width / 2 + dx)
    top = _number(node.y - node.height / 2 + dy)
    width = _number(node.width)
    height = _number(node.height)
    radius = min(height // 2, 18)
    inner_w = width - 2 * radius
    inner_h = height - 2 * radius
    return (
        f"M{left + radius},{top}h{inner_w}"
        f"a{radius},{radius} 0 0 1 {radius},{radius}v{inner_h}"
        f"a{radius},{radius} 0 0 1 -{radius},{radius}h-{inner_w}"
        f"a{radius},{radius} 0 0 1 -{radius},-{radius}v-{inner_h}"
        f"a{radius},{radius} 0 0 1 {radius},-{radius}z"
    )


def build_graphic(
    category: str,
    ideas: list[dict[str, Any]],
    color: str,
    priority_colors: dict[str, str],
) -> dict[str, Any]:
    """Return the mind map of one category as an AVG graphic."""
    root, _ = _build_tree(category, ideas, priority_colors)
    placed = _layout(root)
    nodes = _walk(root)
    left = min(node.x - node.width / 2 for node in nodes) - MARGIN
    right = max(node.x + node.width / 2 for node in nodes) + MARGIN
    top = min(node.y - node.height / 2 for node in nodes) - MARGIN
    bottom = max(node.y + node.height / 2 for node in nodes) + MARGIN
    width = max(right - left, MIN_WIDTH)
    height = max(bottom - top, MIN_HEIGHT)
    # Centered, also when the minimum size made the graphic larger
    dx = width / 2 - (left + right) / 2
    dy = height / 2 - (top + bottom) / 2

    lines: list[dict[str, Any]] = []
    boxes: list[dict[str, Any]] = []

    def connect(parent: _Node, child: _Node, side: int) -> None:
        start_x = parent.x + side * parent.width / 2 + dx
        end_x = child.x - side * child.width / 2 + dx
        middle = (start_x + end_x) / 2
        start_y, end_y = parent.y + dy, child.y + dy
        level = min(child.depth, len(STROKES) - 1)
        lines.append(
            {
                "type": "path",
                "pathData": (
                    f"M{_number(start_x)},{_number(start_y)}"
                    f"C{_number(middle)},{_number(start_y)} "
                    f"{_number(middle)},{_number(end_y)} "
                    f"{_number(end_x)},{_number(end_y)}"
                ),
                "stroke": MUTED_COLOR if child.more else color,
                "strokeWidth": STROKES[level],
                "strokeOpacity": 0.5 if child.more else 0.85,
            }
        )

    def draw(node: _Node) -> None:
        level = min(node.depth, len(FONT_SIZES) - 1)
        if node.depth == 0:
            fill, stroke = color, None
        elif node.more:
            fill, stroke = "#00000000", None
        elif node.depth == 1:
            fill, stroke = f"{color}40", node.accent or color
        else:
            fill, stroke = NODE_COLOR, node.accent
        box: dict[str, Any] = {
            "type": "path",
            "pathData": _box(node, dx, dy),
            "fill": fill,
        }
        if stroke:
            box.update(stroke=stroke, strokeWidth=3 if node.accent else 2)
        boxes.append(box)
        boxes.append(
            {
                "type": "text",
                "text": node.label,
                "x": _number(node.x + dx),
                "y": _number(node.y + dy + FONT_SIZES[level] * 0.35),
                "fontSize": FONT_SIZES[level],
                "fontWeight": "bold" if node.depth <= 1 else "normal",
                "fill": MUTED_COLOR if node.more else TEXT_COLOR,
                "textAnchor": "middle",
            }
        )

    def branch(parent: _Node, child: _Node, side: int) -> None:
        connect(parent, child, side)
        draw(child)
        for grandchild in child.children:
            branch(child, grandchild, side)

    draw(root)
    for child, side in placed:
        branch(root, child, side)
    # The lines go under the boxes
    return {
        "type": "AVG",
        "version": "1.2",
        "width": _number(width),
        "height": _number(height),
        "items": lines + boxes,
    }
