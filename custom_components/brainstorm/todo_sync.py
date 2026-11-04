"""Keep categories in step with to-do lists of other integrations.

A category can be linked to one to-do entity, such as a Bring!, Google Tasks or
Alexa shopping list. Both sides are compared on every change and every few
minutes:

- Active ideas go to the list, and items added there come back as ideas.
- Renaming or ticking off an item on one side does the same on the other.
- Deleting an idea removes its item. An item removed from the list completes
  its idea, as shopping lists drop what was bought.

Each linked idea remembers what the list said at the last sync. That tells a
change on the list from a change in Brainstorm, so neither side has to report
where a change came from, and a sync that finds nothing new calls nothing.
"""
from __future__ import annotations

import asyncio
from collections.abc import Callable
from datetime import datetime, timedelta
import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.todo import TodoListEntityFeature
from homeassistant.const import ATTR_SUPPORTED_FEATURES
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.helpers.start import async_at_started
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_CATEGORY,
    ATTR_DUE,
    ATTR_ID,
    ATTR_STATUS,
    ATTR_TEXT,
    ATTR_TODO_LINK,
    CONF_TODO_SYNC,
    EVENT_IDEA_DELETED,
    SHARE_ALL,
    SHARE_EDIT,
    SOURCE_TODO_SYNC,
)
from .store import BrainstormStore

_LOGGER = logging.getLogger(__name__)

TODO_DOMAIN = "todo"
NEEDS_ACTION = "needs_action"
COMPLETED = "completed"
SYNC_INTERVAL = timedelta(minutes=5)
SYNC_COOLDOWN = 1.0

LINK_ENTITY = "entity"
LINK_UID = "uid"
LINK_SUMMARY = "summary"
LINK_STATUS = "status"
LINK_DUE = "due"


def sync_targets(options: dict[str, Any]) -> dict[str, str]:
    """Return the linked to-do entity of each category from the options."""
    targets = options.get(CONF_TODO_SYNC) or {}
    return {
        category: entity
        for category, entity in targets.items()
        if isinstance(entity, str) and entity.startswith(f"{TODO_DOMAIN}.")
    }


def _idea_status(idea: dict[str, Any]) -> str:
    """Return the to-do status that matches an idea."""
    return NEEDS_ACTION if idea.get(ATTR_STATUS) == "active" else COMPLETED


def _same_text(first: str | None, second: str | None) -> bool:
    """Compare two item texts the way a person would."""
    return (first or "").strip().casefold() == (second or "").strip().casefold()


