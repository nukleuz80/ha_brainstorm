"""Tests for the shape of a note on the mind map."""

from __future__ import annotations

from typing import Any

import pytest
import voluptuous as vol

from homeassistant.core import HomeAssistant

from .conftest import SetupEntry


async def _update(hass: HomeAssistant, **data: Any) -> None:
    await hass.services.async_call("brainstorm", "update_idea", data, blocking=True)


async def test_set_and_clear_shape(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Test that a note keeps its shape until it is cleared."""
    entry = await setup_entry()
    store = entry.runtime_data
    idea = await store.async_add_idea("Urlaub planen", category="Inbox")
    idea_id = idea["id"]

    await _update(hass, id=idea_id, shape="cloud")
    assert store.get_idea(idea_id)["shape"] == "cloud"

    # Other changes leave it alone
    await _update(hass, id=idea_id, text="Urlaub buchen")
    assert store.get_idea(idea_id)["shape"] == "cloud"

    listed = next(i for i in store.get_overview_attributes()["ideas"] if i["id"] == idea_id)
    assert listed["shape"] == "cloud"
    response = await hass.services.async_call(
        "brainstorm", "get_ideas", {}, blocking=True, return_response=True
    )
    assert next(i for i in response["ideas"] if i["id"] == idea_id)["shape"] == "cloud"

    # Empty and None go back to the look of the map
    await _update(hass, id=idea_id, shape="")
    assert "shape" not in store.get_idea(idea_id)
    await _update(hass, id=idea_id, shape="bubble")
    await _update(hass, id=idea_id, shape=None)
    assert "shape" not in store.get_idea(idea_id)
    listed = next(i for i in store.get_overview_attributes()["ideas"] if i["id"] == idea_id)
    assert "shape" not in listed


async def test_unknown_shape_is_refused(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Test that only the shapes the card can draw are taken."""
    entry = await setup_entry()
    store = entry.runtime_data
    idea = await store.async_add_idea("Formen", category="Inbox")
    with pytest.raises(vol.Invalid):
        await _update(hass, id=idea["id"], shape="star")
    assert "shape" not in store.get_idea(idea["id"])


async def test_import_keeps_known_shapes_only(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a JSON import takes a known shape and drops an unknown one."""
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox"]})
    store = entry.runtime_data
    data = {
        "format": "brainstorm_hub",
        "version": 1,
        "ideas": [
            {"id": "a", "text": "A", "shape": "bubble"},
            {"id": "b", "text": "B", "shape": '"><script>'},
        ],
    }
    await hass.services.async_call(
        "brainstorm", "import_json", {"data": data}, blocking=True, return_response=True
    )
    assert store.get_idea("a")["shape"] == "bubble"
    assert "shape" not in store.get_idea("b")
