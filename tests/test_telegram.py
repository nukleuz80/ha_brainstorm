"""Tests for notes by Telegram."""

from __future__ import annotations

from typing import Any

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_mock_service,
)

from custom_components.brainstorm.telegram import (
    TelegramWatcher,
    format_senders,
    normalize_id,
    parse_senders,
)

from .conftest import SetupEntry

JAN = "123456789"
GROUP = "-1001234567890"
OPTIONS = {"telegram_enabled": True, "telegram_senders": {JAN: "person.jan"}}
BOT = {"config_entry_id": "bot-entry", "id": 42, "username": "brainstorm_bot"}


@pytest.fixture
def persons(hass: HomeAssistant) -> None:
    """Two people with their Home Assistant users."""
    hass.states.async_set(
        "person.jan", "home", {"friendly_name": "Jan", "user_id": "user-jan"}
    )
    hass.states.async_set(
        "person.anna", "home", {"friendly_name": "Anna", "user_id": "user-anna"}
    )


def _text(user: str, text: str, chat: str | None = None) -> dict[str, Any]:
    """The data of telegram_text as the Telegram bot integration fires it."""
    return {
        "id": 7,
        "chat_id": int(chat or user),
        "user_id": int(user),
        "from_first": "Jan",
        "from_last": "Beispiel",
        "text": text,
        "bot": BOT,
    }


def _notes(store: Any) -> list[dict[str, Any]]:
    return [idea for idea in store.ideas if idea.get("source") == "telegram"]


def test_ids_and_lines() -> None:
    """Ids keep their digits and the minus of a group."""
    assert normalize_id(" 123 456 789 ") == JAN
    assert normalize_id(GROUP) == GROUP
    assert normalize_id(None) == ""
    senders, bad = parse_senders(f"{JAN} = person.jan\n{GROUP}: Anna\n12 = x\nkaputt")
    assert senders == {JAN: "person.jan", GROUP: "Anna"}
    assert bad == ["12 = x", "kaputt"]
    assert format_senders({JAN: "person.jan"}) == f"{JAN} = person.jan"


async def test_message_becomes_a_note_with_a_reply(
    hass: HomeAssistant, setup_entry: SetupEntry, persons: None
) -> None:
    """Every line of a message is noted, the bot answers in the same chat."""
    replies = async_mock_service(hass, "telegram_bot", "send_message")
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox", "Einkauf"]},
        options={**OPTIONS, "telegram_category": "Einkauf"},
    )
    hass.bus.async_fire("telegram_text", _text(JAN, "Milch\n- Eier"))
    await hass.async_block_till_done()
    notes = _notes(entry.runtime_data)
    assert sorted(note["text"] for note in notes) == ["Eier", "Milch"]
    assert {note["owner"] for note in notes} == {"user-jan"}
    assert {note["device"] for note in notes} == {"Jan"}
    assert len(replies) == 1
    assert replies[0].data["chat_id"] == int(JAN)
    assert replies[0].data["reply_to_message_id"] == 7
    assert replies[0].data["config_entry_id"] == "bot-entry"
    assert replies[0].data["message"].count("✅ Notiert in Einkauf") == 2


async def test_commands(
    hass: HomeAssistant, setup_entry: SetupEntry, persons: None
) -> None:
    """/notiz and /note@bot add a note even with a keyword, other commands not."""
    async_mock_service(hass, "telegram_bot", "send_message")
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox"]},
        options={**OPTIONS, "telegram_prefix": "Notiz"},
    )
    base = {"chat_id": int(JAN), "user_id": int(JAN), "bot": BOT}
    hass.bus.async_fire(
        "telegram_command", {**base, "command": "/notiz", "args": ["Brot", "holen"]}
    )
    hass.bus.async_fire(
        "telegram_command",
        {**base, "command": "/note@brainstorm_bot", "args": ["Käse"]},
    )
    hass.bus.async_fire("telegram_command", {**base, "command": "/start", "args": []})
    hass.bus.async_fire("telegram_command", {**base, "command": "/notiz", "args": []})
    # Without the keyword a plain message is left out, with it noted
    hass.bus.async_fire("telegram_text", _text(JAN, "Hallo"))
    hass.bus.async_fire("telegram_text", _text(JAN, "notiz: Butter"))
    await hass.async_block_till_done()
    assert sorted(note["text"] for note in _notes(entry.runtime_data)) == [
        "Brot holen",
        "Butter",
        "Käse",
    ]


