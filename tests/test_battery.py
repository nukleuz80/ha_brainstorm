"""Tests for battery tasks."""

from __future__ import annotations

from datetime import timedelta
import asyncio
from typing import Any

import pytest

from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from custom_components.brainstorm.store import BrainstormStore

from .conftest import SetupEntry

SENSOR = "sensor.flur_batterie"
BINARY = "binary_sensor.fenster_batterie"
OPTIONS = {
    "battery_enabled": True,
    "battery_threshold": 20,
    "battery_category": "Smarthome",
}


@pytest.fixture(autouse=True)
def _no_confirm_delay(monkeypatch: pytest.MonkeyPatch) -> None:
    """Create battery tasks at once, unless a test checks the wait."""
    monkeypatch.setattr(
        "custom_components.brainstorm.battery.CONFIRM_DELAY", timedelta(0)
    )


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


def _register(
    hass: HomeAssistant, entity_id: str, platform: str, device_id: str
) -> None:
    domain, object_id = entity_id.split(".", 1)
    er.async_get(hass).async_get_or_create(
        domain, platform, object_id, suggested_object_id=object_id, device_id=device_id
    )


def _device(hass: HomeAssistant, name: str) -> str:
    entry = MockConfigEntry(domain="test")
    entry.add_to_hass(hass)
    return dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id, identifiers={("test", name)}, name=name
    ).id


