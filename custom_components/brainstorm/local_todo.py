"""Find and create lists of the Local To-do integration for linked categories.

The lists are linked through the normal to-do sync (todo_sync.py); this
module only finds them and creates a new one for a category.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.util import slugify

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

LOCAL_TODO_DOMAIN = "local_todo"
# What the config flow of Local To-do asks for and stores
LIST_NAME = "todo_list_name"
STORAGE_KEY = "storage_key"
# Choices on the settings page besides a category
CHOICE_NONE = "__none__"
CHOICE_NEW = "__new__"
ENTITY_WAIT = 5.0
ENTITY_POLL = 0.25


@dataclass(frozen=True)
class LocalList:
    """One list of Local To-do."""

    entity_id: str
    name: str


def local_lists(hass: HomeAssistant) -> list[LocalList]:
    """Return the lists of Local To-do, sorted by name."""
    lists: list[LocalList] = []
    for entry in er.async_get(hass).entities.values():
        if entry.platform != LOCAL_TODO_DOMAIN or entry.domain != "todo":
            continue
        if entry.disabled_by is not None:
            continue
        state = hass.states.get(entry.entity_id)
        name = (
            state.name
            if state is not None
            else entry.name or entry.original_name or entry.entity_id
        )
        lists.append(LocalList(entry.entity_id, " ".join(str(name).split())))
    return sorted(lists, key=lambda item: item.name.casefold())


def local_entities(hass: HomeAssistant) -> set[str]:
    """Return the entity ids of all lists of Local To-do."""
    return {item.entity_id for item in local_lists(hass)}


def _entity_of_entry(hass: HomeAssistant, entry_id: str) -> str | None:
    for entity in er.async_entries_for_config_entry(er.async_get(hass), entry_id):
        if entity.domain == "todo":
            return entity.entity_id
    return None


async def async_create_list(hass: HomeAssistant, name: str) -> str:
    """Create a list of Local To-do and return its entity id.

    A list of the same name that exists already is used instead.
    """
    clean = " ".join(name.split())
    key = slugify(clean)
    entry_id: str | None = None
    for entry in hass.config_entries.async_entries(LOCAL_TODO_DOMAIN):
        if entry.data.get(STORAGE_KEY) == key:
            entry_id = entry.entry_id
    if entry_id is None:
        result: dict[str, Any] = await hass.config_entries.flow.async_init(
            LOCAL_TODO_DOMAIN, context={"source": SOURCE_USER}, data={LIST_NAME: clean}
        )
        if result.get("type") is not FlowResultType.CREATE_ENTRY:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="local_todo_failed",
                translation_placeholders={"name": clean},
            )
        entry_id = result["result"].entry_id
        _LOGGER.info("Created the Local To-do list %s", clean)
    # The entity comes once the new entry is set up
    waited = 0.0
    entity_id = _entity_of_entry(hass, entry_id)
    while entity_id is None and waited < ENTITY_WAIT:
        await asyncio.sleep(ENTITY_POLL)
        waited += ENTITY_POLL
        entity_id = _entity_of_entry(hass, entry_id)
    if entity_id is None:
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="local_todo_failed",
            translation_placeholders={"name": clean},
        )
    return entity_id
