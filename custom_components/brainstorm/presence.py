"""Who has a Brainstorm map open right now, kept in memory only."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.util import dt as dt_util

from .const import DOMAIN

# More open maps than this at once are not shown
PRESENCE_MAX = 100

PresenceKey = tuple[int, str]
PresenceListener = Callable[[list[dict[str, Any]]], None]


class Presence:
    """Open maps by connection and card, told to every open map on change."""

    def __init__(self) -> None:
        """Start with nobody present."""
        self._entries: dict[PresenceKey, dict[str, Any]] = {}
        self._listeners: dict[PresenceKey, PresenceListener] = {}

    @property
    def entries(self) -> list[dict[str, Any]]:
        """Return everybody present, oldest first."""
        return [dict(entry) for entry in self._entries.values()]

    @callback
    def join(
        self,
        key: PresenceKey,
        user_id: str,
        name: str,
        category: str | None,
        listener: PresenceListener,
    ) -> bool:
        """Add an open map, returning False when too many are open."""
        if key not in self._entries and len(self._entries) >= PRESENCE_MAX:
            return False
        self._entries[key] = {
            "key": key[1],
            "user_id": user_id,
            "name": name,
            "category": category,
            "editing": None,
            "since": dt_util.utcnow().isoformat(),
        }
        # The others hear of it now, the new map gets the list after its result
        self._broadcast()
        self._listeners[key] = listener
        return True

    def knows(self, key: PresenceKey) -> bool:
        """Return whether this open map has joined."""
        return key in self._entries

    @callback
    def update(
        self, key: PresenceKey, category: str | None, editing: str | None
    ) -> bool:
        """Change what an open map shows, returning False if it is unknown."""
        entry = self._entries.get(key)
        if entry is None:
            return False
        if entry["category"] == category and entry["editing"] == editing:
            # Nothing new, so nobody needs to hear about it
            return True
        entry["category"] = category
        entry["editing"] = editing
        self._broadcast()
        return True

    @callback
    def leave(self, key: PresenceKey) -> None:
        """Remove an open map that was closed or lost its connection."""
        self._listeners.pop(key, None)
        if self._entries.pop(key, None) is not None:
            self._broadcast()

    @callback
    def _broadcast(self) -> None:
        present = self.entries
        for listener in list(self._listeners.values()):
            listener(present)


@callback
def get_presence(hass: HomeAssistant) -> Presence:
    """Return the presence registry, made on first use."""
    key = f"{DOMAIN}_presence"
    if key not in hass.data:
        hass.data[key] = Presence()
    presence: Presence = hass.data[key]
    return presence
