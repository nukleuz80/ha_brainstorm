"""Tests for ChoreOps points in the briefing, streak bonuses, sensor tasks and Assist."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.core import Context, HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import entity_registry as er, llm
from homeassistant.util import dt as dt_util

from custom_components.brainstorm.llm_api import BRAINSTORM_LLM_API_ID
from custom_components.brainstorm.store import BrainstormStore

from .conftest import SetupEntry


def _person(hass: HomeAssistant, name: str, points: str) -> None:
    """Add the points sensor ChoreOps has for every person."""
    entry = er.async_get(hass).async_get_or_create(
        "sensor", "choreops", f"entry1_{name.lower()}_points"
    )
    hass.states.async_set(
        entry.entity_id, points, {"user_name": name, "purpose": "purpose_points"}
    )


def _fake_service(hass: HomeAssistant, service: str, reply: Any = None) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []

    async def handle(call: ServiceCall) -> Any:
        calls.append(dict(call.data))
        return reply

    hass.services.async_register(
        "choreops", service, handle, supports_response=SupportsResponse.OPTIONAL
    )
    return calls


def _days_ago(*offsets: int) -> list[str]:
    today = dt_util.now().date()
    return [(today - timedelta(days=offset)).isoformat() for offset in offsets]


async def test_briefing_names_the_points(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """The daily briefing ends with the points, unless switched off."""
    _person(hass, "Lenja", "120")
    _person(hass, "Jonathan", "80.5")
    _fake_service(hass, "create_chore", {"id": "c1"})
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox"]})
    store: BrainstormStore = entry.runtime_data
    assert store.choreops.points() == {"Jonathan": 80.5, "Lenja": 120.0}
    assert (
        store.reminders.build_digest(dt_util.now())
        == "Punktestand: Jonathan 80.5 und Lenja 120."
    )

    hass.config_entries.async_update_entry(
        entry, options={**entry.options, "choreops_digest": False}
    )
    await hass.async_block_till_done()
    assert entry.runtime_data.reminders.build_digest(dt_util.now()) is None


async def test_streak_bonus_once_per_streak(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """A habit reaching 7 days gives its person bonus points, only once."""
    _person(hass, "Lenja", "10")
    _fake_service(hass, "create_chore", {"id": "c1"})
    calls = _fake_service(hass, "manual_adjust_points")
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox"]},
        options={"choreops_streak_bonus": 5},
    )
    store: BrainstormStore = entry.runtime_data
    idea = await store.async_add_idea("Zähne putzen", assignee="Lenja")
    nobody = await store.async_add_idea("Lesen")
    for habit in (idea, nobody):
        await store.async_update_idea(habit["id"], habit=True)
        store.get_idea(habit["id"])["habit"]["days"] = _days_ago(1, 2, 3, 4, 5, 6)

    await store.async_update_idea(nobody["id"], habit_done=True)
    await store.async_update_idea(idea["id"], habit_done=True)
    await hass.async_block_till_done()
    assert calls == [
        {"user_name": "Lenja", "amount": 5, "reason": "7 Tage Serie: Zähne putzen"}
    ]
    assert len(store.get_idea(idea["id"])["habit_bonus"]) == 1

    # Unticked and ticked again, the milestone was already earned
    await store.async_update_idea(idea["id"], habit_done=False)
    await store.async_update_idea(idea["id"], habit_done=True)
    await hass.async_block_till_done()
    assert len(calls) == 1


async def test_no_bonus_when_switched_off(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Without bonus points nothing is sent to ChoreOps."""
    _person(hass, "Lenja", "10")
    _fake_service(hass, "create_chore", {"id": "c1"})
    calls = _fake_service(hass, "manual_adjust_points")
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox"]})
    store: BrainstormStore = entry.runtime_data
    idea = await store.async_add_idea("Zähne putzen", assignee="Lenja")
    await store.async_update_idea(idea["id"], habit=True)
    store.get_idea(idea["id"])["habit"]["days"] = _days_ago(1, 2, 3, 4, 5, 6)
    await store.async_update_idea(idea["id"], habit_done=True)
    await hass.async_block_till_done()
    assert calls == []


