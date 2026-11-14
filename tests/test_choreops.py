"""Tests for handing Brainstorm tasks over to ChoreOps."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pytest

from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.brainstorm.choreops import match_user
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
    assert overview["choreops"] == {"users": ["Jonathan", "Lenja"]}
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
