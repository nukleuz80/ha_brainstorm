"""Turn a sensor reaching a value into a Brainstorm task that ticks itself off."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.const import (
    ATTR_UNIT_OF_MEASUREMENT,
    EVENT_HOMEASSISTANT_STARTED,
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
from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    ATTR_ID,
    ATTR_SENSOR_RULE,
    ATTR_SENSOR_RULE_DONE,
    ATTR_STATUS,
    CONDITION_ABOVE,
    CONDITION_BELOW,
    CONDITION_STATE,
    CONF_SENSOR_RULES,
    RULE_AUTO_DONE,
    RULE_CATEGORY,
    RULE_CONDITION,
    RULE_ENTITY,
    RULE_ID,
    RULE_RESET,
    RULE_TEXT,
    RULE_VALUE,
    SHARE_ALL,
    SHARE_EDIT,
    SOURCE_SENSOR,
)
from .languages import get_pack

if TYPE_CHECKING:
    from .store import BrainstormStore

_LOGGER = logging.getLogger(__name__)


def to_number(value: Any) -> float | None:
    """Return a value as a number, accepting a comma as decimal sign."""
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(str(value).strip().replace(",", "."))
    except ValueError:
        return None


def rule_met(rule: dict[str, Any], state: State | None) -> bool | None:
    """Return True if the rule is met, False if it is clear, None while unclear.

    With a reset value, a number between the limit and the reset value keeps
    the last status, so a sensor around the limit does not toggle a task.
    """
    if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
        return None
    condition = rule.get(RULE_CONDITION)
    if condition == CONDITION_STATE:
        expected = str(rule.get(RULE_VALUE) or "").strip().casefold()
        return state.state.strip().casefold() == expected
    level = to_number(state.state)
    limit = to_number(rule.get(RULE_VALUE))
    if level is None or limit is None:
        return None
    reset = to_number(rule.get(RULE_RESET))
    if condition == CONDITION_ABOVE:
        if level >= limit:
            return True
        return False if reset is None or level <= reset else None
    if condition == CONDITION_BELOW:
        if level <= limit:
            return True
        return False if reset is None or level >= reset else None
    return None


def valid_rules(options: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the complete rules of the settings."""
    return [
        rule
        for rule in options.get(CONF_SENSOR_RULES) or []
        if rule.get(RULE_ID)
        and rule.get(RULE_ENTITY)
        and rule.get(RULE_CONDITION) in (CONDITION_ABOVE, CONDITION_BELOW, CONDITION_STATE)
        and str(rule.get(RULE_TEXT) or "").strip()
    ]


class SensorRuleWatcher:
    """Create a task when a sensor meets its rule and tick it off once it clears."""

    def __init__(
        self, hass: HomeAssistant, store: BrainstormStore, options: dict[str, Any]
    ) -> None:
        """Remember the rules."""
        self.hass = hass
        self.store = store
        self.rules = valid_rules(options)
        self._unsubs: list[CALLBACK_TYPE] = []
        self._unsub_started: CALLBACK_TYPE | None = None

    async def async_start(self) -> None:
        """Watch the sensors of the rules, starting with a full check once HA runs."""
        if self.rules:
            self._unsubs.append(
                async_track_state_change_event(
                    self.hass,
                    sorted({rule[RULE_ENTITY] for rule in self.rules}),
                    self._handle_state_change,
                )
            )
        if self.hass.state is CoreState.running:
            await self.async_check_all()
        else:
            # Sensors only report their value once their integrations are up
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
        """Check all rules once Home Assistant has started."""
        # The listener is gone once it fired, so it must not be removed on stop
        self._unsub_started = None
        await self.async_check_all()

    async def _handle_state_change(self, event: Event[EventStateChangedData]) -> None:
        """Check the rules of a sensor that changed."""
        entity_id = event.data["entity_id"]
        for rule in self.rules:
            if rule[RULE_ENTITY] == entity_id:
                await self._async_check(rule, event.data["new_state"])

    async def async_check_all(self) -> None:
        """Check every rule, for example after a restart."""
        for rule in self.rules:
            await self._async_check(rule, self.hass.states.get(rule[RULE_ENTITY]))
        # A task of a deleted rule has no one to close it
        known = {rule[RULE_ID] for rule in self.rules}
        stale = {
            idea[ATTR_ID]: {ATTR_SENSOR_RULE_DONE: True}
            for idea in self._open_tasks()
            if idea[ATTR_SENSOR_RULE] not in known
        }
        if stale:
            await self.store.async_set_fields(stale)

    def _open_tasks(self) -> list[dict[str, Any]]:
        """Return the tasks whose sensor is not back to normal yet."""
        return [
            idea
            for idea in self.store.ideas
            if idea.get(ATTR_SENSOR_RULE) and not idea.get(ATTR_SENSOR_RULE_DONE)
        ]

    async def _async_check(self, rule: dict[str, Any], state: State | None) -> None:
        """Create or close the task of one rule."""
        met = rule_met(rule, state)
        if met is None:
            return
        rule_id = rule[RULE_ID]
        tasks = [
            idea for idea in self.store.ideas if idea.get(ATTR_SENSOR_RULE) == rule_id
        ]
        case = next(
            (idea for idea in tasks if not idea.get(ATTR_SENSOR_RULE_DONE)), None
        )
        if met and state is not None:
            # One task per occurrence, and none while an old one is still open
            if case is None and not any(
                idea.get(ATTR_STATUS) == "active" for idea in tasks
            ):
                await self._async_create(rule, state)
            return
        if case is None:
            return
        if rule.get(RULE_AUTO_DONE, True) and case.get(ATTR_STATUS) == "active":
            await self.store.async_update_idea(case[ATTR_ID], status="completed")
        await self.store.async_set_fields({case[ATTR_ID]: {ATTR_SENSOR_RULE_DONE: True}})

    async def _async_create(self, rule: dict[str, Any], state: State) -> None:
        """Add the task of a rule that is met."""
        pack = get_pack(self.hass.config.language)
        unit = state.attributes.get(ATTR_UNIT_OF_MEASUREMENT)
        value = f"{state.state} {unit}" if unit else state.state
        idea = await self.store.async_add_idea(
            text=str(rule[RULE_TEXT]).strip(),
            category=(rule.get(RULE_CATEGORY) or "").strip() or None,
            source=SOURCE_SENSOR,
            device=str(state.name),
            verbatim=True,
            description=pack.msg("sensor_task_description", name=state.name, value=value),
            shares={SHARE_ALL: SHARE_EDIT} if self.store.privacy_enabled else None,
        )
        await self.store.async_set_fields({idea[ATTR_ID]: {ATTR_SENSOR_RULE: rule[RULE_ID]}})
        _LOGGER.info("Sensor task added for %s", state.entity_id)
