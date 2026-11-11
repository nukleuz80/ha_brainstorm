"""Tests for the pinboard, where notes sit freely as sticky notes."""

from __future__ import annotations

from typing import Any

from homeassistant.core import Context, HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from .conftest import SetupEntry


async def _send(client: Any, pins: dict[str, Any]) -> dict[str, Any]:
    await client.send_json_auto_id({"type": "brainstorm/pins", "pins": pins})
    return await client.receive_json()


async def test_pins_keep_place_and_colour(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
    hass_owner_user: Any,
) -> None:
    """A person pins notes they may change; colour stays when only moved."""
    assert await async_setup_component(hass, "websocket_api", {})
    entry = await setup_entry(
        options={"privacy_enabled": True, "privacy_owner": hass_owner_user.id}
    )
    store = entry.runtime_data
    user = hass.auth.async_validate_access_token(hass_read_only_access_token).user
    own = await store.async_add_idea(
        "eigene", category="Inbox", context=Context(user_id=user.id)
    )
    viewed = await store.async_add_idea(
        "nur lesen", category="Inbox", context=Context(user_id=hass_owner_user.id)
    )
    await store.async_set_idea_shares(
        [viewed["id"]], {user.id: "view"}, hass_owner_user.id
    )
    updated_at = own["updated_at"]
    client = await hass_ws_client(hass, hass_read_only_access_token)

    reply = await _send(
        client,
        {
            own["id"]: {"x": 40.04, "y": -12, "color": "pink"},
            viewed["id"]: {"x": 5, "y": 5},
            "missing": {"x": 1, "y": 1},
        },
    )
    assert reply["result"] == {"changed": 1}
    assert store.get_idea(own["id"])["pin"] == {"x": 40.0, "y": -12.0, "color": "pink"}
    assert store.get_idea(own["id"])["updated_at"] == updated_at
    assert "pin" not in store.get_idea(viewed["id"])
    # The map keeps its own places
    assert "map_pos" not in store.get_idea(own["id"])

    # Only moved keeps the colour, the same place again changes nothing
    assert (await _send(client, {own["id"]: {"x": 90, "y": 10}}))["result"]["changed"] == 1
    assert store.get_idea(own["id"])["pin"]["color"] == "pink"
    assert (await _send(client, {own["id"]: {"x": 90, "y": 10}}))["result"]["changed"] == 0
    await _send(client, {own["id"]: {"x": 90, "y": 10, "color": ""}})
    assert store.get_idea(own["id"])["pin"] == {"x": 90.0, "y": 10.0}

    await client.send_json_auto_id({"type": "brainstorm/ideas"})
    ideas = {i["id"]: i for i in (await client.receive_json())["result"]["ideas"]}
    assert ideas[own["id"]]["pin"] == {"x": 90.0, "y": 10.0}

    # Unknown colours are refused, None takes the note off the board
    assert not (await _send(client, {own["id"]: {"x": 1, "y": 1, "color": "red;"}}))["success"]
    await _send(client, {own["id"]: None})
    assert "pin" not in store.get_idea(own["id"])


async def test_pin_follows_the_note(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Another category drops the pin, export and import keep a clean one."""
    entry = await setup_entry()
    store = entry.runtime_data
    idea = await store.async_add_idea("Zettel", category="Alltag")
    other = await store.async_add_idea("Zweiter Zettel", category="Alltag")
    await store.async_set_pins(
        {idea["id"]: {"x": 10, "y": 20, "color": "green"}, other["id"]: {"x": 1, "y": 2}},
        None,
    )

    exported = await hass.services.async_call(
        "brainstorm", "export_json", {}, blocking=True, return_response=True
    )
    pins = {i["text"]: i.get("pin") for i in exported["ideas"]}
    assert pins["Zettel"] == {"x": 10.0, "y": 20.0, "color": "green"}

    for item in exported["ideas"]:
        if item["text"] == "Zweiter Zettel":
            item["pin"] = {"x": "1;color:red", "y": 2}
        else:
            item["pin"] = {"x": 3, "y": 4, "color": "url(x)"}
    for item in list(store.ideas):
        await store.async_delete_idea(item["id"])
    await hass.services.async_call(
        "brainstorm", "import_json", {"data": exported}, blocking=True, return_response=True
    )
    by_text = {i["text"]: i for i in store.ideas}
    assert by_text["Zettel"]["pin"] == {"x": 3.0, "y": 4.0}
    assert "pin" not in by_text["Zweiter Zettel"]

    await store.async_update_idea(by_text["Zettel"]["id"], category="Projekte")
    assert "pin" not in store.get_idea(by_text["Zettel"]["id"])
