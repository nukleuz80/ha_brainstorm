"""Work together with Battery Notes for the battery tasks.

Battery Notes knows the battery type of a device ("2× AA") and when its
battery was last replaced. Battery tasks name the type, and ticking one off
tells Battery Notes the battery was replaced. Putting the batteries of all
open tasks on Bring! is in bring.py.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.core import Context, HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er

from .const import (
    ATTR_BATTERY,
    ATTR_BATTERY_DONE,
    ATTR_STATUS,
    BATTERY_NOTES_DOMAIN,
)

if TYPE_CHECKING:
    from .store import BrainstormStore

_LOGGER = logging.getLogger(__name__)

SERVICE_REPLACED = "set_battery_replaced"
DEVICE_PREFIX = "device:"


@dataclass(frozen=True)
class BatteryType:
    """The batteries a device takes."""

    kind: str
    quantity: int

    @property
    def label(self) -> str:
        """Return the type as shown in a task, such as "2× AA"."""
        return f"{self.quantity}× {self.kind}"


def battery_notes_available(hass: HomeAssistant) -> bool:
    """Tell whether Battery Notes is installed."""
    return hass.services.has_service(BATTERY_NOTES_DOMAIN, SERVICE_REPLACED)


def _quantity(value: Any) -> int:
    try:
        return max(1, int(float(str(value))))
    except (TypeError, ValueError):
        return 1


def battery_type(hass: HomeAssistant, key: str) -> BatteryType | None:
    """Return the battery type Battery Notes knows for a battery task's device."""
    if not key.startswith(DEVICE_PREFIX):
        return None
    device_id = key.removeprefix(DEVICE_PREFIX)
    for entry in er.async_entries_for_device(er.async_get(hass), device_id):
        if entry.platform != BATTERY_NOTES_DOMAIN or entry.domain != "sensor":
            continue
        state = hass.states.get(entry.entity_id)
        kind = state.attributes.get("battery_type") if state is not None else None
        if not kind or not str(kind).strip():
            continue
        return BatteryType(
            " ".join(str(kind).split()),
            _quantity(state.attributes.get("battery_quantity")),
        )
    return None


async def async_mark_replaced(
    hass: HomeAssistant, key: str, context: Context | None = None
) -> bool:
    """Tell Battery Notes that the battery of a device was replaced now."""
    if not key.startswith(DEVICE_PREFIX) or not battery_notes_available(hass):
        return False
    if battery_type(hass, key) is None:
        # Battery Notes does not know this device
        return False
    try:
        await hass.services.async_call(
            BATTERY_NOTES_DOMAIN,
            SERVICE_REPLACED,
            {"device_id": key.removeprefix(DEVICE_PREFIX)},
            blocking=True,
            context=context,
        )
    except HomeAssistantError as err:
        _LOGGER.warning("Battery Notes did not take the new battery: %s", err)
        return False
    return True


def needed_batteries(hass: HomeAssistant, store: BrainstormStore) -> Counter[str]:
    """Return how many batteries of each type the open battery tasks need."""
    needed: Counter[str] = Counter()
    for idea in store.ideas:
        key = idea.get(ATTR_BATTERY)
        if not key or idea.get(ATTR_BATTERY_DONE) or idea.get(ATTR_STATUS) != "active":
            continue
        if (kind := battery_type(hass, str(key))) is not None:
            needed[kind.kind] += kind.quantity
    return needed