async def test_one_task_per_device(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Test that extra sensors for the same battery make no second task."""
    device = _device(hass, "Thermometer Bad")
    _register(hass, "sensor.bad_batterie", "switchbot", device)
    _register(hass, "sensor.bad_batterie_plus", "battery_notes", device)
    _register(hass, "binary_sensor.bad_batterie_low", "battery_notes", device)
    store = await _setup(setup_entry)
    key = f"device:{device}"
    _set_level(hass, "8", "sensor.bad_batterie")
    _set_level(hass, "8", "sensor.bad_batterie_plus")
    hass.states.async_set("binary_sensor.bad_batterie_low", "on", {"device_class": "battery"})
    await hass.async_block_till_done()
    tasks = _tasks(store, key)
    assert len(tasks) == 1
    assert tasks[0]["text"] == "Batterie wechseln: Thermometer Bad (8 %)"

    # One sensor with the new level is not enough while another still says weak
    _set_level(hass, "100", "sensor.bad_batterie")
    _set_level(hass, "100", "sensor.bad_batterie_plus")
    await hass.async_block_till_done()
    assert _tasks(store, key)[0]["status"] == "active"
    hass.states.async_set("binary_sensor.bad_batterie_low", "off", {"device_class": "battery"})
    await hass.async_block_till_done()
    assert _tasks(store, key)[0]["status"] == "completed"


async def test_phones_and_left_out_devices(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that phones are skipped unless wanted, and a left out sensor skips its device."""
    phone = _device(hass, "Handy")
    _register(hass, "sensor.handy_batterie", "mobile_app", phone)
    _register(hass, "sensor.handy_batterie_plus", "battery_notes", phone)
    solar = _device(hass, "Solarbank")
    _register(hass, "sensor.solarbank_ladestand", "anker", solar)
    _register(hass, "sensor.solarbank_ladestand_plus", "battery_notes", solar)
    for entity_id in (
        "sensor.handy_batterie",
        "sensor.handy_batterie_plus",
        "sensor.solarbank_ladestand",
        "sensor.solarbank_ladestand_plus",
    ):
        _set_level(hass, "10", entity_id)
    store = await _setup(setup_entry, battery_exclude=["sensor.solarbank_ladestand"])
    assert _tasks(store, f"device:{phone}") == []
    assert _tasks(store, f"device:{solar}") == []


async def test_phones_when_wanted(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Test that phones can be included."""
    phone = _device(hass, "Handy")
    _register(hass, "sensor.handy_batterie", "mobile_app", phone)
    _set_level(hass, "10", "sensor.handy_batterie")
    store = await _setup(setup_entry, battery_phones=True)
    assert len(_tasks(store, f"device:{phone}")) == 1


async def test_sensors_reporting_together_make_one_task(
    hass: HomeAssistant, setup_entry: SetupEntry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that sensors of one device reporting at once add a single task."""
    original = BrainstormStore.async_add_idea

    async def slow_add(self: BrainstormStore, *args: Any, **kwargs: Any) -> Any:
        # Saving yields to the event loop, which let every sensor add a task
        await asyncio.sleep(0)
        return await original(self, *args, **kwargs)

    monkeypatch.setattr(BrainstormStore, "async_add_idea", slow_add)
    device = _device(hass, "Bewässerung")
    sensors = [f"sensor.bewaesserung_batterie_{index}" for index in range(4)]
    for entity_id in sensors:
        _register(hass, entity_id, "battery_notes", device)
    store = await _setup(setup_entry)
    for entity_id in sensors:
        _set_level(hass, "5", entity_id)
    await hass.async_block_till_done()
    assert len(_tasks(store, f"device:{device}")) == 1


async def test_duplicate_tasks_are_closed_at_start(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that duplicates from older versions are closed, keeping the oldest."""
    _set_level(hass, "5")
    ideas = [
        {
            "id": f"dup{index}",
            "text": "Batterie wechseln: Bewegungsmelder Flur (5 %)",
            "category": "Smarthome",
            "priority": "medium",
            "source": "battery",
            "tags": [],
            "status": "active",
            "parent_id": None,
            "order": index,
            "created_at": f"2026-11-15T22:40:17.41{index}+01:00",
            "updated_at": f"2026-11-15T22:40:17.41{index}+01:00",
            "battery": SENSOR,
        }
        for index in range(3)
    ]
    entry = await setup_entry(
        stored={"ideas": ideas, "categories": ["Inbox", "Smarthome"]},
        options=OPTIONS,
    )
    store: BrainstormStore = entry.runtime_data
    await hass.async_block_till_done()
    tasks = {idea["id"]: idea for idea in _tasks(store)}
    assert len(tasks) == 3
    assert tasks["dup0"]["status"] == "active"
    assert not tasks["dup0"].get("battery_done")
    for key in ("dup1", "dup2"):
        assert tasks[key]["status"] == "completed"
        assert tasks[key]["battery_done"] is True


async def test_single_wrong_level_makes_no_task(
    hass: HomeAssistant, setup_entry: SetupEntry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that a single low report between good ones is ignored.

    A door contact reported 40 % every hour and now and then 17 %, which
    added a task and closed it again an hour later, several times a day.
    """
    monkeypatch.setattr(
        "custom_components.brainstorm.battery.CONFIRM_DELAY", timedelta(hours=3)
    )
    _set_level(hass, "40")
    store = await _setup(setup_entry)
    start = dt_util.utcnow()
    for hours in range(0, 12, 2):
        _set_level(hass, "17")
        async_fire_time_changed(hass, start + timedelta(hours=hours, minutes=1))
        await hass.async_block_till_done()
        _set_level(hass, "40")
        async_fire_time_changed(hass, start + timedelta(hours=hours + 1))
        await hass.async_block_till_done()
    async_fire_time_changed(hass, start + timedelta(hours=20))
    await hass.async_block_till_done()
    assert _tasks(store) == []


async def test_battery_low_for_hours_gets_a_task(
    hass: HomeAssistant, setup_entry: SetupEntry, freezer: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that a battery staying low gets its task once the wait is over."""
    monkeypatch.setattr(
        "custom_components.brainstorm.battery.CONFIRM_DELAY", timedelta(hours=3)
    )
    store = await _setup(setup_entry)
    _set_level(hass, "18")
    await hass.async_block_till_done()
    freezer.tick(timedelta(hours=1))
    _set_level(hass, "unavailable")
    _set_level(hass, "16")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert _tasks(store) == []

    freezer.tick(timedelta(hours=2, minutes=1))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    tasks = _tasks(store)
    assert len(tasks) == 1
    assert tasks[0]["text"] == "Batterie wechseln: Bewegungsmelder Flur (16 %)"

    # A new battery still ticks the task off at once
    _set_level(hass, "100")
    await hass.async_block_till_done()
    assert _tasks(store)[0]["status"] == "completed"


async def test_low_at_start_waits_too(
    hass: HomeAssistant, setup_entry: SetupEntry, freezer: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that a battery low at start waits, and the wait ends on unload."""
    monkeypatch.setattr(
        "custom_components.brainstorm.battery.CONFIRM_DELAY", timedelta(hours=3)
    )
    _set_level(hass, "5")
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox", "Smarthome"]}, options=OPTIONS
    )
    store: BrainstormStore = entry.runtime_data
    assert _tasks(store) == []
    await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    freezer.tick(timedelta(hours=4))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert _tasks(store) == []


async def test_weak_flag_alone_does_not_tick_off_a_level_device(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a weak flag saying "off" is no new battery while the level is gone.

    A water leak sensor at 0 % went offline now and then; its weak flag came
    back first and said "off" before the level was known again.
    """
    device = _device(hass, "Wassermelder")
    _register(hass, "sensor.wasser_batterie", "mqtt", device)
    _register(hass, "binary_sensor.wasser_batterie_low", "mqtt", device)
    store = await _setup(setup_entry)
    key = f"device:{device}"
    _set_level(hass, "0", "sensor.wasser_batterie")
    hass.states.async_set(
        "binary_sensor.wasser_batterie_low", "off", {"device_class": "battery"}
    )
    await hass.async_block_till_done()
    assert _tasks(store, key)[0]["status"] == "active"

    # Radio gap: everything unknown, then the flag returns first
    _set_level(hass, "unknown", "sensor.wasser_batterie")
    hass.states.async_set(
        "binary_sensor.wasser_batterie_low", "unknown", {"device_class": "battery"}
    )
    await hass.async_block_till_done()
    hass.states.async_set(
        "binary_sensor.wasser_batterie_low", "off", {"device_class": "battery"}
    )
    await hass.async_block_till_done()
    assert _tasks(store, key)[0]["status"] == "active"

    # Only a good level means a new battery
    _set_level(hass, "100", "sensor.wasser_batterie")
    await hass.async_block_till_done()
    assert _tasks(store, key)[0]["status"] == "completed"


async def test_level_taking_turns_does_not_tick_off_the_task(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    freezer: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that one good report is no new battery (v1.30.3).

    An Aqara door contact took turns at 19 % and 42 %: its task was made after
    three hours low and ticked off 25 minutes later by the next 42 %.
    """
    monkeypatch.setattr(
        "custom_components.brainstorm.battery.CONFIRM_DELAY", timedelta(hours=3)
    )
    store = await _setup(setup_entry)
    _set_level(hass, "19")
    await hass.async_block_till_done()
    freezer.tick(timedelta(hours=3, minutes=1))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert _tasks(store)[0]["status"] == "active"

    for _round in range(3):
        freezer.tick(timedelta(minutes=25))
        _set_level(hass, "42")
        async_fire_time_changed(hass)
        await hass.async_block_till_done()
        assert _tasks(store)[0]["status"] == "active"
        freezer.tick(timedelta(hours=2, minutes=30))
        _set_level(hass, "19")
        async_fire_time_changed(hass)
        await hass.async_block_till_done()
        assert _tasks(store)[0]["status"] == "active"
        assert "battery_done" not in _tasks(store)[0]

    # The wait of a good level is gone as soon as it is low again
    freezer.tick(timedelta(hours=4))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert _tasks(store)[0]["status"] == "active"


async def test_good_level_lasting_ticks_off_after_the_wait(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    freezer: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that a battery reporting less than full ticks off once it stays good."""
    monkeypatch.setattr(
        "custom_components.brainstorm.battery.CONFIRM_DELAY", timedelta(hours=3)
    )
    _set_level(hass, "10")
    store = await _setup(setup_entry)
    freezer.tick(timedelta(hours=3, minutes=1))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert _tasks(store)[0]["status"] == "active"

    _set_level(hass, "65")
    await hass.async_block_till_done()
    assert _tasks(store)[0]["status"] == "active"
    freezer.tick(timedelta(hours=1))
    _set_level(hass, "64")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert _tasks(store)[0]["status"] == "active"

    freezer.tick(timedelta(hours=2, minutes=1))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert _tasks(store)[0]["status"] == "completed"
    assert _tasks(store)[0]["battery_done"] is True


async def test_good_level_wait_ends_on_unload(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    freezer: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that the wait of a good level does not outlive the entry."""
    monkeypatch.setattr(
        "custom_components.brainstorm.battery.CONFIRM_DELAY", timedelta(hours=3)
    )
    _set_level(hass, "10")
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox", "Smarthome"]}, options=OPTIONS
    )
    store: BrainstormStore = entry.runtime_data
    freezer.tick(timedelta(hours=3, minutes=1))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    _set_level(hass, "60")
    await hass.async_block_till_done()
    await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    freezer.tick(timedelta(hours=4))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert _tasks(store)[0]["status"] == "active"


async def test_good_wait_starts_when_the_flag_clears(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    freezer: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that an old good level beside a weak flag does not end the wait at once."""
    monkeypatch.setattr(
        "custom_components.brainstorm.battery.CONFIRM_DELAY", timedelta(hours=3)
    )
    device = _device(hass, "Fenster")
    _register(hass, "sensor.fenster_level", "mqtt", device)
    _register(hass, "binary_sensor.fenster_low", "mqtt", device)
    key = f"device:{device}"
    _set_level(hass, "60", "sensor.fenster_level")
    freezer.tick(timedelta(days=2))
    store = await _setup(setup_entry)
    hass.states.async_set("binary_sensor.fenster_low", "on", {"device_class": "battery"})
    await hass.async_block_till_done()
    freezer.tick(timedelta(hours=3, minutes=1))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert _tasks(store, key)[0]["status"] == "active"

    hass.states.async_set("binary_sensor.fenster_low", "off", {"device_class": "battery"})
    await hass.async_block_till_done()
    assert _tasks(store, key)[0]["status"] == "active"
    freezer.tick(timedelta(hours=3, minutes=1))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert _tasks(store, key)[0]["status"] == "completed"


async def test_level_back_in_the_gap_restarts_the_wait(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    freezer: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that a level between the threshold and the margin ends the good wait."""
    monkeypatch.setattr(
        "custom_components.brainstorm.battery.CONFIRM_DELAY", timedelta(hours=3)
    )
    _set_level(hass, "10")
    store = await _setup(setup_entry)
    freezer.tick(timedelta(hours=3, minutes=1))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    _set_level(hass, "42")
    await hass.async_block_till_done()
    freezer.tick(timedelta(minutes=30))
    _set_level(hass, "25")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    freezer.tick(timedelta(hours=4, minutes=30))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    _set_level(hass, "42")
    await hass.async_block_till_done()
    assert _tasks(store)[0]["status"] == "active"