async def test_sensor_task_goes_to_choreops(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """A rule with a ChoreOps person hands its task over right away."""
    _person(hass, "Lenja", "10")
    calls = _fake_service(hass, "create_chore", {"id": "c7"})
    rule = {
        "id": "trash01",
        "sensor_entity": "sensor.muell_fuellstand",
        "sensor_condition": "above",
        "sensor_value": "80",
        "sensor_text": "Müll rausbringen",
        "sensor_category": "Inbox",
        "sensor_auto_done": False,
        "sensor_reset": "",
        "sensor_choreops_user": "lenja",
        "sensor_choreops_points": 15,
    }
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox"]}, options={"sensor_rules": [rule]}
    )
    store: BrainstormStore = entry.runtime_data
    hass.states.async_set("sensor.muell_fuellstand", "90")
    await hass.async_block_till_done()
    task = next(i for i in store.ideas if i.get("sensor_rule") == "trash01")
    assert calls[0]["assigned_user_names"] == ["Lenja"]
    assert calls[0]["points"] == 15
    assert task["choreops"]["chore_id"] == "c7"


async def test_sensor_task_stays_when_hand_over_fails(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """An unknown person only costs the chore, the task is still created."""
    _person(hass, "Lenja", "10")
    calls = _fake_service(hass, "create_chore", {"id": "c7"})
    rule = {
        "id": "trash01",
        "sensor_entity": "sensor.muell_fuellstand",
        "sensor_condition": "above",
        "sensor_value": "80",
        "sensor_text": "Müll rausbringen",
        "sensor_category": "Inbox",
        "sensor_choreops_user": "Niemand",
    }
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox"]}, options={"sensor_rules": [rule]}
    )
    hass.states.async_set("sensor.muell_fuellstand", "90")
    await hass.async_block_till_done()
    task = next(i for i in entry.runtime_data.ideas if i.get("sensor_rule") == "trash01")
    assert "choreops" not in task
    assert calls == []


async def test_settings_forms(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """The ChoreOps page and a sensor rule take the new fields."""
    _person(hass, "Lenja", "10")
    _fake_service(hass, "create_chore", {"id": "c1"})
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox"]})
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "integrations"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "choreops"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "choreops_enabled": True,
            "choreops_points": 10,
            "choreops_digest": False,
            "choreops_streak_bonus": 20,
        },
    )
    await hass.async_block_till_done()
    assert entry.options["choreops_digest"] is False
    assert entry.options["choreops_streak_bonus"] == 20
    assert entry.runtime_data.choreops.streak_bonus == 20

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "sensor_rules"}
    )
    result = await hass.config_entries.options.async_configure(result["flow_id"], {})
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "sensor_rule_edit"
    fields = {str(key): key for key in result["data_schema"].schema}
    assert "sensor_choreops_user" in fields
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "sensor_entity": "sensor.muell_fuellstand",
            "sensor_condition": "above",
            "sensor_value": "80",
            "sensor_text": "Müll rausbringen",
            "sensor_category": "Inbox",
            "sensor_auto_done": True,
            "sensor_choreops_user": "Lenja",
            "sensor_choreops_points": 15,
        },
    )
    await hass.async_block_till_done()
    rule = entry.options["sensor_rules"][0]
    assert rule["sensor_choreops_user"] == "Lenja"
    assert rule["sensor_choreops_points"] == 15


async def test_assist_tool(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Assist tells the points and the open chores, only with ChoreOps."""
    _person(hass, "Lenja", "120")
    _person(hass, "Jonathan", "80")
    _fake_service(hass, "create_chore", {"id": "c1"})
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox"]})
    store: BrainstormStore = entry.runtime_data
    idea = await store.async_add_idea("Rasen mähen", assignee="Lenja")
    await hass.services.async_call(
        "brainstorm", "send_to_choreops", {"id": idea["id"], "points": 30}, blocking=True
    )
    context = llm.LLMContext(
        platform="test",
        context=Context(),
        language="de",
        assistant=None,
        device_id=None,
    )
    api = await llm.async_get_api(hass, BRAINSTORM_LLM_API_ID, context)
    assert "brainstorm_choreops_status" in api.api_prompt
    result = await api.async_call_tool(
        llm.ToolInput(tool_name="brainstorm_choreops_status", tool_args={})
    )
    assert result.data["points"] == {"Jonathan": 80.0, "Lenja": 120.0}
    assert result.data["open_chores"] == [
        {"id": idea["id"], "text": "Rasen mähen", "user": "Lenja", "points": 30, "status": "open"}
    ]
    result = await api.async_call_tool(
        llm.ToolInput(tool_name="brainstorm_choreops_status", tool_args={"person": "jonathan"})
    )
    assert result.data == {"points": {"Jonathan": 80.0}, "open_chores": []}

    hass.config_entries.async_update_entry(
        entry, options={**entry.options, "choreops_enabled": False}
    )
    await hass.async_block_till_done()
    api = await llm.async_get_api(hass, BRAINSTORM_LLM_API_ID, context)
    assert "brainstorm_choreops_status" not in [tool.name for tool in api.tools]
