"""Tests for links between notes, frames and callouts on the mind map."""

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


async def test_links_are_cleaned(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Links to itself, unknown or repeated targets are dropped, labels are tidied."""
    entry = await setup_entry()
    store = entry.runtime_data
    roof = await store.async_add_idea("Dach decken", category="Inbox")
    offer = await store.async_add_idea("Angebot einholen", category="Inbox")
    paint = await store.async_add_idea("Fassade streichen", category="Inbox")

    await _update(
        hass,
        id=offer["id"],
        links=[
            {"to": roof["id"], "label": "  gehört   zu ", "blocks": True},
            {"to": roof["id"], "label": "doppelt"},
            {"to": offer["id"]},
            {"to": "gibt-es-nicht"},
            {"to": paint["id"], "blocks": False},
        ],
    )
    assert store.get_idea(offer["id"])["links"] == [
        {"to": roof["id"], "label": "gehört zu", "blocks": True},
        {"to": paint["id"]},
    ]
    assert _listed(store, offer["id"])["links"] == store.get_idea(offer["id"])["links"]

    await _update(hass, id=offer["id"], links=[])
    assert "links" not in store.get_idea(offer["id"])
    await _update(hass, id=offer["id"], links=[{"to": paint["id"]}])
    await _update(hass, id=offer["id"], links=None)
    assert "links" not in store.get_idea(offer["id"])


async def test_bad_links_are_refused(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """A link without a target or with a too long label is refused."""
    entry = await setup_entry()
    store = entry.runtime_data
    a = await store.async_add_idea("A", category="Inbox")
    b = await store.async_add_idea("B", category="Inbox")
    with pytest.raises(vol.Invalid):
        await _update(hass, id=a["id"], links=[{"label": "ohne Ziel"}])
    with pytest.raises(vol.Invalid):
        await _update(hass, id=a["id"], links=[{"to": b["id"], "label": "x" * 41}])
    assert "links" not in store.get_idea(a["id"])


async def test_blocking_link_marks_its_target(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """A note waits for open notes that block it, until they are done."""
    entry = await setup_entry()
    store = entry.runtime_data
    offer = await store.async_add_idea("Angebot einholen", category="Inbox")
    order = await store.async_add_idea("Material bestellen", category="Inbox")
    roof = await store.async_add_idea("Dach decken", category="Inbox")
    await _update(hass, id=offer["id"], links=[{"to": roof["id"], "blocks": True}])
    await _update(hass, id=order["id"], links=[{"to": roof["id"], "blocks": True}])

    waits = sorted(_listed(store, roof["id"])["blocked_by"], key=lambda w: w["text"])
    assert waits == [
        {"id": offer["id"], "text": "Angebot einholen"},
        {"id": order["id"], "text": "Material bestellen"},
    ]
    assert "blocked_by" not in _listed(store, offer["id"])

    await _update(hass, id=offer["id"], status="completed")
    assert _listed(store, roof["id"])["blocked_by"] == [
        {"id": order["id"], "text": "Material bestellen"}
    ]
    await store.async_delete_idea(order["id"])
    assert "blocked_by" not in _listed(store, roof["id"])


async def test_link_to_a_deleted_note_is_hidden(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """The cards never get a link to a note that is gone."""
    entry = await setup_entry()
    store = entry.runtime_data
    a = await store.async_add_idea("A", category="Inbox")
    b = await store.async_add_idea("B", category="Inbox")
    await _update(hass, id=a["id"], links=[{"to": b["id"]}])
    await store.async_delete_idea(b["id"])
    assert "links" not in _listed(store, a["id"])


async def test_frame_and_callout(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Frame and callout are one line of text and go away when empty."""
    entry = await setup_entry()
    store = entry.runtime_data
    idea = await store.async_add_idea("Fliesen", category="Inbox")
    idea_id = idea["id"]

    await _update(hass, id=idea_id, frame="  Phase\n1 ", callout="Farbe noch offen")
    assert store.get_idea(idea_id)["frame"] == "Phase 1"
    listed = _listed(store, idea_id)
    assert listed["frame"] == "Phase 1"
    assert listed["callout"] == "Farbe noch offen"

    with pytest.raises(vol.Invalid):
        await _update(hass, id=idea_id, callout="x" * 201)

    await _update(hass, id=idea_id, frame="", callout=None)
    assert "frame" not in store.get_idea(idea_id)
    assert "callout" not in store.get_idea(idea_id)


async def test_import_keeps_links_frames_and_callouts(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """A JSON import keeps links between imported notes and tidies the rest."""
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox"]})
    store = entry.runtime_data
    data = {
        "format": "brainstorm_hub",
        "version": 1,
        "ideas": [
            {
                "id": "a",
                "text": "A",
                "links": [{"to": "b", "label": "vor", "blocks": True}, {"to": "zzz"}],
                "frame": "Gruppe",
                "callout": "Hinweis",
            },
            {"id": "b", "text": "B", "links": "kaputt", "frame": 7, "callout": ""},
        ],
    }
    await hass.services.async_call(
        "brainstorm", "import_json", {"data": data}, blocking=True, return_response=True
    )
    a = store.get_idea("a")
    assert a["links"] == [{"to": "b", "label": "vor", "blocks": True}]
    assert a["frame"] == "Gruppe"
    assert a["callout"] == "Hinweis"
    b = store.get_idea("b")
    for field in ("links", "frame", "callout"):
        assert field not in b