async def test_group_and_unknown_sender(
    hass: HomeAssistant, setup_entry: SetupEntry, persons: None
) -> None:
    """A group allows everyone in it, a stranger is remembered for the page."""
    replies = async_mock_service(hass, "telegram_bot", "send_message")
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox"]},
        options={
            "telegram_enabled": True,
            "telegram_senders": {GROUP: "person.anna"},
            "telegram_reply": False,
        },
    )
    hass.bus.async_fire("telegram_text", _text("555666777", "Im Chat", GROUP))
    hass.bus.async_fire("telegram_text", _text("987654321", "Fremd"))
    await hass.async_block_till_done()
    notes = _notes(entry.runtime_data)
    assert [note["text"] for note in notes] == ["Im Chat"]
    assert notes[0]["owner"] == "user-anna"
    assert replies == []
    MockConfigEntry(domain="telegram_bot", title="Bot").add_to_hass(hass)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    for step in ("integrations", "telegram_bot"):
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {"next_step_id": step}
        )
    assert "987654321 (Jan Beispiel)" in result["description_placeholders"]["hint"]
    hass.config_entries.options.async_abort(result["flow_id"])


async def test_failing_reply_keeps_the_note(
    hass: HomeAssistant, setup_entry: SetupEntry, persons: None
) -> None:
    """Without the Telegram bot action the note is still added."""
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox"]}, options=OPTIONS
    )
    watcher = TelegramWatcher(hass, entry.runtime_data, OPTIONS)
    assert await watcher.async_handle_message(_text(JAN, "Test")) == ["Test"]


async def test_unload_stops_listening(
    hass: HomeAssistant, setup_entry: SetupEntry, persons: None
) -> None:
    """Both events are listened to while on, and no longer after unloading."""
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox"]}, options=OPTIONS
    )
    listeners = hass.bus.async_listeners()
    assert listeners.get("telegram_text") == 1
    assert listeners.get("telegram_command") == 1
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert hass.bus.async_listeners().get("telegram_text", 0) == 0


async def test_settings_page(
    hass: HomeAssistant, setup_entry: SetupEntry, persons: None
) -> None:
    """Offered once the Telegram bot is set up, the ids are checked and saved."""
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox", "Einkauf"]})
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "integrations"}
    )
    assert "telegram_bot" not in result["menu_options"]
    hass.config_entries.options.async_abort(result["flow_id"])

    MockConfigEntry(domain="telegram_bot", title="Bot").add_to_hass(hass)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert "⚪ Telegram" in result["description_placeholders"]["integrations_status"]
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "integrations"}
    )
    assert "telegram_bot" in result["menu_options"]
    assert result["description_placeholders"]["status_telegram"] == "aus"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "telegram_bot"}
    )
    assert result["type"] is FlowResultType.FORM
    flow_id = result["flow_id"]
    result = await hass.config_entries.options.async_configure(
        flow_id, {"telegram_enabled": True, "telegram_senders": "12 = Jan"}
    )
    assert result["errors"] == {"telegram_senders": "telegram_senders_invalid"}
    result = await hass.config_entries.options.async_configure(
        flow_id, {"telegram_enabled": True}
    )
    assert result["errors"] == {"telegram_senders": "telegram_senders_missing"}
    result = await hass.config_entries.options.async_configure(
        flow_id,
        {
            "telegram_enabled": True,
            "telegram_senders": f"{JAN} = Jan\n{GROUP} = anna",
            "telegram_category": "Einkauf",
            "telegram_reply": True,
        },
    )
    assert result["step_id"] == "integrations"
    assert result["description_placeholders"]["status_telegram"] == "an · 2 Absender"
    assert entry.options["telegram_senders"] == {
        JAN: "person.jan",
        GROUP: "person.anna",
    }
    assert entry.options["telegram_category"] == "Einkauf"
    hass.config_entries.options.async_abort(result["flow_id"])
