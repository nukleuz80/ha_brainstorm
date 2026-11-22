"""Tests for the sentence tester, which shows what Brainstorm makes of a sentence."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from custom_components.brainstorm.const import DOMAIN
from custom_components.brainstorm.store import BrainstormStore, get_loaded_store

from .conftest import SetupEntry


async def test_voice_sentence_gets_category_and_reason(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a spoken note is cleaned and says why it got its category."""
    await setup_entry()
    store = get_loaded_store(hass)
    assert isinstance(store, BrainstormStore)
    preview = store.preview_idea("für den Garten Tomaten düngen", "voice", "de")
    assert preview["mode"] == "voice"
    assert preview["text"] == "Tomaten düngen"
    assert preview["category"] == "Haus & Garten"
    assert preview["category_reason"][0] in {"prefix", "topic", "phrase", "words"}
    assert store.ideas == []


async def test_typed_sentence_without_hints_falls_back(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a sentence without any hint names the fallback."""
    await setup_entry()
    store = get_loaded_store(hass)
    assert store is not None
    preview = store.preview_idea("Xylophon", "typed", "de")
    assert preview["mode"] == "typed"
    assert preview["category_reason"] == ("fallback", None)
    assert preview["due"] is None


async def test_auto_reads_remind_as_reminder(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that "erinnere mich" turns into a reminder with a due time."""
    await setup_entry()
    store = get_loaded_store(hass)
    assert store is not None
    preview = store.preview_idea(
        "Erinnere mich morgen um 8 Uhr an die Mülltonnen", "auto", "de"
    )
    assert preview["mode"] == "reminder"
    assert preview["due"] is not None
    assert "8" not in preview["text"]
    assert "Mülltonnen" in preview["text"]
    assert store.ideas == []


async def test_action_answers_without_saving(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the action, which only answers."""
    await setup_entry()
    response: dict[str, Any] = await hass.services.async_call(
        DOMAIN,
        "test_sentence",
        {"text": "für den Garten Tomaten düngen"},
        blocking=True,
        return_response=True,
    )
    assert response["category"] == "Haus & Garten"
    store = get_loaded_store(hass)
    assert store is not None
    assert store.ideas == []


async def test_options_step_shows_the_result(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the sentence tester in the settings, which keeps the sentence."""
    entry = await setup_entry()
    options = dict(entry.options)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert "sentence_test" in result["menu_options"]
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "sentence_test"}
    )
    assert result["step_id"] == "sentence_test"
    assert result["description_placeholders"]["result"] == ""

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"sentence": "für den Garten Tomaten düngen", "mode": "auto"}
    )
    assert result["step_id"] == "sentence_test"
    shown = result["description_placeholders"]["result"]
    assert "Tomaten düngen" in shown
    assert "Haus & Garten" in shown
    assert "Einträge" not in shown

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"sentence": "setze Butter und Eier auf die Einkaufsliste", "mode": "voice"},
    )
    assert "- Einträge: Butter · Eier" in result["description_placeholders"]["result"]

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"go_back": True, "mode": "auto"}
    )
    assert result["step_id"] == "init"
    assert dict(entry.options) == options


async def test_spoken_shopping_list_picks_the_shopping_category(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that "auf die Einkaufsliste" still names the list once it is cut off."""
    await setup_entry()
    store = get_loaded_store(hass)
    assert store is not None
    preview = store.preview_idea("Toast auf die Einkaufsliste", "voice", "de")
    assert (preview["text"], preview["category"]) == ("Toast", "Alltag")
    assert preview["category_reason"] == ("list", "einkaufsliste")
    await store.async_set_categories([*store.categories, "Einkauf"])
    preview = store.preview_idea("setze Butter auf die Einkaufsliste", "voice", "de")
    assert (preview["text"], preview["category"]) == ("Butter", "Einkauf")
    # Typed, the list name stays in the text and is found as a word
    preview = store.preview_idea("Milch für die Einkaufsliste", "typed", "de")
    assert preview["category"] == "Einkauf"


async def test_device_command_is_flagged(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that the tester warns about a sentence the skill would not store."""
    await setup_entry()
    hass.states.async_set("light.kuche_l1", "off", {"friendly_name": "Küche Schrank"})
    store = get_loaded_store(hass)
    assert store is not None
    assert store.preview_idea("Küche Schrank an", "voice", "de")["device_command"]
    assert not store.preview_idea("notiere Küche Schrank an", "voice", "de")[
        "device_command"
    ]
    assert not store.preview_idea("Küche Schrank an", "typed", "de")["device_command"]
    assert not store.preview_idea("Rufe morgen Oma an", "voice", "de")["device_command"]
