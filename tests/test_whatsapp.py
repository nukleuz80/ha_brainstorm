"""Tests for notes by WhatsApp."""

from __future__ import annotations

from typing import Any

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import async_mock_service

from custom_components.brainstorm.whatsapp import (
    WhatsAppWatcher,
    field_value,
    format_senders,
    normalize_number,
    parse_senders,
    same_number,
)

from .conftest import SetupEntry

EVENT = "whatsapp_message_received"
JAN = "491711234567"
OPTIONS = {
    "whatsapp_enabled": True,
    "whatsapp_senders": {JAN: "person.jan"},
}


@pytest.fixture
def persons(hass: HomeAssistant) -> None:
    """Two people with their Home Assistant users."""
    hass.states.async_set(
        "person.jan", "home", {"friendly_name": "Jan", "user_id": "user-jan"}
    )
    hass.states.async_set(
        "person.anna",
        "home",
        {"friendly_name": "Anna Beispiel", "user_id": "user-anna"},
    )


def _notes(store: Any) -> list[dict[str, Any]]:
    return [idea for idea in store.ideas if idea.get("source") == "whatsapp"]


def test_numbers_are_compared_without_their_form() -> None:
    """Bridge ids, "+", "00" and the national form all mean one number."""
    assert normalize_number("491711234567@c.us") == JAN
    assert normalize_number("+49 171 123-4567") == JAN
    assert normalize_number("0049 171 1234567") == JAN
    assert normalize_number("491711234567@s.whatsapp.net") == JAN
    assert same_number(JAN, normalize_number("0171 1234567"))
    assert not same_number(JAN, "491711234568")
    # Too short to compare by its end
    assert not same_number(JAN, "4567")
    assert not same_number("", JAN)


def test_senders_are_read_from_lines() -> None:
    """One number per line, "=" or ":" before the person, bad lines reported."""
    senders, bad = parse_senders(
        "+49 171 1234567 = person.jan\n\n"
        "0049 160 7654321: Anna Beispiel\nkaputt\n12 = x"
    )
    assert senders == {JAN: "person.jan", "491607654321": "Anna Beispiel"}
    assert bad == ["kaputt", "12 = x"]
    assert format_senders({JAN: "person.jan"}) == "+491711234567 = person.jan"


def test_nested_fields() -> None:
    """A dot leads into a nested field, a missing one gives None."""
    data = {"message": {"text": "Milch"}, "from": "x"}
    assert field_value(data, "message.text") == "Milch"
    assert field_value(data, "message.body") is None
    assert field_value(data, "from.x") is None


async def test_message_becomes_a_note_with_a_reply(
    hass: HomeAssistant, setup_entry: SetupEntry, persons: None
) -> None:
    """A message of ha-whatsapp from a known number is noted for its person."""
    replies = async_mock_service(hass, "whatsapp", "send_message")
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox", "Einkauf"]},
        options={**OPTIONS, "whatsapp_category": "Einkauf"},
    )
    hass.bus.async_fire(EVENT, {"from": f"{JAN}@c.us", "content": "Milch kaufen"})
    await hass.async_block_till_done()
    notes = _notes(entry.runtime_data)
    assert len(notes) == 1
    assert notes[0]["category"] == "Einkauf"
    assert notes[0]["owner"] == "user-jan"
    assert notes[0]["device"] == "Jan"
    assert len(replies) == 1
    assert replies[0].data["target"] == f"{JAN}@c.us"
    assert replies[0].data["message"] == f"✅ Notiert in Einkauf: {notes[0]['text']}"


async def test_unknown_and_own_messages_are_left_out(
    hass: HomeAssistant, setup_entry: SetupEntry, persons: None
) -> None:
    """Strangers, the own replies and empty messages add nothing."""
    replies = async_mock_service(hass, "whatsapp", "send_message")
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox"]}, options=OPTIONS
    )
    hass.bus.async_fire(EVENT, {"from": "491609999999@c.us", "content": "Spam"})
    hass.bus.async_fire(EVENT, {"from": JAN, "content": "✅ Notiert", "fromMe": True})
    hass.bus.async_fire(EVENT, {"from": JAN, "content": "   "})
    hass.bus.async_fire(EVENT, {"content": "Ohne Absender"})
    await hass.async_block_till_done()
    assert _notes(entry.runtime_data) == []
    assert replies == []


