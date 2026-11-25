"""Tests for notes put off until a later day ("Hecke schneiden ab März")."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from freezegun.api import FrozenDateTimeFactory
import pytest

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_capture_events

from custom_components.brainstorm.languages.de import extract_snooze
from custom_components.brainstorm.languages.en import extract_snooze as extract_snooze_en
from custom_components.brainstorm.store import clean_snooze, is_snoozed

from .conftest import SetupEntry

NOW = datetime(2026, 11, 25, 10, 0)


async def _call(hass: HomeAssistant, service: str, **data: Any) -> dict[str, Any] | None:
    return await hass.services.async_call(
        "brainstorm",
        service,
        data,
        blocking=True,
        return_response=service == "add_idea",
    )


def _listed(store: Any, idea_id: str) -> dict[str, Any]:
    return next(i for i in store.get_overview_attributes()["ideas"] if i["id"] == idea_id)


@pytest.mark.parametrize(
    ("spoken", "day", "rest"),
    [
        ("hecke schneiden ab märz", date(2027, 3, 1), "hecke schneiden"),
        ("rasen mähen erst im frühjahr", date(2027, 3, 1), "rasen mähen"),
        ("pool öffnen ab sommer", date(2027, 6, 1), "pool öffnen"),
        ("weihnachtsdeko ab dezember", date(2026, 12, 1), "weihnachtsdeko"),
        ("laub rechen ab november", date(2027, 11, 1), "laub rechen"),
        ("spielhaus streichen ab dem 3. april", date(2027, 4, 3), "spielhaus streichen"),
        ("reifen wechseln nicht vor dem 15.3.", date(2027, 3, 15), "reifen wechseln"),
        ("ab nächster woche zahnarzt anrufen", date(2026, 11, 30), "zahnarzt anrufen"),
        ("garage aufräumen ab nächsten monat", date(2026, 12, 1), "garage aufräumen"),
        ("fenster putzen, ab april", date(2027, 4, 1), "fenster putzen"),
        # A due date, a time, a verb particle and a bare snooze stay as they are
        ("termin am 3. märz", None, "termin am 3. märz"),
        ("ab 18 uhr kochen", None, "ab 18 uhr kochen"),
        ("müll ab holen", None, "müll ab holen"),
        ("ab märz", None, "ab märz"),
    ],
)
def test_german_snooze_words(spoken: str, day: date | None, rest: str) -> None:
    """Test which German words put a note off and until when."""
    assert extract_snooze(spoken, NOW) == (day, rest)


def test_english_snooze_words() -> None:
    """Test the English words for a later start."""
    assert extract_snooze_en("trim hedge from march", NOW) == (date(2027, 3, 1), "trim hedge")
    assert extract_snooze_en("open pool not before summer", NOW) == (
        date(2027, 6, 1),
        "open pool",
    )
    assert extract_snooze_en("meet from 5 pm", NOW) == (None, "meet from 5 pm")


def test_only_a_day_ahead_counts() -> None:
    """Test that today, a past day or broken data is no snooze."""
    today = date(2026, 11, 25)
    assert clean_snooze("2026-12-01", today) == "2026-12-01"
    assert clean_snooze(date(2026, 11, 25), today) is None
    assert clean_snooze("2026-11-01", today) is None
    assert clean_snooze("bald", today) is None
    assert is_snoozed({"status": "active", "snoozed_until": "2026-12-01"}, today)
    assert not is_snoozed({"status": "completed", "snoozed_until": "2026-12-01"}, today)
    assert not is_snoozed({"status": "active", "snoozed_until": "2026-11-25"}, today)


async def test_a_snoozed_note_is_listed_but_counts_nowhere(
    hass: HomeAssistant, setup_entry: SetupEntry, freezer: FrozenDateTimeFactory
) -> None:
    """Test that the cards get the note, while counts, lists and Alexa skip it."""
    freezer.move_to("2026-11-25 10:00:00+01:00")
    entry = await setup_entry()
    store = entry.runtime_data
    hedge = await store.async_add_idea("Hecke schneiden", category="Inbox")
    await store.async_add_idea("Milch", category="Inbox")

    await _call(hass, "update_idea", id=hedge["id"], snoozed_until="2027-03-01")
    assert store.get_idea(hedge["id"])["snoozed_until"] == "2027-03-01"
    overview = store.get_overview_attributes()
    assert _listed(store, hedge["id"])["snoozed_until"] == "2027-03-01"
    assert overview["active_count"] == 1
    assert overview["snoozed_count"] == 1
    assert overview["category_counts"]["Inbox"] == 1
    assert store.category_counts["Inbox"] == 1
    assert [i["text"] for i in store.get_ideas_by_category("Inbox")] == ["Milch"]
    assert len(store.get_ideas_by_category("Inbox", include_snoozed=True)) == 2
    assert "Hecke" not in store.get_announcement_text()
    await hass.async_block_till_done()
    assert hass.states.get("sensor.brainstorm_ideen_ubersicht").state == "1"

    # A day that has passed or an empty value takes the snooze away
    await _call(hass, "update_idea", id=hedge["id"], snoozed_until="2026-11-01")
    assert "snoozed_until" not in store.get_idea(hedge["id"])
    await _call(hass, "update_idea", id=hedge["id"], snoozed_until="2027-03-01")
    await _call(hass, "update_idea", id=hedge["id"], snoozed_until=None)
    assert "snoozed_until" not in store.get_idea(hedge["id"])


async def test_spoken_snooze_puts_a_note_off(
    hass: HomeAssistant, setup_entry: SetupEntry, freezer: FrozenDateTimeFactory
) -> None:
    """Test that "ab März" spoken to Alexa puts the note off and leaves the text."""
    freezer.move_to("2026-11-25 10:00:00+01:00")
    entry = await setup_entry()
    store = entry.runtime_data
    idea = await store.async_add_idea("hecke schneiden ab märz", source="alexa_skill")
    assert idea["text"] == "Hecke schneiden"
    assert idea["snoozed_until"] == "2027-03-01"
    assert idea["raw_text"] == "hecke schneiden ab märz"
    assert idea["due"] is None

    # Typed into the card, the words stay part of the note
    typed = await store.async_add_idea("Konzert ab März planen", source="dashboard")
    assert "snoozed_until" not in typed

    # The action takes a day directly
    response = await _call(
        hass, "add_idea", text="Pool öffnen", category="Inbox", snoozed_until="2027-06-01"
    )
    assert response is not None
    assert response["idea"]["snoozed_until"] == "2027-06-01"


async def test_the_sentence_test_shows_the_snooze(
    hass: HomeAssistant, setup_entry: SetupEntry, freezer: FrozenDateTimeFactory
) -> None:
    """Test that the sentence test tells until when a note is put off."""
    freezer.move_to("2026-11-25 10:00:00+01:00")
    entry = await setup_entry()
    preview = entry.runtime_data.preview_idea("Rasen mähen erst im Frühjahr", "voice")
    assert preview["snoozed_until"] == "2027-03-01"
    assert preview["text"] == "Rasen mähen"


async def test_a_note_comes_back_on_its_day(
    hass: HomeAssistant, setup_entry: SetupEntry, freezer: FrozenDateTimeFactory
) -> None:
    """Test that the note is back at the top on its day, with an event."""
    freezer.move_to("2026-11-25 10:00:00+01:00")
    entry = await setup_entry()
    store = entry.runtime_data
    hedge = await store.async_add_idea("Hecke schneiden", category="Inbox")
    await store.async_add_idea("Milch", category="Inbox")
    await _call(hass, "update_idea", id=hedge["id"], snoozed_until="2026-11-26")
    woke_events = async_capture_events(hass, "brainstorm_idea_woke")

    assert await store.async_wake_snoozed() == []
    freezer.move_to("2026-11-26 12:00:00+00:00")
    store.async_new_day()
    await hass.async_block_till_done()

    assert "snoozed_until" not in store.get_idea(hedge["id"])
    assert store.get_ideas_by_category("Inbox")[0]["id"] == hedge["id"]
    assert [e.data["text"] for e in woke_events] == ["Hecke schneiden"]


async def test_ticking_off_ends_the_snooze(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a note done early does not come back on its day."""
    entry = await setup_entry()
    store = entry.runtime_data
    idea = await store.async_add_idea("Hecke schneiden", category="Inbox")
    later = dt_util.now().date().replace(day=1, year=dt_util.now().year + 1)
    await _call(hass, "update_idea", id=idea["id"], snoozed_until=later.isoformat())
    await _call(hass, "update_idea", id=idea["id"], status="completed")
    assert "snoozed_until" not in store.get_idea(idea["id"])


