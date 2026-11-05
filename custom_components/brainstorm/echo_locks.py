"""Lock times for single Echos, such as nights in the children's room."""

from __future__ import annotations

from datetime import datetime, time
import logging
from typing import Any

from homeassistant.const import SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_track_time_change
from homeassistant.util import dt as dt_util

from .const import CONF_ECHO_LOCKS

_LOGGER = logging.getLogger(__name__)

LOCK_ECHOS = "echos"
LOCK_START = "start"
LOCK_END = "end"
LOCK_DND = "dnd"
# How many lock times the settings page offers
LOCK_SLOTS = 3


def _parse(value: str | None) -> time | None:
    """Parse a stored time of day."""
    return dt_util.parse_time(value) if value else None


def in_window(now: datetime, start: time | None, end: time | None) -> bool:
    """Return whether a time lies in a window, which may span midnight."""
    if start is None or end is None or start == end:
        return False
    current = now.time()
    if start < end:
        return start <= current < end
    return current >= start or current < end


def locked_echos(options: dict[str, Any], now: datetime) -> set[str]:
    """Return the Echos that must stay silent right now."""
    locked: set[str] = set()
    for lock in options.get(CONF_ECHO_LOCKS) or []:
        if in_window(now, _parse(lock.get(LOCK_START)), _parse(lock.get(LOCK_END))):
            locked.update(lock.get(LOCK_ECHOS) or [])
    return locked


def dnd_switch(hass: HomeAssistant, echo: str) -> str | None:
    """Return the Do not disturb switch Alexa Media made for an Echo."""
    registry = er.async_get(hass)
    entry = registry.async_get(echo)
    if entry is None or not entry.device_id:
        return None
    for other in er.async_entries_for_device(registry, entry.device_id):
        if other.domain == "switch" and "do_not_disturb" in other.entity_id:
            return other.entity_id
    return None


class EchoLockManager:
    """Switch Do not disturb on and off with the lock times that ask for it."""

    def __init__(self, hass: HomeAssistant, options: dict[str, Any]) -> None:
        """Remember the lock times."""
        self.hass = hass
        self.locks = [
            lock
            for lock in options.get(CONF_ECHO_LOCKS) or []
            if lock.get(LOCK_DND) and lock.get(LOCK_ECHOS)
        ]
        self._unsubs: list[CALLBACK_TYPE] = []

    async def async_start(self) -> None:
        """Plan the switching, and catch up if a lock time is running."""
        now = dt_util.now()
        for lock in self.locks:
            start, end = _parse(lock.get(LOCK_START)), _parse(lock.get(LOCK_END))
            if start is None or end is None or start == end:
                continue
            for moment, on in ((start, True), (end, False)):
                self._unsubs.append(
                    async_track_time_change(
                        self.hass,
                        self._switcher(lock, on),
                        hour=moment.hour,
                        minute=moment.minute,
                        second=0,
                    )
                )
            if in_window(now, start, end):
                await self.async_set_dnd(lock[LOCK_ECHOS], True)

    @callback
    def async_stop(self) -> None:
        """Stop switching."""
        while self._unsubs:
            self._unsubs.pop()()

    def _switcher(self, lock: dict[str, Any], on: bool) -> Any:
        """Return the job that switches the Echos of a lock time."""

        async def _switch(_now: datetime) -> None:
            await self.async_set_dnd(lock[LOCK_ECHOS], on)

        return _switch

    async def async_set_dnd(self, echos: list[str], on: bool) -> None:
        """Switch Do not disturb of some Echos, skipping those without it."""
        switches = [switch for echo in echos if (switch := dnd_switch(self.hass, echo))]
        missing = len(echos) - len(switches)
        if missing:
            _LOGGER.warning(
                "%s Echo(s) of a lock time have no Do not disturb switch", missing
            )
        if not switches:
            return
        try:
            await self.hass.services.async_call(
                "switch",
                SERVICE_TURN_ON if on else SERVICE_TURN_OFF,
                target={"entity_id": switches},
                blocking=True,
            )
        except HomeAssistantError as err:
            _LOGGER.warning("Could not switch Do not disturb: %s", err)
