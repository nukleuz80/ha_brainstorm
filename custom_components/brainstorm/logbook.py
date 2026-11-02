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
    ATTR_PRIORITY,
    ATTR_SOURCE,
    ATTR_TEXT,
    DOMAIN,
    EVENT_IDEA_ADDED,
    EVENT_IDEA_COMPLETED,
    EVENT_IDEA_DELETED,
    EVENT_IDEA_UPDATED,
    OVERVIEW_ENTITY_ID,
)
from .languages import get_pack
from .store import get_loaded_store


def _visible_text(hass: HomeAssistant, data: dict[str, Any]) -> str:
    """Return an idea's text for the logbook, which every user can read."""
    store = get_loaded_store(hass)
    pack = get_pack(hass.config.language)
    if store is not None and store.privacy_enabled:
        return pack.msg("log_private")
    return data.get(ATTR_TEXT, pack.msg("log_unknown"))


@callback
def async_describe_events(
    hass: HomeAssistant,
    async_describe_event: Callable[
        [str, str, Callable[[LazyEventPartialState | Event], dict[str, Any]]], None
    ],
) -> None:
    """Describe Brainstorm Hub logbook events."""
    pack = get_pack(hass.config.language)

    @callback
    def async_describe_idea_added(event: LazyEventPartialState | Event) -> dict[str, Any]:
        """Describe brainstorm idea added event."""
        data = event.data or {}
        text = _visible_text(hass, data)
        category = data.get(ATTR_CATEGORY, "Inbox")
        priority = data.get(ATTR_PRIORITY)
        source = data.get(ATTR_SOURCE, "manual")
        device = data.get(ATTR_DEVICE)

        prio_tag = ""
        if priority == "urgent":
            prio_tag = f" [{pack.msg('prio_urgent')}]"
        elif priority == "high":
            prio_tag = f" [{pack.msg('prio_high')}]"
        elif priority == "low":
            prio_tag = f" [{pack.msg('prio_low')}]"

        origin_info = f"({category}"
        if device:
            origin_info += f", via {device}"
        elif source and source != "manual":
            origin_info += f", via {source}"
        origin_info += ")"

        cat_prefix = f" ({category})" if category else ""
        display_text = text if len(text) <= 120 else f"{text[:117]}..."

        return {
            LOGBOOK_ENTRY_NAME: f"Brainstorm{cat_prefix}: {display_text}",
            LOGBOOK_ENTRY_MESSAGE: f"{pack.msg('log_added')}{prio_tag} {origin_info}".strip(),
            LOGBOOK_ENTRY_ENTITY_ID: OVERVIEW_ENTITY_ID,
            LOGBOOK_ENTRY_ICON: "mdi:lightbulb-on" if priority != "urgent" else "mdi:alert-circle",
        }

    @callback
    def async_describe_idea_completed(event: LazyEventPartialState | Event) -> dict[str, Any]:
        """Describe brainstorm idea completed event."""
        data = event.data or {}
        text = _visible_text(hass, data)
        category = data.get(ATTR_CATEGORY, "Inbox")
        cat_prefix = f" ({category})" if category else ""
        display_text = text if len(text) <= 120 else f"{text[:117]}..."

        return {
            LOGBOOK_ENTRY_NAME: f"Brainstorm{cat_prefix}: {display_text}",
            LOGBOOK_ENTRY_MESSAGE: pack.msg("log_completed"),
            LOGBOOK_ENTRY_ENTITY_ID: OVERVIEW_ENTITY_ID,
            LOGBOOK_ENTRY_ICON: "mdi:check-circle-outline",
        }

    @callback
    def async_describe_idea_updated(event: LazyEventPartialState | Event) -> dict[str, Any]:
        """Describe brainstorm idea updated event."""
        data = event.data or {}
        text = _visible_text(hass, data)
        category = data.get(ATTR_CATEGORY, "Inbox")
        cat_prefix = f" ({category})" if category else ""
        display_text = text if len(text) <= 120 else f"{text[:117]}..."

        return {
            LOGBOOK_ENTRY_NAME: f"Brainstorm{cat_prefix}: {display_text}",
            LOGBOOK_ENTRY_MESSAGE: pack.msg("log_updated"),
            LOGBOOK_ENTRY_ENTITY_ID: OVERVIEW_ENTITY_ID,
            LOGBOOK_ENTRY_ICON: "mdi:pencil",
        }

    @callback
    def async_describe_idea_deleted(event: LazyEventPartialState | Event) -> dict[str, Any]:
        """Describe brainstorm idea deleted event."""
        data = event.data or {}
        text = _visible_text(hass, data)
        category = data.get(ATTR_CATEGORY, "Inbox")
        cat_prefix = f" ({category})" if category else ""
        display_text = text if len(text) <= 120 else f"{text[:117]}..."

        return {
            LOGBOOK_ENTRY_NAME: f"Brainstorm{cat_prefix}: {display_text}",
            LOGBOOK_ENTRY_MESSAGE: pack.msg("log_deleted"),
            LOGBOOK_ENTRY_ENTITY_ID: OVERVIEW_ENTITY_ID,
            LOGBOOK_ENTRY_ICON: "mdi:delete-outline",
        }

    async_describe_event(DOMAIN, EVENT_IDEA_ADDED, async_describe_idea_added)
    async_describe_event(DOMAIN, EVENT_IDEA_COMPLETED, async_describe_idea_completed)
    async_describe_event(DOMAIN, EVENT_IDEA_UPDATED, async_describe_idea_updated)
    async_describe_event(DOMAIN, EVENT_IDEA_DELETED, async_describe_idea_deleted)

