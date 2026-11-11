"""Tests for comments on notes and mentions with @."""

from __future__ import annotations

from typing import Any

from homeassistant.core import Context, HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.setup import async_setup_component
import pytest
from pytest_homeassistant_custom_component.common import async_capture_events
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.brainstorm.reminders import find_mentions

from .conftest import SetupEntry

OLAF = "user-olaf"
FRIDA = "user-frida"


async def _call(
    hass: HomeAssistant, service: str, user: str | None = OLAF, **data: Any
) -> Any:
    return await hass.services.async_call(
        "brainstorm",
        service,
        data,
        blocking=True,
        return_response=True,
        context=Context(user_id=user),
    )


async def _add(hass: HomeAssistant, text: str, user: str = OLAF) -> str:
    response = await _call(hass, "add_idea", user, text=text, category="Alltag")
    return response["idea"]["id"]


def _people(hass: HomeAssistant) -> None:
    hass.states.async_set("person.frida", "home", {"friendly_name": "Frida Sommer", "user_id": FRIDA})
    hass.states.async_set("person.olaf", "home", {"friendly_name": "Olaf", "user_id": OLAF})


def _notify(hass: HomeAssistant) -> list[ServiceCall]:
    calls: list[ServiceCall] = []

    async def send(call: ServiceCall) -> None:
        calls.append(call)

    hass.services.async_register("notify", "frida_phone", send)
    hass.services.async_register("notify", "olaf_phone", send)
    return calls


async def test_mentions_are_found(hass: HomeAssistant) -> None:
    """Full names and first names count, mail addresses and unknown names not."""
    _people(hass)
    assert find_mentions(hass, "Danke @Frida, und @frida sommer!") == ["person.frida"]
    assert find_mentions(hass, "@Olaf @Frida") == ["person.olaf", "person.frida"]
    assert find_mentions(hass, "olaf@frida.de @Fridabus @Niemand") == []
    assert find_mentions(hass, "ohne") == []


async def test_comments_add_count_and_delete(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Comments keep their order, count in the overview and can be removed."""
    entry = await setup_entry()
    store = entry.runtime_data
    events = async_capture_events(hass, "brainstorm_comment_added")
    idea_id = await _add(hass, "Grillabend")

    first = await _call(hass, "add_comment", id=idea_id, text="  Wer bringt Kohle?  ")
    assert first["comment"]["text"] == "Wer bringt Kohle?"
    assert first["comment"]["by"] == OLAF
    assert first["notified"] == []
    second = await _call(hass, "add_comment", FRIDA, id=idea_id, text="Ich!")
    assert [c["text"] for c in store.get_comments(idea_id, OLAF)] == ["Wer bringt Kohle?", "Ich!"]
    await hass.async_block_till_done()
    assert events[0].data["idea_text"] == "Grillabend"
    assert events[1].data["by"] == FRIDA

    listed = next(i for i in store.get_overview_attributes(OLAF)["ideas"] if i["id"] == idea_id)
    assert listed["comment_count"] == 2
    assert "comments" not in listed

    with pytest.raises(ServiceValidationError):
        await _call(hass, "add_comment", id=idea_id, text="   ")
    with pytest.raises(ServiceValidationError):
        await _call(hass, "add_comment", None, id=idea_id, text="Anonym")
    with pytest.raises(ServiceValidationError):
        await _call(hass, "delete_comment", id=idea_id, comment_id="missing")

    # The note's owner may remove Frida's comment, too
    await _call(hass, "delete_comment", id=idea_id, comment_id=second["comment"]["id"])
    await _call(hass, "delete_comment", id=idea_id, comment_id=first["comment"]["id"])
    assert "comments" not in store.get_idea(idea_id)


async def test_only_author_or_editor_deletes(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """A viewer may comment and remove their own comment, but not others'."""
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox", "Alltag"]},
        options={"privacy_enabled": True, "privacy_owner": OLAF},
    )
    store = entry.runtime_data
    idea_id = await _add(hass, "Geheimer Plan")
    with pytest.raises(ServiceValidationError):
        await _call(hass, "add_comment", FRIDA, id=idea_id, text="Darf ich?")

    await _call(hass, "share", ids=[idea_id], shares={FRIDA: "view"})
    mine = await _call(hass, "add_comment", id=idea_id, text="Von Olaf")
    hers = await _call(hass, "add_comment", FRIDA, id=idea_id, text="Von Frida")
    with pytest.raises(ServiceValidationError):
        await _call(hass, "delete_comment", FRIDA, id=idea_id, comment_id=mine["comment"]["id"])
    await _call(hass, "delete_comment", FRIDA, id=idea_id, comment_id=hers["comment"]["id"])
    assert [c["text"] for c in store.get_comments(idea_id, OLAF)] == ["Von Olaf"]


