"""Tests for the language packs."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest
from homeassistant.core import HomeAssistant

from custom_components.brainstorm.languages import PACKS, get_pack
from custom_components.brainstorm.languages.common import LanguagePack
from custom_components.brainstorm.languages.neutral import PACK as NEUTRAL
from custom_components.brainstorm.store import BrainstormStore

NOW = datetime(2026, 3, 10, 10, 0, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    ("language", "code"),
    [("de", "de"), ("de-AT", "de"), ("DE_ch", "de"), ("xx", "neutral"), (None, "neutral")],
)
def test_get_pack(language: str | None, code: str) -> None:
    """A regional language finds its pack, an unknown one the neutral rules."""
    assert get_pack(language).code == code


@pytest.mark.parametrize("pack", [*PACKS.values(), NEUTRAL], ids=lambda pack: pack.code)
def test_every_pack_handles_any_text(pack: LanguagePack) -> None:
    """No pack fails on text of any kind, including foreign letters and empty text."""
    for text in ("", "   ", "Ça va très bien?", "買い物 リスト", "!!!", "a"):
        pack.clean_text(text, None)
        pack.format_typed(text)
        pack.extract_due(text, NOW)
        pack.parse_due(text, NOW)
        pack.strip_reminder_words(text)
        pack.extract_priority(text)
        pack.starts_with_verb(text)
        pack.validate_ai_rewrite(text, text, text)


@pytest.mark.parametrize("pack", PACKS.values(), ids=lambda pack: pack.code)
def test_every_pack_describes_the_same_categories(pack: LanguagePack) -> None:
    """Aliases and keywords exist for the standard categories of every pack."""
    assert set(pack.category_aliases) == set(pack.category_names)
    assert set(pack.category_keywords) == set(pack.category_names)
    assert pack.ai_cleanup_prompt is not None


async def test_unknown_language_leaves_words_alone(hass: HomeAssistant) -> None:
    """Rules of another language are never applied to a foreign text."""
    hass.config.language = "fr"
    store = BrainstormStore(hass, {})
    text, category, _, priority = store.parse_text_and_category(
        "il faut acheter du lait demain"
    )
    assert text == "Il faut acheter du lait demain"
    assert category == "Inbox"
    assert priority == "medium"
    assert get_pack(hass.config.language).extract_due(text, NOW) == (None, text)


async def test_request_language_wins_over_home_assistant(hass: HomeAssistant) -> None:
    """A request in another language uses that language's rules."""
    hass.config.language = "fr"
    store = BrainstormStore(hass, {})
    store._categories = ["Inbox", "Haus & Garten"]  # noqa: SLF001
    text, category, _, _ = store.parse_text_and_category(
        "der rasen muss gemäht werden", language="de"
    )
    assert text == "Rasen mähen"
    assert category == "Haus & Garten"


async def test_tags_work_in_every_language(hass: HomeAssistant) -> None:
    """The written priority tags are not bound to a language."""
    hass.config.language = "fr"
    store: Any = BrainstormStore(hass, {})
    assert store.parse_priority("Regal !dringend")[1] == "urgent"
    assert store.parse_priority("Regal !urgent")[1] == "urgent"


async def test_service_accepts_a_language(hass: HomeAssistant, setup_entry: Any) -> None:
    """An automation can state the language of its text."""
    hass.config.language = "de"
    await setup_entry()
    response = await hass.services.async_call(
        "brainstorm",
        "add_idea",
        {"text": "the lawn has to be mowed", "source": "assist", "language": "en"},
        blocking=True,
        return_response=True,
    )
    assert response["idea"]["text"] == "Mow lawn"
