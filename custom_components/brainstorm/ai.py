"""Use of an AI task entity for Brainstorm Hub texts."""
from __future__ import annotations

import asyncio
import logging

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)

AI_TIMEOUT_SECONDS = 20


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
