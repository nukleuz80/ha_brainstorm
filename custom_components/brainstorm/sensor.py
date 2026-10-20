"""Sensor platform for Brainstorm Hub."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ATTR_CATEGORY,
    ATTR_CREATED_AT,
    ATTR_ID,
    ATTR_SOURCE,
    ATTR_STATUS,
    ATTR_TEXT,
    DOMAIN,
)
from .store import BrainstormStore

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Brainstorm sensor platform."""
    store: BrainstormStore = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([BrainstormOverviewSensor(store, entry.entry_id)])


class BrainstormOverviewSensor(SensorEntity):
    """Overview sensor for Brainstorm statistics."""

    _attr_has_entity_name = True
    _attr_name = "Brainstorm Ideen Übersicht"
    _attr_icon = "mdi:brain"

    def __init__(self, store: BrainstormStore, entry_id: str) -> None:
        """Initialize the sensor."""
        self._store = store
        self._attr_unique_id = f"{entry_id}_sensor_overview"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="Brainstorm Hub",
            manufacturer="nukleuz80",
            model="Brainstorm Hub",
            sw_version="1.4.0",
        )

    async def async_added_to_hass(self) -> None:
        """Register listener when added to hass."""
        await super().async_added_to_hass()
        self.async_on_remove(self._store.register_listener(self.async_write_ha_state))

    @property
    def native_value(self) -> int:
        """Return the number of active ideas."""
        return len([i for i in self._store.ideas if i.get(ATTR_STATUS) == "active"])

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return detailed statistics and recent ideas."""
        active_ideas = [i for i in self._store.ideas if i.get(ATTR_STATUS) == "active"]
        completed_ideas = [i for i in self._store.ideas if i.get(ATTR_STATUS) == "completed"]

        counts_by_cat = {}
        for cat in self._store.categories:
            counts_by_cat[cat] = len(
                [i for i in active_ideas if i.get(ATTR_CATEGORY) == cat]
            )

        latest = active_ideas[0] if active_ideas else None
        latest_info = None
        if latest:
            latest_info = {
                "text": latest.get(ATTR_TEXT),
                "category": latest.get(ATTR_CATEGORY),
                "created_at": latest.get(ATTR_CREATED_AT),
                "source": latest.get(ATTR_SOURCE),
            }

        recent_list = [
            {
                "text": i.get(ATTR_TEXT),
                "category": i.get(ATTR_CATEGORY),
                "created_at": i.get(ATTR_CREATED_AT),
                "source": i.get(ATTR_SOURCE),
            }
            for i in active_ideas[:5]
        ]

        return {
            "active_count": len(active_ideas),
            "completed_count": len(completed_ideas),
            "categories": self._store.categories,
            "category_counts": counts_by_cat,
            "latest_idea": latest_info,
            "recent_ideas": recent_list,
            "ideas": [
                {
                    "id": i.get(ATTR_ID),
                    "text": i.get(ATTR_TEXT),
                    "category": i.get(ATTR_CATEGORY),
                    "created_at": i.get(ATTR_CREATED_AT),
                    "source": i.get(ATTR_SOURCE),
                    "status": i.get(ATTR_STATUS),
                }
                for i in active_ideas
            ],
            "completed_ideas": [
                {
                    "id": i.get(ATTR_ID),
                    "text": i.get(ATTR_TEXT),
                    "category": i.get(ATTR_CATEGORY),
                    "created_at": i.get(ATTR_CREATED_AT),
                    "source": i.get(ATTR_SOURCE),
                    "status": i.get(ATTR_STATUS),
                }
                for i in completed_ideas[:50]
            ],
        }

