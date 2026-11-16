"""Tests for handing Brainstorm tasks over to ChoreOps."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pytest

from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.brainstorm.choreops import match_user, parse_points, rule_points
from custom_components.brainstorm.const import DOMAIN
from custom_components.brainstorm.store import BrainstormStore

from .conftest import SetupEntry


def _choreops_user(hass: HomeAssistant, name: str) -> None:
    """Add the points sensor ChoreOps has for every person."""
    entry = er.async_get(hass).async_get_or_create(
        "sensor", "choreops", f"entry1_{name.lower()}_points"
    )
    hass.states.async_set(entry.entity_id, "12", {"user_name": name})


def _fake_choreops(hass: HomeAssistant, chore_id: str = "ch1") -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []

    async def create(call: ServiceCall) -> dict[str, Any]:
        calls.append(dict(call.data))
        return {"id": chore_id}

    hass.services.async_register(
        "choreops", "create_chore", create, supports_response=SupportsResponse.OPTIONAL
    )
    return calls


async def _status_sensor(hass: HomeAssistant, chore_id: str = "ch1") -> str:
    entry = er.async_get(hass).async_get_or_create(
        "sensor", "choreops", f"entry1_lenja_{chore_id}_chore_status"
    )
    # The bridge reads new sensors a moment after ChoreOps adds them
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=5))
    await hass.async_block_till_done()
    return entry.entity_id


async def _setup(setup_entry: SetupEntry) -> BrainstormStore:
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox", "Haushalt"]})
    return entry.runtime_data


def test_match_user() -> None:
    """Test that a person is found by name or a unique first name."""
    users = ["Jan", "Jonathan", "Lenja Müller"]
    assert match_user("lenja müller", users) == "Lenja Müller"
    assert match_user("Lenja", users) == "Lenja Müller"
    assert match_user("Jan Meier", users) == "Jan"
    assert match_user("Anna", users) is None
    assert match_user(None, users) is None


async def test_hand_over_and_approve(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Test the whole way: hand over, report done, turned down, approved."""
    store = await _setup(setup_entry)
    _choreops_user(hass, "Lenja")
    _choreops_user(hass, "Jonathan")
    calls = _fake_choreops(hass)
    idea = await store.async_add_idea(
        "Spülmaschine ausräumen", category="Haushalt", assignee="lenja"
    )
    response = await hass.services.async_call(
        DOMAIN,
        "send_to_choreops",
        {"id": idea["id"], "points": 20},
        blocking=True,
        return_response=True,
    )
    assert response == {"chore_id": "ch1", "user": "Lenja"}
    assert calls[0]["name"] == "Spülmaschine ausräumen"
    assert calls[0]["assigned_user_names"] == ["Lenja"]
    assert calls[0]["points"] == 20
    assert calls[0]["frequency"] == "none"
    assert store.get_idea(idea["id"])["choreops"]["status"] == "open"

    overview = store.get_overview_attributes()
    assert overview["choreops"] == {
        "users": ["Jonathan", "Lenja"],
        "points": 10,
        "rewards": False,
        "ai": False,
    }
    shown = next(i for i in overview["ideas"] if i["id"] == idea["id"])
    assert shown["choreops"] == {"user": "Lenja", "points": 20, "status": "open"}

    status = await _status_sensor(hass)
    hass.states.async_set(status, "pending", {"user_name": "Lenja"})
    await hass.async_block_till_done()
    assert store.get_idea(idea["id"])["choreops"]["status"] == "open"

    hass.states.async_set(status, "claimed", {"user_name": "Lenja"})
    await hass.async_block_till_done()
    assert store.get_idea(idea["id"])["choreops"]["status"] == "claimed"
    assert store.get_idea(idea["id"])["choreops"]["done_by"] == "Lenja"

    hass.states.async_set(status, "pending", {"user_name": "Lenja"})
    await hass.async_block_till_done()
    assert store.get_idea(idea["id"])["choreops"]["status"] == "open"

    # An approval from before the hand-over belongs to an older chore
    old = (dt_util.utcnow() - timedelta(days=3)).isoformat()
    hass.states.async_set(status, "completed", {"user_name": "Lenja", "last_approved": old})
    await hass.async_block_till_done()
    assert store.get_idea(idea["id"])["status"] != "completed"

    now = (dt_util.utcnow() + timedelta(seconds=1)).isoformat()
    hass.states.async_set(
        status,
        "approved",
        {"user_name": "Lenja", "last_approved": now, "chore_points_earned": 20},
    )
    await hass.async_block_till_done()
    done = store.get_idea(idea["id"])
    assert done["status"] == "completed"
    assert done["choreops"]["status"] == "approved"
    assert done["choreops"]["points_earned"] == 20


