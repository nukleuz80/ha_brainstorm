"""Use of an AI task entity for Brainstorm Hub texts."""
from __future__ import annotations

import asyncio
import logging
import re

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)

AI_TIMEOUT_SECONDS = 20
# How many subtasks a suggestion may hold, and how long each may be
MAX_SUBTASK_SUGGESTIONS = 8
MAX_SUBTASK_LENGTH = 200

_LIST_MARK = re.compile(r"^\s*(?:[-*•–—]+|\d+\s*[.):]|\[[ xX]?\])\s*")


async def async_generate_text(
    hass: HomeAssistant, entity: str, instructions: str
) -> str | None:
    """Let an AI task entity write a text, returning None on any problem."""
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
    except (HomeAssistantError, ValueError, TimeoutError) as err:
        _LOGGER.warning("Could not get a text from %s: %s", entity, err)
        return None
    text = (result or {}).get("data")
    return text.strip() if isinstance(text, str) and text.strip() else None


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