async def test_the_briefing_names_what_came_back(
    hass: HomeAssistant, setup_entry: SetupEntry, freezer: FrozenDateTimeFactory
) -> None:
    """Test that the briefing says what is back today and skips what still waits."""
    freezer.move_to("2026-11-25 12:00:00+00:00")
    entry = await setup_entry()
    store = entry.runtime_data
    reminders = store.reminders
    hedge = await store.async_add_idea("Hecke schneiden", category="Inbox")
    pool = await store.async_add_idea("Pool öffnen", category="Inbox")
    await _call(hass, "update_idea", id=hedge["id"], snoozed_until="2026-11-26")
    # Due today but still put off: the briefing keeps quiet about it
    await _call(
        hass,
        "update_idea",
        id=pool["id"],
        snoozed_until="2027-06-01",
        due="2026-11-25T08:00:00+00:00",
    )
    assert reminders.build_digest(dt_util.now()) is None

    freezer.move_to("2026-11-26 12:00:00+00:00")
    await store.async_wake_snoozed()
    assert store.get_idea(hedge["id"])["woke_on"] == "2026-11-26"
    assert reminders.build_digest(dt_util.now()) == "Heute wieder da: Hecke schneiden."

    # The next day it is a note like any other
    freezer.move_to("2026-11-27 12:00:00+00:00")
    assert reminders.build_digest(dt_util.now()) is None


async def test_the_review_names_what_comes_back_this_week(
    hass: HomeAssistant, setup_entry: SetupEntry, freezer: FrozenDateTimeFactory
) -> None:
    """Test that the weekly review lists the notes back within seven days."""
    freezer.move_to("2026-11-25 12:00:00+00:00")
    entry = await setup_entry()
    store = entry.runtime_data
    for text, day in (
        ("Reifen wechseln", "2026-11-30"),
        ("Hecke schneiden", "2026-11-27"),
        ("Pool öffnen", "2027-06-01"),
    ):
        idea = await store.async_add_idea(text, category="Inbox")
        await _call(hass, "update_idea", id=idea["id"], snoozed_until=day)
    assert store.reminders.build_review(dt_util.now()) == (
        "In den nächsten 7 Tagen kommt zurück: Hecke schneiden und Reifen wechseln."
    )