async def test_lines_keyword_and_other_bridges(
    hass: HomeAssistant, setup_entry: SetupEntry, persons: None
) -> None:
    """Another bridge with its own event and fields, every line a note."""
    replies = async_mock_service(hass, "notify", "wa")
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox"]},
        options={
            "whatsapp_enabled": True,
            "whatsapp_senders": {"491607654321": "person.anna"},
            "whatsapp_event": "openwa_message",
            "whatsapp_text_field": "message.text",
            "whatsapp_sender_field": "message.chat",
            "whatsapp_prefix": "Notiz",
            "whatsapp_reply_service": "notify.wa",
        },
    )
    store = entry.runtime_data
    hass.bus.async_fire(
        "openwa_message",
        {"message": {"chat": "01607654321", "text": "Notiz: Brot\n- Butter\n\n• Käse"}},
    )
    # Without the keyword, and the default event, nothing is noted
    hass.bus.async_fire(
        "openwa_message", {"message": {"chat": "01607654321", "text": "Hallo"}}
    )
    hass.bus.async_fire(EVENT, {"from": "01607654321", "content": "Notiz: Eier"})
    await hass.async_block_till_done()
    notes = _notes(store)
    assert sorted(note["text"].casefold() for note in notes) == [
        "brot",
        "butter",
        "käse",
    ]
    assert {note["owner"] for note in notes} == {"user-anna"}
    assert len(replies) == 1
    assert replies[0].data["message"].count("✅") == 3


async def test_missing_reply_action_still_notes(
    hass: HomeAssistant, setup_entry: SetupEntry, persons: None
) -> None:
    """Without the reply action, the note is added all the same."""
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox"]}, options=OPTIONS
    )
    watcher = WhatsAppWatcher(hass, entry.runtime_data, OPTIONS)
    assert await watcher.async_handle_message({"from": JAN, "content": "Test"}) == [
        "Test"
    ]


async def test_off_or_without_numbers_does_not_listen(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Switched off, or without allowed numbers, the event is not listened to."""
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox"]})
    for options in ({**OPTIONS, "whatsapp_enabled": False}, {"whatsapp_enabled": True}):
        watcher = WhatsAppWatcher(hass, entry.runtime_data, options)
        listeners = hass.bus.async_listeners().get(EVENT, 0)
        await watcher.async_start()
        assert hass.bus.async_listeners().get(EVENT, 0) == listeners
        watcher.async_stop()


async def test_unload_stops_listening(
    hass: HomeAssistant, setup_entry: SetupEntry, persons: None
) -> None:
    """Unloading the entry removes the listener."""
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox"]}, options=OPTIONS
    )
    assert hass.bus.async_listeners().get(EVENT) == 1
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert hass.bus.async_listeners().get(EVENT, 0) == 0


async def test_settings_page(
    hass: HomeAssistant, setup_entry: SetupEntry, persons: None
) -> None:
    """The page checks the numbers and saves them with their person."""
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox", "Einkauf"]})
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "integrations"}
    )
    assert "WhatsApp" not in result["description_placeholders"]["logos"]
    assert "whatsapp" in result["menu_options"]
    assert result["description_placeholders"]["status_whatsapp"] == "aus"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "whatsapp"}
    )
    assert result["type"] is FlowResultType.FORM
    flow_id = result["flow_id"]
    result = await hass.config_entries.options.async_configure(
        flow_id,
        {"whatsapp_enabled": True, "whatsapp_senders": "+49 171 1234567 = Niemand"},
    )
    assert result["errors"] == {"whatsapp_senders": "whatsapp_senders_invalid"}
    assert "Niemand" in result["description_placeholders"]["hint"]
    result = await hass.config_entries.options.async_configure(
        flow_id, {"whatsapp_enabled": True, "whatsapp_reply": True}
    )
    assert result["errors"] == {"whatsapp_senders": "whatsapp_senders_missing"}
    result = await hass.config_entries.options.async_configure(
        flow_id,
        {
            "whatsapp_enabled": True,
            "whatsapp_senders": "+49 171 1234567 = Jan\n0160 7654321 = anna",
            "whatsapp_category": "Einkauf",
            "whatsapp_reply": False,
        },
    )
    assert result["step_id"] == "integrations"
    assert result["description_placeholders"]["status_whatsapp"] == "an · 2 Nummern"
    assert "WhatsApp" in result["description_placeholders"]["logos"]
    assert entry.options["whatsapp_senders"] == {
        JAN: "person.jan",
        "01607654321": "person.anna",
    }
    assert entry.options["whatsapp_category"] == "Einkauf"
    assert entry.options["whatsapp_reply"] is False
    hass.config_entries.options.async_abort(result["flow_id"])
