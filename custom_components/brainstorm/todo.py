"""Todo platform for Brainstorm Hub."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.todo import (
    TodoItem,
    TodoItemStatus,
    TodoListEntity,
    TodoListEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ATTR_CATEGORY,
    ATTR_DEVICE,
    ATTR_ID,
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
    def _sync_entities() -> None:
        """Add new todo list entities if new categories appeared."""
        new_entities = []
        for cat in store.categories:
            if cat not in existing_categories:
                existing_categories.add(cat)
                new_entities.append(BrainstormTodoList(store, cat, entry.entry_id))
        if new_entities:
            async_add_entities(new_entities)

    # Initial registration
    _sync_entities()
    # Register listener to catch dynamically added categories
    entry.async_on_unload(store.register_listener(_sync_entities))


class BrainstormTodoList(TodoListEntity):
    """A To-do list representing a Brainstorm category."""

    _attr_has_entity_name = True
    _attr_supported_features = (
        TodoListEntityFeature.CREATE_TODO_ITEM
        | TodoListEntityFeature.UPDATE_TODO_ITEM
        | TodoListEntityFeature.DELETE_TODO_ITEM
    )

    def __init__(self, store: BrainstormStore, category: str, entry_id: str) -> None:
        """Initialize the todo list."""
        self._store = store
        self._category = category
        safe_cat = category.lower().replace(" ", "_").replace("&", "und")
        self._attr_unique_id = f"{entry_id}_todo_{safe_cat}"
        self._attr_name = f"Brainstorm: {category}"
        self._attr_icon = "mdi:lightbulb-outline"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="Brainstorm Hub",
            manufacturer="nukleuz80",
            model="Brainstorm Hub",
            sw_version="1.4.20",
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
            is_done = item.get(ATTR_STATUS) == "completed"
            status = TodoItemStatus.COMPLETED if is_done else TodoItemStatus.NEEDS_ACTION
            src = item.get(ATTR_SOURCE)
            dev = item.get(ATTR_DEVICE)
            desc = None
            if dev and src:
                desc = f"Quelle: {src} ({dev})"
            elif dev:
                desc = f"Gerät: {dev}"
            elif src:
                desc = f"Quelle: {src}"

            todo_items.append(
                TodoItem(
                    uid=item[ATTR_ID],
                    summary=item.get(ATTR_TEXT, ""),
                    status=status,
                    description=desc,
                )
            )
        return todo_items

    async def async_create_todo_item(self, item: TodoItem) -> None:
        """Create a new idea item in this category."""
        await self._store.async_add_idea(
            text=item.summary,
            category=self._category,
            source="todo_list",
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
        )

    async def async_delete_todo_items(self, uids: list[str]) -> None:
        """Delete idea items."""
        for uid in uids:
            await self._store.async_delete_idea(uid)

