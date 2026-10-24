"""Describe Brainstorm Hub logbook events."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.components.logbook import (
    LOGBOOK_ENTRY_ENTITY_ID,
    LOGBOOK_ENTRY_ICON,
    LOGBOOK_ENTRY_MESSAGE,
    LOGBOOK_ENTRY_NAME,
    LazyEventPartialState,
)
from homeassistant.core import Event, HomeAssistant, callback

from .const import (
    ATTR_CATEGORY,
    ATTR_DEVICE,
    ATTR_SOURCE,
    ATTR_TEXT,
    DOMAIN,
    EVENT_IDEA_ADDED,
    EVENT_IDEA_COMPLETED,
    EVENT_IDEA_DELETED,
    EVENT_IDEA_UPDATED,
)

OVERVIEW_ENTITY_ID = "sensor.brainstorm_ideen_ubersicht"


@callback
def async_describe_events(
    hass: HomeAssistant,
    async_describe_event: Callable[
        [str, str, Callable[[LazyEventPartialState | Event], dict[str, Any]]], None
    ],
) -> None:
    """Describe Brainstorm Hub logbook events."""

    @callback
    def async_describe_idea_added(event: LazyEventPartialState | Event) -> dict[str, Any]:
        """Describe brainstorm idea added event."""
        data = event.data or {}
        text = data.get(ATTR_TEXT, "Unbekannte Notiz")
        category = data.get(ATTR_CATEGORY, "Inbox")
        source = data.get(ATTR_SOURCE, "manual")
        device = data.get(ATTR_DEVICE)

        origin_info = f"({category}"
        if device:
            origin_info += f", via {device}"
        elif source and source != "manual":
            origin_info += f", via {source}"
        origin_info += ")"

        return {
            LOGBOOK_ENTRY_NAME: "Brainstorm Hub",
            LOGBOOK_ENTRY_MESSAGE: f"Idee erfasst: \"{text}\" {origin_info}",
            LOGBOOK_ENTRY_ENTITY_ID: OVERVIEW_ENTITY_ID,
            LOGBOOK_ENTRY_ICON: "mdi:lightbulb-on",
        }

    @callback
    def async_describe_idea_completed(event: LazyEventPartialState | Event) -> dict[str, Any]:
        """Describe brainstorm idea completed event."""
        data = event.data or {}
        text = data.get(ATTR_TEXT, "Unbekannte Notiz")
        category = data.get(ATTR_CATEGORY, "Inbox")

        return {
            LOGBOOK_ENTRY_NAME: "Brainstorm Hub",
            LOGBOOK_ENTRY_MESSAGE: f"Idee erledigt: \"{text}\" ({category})",
            LOGBOOK_ENTRY_ENTITY_ID: OVERVIEW_ENTITY_ID,
            LOGBOOK_ENTRY_ICON: "mdi:check-circle-outline",
        }

    @callback
    def async_describe_idea_updated(event: LazyEventPartialState | Event) -> dict[str, Any]:
        """Describe brainstorm idea updated event."""
        data = event.data or {}
        text = data.get(ATTR_TEXT, "Unbekannte Notiz")
        category = data.get(ATTR_CATEGORY, "Inbox")

        return {
            LOGBOOK_ENTRY_NAME: "Brainstorm Hub",
            LOGBOOK_ENTRY_MESSAGE: f"Idee geändert: \"{text}\" ({category})",
            LOGBOOK_ENTRY_ENTITY_ID: OVERVIEW_ENTITY_ID,
            LOGBOOK_ENTRY_ICON: "mdi:pencil",
        }

    @callback
    def async_describe_idea_deleted(event: LazyEventPartialState | Event) -> dict[str, Any]:
        """Describe brainstorm idea deleted event."""
        data = event.data or {}
        text = data.get(ATTR_TEXT, "Unbekannte Notiz")
        category = data.get(ATTR_CATEGORY, "Inbox")

        return {
            LOGBOOK_ENTRY_NAME: "Brainstorm Hub",
            LOGBOOK_ENTRY_MESSAGE: f"Idee gelöscht: \"{text}\" ({category})",
            LOGBOOK_ENTRY_ENTITY_ID: OVERVIEW_ENTITY_ID,
            LOGBOOK_ENTRY_ICON: "mdi:delete-outline",
        }

    async_describe_event(DOMAIN, EVENT_IDEA_ADDED, async_describe_idea_added)
    async_describe_event(DOMAIN, EVENT_IDEA_COMPLETED, async_describe_idea_completed)
    async_describe_event(DOMAIN, EVENT_IDEA_UPDATED, async_describe_idea_updated)
    async_describe_event(DOMAIN, EVENT_IDEA_DELETED, async_describe_idea_deleted)

