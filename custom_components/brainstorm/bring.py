"""Find the lists of the Bring! integration and keep one note per list.

With Bring switched on, every Bring list becomes a main note in one category,
and its items become subtasks of that note. The sync itself is done by the
to-do sync; this module only says which lists there are and which note
stands for each of them.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_BRING_LIST,
    ATTR_CATEGORY,
    ATTR_ID,
    ATTR_PARENT_ID,
    ATTR_STATUS,
    ATTR_TEXT,
    ATTR_TODO_LINK,
    ATTR_UPDATED_AT,
    CONF_BRING_CATEGORY,
    CONF_BRING_DEFAULT_LIST,
    CONF_BRING_DONE_DAYS,
    CONF_BRING_ENABLED,
    CONF_BRING_LISTS,
    DEFAULT_BRING_DONE_DAYS,
    SHARE_ALL,
    SHARE_EDIT,
    SOURCE_BRING,
)
from .store import BrainstormStore

_LOGGER = logging.getLogger(__name__)

BRING_DOMAIN = "bring"


@dataclass(frozen=True)
class BringList:
    """A list of the Bring! integration."""

    entity_id: str
    name: str
    device_id: str | None


@dataclass(frozen=True)
class BringSettings:
    """What the person chose for Bring! in the settings."""

    category: str
    lists: tuple[str, ...]
    default_list: str | None
    done_days: int = DEFAULT_BRING_DONE_DAYS


def bring_settings(options: dict[str, Any]) -> BringSettings | None:
    """Return the Bring! settings, or None while Bring! is switched off."""
    category = (options.get(CONF_BRING_CATEGORY) or "").strip()
    if not options.get(CONF_BRING_ENABLED) or not category:
        return None
    return BringSettings(
        category=category,
        lists=tuple(options.get(CONF_BRING_LISTS) or ()),
        default_list=options.get(CONF_BRING_DEFAULT_LIST) or None,
        done_days=max(0, int(options.get(CONF_BRING_DONE_DAYS, DEFAULT_BRING_DONE_DAYS))),
    )


def bring_lists(hass: HomeAssistant) -> list[BringList]:
    """Return the to-do lists of the Bring! integration, sorted by name."""
    entities = er.async_get(hass)
    devices = dr.async_get(hass)
    found: list[BringList] = []
    for entry in entities.entities.values():
        if (
            entry.platform != BRING_DOMAIN
            or entry.domain != "todo"
            or entry.disabled_by is not None
        ):
            continue
        device = devices.async_get(entry.device_id) if entry.device_id else None
        state = hass.states.get(entry.entity_id)
        name = (
            entry.name
            or (device and (device.name_by_user or device.name))
            or (state and state.name)
            or entry.original_name
            or entry.entity_id.split(".", 1)[1].replace("_", " ").title()
        )
        found.append(BringList(entry.entity_id, name, entry.device_id))
    return sorted(found, key=lambda bring: bring.name.casefold())


def bring_activity_entities(hass: HomeAssistant, lists: list[BringList]) -> list[str]:
    """Return the activity events of Bring!, which fire when others change a list."""
    devices = {bring.device_id for bring in lists if bring.device_id}
    return [
        entry.entity_id
        for entry in er.async_get(hass).entities.values()
        if entry.platform == BRING_DOMAIN
        and entry.domain == "event"
        and entry.device_id in devices
    ]


def chosen_lists(hass: HomeAssistant, settings: BringSettings) -> list[BringList]:
    """Return the lists to sync: the chosen ones, or all of them, new ones too."""
    lists = bring_lists(hass)
    if not settings.lists:
        return lists
    return [bring for bring in lists if bring.entity_id in settings.lists]


def default_list(lists: list[BringList], settings: BringSettings) -> BringList | None:
    """Return the list that gets notes without a list."""
    for bring in lists:
        if bring.entity_id == settings.default_list:
            return bring
    return lists[0] if lists else None


async def async_ensure_list_notes(
    store: BrainstormStore, settings: BringSettings, lists: list[BringList]
) -> dict[str, str]:
    """Keep one main note per Bring list and return their IDs by list.

    A note of a list that is no longer synced is archived. A list note that
    was deleted comes back, and the items it left behind hang on it again.
    """
    if settings.category not in store.categories:
        await store.async_add_category(settings.category)
    wanted = {bring.entity_id: bring for bring in lists}
    notes: dict[str, str] = {}
    for idea in list(store.ideas):
        entity_id = (idea.get(ATTR_BRING_LIST) or {}).get("entity")
        if not entity_id:
            continue
        bring = wanted.get(entity_id)
        if bring is None or entity_id in notes:
            if idea.get(ATTR_STATUS) != "archived":
                await store.async_update_idea(idea[ATTR_ID], status="archived")
            continue
        notes[entity_id] = idea[ATTR_ID]
        changes: dict[str, Any] = {}
        if idea.get(ATTR_TEXT) != bring.name:
            changes["text"] = bring.name
        if idea.get(ATTR_CATEGORY) != settings.category:
            changes["category"] = settings.category
        if idea.get(ATTR_STATUS) != "active":
            changes["status"] = "active"
        if idea.get(ATTR_PARENT_ID):
            changes["parent_id"] = None
            changes["update_parent"] = True
        if changes:
            await store.async_update_idea(idea[ATTR_ID], **changes)

    for entity_id, bring in wanted.items():
        if entity_id in notes:
            continue
        note = await store.async_add_idea(
            text=bring.name,
            category=settings.category,
            source=SOURCE_BRING,
            verbatim=True,
            shares={SHARE_ALL: SHARE_EDIT} if store.privacy_enabled else None,
        )
        await store.async_mark_fields(note[ATTR_ID], {ATTR_BRING_LIST: {"entity": entity_id}})
        notes[entity_id] = note[ATTR_ID]
        _LOGGER.debug("Bring list %s now has the note %s", entity_id, note[ATTR_ID])

    # Items of a deleted list note hang on its new note again
    for idea in list(store.ideas):
        link = idea.get(ATTR_TODO_LINK) or {}
        parent = notes.get(link.get("entity") or "")
        if (
            parent
            and idea.get(ATTR_CATEGORY) == settings.category
            and not idea.get(ATTR_PARENT_ID)
            and not idea.get(ATTR_BRING_LIST)
        ):
            await store.async_update_idea(
                idea[ATTR_ID], parent_id=parent, update_parent=True
            )
    return notes


def done_to_archive(
    store: BrainstormStore, settings: BringSettings, now: datetime
) -> list[str]:
    """Return the bought items that were ticked off long enough ago.

    They leave the completed view of Brainstorm and stay in Bring, where its
    recent list keeps them for buying again.
    """
    if settings.done_days <= 0:
        return []
    limit = now - timedelta(days=settings.done_days)
    found: list[str] = []
    for idea in store.ideas:
        if (
            idea.get(ATTR_STATUS) != "completed"
            or idea.get(ATTR_CATEGORY) != settings.category
            or idea.get(ATTR_BRING_LIST)
        ):
            continue
        done_at = dt_util.parse_datetime(idea.get(ATTR_UPDATED_AT) or "")
        if done_at is not None and done_at <= limit:
            found.append(idea[ATTR_ID])
    return found


BRING_MESSAGES = ("going_shopping", "changed_list", "shopping_done", "urgent_message")


def bring_message_target(
    hass: HomeAssistant, store: BrainstormStore, idea: dict[str, Any]
) -> tuple[str, str | None] | None:
    """Return the Bring list a note stands for or sits on, with its item.

    A list note gives its list; an item gives the list it is linked to, or
    the list of its parent note, together with its text for urgent messages.
    """
    if note := idea.get(ATTR_BRING_LIST):
        return note["entity"], None
    lists = {bring.entity_id for bring in bring_lists(hass)}
    linked = (idea.get(ATTR_TODO_LINK) or {}).get("entity")
    if linked in lists:
        return linked, idea[ATTR_TEXT]
    parent = store.get_idea(idea.get(ATTR_PARENT_ID) or "")
    if parent and (note := parent.get(ATTR_BRING_LIST)):
        return note["entity"], idea[ATTR_TEXT]
    return None
