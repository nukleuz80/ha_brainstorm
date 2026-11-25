"""Tests for templates: a note with its subtasks to create again and again."""

from __future__ import annotations

from typing import Any

import pytest

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError

from custom_components.brainstorm.languages.de import template_names
from custom_components.brainstorm.languages.en import template_names as template_names_en

from .conftest import SetupEntry


async def _call(hass: HomeAssistant, service: str, **data: Any) -> dict[str, Any]:
    return await hass.services.async_call(
        "brainstorm", service, data, blocking=True, return_response=True
    )


async def _packing_list(store: Any) -> dict[str, Any]:
    root = await store.async_add_idea("Packliste Urlaub", category="Projekte", source="dashboard")
    for text in ("Pass", "Ladekabel", "Sonnencreme"):
        await store.async_add_idea(text, category="Projekte", parent_id=root["id"], source="dashboard")
    cables = next(i for i in store.children_of(root["id"]) if i["text"] == "Ladekabel")
    await store.async_add_idea("USB-C", category="Projekte", parent_id=cables["id"], source="dashboard")
    return root


def _tree(store: Any, idea_id: str) -> list[Any]:
    return [
        (child["text"], _tree(store, child["id"])) if store.children_of(child["id"]) else child["text"]
        for child in store.children_of(idea_id)
    ]


@pytest.mark.parametrize(
    ("spoken", "names"),
    [
        ("Packliste Urlaub anlegen", ["packliste urlaub"]),
        ("Vorlage Grillabend", ["grillabend"]),
        ("die Vorlage Grillabend erstellen", ["grillabend"]),
        ("Grillabend aus der Vorlage", ["grillabend"]),
        ("eine neue Packliste anlegen", ["packliste"]),
        ("Milch kaufen", []),
    ],
)
def test_german_template_sentences(spoken: str, names: list[str]) -> None:
    """Test which German sentences ask for a template."""
    assert template_names(spoken)[: len(names) or None] == names


def test_english_template_sentences() -> None:
    """Test the English sentences for a template."""
    assert template_names_en("create packing list") == ["packing list"]
    assert template_names_en("BBQ from template") == ["bbq"]
    assert template_names_en("buy milk") == []


async def test_save_and_create_a_template(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Test that a copy has the same subtasks in the same order, all open."""
    entry = await setup_entry()
    store = entry.runtime_data
    root = await _packing_list(store)
    first = store.children_of(root["id"])[0]
    await store.async_update_idea(first["id"], status="completed")

    saved = (await _call(hass, "save_template", id=root["id"]))["template"]
    assert saved["name"] == "Packliste Urlaub"
    assert saved["category"] == "Projekte"
    assert saved["count"] == 5

    copy = (await _call(hass, "create_from_template", template="packliste urlaub"))["idea"]
    assert copy["id"] != root["id"]
    assert copy["text"] == "Packliste Urlaub"
    assert copy["category"] == "Projekte"
    assert _tree(store, copy["id"]) == _tree(store, root["id"])
    assert all(
        store.get_idea(child["id"])["status"] == "active" for child in store.children_of(copy["id"])
    )
    # The copy is the top note of its list
    assert store.children_of(None, "Projekte")[0]["id"] == copy["id"]


async def test_a_template_of_the_same_name_is_replaced(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that saving again updates the template instead of adding one."""
    entry = await setup_entry()
    store = entry.runtime_data
    root = await _packing_list(store)
    await _call(hass, "save_template", id=root["id"], name="Urlaub")
    await store.async_add_idea("Badehose", category="Projekte", parent_id=root["id"], source="dashboard")
    again = (await _call(hass, "save_template", id=root["id"], name="urlaub"))["template"]
    assert len(store.templates()) == 1
    assert again["count"] == 6

    copy = (
        await _call(hass, "create_from_template", template=again["id"], category="Inbox")
    )["idea"]
    assert copy["category"] == "Inbox"
    assert {c["category"] for c in store.children_of(copy["id"])} == {"Inbox"}

    assert (await _call(hass, "delete_template", template="Urlaub"))["deleted"] is True
    assert store.templates() == []
    with pytest.raises(ServiceValidationError):
        await _call(hass, "create_from_template", template="Urlaub")


async def test_spoken_sentence_creates_the_template(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that Alexa's "Packliste Urlaub anlegen" creates the copy."""
    entry = await setup_entry()
    store = entry.runtime_data
    root = await _packing_list(store)
    await store.async_save_template(root["id"])

    copy = await store.async_add_idea("packliste urlaub anlegen", source="alexa_skill")
    assert copy["text"] == "Packliste Urlaub"
    assert copy["id"] != root["id"]
    assert len(store.children_of(copy["id"])) == 3

    # Without a template of that name it stays a note, typed text always does
    note = await store.async_add_idea("konto anlegen", source="alexa_skill")
    assert store.children_of(note["id"]) == []
    typed = await store.async_add_idea("Packliste Urlaub anlegen", source="dashboard")
    assert typed["text"] == "Packliste Urlaub anlegen"


async def test_templates_survive_a_restart(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that templates are stored and broken entries dropped."""
    entry = await setup_entry()
    store = entry.runtime_data
    root = await _packing_list(store)
    await store.async_save_template(root["id"])
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    store = entry.runtime_data
    assert [t["name"] for t in store.templates()] == ["Packliste Urlaub"]


async def test_websocket_lists_the_templates(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_ws_client: Any
) -> None:
    """Test the list the cards read."""
    entry = await setup_entry()
    store = entry.runtime_data
    root = await _packing_list(store)
    await store.async_save_template(root["id"], "Urlaub")
    client = await hass_ws_client(hass)
    await client.send_json({"id": 1, "type": "brainstorm/templates"})
    response = await client.receive_json()
    assert response["success"]
    assert [(t["name"], t["count"]) for t in response["result"]["templates"]] == [("Urlaub", 5)]
