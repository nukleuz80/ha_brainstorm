"""Todo platform for Brainstorm Hub."""
from __future__ import annotations

from datetime import datetime, time
import logging

from homeassistant.components.todo import (
    TodoItem,
    TodoItemStatus,
    TodoListEntity,
    TodoListEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_DEVICE,
    ATTR_DUE,
    ATTR_ID,
    ATTR_PRIORITY,
    ATTR_SOURCE,
    ATTR_STATUS,
    ATTR_TEXT,
    DOMAIN,
)
from .store import BrainstormStore

PARALLEL_UPDATES = 0

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Brainstorm todo platform from a config entry."""
    store: BrainstormStore = (
        entry.runtime_data
        if hasattr(entry, "runtime_data") and entry.runtime_data is not None
        else hass.data[DOMAIN][entry.entry_id]
    )

    existing_categories: set[str] = set()

    @callback
    def _remove_stale_entities() -> None:
        """Remove todo list entities of categories that no longer exist."""
        registry = er.async_get(hass)
        valid_ids = {_todo_unique_id(entry.entry_id, c) for c in store.categories}
        for reg_entry in er.async_entries_for_config_entry(registry, entry.entry_id):
            if reg_entry.domain == "todo" and reg_entry.unique_id not in valid_ids:
                registry.async_remove(reg_entry.entity_id)

    @callback
    def _sync_entities() -> None:
        """Add and remove todo list entities when categories changed."""
        current = set(store.categories)
        new_entities = [
            BrainstormTodoList(store, cat, entry.entry_id)
            for cat in store.categories
            if cat not in existing_categories
        ]
        removed = existing_categories - current
        existing_categories.clear()
        existing_categories.update(current)
        if new_entities:
            async_add_entities(new_entities)
        if removed:
            _remove_stale_entities()

    # Initial registration, also cleans up entities left over from older versions
    _remove_stale_entities()
    _sync_entities()
    # Register listener to catch dynamically added categories
    entry.async_on_unload(store.register_listener(_sync_entities))


def _todo_unique_id(entry_id: str, category: str) -> str:
    """Return the unique ID of a category's todo list."""
    safe_cat = category.lower().replace(" ", "_").replace("&", "und")
    return f"{entry_id}_todo_{safe_cat}"


DUE_DATE_TIME = time(9, 0)


def _due_from_item(item: TodoItem) -> datetime | None:
    """Return when a to-do item is due, a plain date meaning 09:00."""
    if isinstance(item.due, datetime):
        return dt_util.as_local(item.due)
    if item.due is not None:
        return datetime.combine(item.due, DUE_DATE_TIME, dt_util.DEFAULT_TIME_ZONE)
    return None


class BrainstormTodoList(TodoListEntity):
    """A To-do list representing a Brainstorm category."""

    _attr_has_entity_name = True
    _attr_supported_features = (
        TodoListEntityFeature.CREATE_TODO_ITEM
        | TodoListEntityFeature.UPDATE_TODO_ITEM
        | TodoListEntityFeature.DELETE_TODO_ITEM
        | TodoListEntityFeature.SET_DUE_DATETIME_ON_ITEM
        | TodoListEntityFeature.SET_DUE_DATE_ON_ITEM
    )

    def __init__(self, store: BrainstormStore, category: str, entry_id: str) -> None:
        """Initialize the todo list."""
        self._store = store
        self._category = category
        self._attr_unique_id = _todo_unique_id(entry_id, category)
        self._attr_name = f"Brainstorm: {category}"
        self._attr_icon = "mdi:lightbulb-outline"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="Brainstorm Hub",
            manufacturer="nukleuz80",
            model="Brainstorm Hub",
            sw_version=store.integration_version,
        )

    async def async_added_to_hass(self) -> None:
        """Register listener when added to hass."""
        await super().async_added_to_hass()
        self.async_on_remove(self._store.register_listener(self.async_write_ha_state))

    @property
    def todo_items(self) -> list[TodoItem] | None:
        """Return the items on this list."""
        items = self._store.get_ideas_by_category(self._category, status=None)
        todo_items = []
        for item in items:
            if item.get(ATTR_STATUS) == "archived":
                continue
            is_done = item.get(ATTR_STATUS) == "completed"
            status = TodoItemStatus.COMPLETED if is_done else TodoItemStatus.NEEDS_ACTION
            src = item.get(ATTR_SOURCE)
            dev = item.get(ATTR_DEVICE)
            prio = item.get(ATTR_PRIORITY, "medium")

            parts = []
            if prio == "urgent":
                parts.append("Priorität: 🔥 Dringend")
            elif prio == "high":
                parts.append("Priorität: 🔴 Hoch")
            elif prio == "low":
                parts.append("Priorität: 🟢 Niedrig")

            if dev and src:
                parts.append(f"Quelle: {src} ({dev})")
            elif dev:
                parts.append(f"Gerät: {dev}")
            elif src:
                parts.append(f"Quelle: {src}")

            desc = " • ".join(parts) if parts else None

            todo_items.append(
                TodoItem(
                    uid=item[ATTR_ID],
                    summary=item.get(ATTR_TEXT, ""),
                    status=status,
                    description=desc,
                    due=dt_util.parse_datetime(item[ATTR_DUE]) if item.get(ATTR_DUE) else None,
                )
            )
        return todo_items

    async def async_create_todo_item(self, item: TodoItem) -> None:
        """Create a new idea item in this category."""
        await self._store.async_add_idea(
            text=item.summary,
            category=self._category,
            source="todo_list",
            context=self._context,
            due=_due_from_item(item),
        )

    async def async_update_todo_item(self, item: TodoItem) -> None:
        """Update an idea item."""
        new_status = (
            "completed"
            if item.status == TodoItemStatus.COMPLETED
            else "active"
        )
        await self._store.async_update_idea(
            idea_id=item.uid,
            text=item.summary,
            category=self._category,
            status=new_status,
            context=self._context,
            due=_due_from_item(item),
            update_due=True,
        )

    async def async_delete_todo_items(self, uids: list[str]) -> None:
        """Delete idea items."""
        for uid in uids:
            await self._store.async_delete_idea(uid, context=self._context)

