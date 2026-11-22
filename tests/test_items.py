"""Tests for several items spoken in one sentence."""

from __future__ import annotations

from typing import Any

import pytest
from homeassistant.core import HomeAssistant

from custom_components.brainstorm.items import split_items
from custom_components.brainstorm.languages.de import PACK as DE
from custom_components.brainstorm.languages.en import PACK as EN
from custom_components.brainstorm.languages.neutral import PACK as NEUTRAL
from custom_components.brainstorm.store import BrainstormStore


@pytest.mark.parametrize(
    ("text", "items"),
    [
        ("Butter und Eier", ["Butter", "Eier"]),
        ("Butter, Eier und Milch", ["Butter", "Eier", "Milch"]),
        ("Butter, Eier, und Milch", ["Butter", "Eier", "Milch"]),
        ("Brot sowie Brötchen", ["Brot", "Brötchen"]),
        ("Salz und Pfeffer", ["Salz und Pfeffer"]),
        ("Nudeln, Salz und Pfeffer", ["Nudeln", "Salz und Pfeffer"]),
        ("1,5 kg Mehl und Zucker", ["1,5 kg Mehl", "Zucker"]),
        ("Ben & Jerrys", ["Ben & Jerrys"]),
        ("Butter und", ["Butter und"]),
        ("Milch #bio und Eier", ["Milch #bio und Eier"]),
        (
            "Kinder abholen und dann noch schnell zum Bäcker fahren",
            ["Kinder abholen und dann noch schnell zum Bäcker fahren"],
        ),
    ],
)
def test_split_items_german(text: str, items: list[str]) -> None:
    """Separators split, pairs, decimal commas, tags and sentences do not."""
    assert split_items(text, DE) == items


def test_split_items_english_and_neutral() -> None:
    """English has its own words and pairs, the neutral rules never split."""
    assert split_items("Butter and eggs", EN) == ["Butter", "Eggs"]
    assert split_items("Sweet and sour sauce, rice", EN) == [
        "Sweet and sour sauce",
        "Rice",
    ]
    assert split_items("Butter, Eier", NEUTRAL) == ["Butter, Eier"]


@pytest.fixture
async def store(hass: HomeAssistant, hass_storage: dict[str, Any]) -> BrainstormStore:
    """Return a loaded store with a shopping category of its own."""
    instance = BrainstormStore(hass, {})
    await instance.async_load()
    await instance.async_set_categories([*instance.categories, "Einkauf"])
    return instance


async def test_spoken_items_become_entries(store: BrainstormStore) -> None:
    """A spoken note for the shopping category gets one entry per item."""
    first = await store.async_add_idea(
        "Butter, Eier und Milch", category="Einkauf", spoken=True, language="de"
    )
    texts = sorted(i["text"] for i in store.ideas)
    assert texts == ["Butter", "Eier", "Milch"]
    assert first["text"] == "Butter"
    assert {i["category"] for i in store.ideas} == {"Einkauf"}


async def test_only_lists_and_spoken_notes_are_split(
    hass: HomeAssistant, hass_storage: dict[str, Any], store: BrainstormStore
) -> None:
    """Typed notes and standard categories stay whole, unless the list is named."""
    await store.async_add_idea(
        "Butter und Eier", category="Einkauf", spoken=False, language="de"
    )
    await store.async_add_idea(
        "Hecke und Rasen schneiden", category="Alltag", spoken=True, language="de"
    )
    assert len(store.ideas) == 2
    await store.async_add_idea(
        "Toast und Käse", category="Alltag", spoken=True, language="de", list_named=True
    )
    assert {"Toast", "Käse"} <= {i["text"] for i in store.ideas}

    switched_off = BrainstormStore(hass, {"split_items": False})
    await switched_off.async_load()
    before = len(switched_off.ideas)
    idea = await switched_off.async_add_idea(
        "Brot und Milch", category="Einkauf", spoken=True, language="de"
    )
    assert idea["text"] == "Brot und Milch"
    assert len(switched_off.ideas) == before + 1


async def test_sentence_tester_shows_the_items(store: BrainstormStore) -> None:
    """The sentence tester lists the entries a note would become."""
    preview = store.preview_idea(
        "setze Butter und Eier auf die Einkaufsliste", "voice", "de"
    )
    assert preview["category"] == "Einkauf"
    assert preview["items"] == ["Butter", "Eier"]
    preview = store.preview_idea("Salz und Pfeffer auf die Einkaufsliste", "voice", "de")
    assert preview["items"] == ["Salz und Pfeffer"]