class TodoSyncManager:
    """Keeps every linked category in step with its to-do entity."""

    def __init__(
        self, hass: HomeAssistant, store: BrainstormStore, options: dict[str, Any]
    ) -> None:
        """Initialize the manager."""
        self.hass = hass
        self.store = store
        self.targets = sync_targets(options)
        self._lock = asyncio.Lock()
        self._unsubs: list[Callable[[], None]] = []
        self._pending_removals: list[tuple[str, str]] = []
        self._started = False
        self._failed: set[str] = set()
        self._debouncer = Debouncer(
            hass,
            _LOGGER,
            cooldown=SYNC_COOLDOWN,
            immediate=False,
            function=self.async_sync,
        )

    async def async_start(self) -> None:
        """Forget links of lists no longer chosen and start watching both sides."""
        await self._async_drop_stale_links()
        if not self.targets:
            return
        self._unsubs.append(self.store.register_listener(self._schedule))
        self._unsubs.append(
            self.hass.bus.async_listen(EVENT_IDEA_DELETED, self._on_deleted)
        )
        self._unsubs.append(
            async_track_state_change_event(
                self.hass, list(set(self.targets.values())), self._on_list_changed
            )
        )
        self._unsubs.append(
            async_track_time_interval(self.hass, self._on_interval, SYNC_INTERVAL)
        )
        # The other integration may still be loading while Brainstorm starts
        self._unsubs.append(async_at_started(self.hass, self._on_started))

    @callback
    def async_stop(self) -> None:
        """Stop watching and drop a sync that was about to run."""
        for unsub in self._unsubs:
            unsub()
        self._unsubs.clear()
        self._debouncer.async_shutdown()

    async def _async_drop_stale_links(self) -> None:
        """Remove links to lists that are no longer linked to their category.

        Unlinking a list in the settings leaves its items alone.
        """
        stale = {
            idea[ATTR_ID]: None
            for idea in self.store.ideas
            if (link := idea.get(ATTR_TODO_LINK))
            and link.get(LINK_ENTITY) not in self.targets.values()
        }
        if stale:
            await self.store.async_set_links(stale)

    @callback
    def _on_started(self, _hass: HomeAssistant) -> None:
        """Run the first sync once Home Assistant has started."""
        self._started = True
        self._schedule()

    @callback
    def _schedule(self, *_args: Any) -> None:
        """Run a sync soon, several changes in a row giving one sync."""
        if self._started:
            self._debouncer.async_schedule_call()

    @callback
    def _on_list_changed(self, _event: Event) -> None:
        """React to a change of a linked list."""
        self._schedule()

    @callback
    def _on_interval(self, _now: datetime) -> None:
        """Catch renames, which do not change the state of a list."""
        self._schedule()

    @callback
    def _on_deleted(self, event: Event) -> None:
        """Remove the item of a deleted idea from its list."""
        link = event.data.get(ATTR_TODO_LINK)
        if not link or not link.get(LINK_UID):
            return
        self._pending_removals.append((link[LINK_ENTITY], link[LINK_UID]))
        # Brought back, the idea gets a new item instead of completing itself
        deleted = self.store.deleted_idea(event.data.get(ATTR_ID) or "")
        if deleted is not None:
            deleted.pop(ATTR_TODO_LINK, None)
        self._schedule()

    def _eligible(self, idea: dict[str, Any], category: str) -> bool:
        """Return whether an idea belongs on the list of its category."""
        if idea.get(ATTR_CATEGORY) != category or idea.get(ATTR_STATUS) == "archived":
            return False
        # Everyone who can open the other list sees it, like the to-do lists here
        return not self.store.privacy_enabled or self.store.is_shared_with_all(idea)

    async def async_sync(self) -> None:
        """Compare every linked category with its list once."""
        async with self._lock:
            removals, self._pending_removals = self._pending_removals, []
            for entity_id, uid in removals:
                await self._async_call(entity_id, "remove_item", {"item": [uid]})
            for category, entity_id in self.targets.items():
                if category not in self.store.categories:
                    continue
                try:
                    await self._async_sync_one(category, entity_id)
                except HomeAssistantError as err:
                    if entity_id not in self._failed:
                        _LOGGER.warning(
                            "Could not sync category %s with %s: %s",
                            category,
                            entity_id,
                            err,
                        )
                    self._failed.add(entity_id)
                else:
                    self._failed.discard(entity_id)

    async def _async_get_items(self, entity_id: str) -> dict[str, dict[str, Any]]:
        """Return the items of a list by their ID."""
        state = self.hass.states.get(entity_id)
        if state is None or state.state == "unavailable":
            raise HomeAssistantError(f"{entity_id} is not available")
        response = await self.hass.services.async_call(
            TODO_DOMAIN,
            "get_items",
            {"status": [NEEDS_ACTION, COMPLETED]},
            target={"entity_id": entity_id},
            blocking=True,
            return_response=True,
        )
        items = (response or {}).get(entity_id, {}).get("items", [])
        return {item["uid"]: item for item in items if item.get("uid")}

    async def _async_call(
        self, entity_id: str, service: str, data: dict[str, Any]
    ) -> None:
        """Change a list, logging instead of failing the whole sync."""
        try:
            await self.hass.services.async_call(
                TODO_DOMAIN,
                service,
                data,
                target={"entity_id": entity_id},
                blocking=True,
            )
        except (HomeAssistantError, vol.Invalid, ValueError) as err:
            _LOGGER.warning("%s on %s failed: %s", service, entity_id, err)

    def _due_data(self, entity_id: str, due: str | None) -> dict[str, Any]:
        """Return the due date fields a list understands for an idea's due time."""
        when = dt_util.parse_datetime(due) if due else None
        state = self.hass.states.get(entity_id)
        if when is None or state is None:
            return {}
        features = state.attributes.get(ATTR_SUPPORTED_FEATURES, 0)
        if features & TodoListEntityFeature.SET_DUE_DATETIME_ON_ITEM:
            return {"due_datetime": dt_util.as_local(when).isoformat()}
        if features & TodoListEntityFeature.SET_DUE_DATE_ON_ITEM:
            return {"due_date": dt_util.as_local(when).date().isoformat()}
        return {}

    async def _async_sync_one(self, category: str, entity_id: str) -> None:
        """Compare one category with its list and settle the differences."""
        items = await self._async_get_items(entity_id)
        links: dict[str, dict[str, Any] | None] = {}
        claimed: set[str] = set()
        to_add: list[dict[str, Any]] = []

        for idea in list(self.store.ideas):
            link = idea.get(ATTR_TODO_LINK)
            linked_here = bool(link) and link.get(LINK_ENTITY) == entity_id
            if not self._eligible(idea, category):
                if linked_here:
                    # Moved to another list, made private or archived
                    if link.get(LINK_UID) in items:
                        await self._async_call(
                            entity_id, "remove_item", {"item": [link[LINK_UID]]}
                        )
                    links[idea[ATTR_ID]] = None
                continue
            if link and not linked_here:
                links[idea[ATTR_ID]] = link = None
            if not link:
                if idea.get(ATTR_STATUS) == "active":
                    to_add.append(idea)
                continue
            uid = link.get(LINK_UID)
            if uid is None:
                # Added before, but the list had not shown the new item yet
                match = self._find_unclaimed(
                    items, claimed, link.get(LINK_SUMMARY) or idea[ATTR_TEXT]
                )
                if match is None:
                    continue
                uid = match
                link = {**link, LINK_UID: uid}
            if uid not in items:
                # Removed on the list, which shopping lists do with what was bought
                if idea.get(ATTR_STATUS) == "active":
                    await self.store.async_update_idea(idea[ATTR_ID], status="completed")
                links[idea[ATTR_ID]] = None
                continue
            claimed.add(uid)
            links[idea[ATTR_ID]] = await self._async_settle(
                entity_id, idea, link, items[uid]
            )

        for idea in to_add:
            match = self._find_unclaimed(items, claimed, idea[ATTR_TEXT], NEEDS_ACTION)
            if match is not None:
                claimed.add(match)
                # Coupled for the first time, the spelling on the list wins
                link = self._link(entity_id, items[match], idea.get(ATTR_DUE))
                link[LINK_SUMMARY] = idea[ATTR_TEXT]
                links[idea[ATTR_ID]] = await self._async_settle(
                    entity_id, idea, link, items[match]
                )
                continue
            await self._async_call(
                entity_id,
                "add_item",
                {"item": idea[ATTR_TEXT], **self._due_data(entity_id, idea.get(ATTR_DUE))},
            )
            links[idea[ATTR_ID]] = {
                LINK_ENTITY: entity_id,
                LINK_UID: None,
                LINK_SUMMARY: idea[ATTR_TEXT],
                LINK_STATUS: NEEDS_ACTION,
                LINK_DUE: idea.get(ATTR_DUE),
            }

        pending = [
            idea_id
            for idea_id, link in links.items()
            if link and link.get(LINK_UID) is None
        ]
        if pending:
            # Most lists show a new item at once, which gives it its ID now
            fresh = await self._async_get_items(entity_id)
            known = set(items)
            for idea_id in pending:
                link = links[idea_id]
                match = self._find_unclaimed(
                    {u: i for u, i in fresh.items() if u not in known},
                    claimed,
                    link[LINK_SUMMARY],
                )
                if match is not None:
                    claimed.add(match)
                    link[LINK_UID] = match

        # What is left on the list is new there and becomes an idea
        for uid, item in items.items():
            if uid in claimed or item.get("status") != NEEDS_ACTION:
                continue
            if not (item.get("summary") or "").strip():
                continue
            idea = await self.store.async_add_idea(
                text=item["summary"],
                category=category,
                source=SOURCE_TODO_SYNC,
                verbatim=True,
                shares={SHARE_ALL: SHARE_EDIT} if self.store.privacy_enabled else None,
            )
            links[idea[ATTR_ID]] = self._link(entity_id, item, idea.get(ATTR_DUE))

        await self.store.async_set_links(
            {
                idea_id: link
                for idea_id, link in links.items()
                if self.store.get_idea(idea_id) is not None
            }
        )

    @staticmethod
    def _find_unclaimed(
        items: dict[str, dict[str, Any]],
        claimed: set[str],
        text: str,
        status: str | None = None,
    ) -> str | None:
        """Return an item with this text that no idea is linked to yet."""
        for uid, item in items.items():
            if uid in claimed or not _same_text(item.get("summary"), text):
                continue
            if status is None or item.get("status") == status:
                return uid
        return None

    @staticmethod
    def _link(
        entity_id: str, item: dict[str, Any], due: str | None
    ) -> dict[str, Any]:
        """Return a link that records what the list says about an item now."""
        return {
            LINK_ENTITY: entity_id,
            LINK_UID: item["uid"],
            LINK_SUMMARY: item.get("summary") or "",
            LINK_STATUS: item.get("status") or NEEDS_ACTION,
            LINK_DUE: due,
        }

    async def _async_settle(
        self,
        entity_id: str,
        idea: dict[str, Any],
        link: dict[str, Any],
        item: dict[str, Any],
    ) -> dict[str, Any]:
        """Bring an idea and its item together, a change on the list winning."""
        summary = item.get("summary") or ""
        status = item.get("status") or NEEDS_ACTION
        text_on_list = summary != link.get(LINK_SUMMARY)
        status_on_list = status != link.get(LINK_STATUS)

        new_text = summary if text_on_list and summary.strip() else None
        new_status = None
        if status_on_list and status != _idea_status(idea):
            new_status = "completed" if status == COMPLETED else "active"
        if new_text is not None and new_text == idea[ATTR_TEXT]:
            new_text = None
        if new_text is not None or new_status is not None:
            idea = await self.store.async_update_idea(
                idea[ATTR_ID], text=new_text, status=new_status
            ) or idea

        update: dict[str, Any] = {}
        if idea[ATTR_TEXT] != summary and not text_on_list:
            update["rename"] = idea[ATTR_TEXT]
        if _idea_status(idea) != status and not status_on_list:
            update["status"] = _idea_status(idea)
        due = idea.get(ATTR_DUE)
        if due and due != link.get(LINK_DUE):
            update.update(self._due_data(entity_id, due))
        if update:
            await self._async_call(
                entity_id, "update_item", {"item": item["uid"], **update}
            )
        return {
            LINK_ENTITY: entity_id,
            LINK_UID: item["uid"],
            LINK_SUMMARY: update.get("rename", summary),
            LINK_STATUS: update.get("status", status),
            LINK_DUE: due,
        }
