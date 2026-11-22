"""Tests for categories learned from notes moved by hand."""

from __future__ import annotations

from typing import Any

import pytest
from homeassistant.core import Context, HomeAssistant

from custom_components.brainstorm.const import (
    CONF_LEARN_CATEGORIES,
    DOMAIN,
    LEARNED_WORDS_MAX,
    STORAGE_KEY,
)
from custom_components.brainstorm.store import BrainstormStore

from .conftest import SetupEntry


@pytest.fixture
async def store(hass: HomeAssistant, hass_storage: dict[str, Any]) -> BrainstormStore:
    """Return a loaded store with the standard categories and 'Kinder'."""
    instance = BrainstormStore(hass, {})
    await instance.async_load()
    await instance.async_set_categories([*instance.categories, "Kinder"])
    return instance


async def test_a_moved_note_teaches_its_words(store: BrainstormStore) -> None:
    """After a move by hand, a similar note lands in the new category."""
    first = await store.async_add_idea("Zahnspange abholen", source="manual")
    assert first["category"] != "Kinder"

    await store.async_update_idea(first["id"], category="Kinder", learn=True)
    assert store.learned_words["zahnspange"] == "Kinder"
    assert "abholen" in store.learned_words

    reasons: dict[str, Any] = {}
    _, category, _, _ = store.parse_text_and_category(
        "Termin für die Zahnspange", reasons=reasons
    )
    assert category == "Kinder"
    assert reasons["category"] == ("learned", ["zahnspange"])


async def test_a_move_without_learn_teaches_nothing(store: BrainstormStore) -> None:
    """Moves by syncs, the AI or automations do not count."""
    idea = await store.async_add_idea("Zahnspange abholen", source="manual")
    await store.async_update_idea(idea["id"], category="Kinder")
    assert store.learned_words == {}


async def test_common_words_and_subtasks_are_not_learned(
    store: BrainstormStore,
) -> None:
    """Filler words say nothing, and a subtask follows its parent."""
    idea = await store.async_add_idea("bitte noch Zahnspange", source="manual")
    await store.async_update_idea(idea["id"], category="Kinder", learn=True)
    assert set(store.learned_words) == {"zahnspange"}

    child = await store.async_add_idea(
        "Schulranzen kaufen", source="manual", parent_id=idea["id"]
    )
    await store.async_update_idea(child["id"], category="Alltag", learn=True)
    assert "schulranzen" not in store.learned_words


async def test_moving_to_the_inbox_forgets(store: BrainstormStore) -> None:
    """The Inbox means the note belongs nowhere, the latest move wins."""
    idea = await store.async_add_idea("Zahnspange abholen", source="manual")
    await store.async_update_idea(idea["id"], category="Kinder", learn=True)
    await store.async_update_idea(idea["id"], category="Alltag", learn=True)
    assert store.learned_words["zahnspange"] == "Alltag"

    await store.async_update_idea(idea["id"], category="Inbox", learn=True)
    assert "zahnspange" not in store.learned_words


async def test_a_category_name_beats_a_learned_word(store: BrainstormStore) -> None:
    """A learned word counts more than a keyword, but less than a named list."""
    idea = await store.async_add_idea("Zahnspange abholen", source="manual")
    await store.async_update_idea(idea["id"], category="Kinder", learn=True)
    _, category, _, _ = store.parse_text_and_category("Zahnspange im Smarthome")
    assert category == "Smarthome"


async def test_removed_category_and_limit(store: BrainstormStore) -> None:
    """Words of a removed category go, and only the newest words stay."""
    idea = await store.async_add_idea("Zahnspange abholen", source="manual")
    await store.async_update_idea(idea["id"], category="Kinder", learn=True)
    await store.async_remove_category("Kinder")
    assert store.learned_words == {}

    for number in range(LEARNED_WORDS_MAX + 5):
        store._learn_category(f"wort{number:04d}", "Alltag")
    assert len(store.learned_words) == LEARNED_WORDS_MAX
    assert "wort0000" not in store.learned_words
    assert f"wort{LEARNED_WORDS_MAX + 4:04d}" in store.learned_words


async def test_learned_words_survive_a_restart_unless_turned_off(
    hass: HomeAssistant, hass_storage: dict[str, Any], store: BrainstormStore
) -> None:
    """The words are stored; with the option off they are forgotten."""
    idea = await store.async_add_idea("Zahnspange abholen", source="manual")
    await store.async_update_idea(idea["id"], category="Kinder", learn=True)
    assert hass_storage[STORAGE_KEY]["data"]["learned_words"]["zahnspange"] == "Kinder"

    again = BrainstormStore(hass, {})
    await again.async_load()
    assert again.learned_words["zahnspange"] == "Kinder"

    off = BrainstormStore(hass, {CONF_LEARN_CATEGORIES: False})
    await off.async_load()
    assert off.learned_words == {}
    _, category, _, _ = off.parse_text_and_category("Termin für die Zahnspange")
    assert category != "Kinder"


async def test_the_update_service_learns_only_for_people(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_admin_user: Any
) -> None:
    """A person moving a note teaches, an automation does not."""
    store = (await setup_entry()).runtime_data
    await store.async_set_categories([*store.categories, "Kinder"])
    idea = await store.async_add_idea("Zahnspange abholen", source="manual")

    await hass.services.async_call(
        DOMAIN, "update_idea", {"id": idea["id"], "category": "Kinder"}, blocking=True
    )
    assert store.learned_words == {}

    await hass.services.async_call(
        DOMAIN,
        "update_idea",
        {"id": idea["id"], "category": "Alltag"},
        blocking=True,
        context=Context(user_id=hass_admin_user.id),
    )
    assert store.learned_words["zahnspange"] == "Alltag"
