"""Tests for lock times of single Echos."""

from __future__ import annotations

from datetime import datetime, time, timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_mock_service,
)

from custom_components.brainstorm.echo_locks import in_window, locked_echos

from .conftest import SetupEntry
from .test_reminders import PUSH, _due_idea, _setup

KIDS = "media_player.kinderzimmer"
KITCHEN = "media_player.kuche"


def _lock_now(echos: list[str], dnd: bool = False) -> dict[str, Any]:
    """Return a lock time running right now."""
    now = dt_util.now()
    return {
        "echos": echos,
        "start": (now - timedelta(hours=1)).strftime("%H:%M:00"),
        "end": (now + timedelta(hours=1)).strftime("%H:%M:00"),
        "dnd": dnd,
    }


def _lock_later(echos: list[str]) -> dict[str, Any]:
    """Return a lock time that is not running now."""
    now = dt_util.now()
    return {
        "echos": echos,
        "start": (now + timedelta(hours=2)).strftime("%H:%M:00"),
        "end": (now + timedelta(hours=3)).strftime("%H:%M:00"),
    }


def test_window_spans_midnight() -> None:
    """Test lock windows, also over midnight."""
    day = datetime(2026, 11, 5, 23, 30)
    assert in_window(day, time(21), time(7))
    assert in_window(day.replace(hour=3), time(21), time(7))
    assert not in_window(day.replace(hour=12), time(21), time(7))
    assert in_window(day.replace(hour=12), time(9), time(13))
    assert not in_window(day, time(9), time(9))
    options = {"echo_locks": [{"echos": [KIDS], "start": "21:00:00", "end": "07:00:00"}]}
    assert locked_echos(options, day) == {KIDS}
    assert locked_echos(options, day.replace(hour=12)) == set()


async def test_locked_echo_is_left_out(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that other Echos still speak and the phone waits as usual."""
    entry, alexa, push = await _setup(
        hass,
        setup_entry,
        reminder_alexa="fixed",
        reminder_echos=[KIDS, KITCHEN],
        reminder_notify=[PUSH],
        reminder_delay=15,
        echo_locks=[_lock_now([KIDS]), _lock_later([KITCHEN])],
    )
    await _due_idea(entry)
    await entry.runtime_data.reminders.async_check(dt_util.now())
    await hass.async_block_till_done()
    assert alexa[0].data["target"] == [KITCHEN]
    assert not push


async def test_all_echos_locked_goes_to_phone(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a reminder reaches the phone at once if every Echo is locked."""
    entry, alexa, push = await _setup(
        hass,
        setup_entry,
        reminder_alexa="fixed",
        reminder_echos=[KIDS],
        reminder_notify=[PUSH],
        reminder_delay=15,
        echo_locks=[_lock_now([KIDS])],
    )
    await _due_idea(entry)
    await entry.runtime_data.reminders.async_check(dt_util.now())
    await hass.async_block_till_done()
    assert not alexa
    assert len(push) == 1


async def test_test_message_speaks_in_lock_time(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a test someone starts still speaks."""
    entry, alexa, _ = await _setup(
        hass,
        setup_entry,
        reminder_alexa="fixed",
        reminder_echos=[KIDS],
        echo_locks=[_lock_now([KIDS])],
    )
    results = await entry.runtime_data.reminders.async_send_test()
    assert results[0][1] is True
    assert alexa[0].data["target"] == [KIDS]


def _echo_with_dnd(hass: HomeAssistant) -> str:
    """Register an Echo with its Do not disturb switch, as Alexa Media does."""
    config = MockConfigEntry(domain="alexa_media")
    config.add_to_hass(hass)
    device = dr.async_get(hass).async_get_or_create(
        config_entry_id=config.entry_id, identifiers={("alexa_media", "kids")}
    )
    registry = er.async_get(hass)
    registry.async_get_or_create(
        "media_player", "alexa_media", "kids", suggested_object_id="kinderzimmer",
        device_id=device.id,
    )
    switch = registry.async_get_or_create(
        "switch", "alexa_media", "kids_dnd",
        suggested_object_id="kinderzimmer_do_not_disturb_switch", device_id=device.id,
    )
    return switch.entity_id


async def test_dnd_is_switched_on_in_a_running_lock_time(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that Do not disturb is caught up when a lock time is running."""
    switch = _echo_with_dnd(hass)
    turn_on = async_mock_service(hass, "switch", "turn_on")
    turn_off = async_mock_service(hass, "switch", "turn_off")
    await setup_entry(options={"echo_locks": [_lock_now([KIDS], dnd=True)]})
    assert turn_on[0].data["entity_id"] == [switch]
    assert not turn_off


async def test_no_dnd_without_the_wish(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a lock time without the wish leaves Do not disturb alone."""
    _echo_with_dnd(hass)
    turn_on = async_mock_service(hass, "switch", "turn_on")
    await setup_entry(options={"echo_locks": [_lock_now([KIDS])]})
    assert not turn_on


async def test_options_lock_times(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Test entering, checking and showing lock times."""
    entry = await setup_entry()
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "reminders"}
    )
    assert "reminder_locks" in result["menu_options"]
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "reminder_locks"}
    )
    assert result["type"] is FlowResultType.FORM

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"lock_1_echos": [KIDS], "lock_1_start": "21:00:00"}
    )
    assert result["errors"] == {"lock_1_echos": "lock_time_missing"}

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "lock_1_echos": [KIDS],
            "lock_1_start": "21:00:00",
            "lock_1_end": "07:00:00",
            "lock_1_dnd": True,
            "lock_2_start": "12:00:00",
        },
    )
    assert result["type"] is FlowResultType.MENU
    await hass.async_block_till_done()
    assert entry.options["echo_locks"] == [
        {"echos": [KIDS], "start": "21:00:00", "end": "07:00:00", "dnd": True}
    ]
    assert "21:00–07:00 🔕" in result["description_placeholders"]["status_locks"]

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "reminder_locks"}
    )
    defaults = {
        str(key): key.description["suggested_value"]
        for key in result["data_schema"].schema
        if getattr(key, "description", None)
    }
    assert defaults["lock_1_echos"] == [KIDS]
    assert defaults["lock_1_end"] == "07:00:00"
