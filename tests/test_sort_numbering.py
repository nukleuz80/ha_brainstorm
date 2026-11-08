"""Tests for numbering and sorting the subtasks of a note."""

from __future__ import annotations

from typing import Any

import pytest
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError

from .conftest import SetupEntry


async def _call(hass: HomeAssistant, service: str, **data: Any) -> Any:
    return await hass.services.async_call(
        "brainstorm", service, data, blocking=True, return_response=service == "sort_children"
    )


def _texts(store: Any, parent_id: str | None, category: str = "Inbox") -> list[str]:
    return [i["text"] for i in store.children_of(parent_id, category)]


async def test_numbering_is_set_and_cleared(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Only known styles are taken; empty or None removes the numbering."""
    entry = await setup_entry()
    store = entry.runtime_data
    idea = await store.async_add_idea("Plan", category="Inbox")
    idea_id = idea["id"]

    await _call(hass, "update_idea", id=idea_id, numbering="decimal")
    assert store.get_idea(idea_id)["numbering"] == "decimal"
    listed = next(i for i in store.get_overview_attributes()["ideas"] if i["id"] == idea_id)
    assert listed["numbering"] == "decimal"

    with pytest.raises(vol.Invalid):
        await _call(hass, "update_idea", id=idea_id, numbering="greek")
    assert store.get_idea(idea_id)["numbering"] == "decimal"

    await _call(hass, "update_idea", id=idea_id, numbering="")
    assert "numbering" not in store.get_idea(idea_id)
    await _call(hass, "update_idea", id=idea_id, numbering="roman")
    await _call(hass, "update_idea", id=idea_id, numbering=None)
    assert "numbering" not in store.get_idea(idea_id)


async def test_sort_children_keeps_other_notes_in_place(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Sorting moves only the subtasks, inside the places they already had."""
    entry = await setup_entry()
    store = entry.runtime_data
    other = await store.async_add_idea("Anderes", category="Inbox")
    root = await store.async_add_idea("Umzug", category="Inbox")
    for text, prio in (("Zettel", "low"), ("Auto", "urgent"), ("Miete", "high")):
        await store.async_add_idea(text, category="Inbox", parent_id=root["id"], priority=prio)
    await store.async_reorder_ideas([i["id"] for i in store.ideas])
    before = [i["id"] for i in store.ideas]

    result = await _call(hass, "sort_children", parent_id=root["id"], by="text")
    assert result == {"success": True, "sorted": 3}
    assert _texts(store, root["id"]) == ["Auto", "Miete", "Zettel"]
    after = [i["id"] for i in store.ideas]
    # Notes that are no subtasks keep their index
    for idea_id in (other["id"], root["id"]):
        assert after.index(idea_id) == before.index(idea_id)

    await _call(hass, "sort_children", parent_id=root["id"], by="text", reverse=True)
    assert _texts(store, root["id"]) == ["Zettel", "Miete", "Auto"]
    await _call(hass, "sort_children", parent_id=root["id"], by="priority")
    assert _texts(store, root["id"]) == ["Auto", "Miete", "Zettel"]


async def test_sort_by_due_puts_undated_last(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Notes without a due date stay at the end, also in reverse."""
    entry = await setup_entry()
    store = entry.runtime_data
    root = await store.async_add_idea("Reise", category="Inbox")
    later = await store.async_add_idea("Hotel", category="Inbox", parent_id=root["id"])
    await store.async_add_idea("Koffer", category="Inbox", parent_id=root["id"])
    soon = await store.async_add_idea("Pass", category="Inbox", parent_id=root["id"])
    await _call(hass, "update_idea", id=later["id"], due="2030-05-02T10:00:00+02:00")
    await _call(hass, "update_idea", id=soon["id"], due="2030-04-01T10:00:00+02:00")

    await _call(hass, "sort_children", parent_id=root["id"], by="due")
    assert _texts(store, root["id"]) == ["Pass", "Hotel", "Koffer"]
    await _call(hass, "sort_children", parent_id=root["id"], by="due", reverse=True)
    assert _texts(store, root["id"]) == ["Hotel", "Pass", "Koffer"]


async def test_sort_main_notes_of_a_category(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Without a parent the main notes of the category are sorted, not others."""
    entry = await setup_entry()
    store = entry.runtime_data
    await store.async_add_idea("Birne", category="Inbox")
    apple = await store.async_add_idea("Apfel", category="Inbox")
    await store.async_add_idea("Zwiebel", category="Inbox", parent_id=apple["id"])
    cola = await store.async_add_idea("Cola", category="Alltag")

    await _call(hass, "sort_children", category="Inbox", by="text")
    assert _texts(store, None) == ["Apfel", "Birne"]
    assert cola["category"] != "Inbox"
    assert _texts(store, None, cola["category"]) == ["Cola"]

    with pytest.raises(ServiceValidationError):
        await _call(hass, "sort_children", by="text")
    with pytest.raises(ServiceValidationError):
        await _call(hass, "sort_children", parent_id="gibt-es-nicht", by="text")


async def test_import_keeps_known_numbering(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """A JSON import keeps a known numbering style and drops the rest."""
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox"]})
    store = entry.runtime_data
    data = {
        "format": "brainstorm_hub",
        "version": 1,
        "ideas": [
            {"id": "a", "text": "A", "numbering": "alpha"},
            {"id": "b", "text": "B", "numbering": "<b>"},
        ],
    }
    await hass.services.async_call(
        "brainstorm", "import_json", {"data": data}, blocking=True, return_response=True
    )
    assert store.get_idea("a")["numbering"] == "alpha"
    assert "numbering" not in store.get_idea("b")


async def test_fixed_order_undoes_a_sort(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """A fixed list of IDs brings back an earlier order."""
    entry = await setup_entry()
    store = entry.runtime_data
    root = await store.async_add_idea("Liste", category="Inbox")
    for text in ("C", "A", "B"):
        await store.async_add_idea(text, category="Inbox", parent_id=root["id"])
    before = [i["id"] for i in store.children_of(root["id"])]
    original = _texts(store, root["id"])

    await _call(hass, "sort_children", parent_id=root["id"], by="text")
    assert _texts(store, root["id"]) == ["A", "B", "C"]
    await _call(hass, "sort_children", parent_id=root["id"], ids=before)
    assert _texts(store, root["id"]) == original

    with pytest.raises(ServiceValidationError):
        await _call(hass, "sort_children", parent_id=root["id"])
