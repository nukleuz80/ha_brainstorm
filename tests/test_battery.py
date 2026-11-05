"""Tests for battery tasks."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.brainstorm.store import BrainstormStore

from .conftest import SetupEntry

SENSOR = "sensor.flur_batterie"
BINARY = "binary_sensor.fenster_batterie"
OPTIONS = {
    "battery_enabled": True,
    "battery_threshold": 20,
    "battery_category": "Smarthome",
}


def _set_level(hass: HomeAssistant, level: str, entity_id: str = SENSOR) -> None:
    hass.states.async_set(
        entity_id,
        level,
        {
            "device_class": "battery",
            "unit_of_measurement": "%",
            "friendly_name": "Bewegungsmelder Flur Batterie",
        },
    )


def _set_low(hass: HomeAssistant, low: bool) -> None:
    hass.states.async_set(
        BINARY,
        "on" if low else "off",
        {"device_class": "battery", "friendly_name": "Fenster Bad Batterie"},
    )


def _tasks(store: BrainstormStore, entity_id: str = SENSOR) -> list[dict[str, Any]]:
    return [idea for idea in store.ideas if idea.get("battery") == entity_id]


async def _setup(
    setup_entry: SetupEntry, **options: Any
) -> BrainstormStore:
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox", "Smarthome"]},
        options={**OPTIONS, **options},
    )
    return entry.runtime_data


async def test_low_level_creates_one_task_and_a_new_battery_ticks_it_off(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the whole life of a battery task."""
    store = await _setup(setup_entry)
    _set_level(hass, "35")
    await hass.async_block_till_done()
    assert _tasks(store) == []

    _set_level(hass, "18")
    await hass.async_block_till_done()
    _set_level(hass, "12")
    await hass.async_block_till_done()
    tasks = _tasks(store)
    assert len(tasks) == 1
    assert tasks[0]["text"] == "Batterie wechseln: Bewegungsmelder Flur (18 %)"
    assert tasks[0]["category"] == "Smarthome"
    assert tasks[0]["source"] == "battery"
    assert tasks[0]["status"] == "active"

    # Just above the threshold still counts as the old battery
    _set_level(hass, "25")
    await hass.async_block_till_done()
    assert _tasks(store)[0]["status"] == "active"

    _set_level(hass, "100")
    await hass.async_block_till_done()
    assert _tasks(store)[0]["status"] == "completed"
    assert _tasks(store)[0]["battery_done"] is True

    # The next weak battery is a new task
    _set_level(hass, "15")
    await hass.async_block_till_done()
    assert [task["status"] for task in _tasks(store)].count("active") == 1


async def test_weak_battery_sensor(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Test a sensor that only says whether its battery is weak."""
    store = await _setup(setup_entry)
    _set_low(hass, True)
    await hass.async_block_till_done()
    tasks = _tasks(store, BINARY)
    assert len(tasks) == 1
    assert tasks[0]["text"] == "Batterie wechseln: Fenster Bad"
    _set_low(hass, False)
    await hass.async_block_till_done()
    assert _tasks(store, BINARY)[0]["status"] == "completed"


async def test_task_ticked_off_by_hand_does_not_come_back(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a task ticked off before the battery is replaced stays done."""
    store = await _setup(setup_entry)
    _set_level(hass, "10")
    await hass.async_block_till_done()
    task = _tasks(store)[0]
    await store.async_update_idea(task["id"], status="completed")
    _set_level(hass, "8")
    await hass.async_block_till_done()
    assert len(_tasks(store)) == 1
    _set_level(hass, "90")
    await hass.async_block_till_done()
    assert _tasks(store)[0]["battery_done"] is True
    _set_level(hass, "10")
    await hass.async_block_till_done()
    assert len(_tasks(store)) == 2


async def test_batteries_already_low_at_start_and_left_out(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the check at start and the batteries left out."""
    _set_level(hass, "5")
    _set_low(hass, True)
    hass.states.async_set("sensor.other", "3", {"unit_of_measurement": "%"})
    store = await _setup(setup_entry, battery_exclude=[BINARY])
    assert len(_tasks(store)) == 1
    assert _tasks(store, BINARY) == []
    assert _tasks(store, "sensor.other") == []
    _set_low(hass, True)
    hass.states.async_set(BINARY, "on", {"device_class": "battery", "x": 1})
    await hass.async_block_till_done()
    assert _tasks(store, BINARY) == []


async def test_switched_off_creates_nothing(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that battery tasks are off unless switched on."""
    _set_level(hass, "5")
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox"]})
    _set_level(hass, "4")
    await hass.async_block_till_done()
    assert _tasks(entry.runtime_data) == []


async def test_unclear_states_are_ignored(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that an unavailable sensor neither creates nor closes a task."""
    store = await _setup(setup_entry)
    _set_level(hass, "unavailable")
    await hass.async_block_till_done()
    assert _tasks(store) == []
    _set_level(hass, "10")
    await hass.async_block_till_done()
    _set_level(hass, "unknown")
    await hass.async_block_till_done()
    assert _tasks(store)[0]["status"] == "active"


async def test_options_battery_page(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test switching battery tasks on with a new category."""
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox", "Smarthome"]})
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert "battery" in result["menu_options"]
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "battery"}
    )
    assert result["type"] is FlowResultType.FORM
    defaults = {
        str(key): key.default() for key in result["data_schema"].schema if callable(getattr(key, "default", None))
    }
    assert defaults["battery_category"] == "Smarthome"
    assert defaults["battery_threshold"] == 20

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"battery_enabled": True, "battery_category": " "}
    )
    assert result["errors"] == {"battery_category": "battery_category_missing"}
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "battery_enabled": True,
            "battery_category": "Batterien",
            "battery_threshold": 15.0,
            "battery_exclude": [BINARY],
        },
    )
    assert result["type"] is FlowResultType.MENU
    await hass.async_block_till_done()
    assert entry.options["battery_threshold"] == 15
    assert entry.options["battery_exclude"] == [BINARY]
    assert "Batterien" in entry.runtime_data.categories
