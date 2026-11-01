"""Sensor platform for Brainstorm Hub."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import Context, HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ATTR_STATUS, DOMAIN, OVERVIEW_ENTITY_ID
from .store import BrainstormConfigEntry, BrainstormStore

PARALLEL_UPDATES = 0

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BrainstormConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Brainstorm sensor platform."""
    store = entry.runtime_data
    async_add_entities([BrainstormOverviewSensor(store, entry.entry_id)])


class BrainstormOverviewSensor(SensorEntity):
    """Overview sensor for Brainstorm statistics."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_translation_key = "overview"
    _attr_icon = "mdi:brain"
    # The cards read these live; recording them would exceed the 16 KB recorder limit
    _unrecorded_attributes = frozenset(
        {
            "speech_overview",
            "last_action",
            "latest_idea",
            "recent_ideas",
            "ideas",
            "completed_ideas",
        }
    )

    def __init__(self, store: BrainstormStore, entry_id: str) -> None:
        """Initialize the sensor."""
        self._store = store
        # Cards and logbook expect this ID regardless of the device name
        self.entity_id = OVERVIEW_ENTITY_ID
        self._attr_unique_id = f"{entry_id}_sensor_overview"
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
        self.async_on_remove(self._store.register_listener(self._handle_store_update))

    @callback
    def _handle_store_update(self, context: Context | None = None) -> None:
        """Handle store update and preserve trigger context."""
        if context is not None:
            self.async_set_context(context)
        self.async_write_ha_state()

    @property
    def native_value(self) -> int:
        """Return the number of active ideas."""
        return len([i for i in self._store.ideas if i.get(ATTR_STATUS) == "active"])

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return statistics and ideas, which only the owners see while private."""
        if self._store.privacy_enabled:
            return self._store.get_public_attributes()
        return self._store.get_overview_attributes()
