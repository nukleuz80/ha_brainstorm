"""Tests for the English rules."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from homeassistant.core import HomeAssistant

from custom_components.brainstorm.const import STORAGE_KEY
from custom_components.brainstorm.languages.en import (
    PACK,
    clean_text,
    extract_spoken_due,
    extract_spoken_priority,
    format_typed_text,
    parse_due,
    validate_ai_rewrite,
)
from custom_components.brainstorm.reminders import build_reminder_request
from custom_components.brainstorm.store import BrainstormStore

# A Tuesday
NOW = datetime(2026, 3, 10, 10, 0, tzinfo=timezone.utc)


def _at(days: int, hour: int, minute: int = 0) -> datetime:
    """Return a time relative to the test's now."""
    return (NOW + timedelta(days=days)).replace(hour=hour, minute=minute)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("the lawn has to be mowed", "Mow lawn"),
        ("the lawn needs to be mowed", "Mow lawn"),
        ("the lawn needs mowing", "Mow lawn"),
        ("the trash has to be taken out", "Take out trash"),
        ("the kids have to be picked up from the airport", "Pick up kids from the airport"),
        ("the car must be washed", "Wash car"),
        ("the bill should be paid", "Pay bill"),
        ("i need to call the doctor", "Call doctor"),
        ("we should probably call the plumber", "Call plumber"),
        ("i've got to buy milk", "Buy milk"),
        ("don't forget to buy milk", "Buy milk"),
        ("do not forget the milk", "Milk"),
        ("remember to fix the bike", "Fix bike"),
        ("remind me to water the plants", "Water plants"),
        ("note that we need to clean the patio", "Clean patio"),
        ("please write down that i need to clean the patio", "Clean patio"),
        ("can you note replace the battery", "Replace battery"),
        ("new idea build a shelf", "Build shelf"),
        ("um okay fix the fence", "Fix fence"),
        ("mow the lawn", "Mow lawn"),
        ("pick up the parcel from the post office", "Pick up parcel from the post office"),
        ("the printer is broken", "Printer broken"),
        ("buy milk.", "Buy milk"),
        ("the idea from anna", "Idea from anna"),
    ],
)
def test_clean_text(raw: str, expected: str) -> None:
    """Spoken sentences become short tasks."""
    assert clean_text(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("the bill wasn't paid", "The bill wasn't paid"),
        ("the bill was not paid", "The bill was not paid"),
        ("the lawn must not be mowed", "The lawn must not be mowed"),
        ("why was the door open?", "Why was the door open?"),
        ("if the door is open", "If the door is open"),
        ("the car needs gas", "The car needs gas"),
        ("the lawn has to be florped", "The lawn has to be florped"),
        ("i need to call mom because she is sick", "I need to call mom because she is sick"),
        ("the mower is cheap", "The mower is cheap"),
    ],
)
def test_sentences_that_keep_their_meaning(raw: str, expected: str) -> None:
    """A sentence that cannot be reduced completely keeps its words."""
    assert clean_text(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("plant the tomatoes", "Plant tomatoes"),
        ("paint the wall", "Paint wall"),
        ("check the iphone and the wifi", "Check iPhone and wifi".replace("wifi", "Wi-Fi")),
        ("call home assistant support", "Call Home Assistant support"),
    ],
)
def test_words_and_spellings(raw: str, expected: str) -> None:
    """Words that only look like a negation stay, known spellings are applied."""
    assert clean_text(raw) == expected


def test_typed_text_keeps_its_words() -> None:
    """Typed text only gets a capital first letter."""
    assert format_typed_text("the lawn has to be mowed") == "The lawn has to be mowed"


@pytest.mark.parametrize(
    ("spoken", "due", "text"),
    [
        ("call the doctor tomorrow", _at(1, 9), "call the doctor"),
        ("tomorrow at 8 take out the bins", _at(1, 8), "take out the bins"),
        ("call mom tomorrow at 8:30 am", _at(1, 8, 30), "call mom"),
        ("call mom tomorrow at 5", _at(1, 17), "call mom"),
        ("call mom tomorrow morning", _at(1, 8), "call mom"),
        ("call mom the day after tomorrow", _at(2, 9), "call mom"),
        ("call mom today at 5 pm", _at(0, 17), "call mom"),
        ("call mom tonight", _at(0, 19), "call mom"),
        ("call mom tonight at 9", _at(0, 21), "call mom"),
        ("call mom tonight at half past eight", _at(0, 20, 30), "call mom"),
        ("call mom on friday", _at(3, 9), "call mom"),
        ("call mom next monday at 5 pm", _at(6, 17), "call mom"),
        ("call mom next week", _at(6, 9), "call mom"),
        ("call mom in 2 hours", NOW + timedelta(hours=2), "call mom"),
        ("call mom in an hour", NOW + timedelta(hours=1), "call mom"),
        ("call mom in half an hour", NOW + timedelta(minutes=30), "call mom"),
        ("call mom in three days", _at(3, 9), "call mom"),
        ("pay rent on march 15th", _at(5, 9), "pay rent"),
        ("pay rent on the 15th of march", _at(5, 9), "pay rent"),
        ("call mom tomorrow at quarter to five", _at(1, 16, 45), "call mom"),
        ("call mom at noon", _at(0, 12), "call mom"),
        ("call mom at 9", _at(0, 21), "call mom"),
        ("call mom at 11", _at(0, 11), "call mom"),
    ],
)
def test_parse_due(spoken: str, due: datetime, text: str) -> None:
    """Spoken dates and times are found and leave the text."""
    assert parse_due(spoken, NOW) == (due, text)


