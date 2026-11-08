"""Tests for markers and progress of a note, as in MindManager."""

from __future__ import annotations

from typing import Any

import pytest
import voluptuous as vol

from homeassistant.core import HomeAssistant

from .conftest import SetupEntry


async def _update(hass: HomeAssistant, **data: Any) -> None:
    await hass.services.async_call("brainstorm", "update_idea", data, blocking=True)


def _listed(store: Any, idea_id: str) -> dict[str, Any]:
    return next(i for i in store.get_overview_attributes()["ideas"] if i["id"] == idea_id)


async def test_set_and_clear_markers(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Markers are kept once each, in a fixed order, until they are cleared."""
    entry = await setup_entry()
    store = entry.runtime_data
    idea = await store.async_add_idea("Angebot Dach", category="Inbox")
    idea_id = idea["id"]

    await _update(hass, id=idea_id, markers=["money", "question", "money"])
    assert store.get_idea(idea_id)["markers"] == ["question", "money"]
    assert _listed(store, idea_id)["markers"] == ["question", "money"]

    # Other changes leave them alone, a single value is a list of one
    await _update(hass, id=idea_id, text="Angebot Dach prüfen")
    assert store.get_idea(idea_id)["markers"] == ["question", "money"]
    await _update(hass, id=idea_id, markers="star")
    assert store.get_idea(idea_id)["markers"] == ["star"]

    await _update(hass, id=idea_id, markers=[])
    assert "markers" not in store.get_idea(idea_id)
    await _update(hass, id=idea_id, markers=["flag"])
    await _update(hass, id=idea_id, markers=None)
    assert "markers" not in store.get_idea(idea_id)
    assert "markers" not in _listed(store, idea_id)


async def test_unknown_marker_is_refused(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Only markers the cards can show are taken."""
    entry = await setup_entry()
    store = entry.runtime_data
    idea = await store.async_add_idea("Marker", category="Inbox")
    with pytest.raises(vol.Invalid):
        await _update(hass, id=idea["id"], markers=["question", "<b>"])
    assert "markers" not in store.get_idea(idea["id"])


async def test_set_and_clear_progress(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Progress goes in quarters, 0 and None remove it, other values are refused."""
    entry = await setup_entry()
    store = entry.runtime_data
    idea = await store.async_add_idea("Zaun streichen", category="Inbox")
    idea_id = idea["id"]

    await _update(hass, id=idea_id, progress=50)
    assert store.get_idea(idea_id)["progress"] == 50
    assert _listed(store, idea_id)["progress"] == 50
    await _update(hass, id=idea_id, progress="75")
    assert store.get_idea(idea_id)["progress"] == 75

    with pytest.raises(vol.Invalid):
        await _update(hass, id=idea_id, progress=30)
    assert store.get_idea(idea_id)["progress"] == 75

    await _update(hass, id=idea_id, progress=0)
    assert "progress" not in store.get_idea(idea_id)
    await _update(hass, id=idea_id, progress=100)
    await _update(hass, id=idea_id, progress=None)
    assert "progress" not in store.get_idea(idea_id)
    assert "progress" not in _listed(store, idea_id)


async def test_progress_rolls_up_from_subtasks(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """A parent shows done/total of its subtasks and the mean of their progress."""
    entry = await setup_entry()
    store = entry.runtime_data
    root = await store.async_add_idea("Umzug", category="Inbox")
    boxes = await store.async_add_idea("Kartons", category="Inbox", parent_id=root["id"])
    van = await store.async_add_idea("Transporter", category="Inbox", parent_id=root["id"])
    kitchen = await store.async_add_idea("Küche", category="Inbox", parent_id=root["id"])
    plates = await store.async_add_idea("Teller", category="Inbox", parent_id=kitchen["id"])
    await store.async_add_idea("Töpfe", category="Inbox", parent_id=kitchen["id"])
    gone = await store.async_add_idea("Alt", category="Inbox", parent_id=root["id"])
    plain = await store.async_add_idea("Ohne Unteraufgaben", category="Inbox")

    await _update(hass, id=boxes["id"], status="completed")
    await _update(hass, id=van["id"], progress=50)
    await _update(hass, id=plates["id"], status="completed")
    await _update(hass, id=gone["id"], status="archived")

    # Küche: Teller 100, Töpfe 0 -> 50; Umzug: Kartons 100, Transporter 50, Küche 50
    assert _listed(store, kitchen["id"])["subtasks"] == {"done": 1, "total": 2, "percent": 50}
    assert _listed(store, root["id"])["subtasks"] == {"done": 1, "total": 3, "percent": 67}
    assert "subtasks" not in _listed(store, plain["id"])
    assert "subtasks" not in _listed(store, van["id"])

    # Ticking off the parent itself does not change what its subtasks say
    await _update(hass, id=kitchen["id"], status="completed")
    assert _listed(store, root["id"])["subtasks"] == {"done": 2, "total": 3, "percent": 83}


async def test_progress_survives_a_parent_cycle(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Broken stored data with a cycle of parents does not hang the overview."""
    entry = await setup_entry(
        stored={
            "categories": ["Inbox"],
            "ideas": [
                {"id": "a", "text": "A", "category": "Inbox", "status": "active", "parent_id": "b"},
                {"id": "b", "text": "B", "category": "Inbox", "status": "active", "parent_id": "a"},
            ],
        }
    )
    store = entry.runtime_data
    ideas = {i["id"]: i for i in store.get_overview_attributes()["ideas"]}
    assert ideas["a"]["subtasks"]["total"] == 1
    assert ideas["b"]["subtasks"]["total"] == 1


async def test_import_keeps_known_markers_and_progress(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """A JSON import keeps known markers and steps and drops the rest."""
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox"]})
    store = entry.runtime_data
    data = {
        "format": "brainstorm_hub",
        "version": 1,
        "ideas": [
            {"id": "a", "text": "A", "markers": ["money", "nope", "idea"], "progress": 25},
            {"id": "b", "text": "B", "markers": "<script>", "progress": 33},
            {"id": "c", "text": "C", "markers": ["nope"], "progress": True},
        ],
    }
    await hass.services.async_call(
        "brainstorm", "import_json", {"data": data}, blocking=True, return_response=True
    )
    assert store.get_idea("a")["markers"] == ["idea", "money"]
    assert store.get_idea("a")["progress"] == 25
    for idea_id in ("b", "c"):
        assert "markers" not in store.get_idea(idea_id)
        assert "progress" not in store.get_idea(idea_id)
