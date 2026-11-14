"""Tests for repeating ideas whose assignee changes every round."""

from __future__ import annotations

from datetime import timedelta
from typing import Any
from unittest.mock import patch

import pytest
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from custom_components.brainstorm.store import BrainstormStore

from .conftest import SetupEntry

ANNA = "person.anna"
BEN = "person.ben"
CARLA = "person.carla"


def _people(hass: HomeAssistant) -> None:
    for person, user in ((ANNA, "user_anna"), (BEN, "user_ben"), (CARLA, None)):
        attributes = {"user_id": user} if user else {}
        hass.states.async_set(person, "home", attributes)


async def _call(hass: HomeAssistant, **data: Any) -> None:
    await hass.services.async_call("brainstorm", "update_idea", data, blocking=True)


async def _tick_off(store: BrainstormStore, idea_id: str) -> dict[str, Any]:
    """Tick off a round and return the next one."""
    await store.async_update_idea(idea_id, status="completed")
    return store.get_idea(store.get_idea(idea_id)["repeated_as"])


async def _repeating(
    hass: HomeAssistant, store: BrainstormStore, mode: str, people: list[str]
) -> dict[str, Any]:
    idea = await store.async_add_idea("Müll rausbringen", category="Inbox")
    await _call(
        hass, id=idea["id"], repeat="weekly", rotation={"mode": mode, "people": people}
    )
    return store.get_idea(idea["id"])


async def test_taking_turns(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Each round goes to the next person and back to the first."""
    _people(hass)
    entry = await setup_entry()
    store = entry.runtime_data
    idea = await _repeating(hass, store, "turn", [ANNA, BEN, CARLA])
    # The note goes to the first person at once, who may then edit it
    assert idea["assignee"] == ANNA
    assert idea["shares"]["user_anna"] == "edit"
    listed = next(i for i in store.get_overview_attributes()["ideas"] if i["id"] == idea["id"])
    assert listed["rotation"] == {"mode": "turn", "people": [ANNA, BEN, CARLA]}

    second = await _tick_off(store, idea["id"])
    assert second["assignee"] == BEN
    assert second["shares"]["user_ben"] == "edit"
    assert second["rotation"]["mode"] == "turn"
    assert "rotation" not in store.get_idea(idea["id"])
    third = await _tick_off(store, second["id"])
    assert third["assignee"] == CARLA
    fourth = await _tick_off(store, third["id"])
    assert fourth["assignee"] == ANNA


async def test_reopening_gives_the_rotation_back(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Reopening takes the next round back, the turn stays with the person."""
    _people(hass)
    entry = await setup_entry()
    store = entry.runtime_data
    idea = await _repeating(hass, store, "turn", [ANNA, BEN])
    await _tick_off(store, idea["id"])
    await store.async_update_idea(idea["id"], status="active")
    reopened = store.get_idea(idea["id"])
    assert reopened["assignee"] == ANNA
    assert reopened["rotation"]["people"] == [ANNA, BEN]
    assert (await _tick_off(store, idea["id"]))["assignee"] == BEN


async def test_fewest_done_goes_first(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """The person who finished the fewest notes lately gets the next round."""
    _people(hass)
    entry = await setup_entry()
    store = entry.runtime_data
    old = dt_util.now() - timedelta(days=40)
    for text, person in (("Einkauf", BEN), ("Rasen", BEN), ("Alt", CARLA), ("Alt 2", CARLA)):
        done = await store.async_add_idea(text, category="Inbox", assignee=person)
        await store.async_update_idea(done["id"], status="completed")
    # Done long ago, these do not count
    for idea in store.ideas:
        if idea["text"].startswith("Alt"):
            await store.async_set_fields({idea["id"]: {"completed_at": old.isoformat()}})

    idea = await _repeating(hass, store, "fewest", [ANNA, BEN, CARLA])
    # Anna has done this round now, Carla has nothing within 30 days
    nxt = await _tick_off(store, idea["id"])
    assert nxt["assignee"] == CARLA
    # Anna 1, Ben 2, Carla 1: a tie goes to the next in turn after Carla
    assert (await _tick_off(store, nxt["id"]))["assignee"] == ANNA


async def test_random_never_picks_the_same_person(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Random leaves out whoever had the last round."""
    _people(hass)
    entry = await setup_entry()
    store = entry.runtime_data
    idea = await _repeating(hass, store, "random", [ANNA, BEN, CARLA])
    with patch(
        "custom_components.brainstorm.store.random.choice", side_effect=lambda seq: seq[-1]
    ) as choice:
        nxt = await _tick_off(store, idea["id"])
    choice.assert_called_once_with([BEN, CARLA])
    assert nxt["assignee"] == CARLA


async def test_subtasks_and_arrival_reminder_follow(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Subtasks of the person and a reminder on arrival go to the next one."""
    _people(hass)
    entry = await setup_entry()
    store = entry.runtime_data
    idea = await _repeating(hass, store, "turn", [ANNA, BEN])
    await store.async_set_fields(
        {idea["id"]: {"trigger": {"zone": "zone.home", "person": ANNA}}}
    )
    await store.async_add_idea("Tonne raus", parent_id=idea["id"], category="Inbox", assignee=ANNA)
    await store.async_add_idea("Gelber Sack", parent_id=idea["id"], category="Inbox", assignee=CARLA)
    nxt = await _tick_off(store, idea["id"])
    assert nxt["trigger"] == {"zone": "zone.home", "person": BEN}
    children = {i["text"]: i for i in store.ideas if i.get("parent_id") == nxt["id"]}
    assert children["Tonne raus"]["assignee"] == BEN
    assert children["Gelber Sack"]["assignee"] == CARLA
    assert "rotation" not in children["Tonne raus"]


async def test_rotation_is_checked_and_cleared(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Only persons, at least two, and empty ends the rotation."""
    _people(hass)
    entry = await setup_entry()
    store = entry.runtime_data
    idea = await _repeating(hass, store, "turn", [BEN, ANNA])
    for bad in (
        {"mode": "turn", "people": [ANNA]},
        {"mode": "turn", "people": [ANNA, "light.kitchen"]},
        {"mode": "often", "people": [ANNA, BEN]},
    ):
        with pytest.raises(vol.Invalid):
            await _call(hass, id=idea["id"], rotation=bad)
    # A note already with someone of the turn stays with them
    await _call(hass, id=idea["id"], rotation={"mode": "fewest", "people": [ANNA, BEN]})
    assert store.get_idea(idea["id"])["assignee"] == BEN
    await _call(hass, id=idea["id"], rotation=None)
    assert "rotation" not in store.get_idea(idea["id"])
    assert store.get_idea(idea["id"])["assignee"] == BEN
