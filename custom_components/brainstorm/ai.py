"""Use of an AI task entity for Brainstorm Hub texts."""
from __future__ import annotations

import asyncio
import logging
import re
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .outline import parse_markdown

_LOGGER = logging.getLogger(__name__)

AI_TIMEOUT_SECONDS = 20
# Pause before asking a refusing provider once more
AI_RETRY_DELAY_SECONDS = 2
# How many subtasks a suggestion may hold, and how long each may be
MAX_SUBTASK_SUGGESTIONS = 8
MAX_SUBTASK_LENGTH = 200

_LIST_MARK = re.compile(r"^\s*(?:[-*•–—]+|\d+\s*[.):]|\[[ xX]?\])\s*")


class AIUnavailableError(HomeAssistantError):
    """The AI did not answer, for example because its provider is overloaded."""

    def __init__(self, reason: str, *, timed_out: bool = False) -> None:
        """Remember whether the AI only took too long."""
        super().__init__(reason)
        self.timed_out = timed_out


async def async_request_text(
    hass: HomeAssistant, entity: str, instructions: str
) -> str | None:
    """Let an AI task entity write a text, None when the answer is empty.

    Raises AIUnavailableError when the AI gave no answer at all.
    """
    try:
        async with asyncio.timeout(AI_TIMEOUT_SECONDS):
            result = await hass.services.async_call(
                "ai_task",
                "generate_data",
                {
                    "task_name": "Brainstorm",
                    "instructions": instructions,
                    "entity_id": entity,
                },
                blocking=True,
                return_response=True,
            )
    except TimeoutError as err:
        _LOGGER.warning("No text from %s within %s s", entity, AI_TIMEOUT_SECONDS)
        raise AIUnavailableError("timeout", timed_out=True) from err
    except (HomeAssistantError, ValueError) as err:
        _LOGGER.warning("Could not get a text from %s: %s", entity, err)
        raise AIUnavailableError(str(err)) from err
    text = (result or {}).get("data")
    return text.strip() if isinstance(text, str) and text.strip() else None


async def async_generate_text(
    hass: HomeAssistant, entity: str, instructions: str
) -> str | None:
    """Let an AI task entity write a text, returning None on any problem."""
    try:
        return await async_request_text(hass, entity, instructions)
    except AIUnavailableError:
        return None


async def async_request_text_with_retry(
    hass: HomeAssistant, entity: str, instructions: str
) -> str | None:
    """Ask once more after a short pause when the provider refused the first time.

    A timeout is not repeated, as the person would wait twice as long.
    """
    try:
        return await async_request_text(hass, entity, instructions)
    except AIUnavailableError as err:
        if err.timed_out:
            raise
    await asyncio.sleep(AI_RETRY_DELAY_SECONDS)
    return await async_request_text(hass, entity, instructions)


def parse_subtask_suggestions(text: str | None, known: list[str]) -> list[str]:
    """Turn the AI's answer into clean subtasks, one per line, without repeats."""
    if not text:
        return []
    seen = {item.strip().casefold() for item in known if item}
    suggestions: list[str] = []
    for line in text.splitlines():
        item = _LIST_MARK.sub("", line).strip().strip("*_\"'„“”` ").strip()
        # A heading such as "Unteraufgaben:" is no task
        if not item or item.endswith(":"):
            continue
        item = item[:MAX_SUBTASK_LENGTH].strip()
        key = item.casefold()
        if key in seen:
            continue
        seen.add(key)
        suggestions.append(item)
        if len(suggestions) >= MAX_SUBTASK_SUGGESTIONS:
            break
    return suggestions


# A mind map from a topic or a text: how much goes in and comes back
MAP_INPUT_MAX_LENGTH = 6000
MAP_MAX_NODES = 40
MAP_MAX_DEPTH = 3
_FENCE = re.compile(r"^\s*(```|~~~)")


def parse_map_outline(text: str | None) -> list[dict[str, Any]]:
    """Turn the AI's indented list into nodes with text and depth.

    Depth 0 is the title; deeper levels than MAP_MAX_DEPTH move up to it, and
    the depth never jumps by more than one from line to line.
    """
    if not text:
        return []
    lines = [line for line in text.splitlines() if not _FENCE.match(line)]
    nodes: list[dict[str, Any]] = []
    seen: set[tuple[int, str]] = set()
    previous = -1
    for node in parse_markdown("\n".join(lines)):
        item = node.text.strip().strip("*_\"'„“”` ").strip()
        if not item or (item.endswith(":") and not nodes):
            continue
        item = item[:MAX_SUBTASK_LENGTH].strip()
        depth = min(node.depth, MAP_MAX_DEPTH, previous + 1)
        key = (depth, item.casefold())
        if key in seen:
            continue
        seen.add(key)
        nodes.append({"text": item, "depth": depth})
        previous = depth
        if len(nodes) >= MAP_MAX_NODES:
            break
    return nodes


# How much of a branch or a list goes to the AI at most
MAX_BRANCH_LINES = 80
MAX_LOOSE_IDEAS = 30
MAX_PARENT_CANDIDATES = 80
_PAIR = re.compile(r"\bL\s*(\d+)\b\D*?\bK\s*(\d+)\b", re.IGNORECASE)


def clean_summary(text: str | None, limit: int) -> str | None:
    """Turn the AI's summary into plain text, without a heading or list marks."""
    if not text:
        return None
    lines = []
    for line in text.splitlines():
        line = _LIST_MARK.sub("", line).strip().strip("*_#` ").strip()
        if line and not (line.endswith(":") and len(line) < 40):
            lines.append(line)
    summary = " ".join(lines).strip()
    return summary[:limit].strip() or None


def parse_parent_suggestions(
    text: str | None, loose_count: int, candidate_count: int
) -> list[tuple[int, int]]:
    """Read lines such as 'L2 -> K5' as (loose index, candidate index), 0-based.

    Each loose idea gets at most one parent; unknown numbers are left out.
    """
    if not text:
        return []
    pairs: list[tuple[int, int]] = []
    seen: set[int] = set()
    for line in text.splitlines():
        match = _PAIR.search(line)
        if not match:
            continue
        loose, candidate = int(match.group(1)) - 1, int(match.group(2)) - 1
        if not (0 <= loose < loose_count and 0 <= candidate < candidate_count):
            continue
        if loose in seen:
            continue
        seen.add(loose)
        pairs.append((loose, candidate))
    return pairs