async def test_refusals(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Test what cannot be handed over."""
    store = await _setup(setup_entry)
    idea = await store.async_add_idea("Rasen mähen", assignee="Anna")
    with pytest.raises(ServiceValidationError) as err:
        await hass.services.async_call(
            DOMAIN, "send_to_choreops", {"id": idea["id"]}, blocking=True
        )
    assert err.value.translation_key == "choreops_missing"
    assert store.get_overview_attributes()["choreops"] is None

    _choreops_user(hass, "Lenja")
    _fake_choreops(hass)
    with pytest.raises(ServiceValidationError) as err:
        await hass.services.async_call(
            DOMAIN, "send_to_choreops", {"id": idea["id"]}, blocking=True
        )
    assert err.value.translation_key == "choreops_no_user"

    await hass.services.async_call(
        DOMAIN, "send_to_choreops", {"id": idea["id"], "user": "Lenja"}, blocking=True
    )
    with pytest.raises(ServiceValidationError) as err:
        await hass.services.async_call(
            DOMAIN, "send_to_choreops", {"id": idea["id"], "user": "Lenja"}, blocking=True
        )
    assert err.value.translation_key == "choreops_already"
    assert "choreops" not in store.export_json()["ideas"][0]


async def test_approved_while_off(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Test that an approval Brainstorm missed is caught up at the start."""
    since = (dt_util.utcnow() - timedelta(hours=2)).isoformat()
    later = (dt_util.utcnow() - timedelta(hours=1)).isoformat()
    registry = er.async_get(hass)
    entry = registry.async_get_or_create("sensor", "choreops", "entry1_lenja_ch9_chore_status")
    hass.states.async_set(
        entry.entity_id, "completed", {"user_name": "Lenja", "last_approved": later}
    )
    idea = {
        "id": "a1",
        "text": "Zimmer aufräumen",
        "category": "Inbox",
        "status": "active",
        "priority": "medium",
        "created_at": since,
        "choreops": {"chore_id": "ch9", "user": "Lenja", "points": 5, "status": "open", "since": since},
    }
    stored = await setup_entry(stored={"ideas": [idea], "categories": ["Inbox"]})
    await hass.async_block_till_done()
    assert stored.runtime_data.get_idea("a1")["status"] == "completed"


async def test_settings_page(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Test the ChoreOps page under connected integrations."""
    _choreops_user(hass, "Lenja")
    calls = _fake_choreops(hass)
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox"]})
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert "integrations" in result["menu_options"]
    # The menu shows a green dot for ChoreOps, as it is switched on, no logos
    placeholders = result["description_placeholders"]
    assert "logos" not in placeholders
    assert placeholders["integrations_status"] == "🟢 ChoreOps · ⚪ Lokale To-do"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "integrations"}
    )
    assert "choreops" in result["menu_options"]
    assert "bring" not in result["menu_options"]
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "choreops"}
    )
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"choreops_enabled": True, "choreops_points": 25}
    )
    assert result["step_id"] == "integrations"
    await hass.async_block_till_done()
    store = entry.runtime_data
    assert store.get_overview_attributes()["choreops"]["points"] == 25

    # Without points the action takes the default from the settings
    idea = await store.async_add_idea("Rasen mähen", assignee="Lenja")
    await hass.services.async_call(
        DOMAIN, "send_to_choreops", {"id": idea["id"]}, blocking=True
    )
    assert calls[0]["points"] == 25

    hass.config_entries.async_update_entry(
        entry, options={**entry.options, "choreops_enabled": False}
    )
    await hass.async_block_till_done()
    store = entry.runtime_data
    assert store.get_overview_attributes()["choreops"] is None
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["description_placeholders"]["integrations_status"] == (
        "⚪ ChoreOps · ⚪ Lokale To-do"
    )
    hass.config_entries.options.async_abort(result["flow_id"])
    other = await store.async_add_idea("Laub fegen", assignee="Lenja")
    with pytest.raises(ServiceValidationError) as err:
        await hass.services.async_call(
            DOMAIN, "send_to_choreops", {"id": other["id"]}, blocking=True
        )
    assert err.value.translation_key == "choreops_off"


def _fake_rewards(hass: HomeAssistant) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []

    async def create(call: ServiceCall) -> dict[str, Any]:
        calls.append(dict(call.data))
        return {"id": f"rw{len(calls)}"}

    hass.services.async_register(
        "choreops", "create_reward", create, supports_response=SupportsResponse.OPTIONAL
    )
    return calls


async def test_wish_becomes_reward(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Test that a wish becomes a ChoreOps reward, once."""
    store = await _setup(setup_entry)
    _choreops_user(hass, "Lenja")
    _choreops_user(hass, "Jonathan")
    _fake_choreops(hass)
    calls = _fake_rewards(hass)
    wish = await store.async_add_idea(
        "Kino mit Popcorn", category="Haushalt", description="Freitagabend"
    )
    response = await hass.services.async_call(
        DOMAIN,
        "send_reward_to_choreops",
        {"id": wish["id"], "cost": 120},
        blocking=True,
        return_response=True,
    )
    assert response == {"reward_id": "rw1", "cost": 120}
    assert calls[0] == {
        "name": "Kino mit Popcorn",
        "cost": 120,
        "labels": ["brainstorm"],
        "assigned_user_names": ["*"],
        "description": "Freitagabend",
    }
    overview = store.get_overview_attributes()
    assert overview["choreops"]["rewards"] is True
    shown = next(i for i in overview["ideas"] if i["id"] == wish["id"])
    assert shown["choreops_reward"] == {"name": "Kino mit Popcorn", "cost": 120, "users": []}
    # The reward is not part of an export to another Home Assistant
    assert "choreops_reward" not in store.export_json()["ideas"][0]

    with pytest.raises(ServiceValidationError) as err:
        await hass.services.async_call(
            DOMAIN, "send_reward_to_choreops", {"id": wish["id"], "cost": 5}, blocking=True
        )
    assert err.value.translation_key == "choreops_reward_already"

    other = await store.async_add_idea("Eis essen", category="Haushalt")
    await hass.services.async_call(
        DOMAIN,
        "send_reward_to_choreops",
        {"id": other["id"], "cost": 30, "users": ["lenja", "Lenja"], "name": "Eis"},
        blocking=True,
    )
    assert calls[1]["assigned_user_names"] == ["Lenja"]
    assert calls[1]["name"] == "Eis"
    with pytest.raises(ServiceValidationError) as err:
        third = await store.async_add_idea("Zoo", category="Haushalt")
        await hass.services.async_call(
            DOMAIN,
            "send_reward_to_choreops",
            {"id": third["id"], "cost": 30, "users": ["Anna"]},
            blocking=True,
        )
    assert err.value.translation_key == "choreops_no_user"


def test_rule_points_and_parsing() -> None:
    """Test the points without AI and reading the answer of the AI."""
    assert rule_points({"priority": "medium"}, "chore", 10) == 10
    assert rule_points({"priority": "urgent"}, "chore", 10) == 20
    assert rule_points({"priority": "low"}, "chore", 10) == 5
    assert rule_points({"priority": "medium"}, "chore", 10, open_subtasks=2) == 20
    assert rule_points({"priority": "medium"}, "chore", 10, open_subtasks=40) == 40
    assert rule_points({}, "reward", 10) == 50
    assert rule_points({"votes": {"u1": 3, "u2": 1}}, "reward", 10) == 70
    assert rule_points({}, "chore", 2) == 2
    assert parse_points("L1: 15\n- L3 = 40 Punkte\nL9: 5\nL1: 99\nquatsch", 3, 30) == {
        0: 15,
        2: 30,
    }
    assert parse_points(None, 3, 30) == {}


async def test_suggest_points(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_ws_client: WebSocketGenerator
) -> None:
    """Test points from the AI, with the rule for what it leaves out."""
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox", "Haushalt"]})
    store: BrainstormStore = entry.runtime_data
    big = await store.async_add_idea("Keller aufräumen", category="Haushalt", priority="high")
    await store.async_add_idea("Regal", category="Haushalt", parent_id=big["id"])
    small = await store.async_add_idea("Müll rausbringen", category="Haushalt")
    client = await hass_ws_client(hass)

    await client.send_json_auto_id(
        {"type": "brainstorm/choreops/suggest_points", "ids": [big["id"], small["id"], "weg"]}
    )
    reply = await client.receive_json()
    assert reply["result"] == {"points": {big["id"]: 20, small["id"]: 10}, "source": "rule"}

    prompts: list[str] = []

    async def generate(call: ServiceCall) -> dict[str, Any]:
        prompts.append(call.data["instructions"])
        return {"data": "L1: 35"}

    hass.services.async_register(
        "ai_task", "generate_data", generate, supports_response=SupportsResponse.ONLY
    )
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, "ai_entity": "ai_task.test"}
    )
    await hass.async_block_till_done()
    await client.send_json_auto_id(
        {
            "type": "brainstorm/choreops/suggest_points",
            "ids": [big["id"], small["id"]],
            "language": "de",
        }
    )
    reply = await client.receive_json()
    assert reply["result"]["source"] == "ai"
    assert reply["result"]["points"][big["id"]] == 35
    assert reply["result"]["points"][small["id"]] == 10
    assert "L1: Keller aufräumen (Unteraufgaben: 1)" in prompts[0]

    await client.send_json_auto_id(
        {"type": "brainstorm/choreops/suggest_points", "ids": [small["id"]], "kind": "reward"}
    )
    reply = await client.receive_json()
    assert reply["result"]["points"] == {small["id"]: 35}
    assert "ChoreOps" in prompts[1]
