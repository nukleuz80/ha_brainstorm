"""Turn low batteries into Brainstorm tasks that tick themselves off."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    EVENT_HOMEASSISTANT_STARTED,
    EVENT_STATE_CHANGED,
    STATE_ON,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import (
    CALLBACK_TYPE,
    CoreState,
    Event,
    EventStateChangedData,
    HomeAssistant,
    State,
    callback,
)
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .const import (
    ATTR_BATTERY,
    ATTR_BATTERY_DONE,
    ATTR_ID,
    ATTR_STATUS,
    CONF_BATTERY_CATEGORY,
    CONF_BATTERY_ENABLED,
    CONF_BATTERY_EXCLUDE,
    CONF_BATTERY_PHONES,
    CONF_BATTERY_THRESHOLD,
    DEFAULT_BATTERY_THRESHOLD,
    SHARE_ALL,
    SHARE_EDIT,
    SOURCE_BATTERY,
)
from .languages import get_pack

if TYPE_CHECKING:
    from .store import BrainstormStore

_LOGGER = logging.getLogger(__name__)

BATTERY_DOMAINS = ("sensor", "binary_sensor")
# A level must rise this far above the threshold to count as a new battery
RECOVER_MARGIN = 10
_NAME_SUFFIXES = (" battery level", " battery", " batterie", " akku", " batteriestand")


def is_battery_state(state: State | None) -> bool:
    """Return whether a state belongs to a battery sensor."""
    return (
        state is not None
        and state.domain in BATTERY_DOMAINS
        and state.attributes.get(ATTR_DEVICE_CLASS) == "battery"
    )


def battery_level(state: State) -> float | None:
    """Return the level of a percentage battery sensor, if it reports one."""
    if state.domain != "sensor":
        return None
    try:
        return float(state.state)
    except (TypeError, ValueError):
        return None


def battery_status(state: State, threshold: int) -> bool | None:
    """Return True for a low, False for a good battery, None while unclear.

    A level between the threshold and the margin above it keeps the last
    status, so a battery around the threshold does not toggle a task.
    """
    if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
        return None
    if state.domain == "binary_sensor":
        return state.state == STATE_ON
    level = battery_level(state)
    if level is None:
        return None
    if level <= threshold:
        return True
    if level >= threshold + RECOVER_MARGIN:
        return False
    return None


class BatteryWatcher:
    """Create a task for every low battery and tick it off once it is replaced."""

    def __init__(
        self, hass: HomeAssistant, store: BrainstormStore, options: dict[str, Any]
    ) -> None:
        """Remember the settings."""
        self.hass = hass
        self.store = store
        self.enabled = bool(options.get(CONF_BATTERY_ENABLED, False))
        self.threshold = int(
            options.get(CONF_BATTERY_THRESHOLD, DEFAULT_BATTERY_THRESHOLD)
        )
        self.category = (options.get(CONF_BATTERY_CATEGORY) or "").strip()
        self.exclude = set(options.get(CONF_BATTERY_EXCLUDE) or [])
        self.phones = bool(options.get(CONF_BATTERY_PHONES, False))
        self._unsubs: list[CALLBACK_TYPE] = []
        self._unsub_started: CALLBACK_TYPE | None = None

    async def async_start(self) -> None:
        """Watch battery sensors, starting with a full check once HA runs."""
        if not self.enabled:
            return
        self._unsubs.append(
            self.hass.bus.async_listen(
                EVENT_STATE_CHANGED,
                self._handle_state_change,
                event_filter=self._is_watched_event,
            )
        )
        if self.hass.state is CoreState.running:
            await self.async_check_all()
        else:
            # Sensors only report their level once their integrations are up
            self._unsub_started = self.hass.bus.async_listen_once(
                EVENT_HOMEASSISTANT_STARTED, self._handle_started
            )

    @callback
    def async_stop(self) -> None:
        """Stop watching."""
        while self._unsubs:
            self._unsubs.pop()()
        if self._unsub_started is not None:
            self._unsub_started()
            self._unsub_started = None

    async def _handle_started(self, _event: Event) -> None:
        """Check all batteries once Home Assistant has started."""
        # The listener is gone once it fired, so it must not be removed on stop
        self._unsub_started = None
        await self.async_check_all()

    @callback
    def _is_watched_event(self, data: EventStateChangedData) -> bool:
        """Only let battery sensors through, as this runs for every change."""
        return is_battery_state(data["new_state"])

    async def _handle_state_change(self, event: Event[EventStateChangedData]) -> None:
        """React to a battery sensor that changed."""
        groups = self._groups()
        key = self._key(event.data["entity_id"])
        if key in groups:
            await self._async_check(key, groups[key])

    def _key(self, entity_id: str) -> str:
        """Return the device a battery sensor belongs to, or the sensor itself.

        Integrations like Battery Notes add more sensors for the same battery,
        and one device must not get a task per sensor.
        """
        entry = er.async_get(self.hass).async_get(entity_id)
        if entry is not None and entry.device_id:
            return f"device:{entry.device_id}"
        return entity_id

    def _groups(self) -> dict[str, list[State]]:
        """Return the battery sensors per device, without the devices left out."""
        registry = er.async_get(self.hass)
        groups: dict[str, list[State]] = {}
        skipped: set[str] = set()
        for state in self.hass.states.async_all(BATTERY_DOMAINS):
            if not is_battery_state(state):
                continue
            key = self._key(state.entity_id)
            groups.setdefault(key, []).append(state)
            entry = registry.async_get(state.entity_id)
            # Leaving out one sensor leaves out its whole device
            if state.entity_id in self.exclude or (
                # Phones and tablets are charged every day, not replaced
                not self.phones and entry is not None and entry.platform == "mobile_app"
            ):
                skipped.add(key)
        return {key: states for key, states in groups.items() if key not in skipped}

    async def async_check_all(self) -> None:
        """Check every battery, for example after a restart."""
        groups = self._groups()
        for key, states in groups.items():
            await self._async_check(key, states)
        # A task for a battery left out or removed has no one to close it
        for idea in self._open_tasks():
            if idea[ATTR_BATTERY] not in groups:
                await self.store.async_set_fields({idea[ATTR_ID]: {ATTR_BATTERY_DONE: True}})

    def _open_tasks(self) -> list[dict[str, Any]]:
        """Return the battery tasks whose battery was not replaced yet."""
        return [
            idea
            for idea in self.store.ideas
            if idea.get(ATTR_BATTERY) and not idea.get(ATTR_BATTERY_DONE)
        ]

    async def _async_check(self, key: str, states: list[State]) -> None:
        """Create or close the task for one battery.

        A device is low while any of its sensors says so, and only counts as
        having a new battery when none does and at least one says it is good.
        """
        statuses = [battery_status(state, self.threshold) for state in states]
        low_states = [state for state, low in zip(states, statuses) if low]
        if low_states:
            low = True
        elif False in statuses:
            low = False
        else:
            return
        task = next(
            (idea for idea in self._open_tasks() if idea[ATTR_BATTERY] == key), None
        )
        if low and task is None:
            # A level says more than a weak flag
            state = min(
                low_states,
                key=lambda item: (battery_level(item) is None, battery_level(item) or 0),
            )
            await self._async_create(key, state)
        elif not low and task is not None:
            # A new battery: tick the task off, or just close the case if done
            if task.get(ATTR_STATUS) == "active":
                await self.store.async_update_idea(task[ATTR_ID], status="completed")
            await self.store.async_set_fields({task[ATTR_ID]: {ATTR_BATTERY_DONE: True}})

    async def _async_create(self, key: str, state: State) -> None:
        """Add the task for a low battery."""
        pack = get_pack(self.hass.config.language)
        name = self.device_name(state)
        level = battery_level(state)
        text = (
            pack.msg("battery_task_level", name=name, level=round(level))
            if level is not None
            else pack.msg("battery_task", name=name)
        )
        idea = await self.store.async_add_idea(
            text=text,
            category=self.category or None,
            source=SOURCE_BATTERY,
            verbatim=True,
            shares={SHARE_ALL: SHARE_EDIT} if self.store.privacy_enabled else None,
        )
        await self.store.async_set_fields({idea[ATTR_ID]: {ATTR_BATTERY: key}})
        _LOGGER.info("Battery task added for %s", state.entity_id)

    def device_name(self, state: State) -> str:
        """Return the name of the device the battery is in."""
        entry = er.async_get(self.hass).async_get(state.entity_id)
        if entry is not None and entry.device_id:
            device = dr.async_get(self.hass).async_get(entry.device_id)
            if device is not None and (device.name_by_user or device.name):
                return str(device.name_by_user or device.name)
        name = str(state.name)
        lowered = name.casefold()
        for suffix in _NAME_SUFFIXES:
            if lowered.endswith(suffix) and len(name) > len(suffix):
                return name[: -len(suffix)].strip()
        return name