def test_a_passed_month_date_means_next_year() -> None:
    """A date in the past is the one of next year."""
    assert parse_due("pay rent on january 5th", NOW)[0] == datetime(
        2027, 1, 5, 9, 0, tzinfo=timezone.utc
    )


@pytest.mark.parametrize(
    ("spoken", "due", "text"),
    [
        ("i need to call the doctor tomorrow", _at(1, 9), "i need to call the doctor"),
        ("pay the bill by friday", _at(3, 9), "pay the bill"),
        ("finish the report no later than tomorrow", _at(1, 9), "finish the report"),
    ],
)
def test_extract_spoken_due(spoken: str, due: datetime, text: str) -> None:
    """A clear day becomes a due date."""
    assert extract_spoken_due(spoken, NOW) == (due, text)


@pytest.mark.parametrize(
    "spoken",
    [
        "water plants every monday",
        "the plumber was here on friday",
        "call mom in the morning",
        "what is on tomorrow?",
        "today",
        "check tomorrow's weather",
        "bins go out on mondays",
        "mow lawn today at 8 am",
        "3/4 of the wall",
    ],
)
def test_no_due_date(spoken: str) -> None:
    """Recurring or past days, passed times and plain times are no due date."""
    assert extract_spoken_due(spoken, NOW) == (None, spoken)


@pytest.mark.parametrize(
    ("spoken", "text", "priority"),
    [
        ("urgently call the doctor", "call the doctor", "urgent"),
        ("call the doctor asap", "call the doctor", "urgent"),
        ("call the doctor as soon as possible", "call the doctor", "urgent"),
        ("call the doctor right away", "call the doctor", "urgent"),
        ("really important call the bank", "call the bank", "high"),
        ("definitely call the bank", "call the bank", "high"),
        ("paint the shed someday", "paint the shed", "low"),
        ("paint the shed when there's time", "paint the shed", "low"),
        ("paint the shed no rush", "paint the shed", "low"),
        ("this is not urgent", "this is not urgent", None),
        ("the call isn't important", "the call isn't important", None),
        ("the call is really important", "the call is really important", None),
        ("is this urgent?", "is this urgent?", None),
        ("buy milk", "buy milk", None),
    ],
)
def test_extract_spoken_priority(
    spoken: str, text: str, priority: str | None
) -> None:
    """Priority words are found anywhere, unless they describe something else."""
    assert extract_spoken_priority(spoken) == (text, priority)


@pytest.mark.parametrize(
    ("candidate", "result"),
    [
        ("Mow lawn", "Mow lawn"),
        ("Mow the lawn.", "Mow the lawn"),
        ("Mow lawn on Friday", None),
        ("Do not mow lawn", None),
        ("Mow lawn 5 times", None),
        ("", None),
    ],
)
def test_validate_ai_rewrite(candidate: str, result: str | None) -> None:
    """An AI may only shorten what was said."""
    assert validate_ai_rewrite("the lawn has to be mowed", "Mow lawn", candidate) == result


def test_ai_prompt_contains_the_note() -> None:
    """The AI gets the spoken text and the result of the rules."""
    prompt = PACK.ai_cleanup_prompt("the lawn has to be mowed", "Mow lawn")
    assert "the lawn has to be mowed" in prompt
    assert "Mow lawn" in prompt


@pytest.fixture
async def store(hass: HomeAssistant, hass_storage: dict[str, Any]) -> BrainstormStore:
    """Return a loaded store of a new installation in English."""
    hass.config.language = "en"
    instance = BrainstormStore(hass, {})
    await instance.async_load()
    return instance


async def test_new_installation_gets_english_categories(store: BrainstormStore) -> None:
    """Only a new installation gets these names."""
    assert store.categories == [
        "Inbox",
        "Smart Home",
        "House & Garden",
        "Projects",
        "Daily Life",
    ]


