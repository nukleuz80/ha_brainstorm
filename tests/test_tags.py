"""Tests for tags: #words in a note that the cards filter by."""
from __future__ import annotations

from typing import Any

import pytest
from homeassistant.core import HomeAssistant

from custom_components.brainstorm.store import BrainstormStore


@pytest.fixture
async def store(hass: HomeAssistant, hass_storage: dict[str, Any]) -> BrainstormStore:
    """Return a loaded store."""
    instance = BrainstormStore(hass, {})
    await instance.async_load()
    return instance


async def test_typed_tags_stay_in_the_text(store: BrainstormStore) -> None:
    """A typed note keeps its tags where they were written."""
    idea = await store.async_add_idea("Rasen mähen #garten #Wochenende", source="dashboard")
    assert idea["text"] == "Rasen mähen #garten #Wochenende"
    assert sorted(idea["tags"]) == ["garten", "wochenende"]


async def test_spoken_hashtag_becomes_a_tag(store: BrainstormStore) -> None:
    """'hashtag wochenende' said to Alexa becomes #wochenende at the end."""
    idea = await store.async_add_idea(
        "der rasen muss gemäht werden hashtag wochenende", source="Alexa"
    )
    assert idea["text"] == "Rasen mähen #wochenende"
    assert idea["tags"] == ["wochenende"]


async def test_tags_do_not_break_up_a_spoken_sentence(store: BrainstormStore) -> None:
    """The sentence is shortened as if the tag were not there."""
    with_tag = await store.async_add_idea(
        "der rasen muss gemäht werden #garten", source="Alexa"
    )
    assert with_tag["text"] == "Rasen mähen #garten"


async def test_numbers_and_words_with_hash_are_no_tags(store: BrainstormStore) -> None:
    """'#1' is a number and 'a#b' no tag, '#3d-druck' is one."""
    idea = await store.async_add_idea("Prio #1 für a#b und #3d-druck", source="dashboard")
    assert idea["tags"] == ["3d-druck"]


async def test_tags_reach_the_cards(store: BrainstormStore) -> None:
    """Tags given by an action, not in the text, are shown to the cards too."""
    await store.async_add_idea("Lampe tauschen", source="dashboard", tags=["keller"])
    plain = await store.async_add_idea("Ohne Tag", source="dashboard")
    ideas = {i["id"]: i for i in store.get_overview_attributes()["ideas"]}
    assert [i["tags"] for i in ideas.values() if i["text"] == "Lampe tauschen"] == [["keller"]]
    assert "tags" not in ideas[plain["id"]]