async def test_mentioned_people_get_a_message(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Only named people with channels hear about it, never the author."""
    _people(hass)
    calls = _notify(hass)
    await setup_entry(
        options={
            "persons_enabled": True,
            "person_rules": {
                "person.frida": {"notify": ["notify.frida_phone"]},
                "person.olaf": {"notify": ["notify.olaf_phone"]},
            },
        }
    )
    idea_id = await _add(hass, "Grillabend")

    response = await _call(
        hass, "add_comment", id=idea_id, text="@Frida bringst du Salat? @Olaf"
    )
    await hass.async_block_till_done()
    assert response["notified"] == ["person.frida"]
    assert response["comment"]["mentions"] == ["person.frida", "person.olaf"]
    assert len(calls) == 1
    assert calls[0].service == "frida_phone"
    assert "Grillabend" in calls[0].data["message"]
    assert "Salat" in calls[0].data["message"]

    quiet = await _call(hass, "add_comment", id=idea_id, text="@Frida", notify=False)
    assert quiet["notified"] == []
    assert len(calls) == 1


async def test_mentions_respect_privacy(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Someone who may not see the note is not told about it."""
    _people(hass)
    calls = _notify(hass)
    await setup_entry(
        stored={"ideas": [], "categories": ["Inbox", "Alltag"]},
        options={
            "privacy_enabled": True,
            "privacy_owner": OLAF,
            "persons_enabled": True,
            "person_rules": {"person.frida": {"notify": ["notify.frida_phone"]}},
        },
    )
    idea_id = await _add(hass, "Überraschung für Frida")
    response = await _call(hass, "add_comment", id=idea_id, text="@Frida darf nichts wissen")
    assert response["notified"] == []
    assert not calls


async def test_comments_stay_out_of_exports(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """User IDs in comments do not travel in a JSON export."""
    await setup_entry()
    idea_id = await _add(hass, "Ausflug")
    await _call(hass, "add_comment", id=idea_id, text="Ich fahre")
    response = await _call(hass, "export_json")
    exported = next(i for i in response["ideas"] if i["id"] == idea_id)
    assert "comments" not in exported


async def test_websocket_lists_comments(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_ws_client: WebSocketGenerator, hass_admin_user: Any
) -> None:
    """The command adds names and who may delete what."""
    assert await async_setup_component(hass, "websocket_api", {})
    await setup_entry()
    me = hass_admin_user.id
    idea_id = await _add(hass, "Kino", me)
    await _call(hass, "add_comment", me, id=idea_id, text="Freitag?")
    await _call(hass, "add_comment", FRIDA, id=idea_id, text="Samstag!")
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "brainstorm/comments", "idea_id": idea_id})
    result = (await client.receive_json())["result"]
    assert [c["text"] for c in result["comments"]] == ["Freitag?", "Samstag!"]
    assert result["comments"][0]["mine"] is True
    assert result["comments"][0]["name"] == hass_admin_user.name
    assert result["comments"][1]["mine"] is False
    assert result["comments"][1]["can_delete"] is True

    await client.send_json_auto_id({"type": "brainstorm/comments", "idea_id": "missing"})
    assert (await client.receive_json())["error"]["code"] == "not_found"
