"""Tests for notes that are captured a second time."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from custom_components.brainstorm.const import CONF_MERGE_DUPLICATES
from custom_components.brainstorm.store import BrainstormStore

from .conftest import SetupEntry


@pytest.fixture
async def store(hass: HomeAssistant, hass_storage: dict[str, Any]) -> BrainstormStore:
    """Return a loaded store with a shopping category of its own."""
    instance = BrainstormStore(hass, {})
    await instance.async_load()
    await instance.async_set_categories([*instance.categories, "Einkauf"])
    return instance


def _open(store: BrainstormStore, category: str) -> list[str]:
    return [
        i["text"]
        for i in store.get_overview_attributes()["ideas"]
        if i["category"] == category and i["status"] == "active"
    ]


async def test_the_same_note_is_not_added_twice(store: BrainstormStore) -> None:
    """Case, punctuation and tags do not count, the note moves to the top."""
    first = await store.async_add_idea("Milch", category="Einkauf", source="manual")
    await store.async_add_idea("Brot", category="Einkauf", source="manual")

    again = await store.async_add_idea("milch. #bio", category="Einkauf", source="manual")
    assert again["duplicate"] is True
    assert again["id"] == first["id"]
    assert _open(store, "Einkauf").count("Milch") == 1
    assert store.get_idea(first["id"])["order"] < store.get_idea(
        next(i["id"] for i in store.get_overview_attributes()["ideas"] if i["text"] == "Brot")
    )["order"]
    assert "duplicate" not in store.get_idea(first["id"])


async def test_spoken_items_skip_what_is_there(store: BrainstormStore) -> None:
    """Only the new item of 'Butter und Milch' is added."""
    await store.async_add_idea("Milch", category="Einkauf", source="manual")
    added = await store.async_add_idea("Butter und Milch", category="Einkauf")
    assert added["text"] == "Butter"
    assert "duplicate" not in added
    assert sorted(_open(store, "Einkauf")) == ["Butter", "Milch"]


async def test_when_a_note_is_added_anyway(store: BrainstormStore) -> None:
    """Another category, a done note, a subtask or a due date mean a new note."""
    milk = await store.async_add_idea("Milch", category="Einkauf", source="manual")
    other = await store.async_add_idea("Milch", category="Alltag", source="manual")
    assert "duplicate" not in other

    child = await store.async_add_idea(
        "Milch", category="Einkauf", source="manual", parent_id=other["id"]
    )
    assert "duplicate" not in child

    due = await store.async_add_idea(
        "Milch",
        category="Einkauf",
        source="manual",
        due=dt_util.now() + timedelta(days=1),
    )
    assert "duplicate" not in due

    synced = await store.async_add_idea(
        "Milch", category="Einkauf", source="bring", verbatim=True
    )
    assert "duplicate" not in synced

    await store.async_update_idea(milk["id"], status="completed")
    await store.async_update_idea(due["id"], status="completed")
    await store.async_update_idea(synced["id"], status="completed")
    fresh = await store.async_add_idea("Milch", category="Einkauf", source="manual")
    assert "duplicate" not in fresh


async def test_merging_can_be_turned_off(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    """With the option off every note is added."""
    store = BrainstormStore(hass, {CONF_MERGE_DUPLICATES: False})
    await store.async_load()
    await store.async_add_idea("Milch", category="Alltag", source="manual")
    again = await store.async_add_idea("Milch", category="Alltag", source="manual")
    assert "duplicate" not in again
    assert _open(store, "Alltag").count("Milch") == 2


async def test_a_private_note_of_someone_else_is_no_twin(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_admin_user: Any
) -> None:
    """A note the user cannot change is not merged with, it would vanish for them."""
    entry = await setup_entry(
        options={"privacy_enabled": True, "privacy_owner": hass_admin_user.id}
    )
    store = entry.runtime_data
    mine = await store.async_add_idea(
        "Milch", category="Alltag", source="manual", owner=hass_admin_user.id
    )
    theirs = await store.async_add_idea(
        "Milch", category="Alltag", source="manual", owner="someone-else"
    )
    assert theirs["id"] != mine["id"]
    assert "duplicate" not in theirs


async def test_the_service_answers_with_the_twin(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """The card learns from the answer that the note was already there."""
    await setup_entry()
    data = {"text": "Milch", "category": "Alltag", "source": "dashboard"}
    first = await hass.services.async_call(
        "brainstorm", "add_idea", data, blocking=True, return_response=True
    )
    again = await hass.services.async_call(
        "brainstorm", "add_idea", data, blocking=True, return_response=True
    )
    assert again["idea"]["duplicate"] is True
    assert again["idea"]["id"] == first["idea"]["id"]
