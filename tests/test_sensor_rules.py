"""Tests for tasks that a sensor creates."""

from __future__ import annotations

from typing import Any

import pytest

from homeassistant.core import HomeAssistant, State
from homeassistant.data_entry_flow import FlowResultType

from custom_components.brainstorm.sensor_rules import rule_met
from custom_components.brainstorm.store import BrainstormStore

from .conftest import SetupEntry

FILTER = "sensor.wasserfilter_betriebsstunden"
WASHER = "sensor.waschmaschine_status"
FILTER_RULE = {
    "id": "filter01",
    "sensor_entity": FILTER,
    "sensor_condition": "above",
    "sensor_value": "300",
    "sensor_text": "Wasserfilter wechseln",
    "sensor_category": "Smarthome",
    "sensor_auto_done": True,
    "sensor_reset": "0",
}
WASHER_RULE = {
    "id": "washer01",
    "sensor_entity": WASHER,
    "sensor_condition": "state",
    "sensor_value": "Fertig",
    "sensor_text": "Waschmaschine ausräumen",
    "sensor_category": "Alltag",
    "sensor_auto_done": True,
    "sensor_reset": "",
}


def _set_hours(hass: HomeAssistant, hours: str) -> None:
    hass.states.async_set(
        FILTER,
        hours,
        {"unit_of_measurement": "h", "friendly_name": "Wasserfilter Betriebsstunden"},
    )


def _tasks(store: BrainstormStore, rule_id: str = "filter01") -> list[dict[str, Any]]:
    return [idea for idea in store.ideas if idea.get("sensor_rule") == rule_id]


async def _setup(setup_entry: SetupEntry, *rules: dict[str, Any]) -> BrainstormStore:
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox", "Smarthome", "Alltag"]},
        options={"sensor_rules": list(rules or [FILTER_RULE])},
    )
    return entry.runtime_data