@pytest.mark.parametrize(
    ("spoken", "text", "category", "priority"),
    [
        ("the lawn has to be mowed", "Mow lawn", "House & Garden", "medium"),
        ("in the garden: plant roses", "Plant roses", "House & Garden", "medium"),
        ("for the garden fertilize tomatoes", "Fertilize tomatoes", "House & Garden", "medium"),
        ("for smart home replace the sensor", "Replace sensor", "Smart Home", "medium"),
        ("zigbee sensor needs a new battery", "Zigbee sensor needs a new battery", "Smart Home", "medium"),
        ("project shelf build it", "Shelf build it", "Projects", "medium"),
        ("buy milk", "Buy milk", "Daily Life", "medium"),
        ("urgent: call the dentist", "Call dentist", "Daily Life", "urgent"),
        ("high priority call the dentist", "Call dentist", "Daily Life", "high"),
        ("low priority call the dentist", "Call dentist", "Daily Life", "low"),
        ("xyzzy", "Xyzzy", "Inbox", "medium"),
    ],
)
async def test_parse_text_and_category(
    store: BrainstormStore, spoken: str, text: str, category: str, priority: str
) -> None:
    """Categories and priorities are found in English sentences."""
    assert store.parse_text_and_category(spoken)[0:2] == (text, category)
    assert store.parse_text_and_category(spoken)[3] == priority


async def test_garden_stays_when_it_is_the_subject(store: BrainstormStore) -> None:
    """A category name that is the subject stays part of the text."""
    text, category, _, _ = store.parse_text_and_category("garden needs a new fence")
    assert text == "Garden needs a new fence"
    assert category == "House & Garden"


async def test_english_keywords_reach_german_categories(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    """Stored German categories work in English without being renamed."""
    hass.config.language = "en"
    stored = {
        "categories": ["Inbox", "Smarthome", "Haus & Garten", "Projekte", "Alltag", "Axis"],
        "ideas": [
            {"id": "abc", "text": "Rasen mähen", "category": "Haus & Garten", "status": "active"}
        ],
    }
    hass_storage[STORAGE_KEY] = {"version": 1, "minor_version": 1, "key": STORAGE_KEY, "data": stored}
    store = BrainstormStore(hass, {})
    await store.async_load()

    assert store.categories == stored["categories"]
    assert store.parse_text_and_category("the lawn has to be mowed")[:2] == (
        "Mow lawn",
        "Haus & Garten",
    )
    assert store.parse_text_and_category("project shelf build it")[1] == "Projekte"
    assert store.parse_text_and_category("für den Garten Tomaten düngen", language="de")[:2] == (
        "Tomaten düngen",
        "Haus & Garten",
    )
    assert [idea["text"] for idea in store.ideas] == ["Rasen mähen"]


async def test_add_idea_uses_the_language(store: BrainstormStore) -> None:
    """A spoken English note gets its date and priority."""
    idea = await store.async_add_idea(
        "i really need to call the doctor tomorrow asap", source="assist"
    )
    assert idea["text"] == "Call doctor"
    assert idea["priority"] == "urgent"
    assert idea["due"]
    assert idea["raw_text"] == "i really need to call the doctor tomorrow asap"


@pytest.mark.parametrize(
    ("due", "spoken"),
    [
        (_at(0, 17), "today at 5 pm"),
        (_at(1, 8, 30), "tomorrow at 8:30 am"),
        (_at(2, 12), "the day after tomorrow at 12 pm"),
        (_at(3, 0), "on Friday, March 13, at 12 am"),
    ],
)
def test_format_due(due: datetime, spoken: str) -> None:
    """Dates are read the way people say them."""
    assert PACK.format_due(due, NOW.date()) == spoken


async def test_english_reminder_words(hass: HomeAssistant) -> None:
    """A reminder understands who, when and where in English."""
    hass.config.language = "en"
    hass.states.async_set("person.alex", "home", {"friendly_name": "Alex"})
    hass.states.async_set("zone.market", "0", {"friendly_name": "Market"})
    options = {
        "persons_enabled": True,
        "arrival_enabled": True,
        "places_enabled": True,
        "default_person": "person.me",
    }
    home = build_reminder_request(
        hass, options, "the bins when i get home", NOW
    )
    assert home.trigger == {"zone": "zone.home", "person": "person.me"}
    assert home.text == "the bins"
    place = build_reminder_request(
        hass, options, "the milk when i get to market", NOW
    )
    assert place.trigger == {"zone": "zone.market", "person": "person.me"}
    assert place.text == "the milk"
    person = build_reminder_request(
        hass, options, "alex tomorrow at 8 to take out the bins", NOW
    )
    assert person.assignee == "person.alex"
    assert person.due == _at(1, 8)
    assert person.text == "take out the bins"


async def test_english_texts_of_a_store(store: BrainstormStore) -> None:
    """Spoken overviews are in the language of Home Assistant."""
    assert store.get_overview_text() == "You have no open notes in Brainstorm right now."
    await store.async_add_idea("buy milk", category="Daily Life", source="dashboard")
    await store.async_add_idea("buy eggs", category="Daily Life", source="dashboard")
    assert store.get_overview_text() == (
        "You have 2 entries: 2 in Daily Life. Which category?"
    )
    assert store.get_announcement_text("Daily Life") in (
        "Daily Life has two entries: Buy eggs and Buy milk.",
        "Daily Life has two entries: Buy milk and Buy eggs.",
    )
    assert store.get_announcement_text("Daily Life", language="de").startswith(
        "Daily Life hat zwei Einträge: "
    )