async def test_limit_creates_one_task_and_the_reset_ticks_it_off(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the whole life of a task from a counter that is reset."""
    _set_hours(hass, "120")
    store = await _setup(setup_entry)
    assert _tasks(store) == []

    _set_hours(hass, "300")
    await hass.async_block_till_done()
    _set_hours(hass, "310")
    await hass.async_block_till_done()
    tasks = _tasks(store)
    assert len(tasks) == 1
    assert tasks[0]["text"] == "Wasserfilter wechseln"
    assert tasks[0]["category"] == "Smarthome"
    assert tasks[0]["source"] == "sensor"
    assert tasks[0]["device"] == "Wasserfilter Betriebsstunden"
    assert tasks[0]["description"] == "Ausgelöst von Wasserfilter Betriebsstunden: 300 h"

    # Below the limit but above the reset value is still the old filter
    _set_hours(hass, "150")
    await hass.async_block_till_done()
    assert _tasks(store)[0]["status"] == "active"

    _set_hours(hass, "0")
    await hass.async_block_till_done()
    assert _tasks(store)[0]["status"] == "completed"
    assert _tasks(store)[0]["sensor_rule_done"] is True

    _set_hours(hass, "301")
    await hass.async_block_till_done()
    assert sorted(task["status"] for task in _tasks(store)) == ["active", "completed"]


async def test_state_rule_and_start_check(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test a rule on a state, already met when Home Assistant starts."""
    hass.states.async_set(WASHER, "fertig", {"friendly_name": "Waschmaschine"})
    store = await _setup(setup_entry, WASHER_RULE)
    tasks = _tasks(store, "washer01")
    assert len(tasks) == 1
    assert tasks[0]["category"] == "Alltag"
    hass.states.async_set(WASHER, "Aus", {"friendly_name": "Waschmaschine"})
    await hass.async_block_till_done()
    assert _tasks(store, "washer01")[0]["status"] == "completed"


async def test_ticked_off_by_hand_comes_back_only_after_normal(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a task ticked off early is not created again at once."""
    _set_hours(hass, "320")
    store = await _setup(setup_entry)
    await store.async_update_idea(_tasks(store)[0]["id"], status="completed")
    _set_hours(hass, "330")
    await hass.async_block_till_done()
    assert len(_tasks(store)) == 1
    _set_hours(hass, "0")
    await hass.async_block_till_done()
    _set_hours(hass, "305")
    await hass.async_block_till_done()
    assert len(_tasks(store)) == 2


async def test_without_auto_done_the_task_stays_and_is_not_doubled(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test a rule that leaves ticking off to people."""
    _set_hours(hass, "400")
    store = await _setup(setup_entry, {**FILTER_RULE, "sensor_auto_done": False})
    _set_hours(hass, "0")
    await hass.async_block_till_done()
    assert _tasks(store)[0]["status"] == "active"
    # The open task still stands for the new occurrence
    _set_hours(hass, "350")
    await hass.async_block_till_done()
    assert len(_tasks(store)) == 1


async def test_deleted_rule_closes_its_case(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a task whose rule is gone is left alone, but closed."""
    _set_hours(hass, "400")
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox", "Smarthome"]},
        options={"sensor_rules": [FILTER_RULE]},
    )
    hass.config_entries.async_update_entry(entry, options={"sensor_rules": []})
    await hass.async_block_till_done()
    task = _tasks(entry.runtime_data)[0]
    assert task["status"] == "active"
    assert task["sensor_rule_done"] is True


@pytest.mark.parametrize(
    ("rule", "value", "expected"),
    [
        ({"sensor_condition": "above", "sensor_value": "10,5"}, "10.5", True),
        ({"sensor_condition": "above", "sensor_value": "10"}, "9", False),
        ({"sensor_condition": "above", "sensor_value": "10", "sensor_reset": "5"}, "7", None),
        ({"sensor_condition": "below", "sensor_value": "20"}, "20", True),
        ({"sensor_condition": "below", "sensor_value": "20", "sensor_reset": "30"}, "25", None),
        ({"sensor_condition": "below", "sensor_value": "20", "sensor_reset": "30"}, "30", False),
        ({"sensor_condition": "below", "sensor_value": "20"}, "unavailable", None),
        ({"sensor_condition": "below", "sensor_value": "20"}, "on", None),
        ({"sensor_condition": "state", "sensor_value": "on"}, "on", True),
        ({"sensor_condition": "state", "sensor_value": "on"}, "off", False),
    ],
)
def test_rule_met(rule: dict[str, Any], value: str, expected: bool | None) -> None:
    """Test the conditions, the reset value and unclear states."""
    assert rule_met(rule, State("sensor.x", value)) is expected


async def test_options_add_change_and_delete_a_rule(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the settings pages of the rules."""
    _set_hours(hass, "10")
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox", "Smarthome"]})
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert "sensor_rules" in result["menu_options"]
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "sensor_rules"}
    )
    assert result["step_id"] == "sensor_rules"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"sensor_rule": "new"}
    )
    assert result["step_id"] == "sensor_rule_edit"
    fields = {str(key) for key in result["data_schema"].schema}
    assert "sensor_delete" not in fields

    form = {
        "sensor_entity": FILTER,
        "sensor_condition": "above",
        "sensor_value": "dreihundert",
        "sensor_text": " ",
        "sensor_category": "Wartung",
        "sensor_auto_done": True,
        "sensor_reset": "",
    }
    result = await hass.config_entries.options.async_configure(result["flow_id"], form)
    assert result["errors"] == {
        "sensor_text": "sensor_text_missing",
        "sensor_value": "sensor_value_number",
    }
    form.update(sensor_value="300", sensor_text="Filter wechseln", sensor_reset="400")
    result = await hass.config_entries.options.async_configure(result["flow_id"], form)
    assert result["errors"] == {"sensor_reset": "sensor_reset_invalid"}
    form.update(sensor_reset="0")
    result = await hass.config_entries.options.async_configure(result["flow_id"], form)
    await hass.async_block_till_done()
    assert result["step_id"] == "sensor_rules"
    rules = entry.options["sensor_rules"]
    assert len(rules) == 1
    rule_id = rules[0]["id"]
    assert rules[0]["sensor_text"] == "Filter wechseln"
    assert "Wartung" in entry.runtime_data.categories
    assert "Filter wechseln (Wasserfilter Betriebsstunden ≥ 300)" in (
        result["description_placeholders"]["rules"]
    )

    # The new rule works at once
    _set_hours(hass, "300")
    await hass.async_block_till_done()
    assert len(_tasks(entry.runtime_data, rule_id)) == 1

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"sensor_rule": rule_id}
    )
    assert "sensor_delete" in {str(key) for key in result["data_schema"].schema}
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {**form, "sensor_value": "250"}
    )
    await hass.async_block_till_done()
    assert entry.options["sensor_rules"][0]["sensor_value"] == "250"
    assert entry.options["sensor_rules"][0]["id"] == rule_id

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"sensor_rule": rule_id}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {**form, "sensor_delete": True}
    )
    await hass.async_block_till_done()
    assert entry.options["sensor_rules"] == []
