"""Named holidays as spoken due dates (v1.30.2)."""
from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from custom_components.brainstorm.languages import de, en
from custom_components.brainstorm.languages.common import holiday_date

NOW = datetime(2026, 11, 27, 12, 0, tzinfo=timezone.utc)


def _at(month: int, day: int, hour: int = 9, year: int = 2026) -> datetime:
    return datetime(year, month, day, hour, 0, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    ("key", "today", "expected"),
    [
        ("advent_1", date(2026, 11, 27), date(2026, 11, 29)),
        ("advent_4", date(2026, 11, 27), date(2026, 12, 20)),
        # Christmas Eve on a Sunday is the fourth Advent itself
        ("advent_4", date(2023, 12, 1), date(2023, 12, 24)),
        ("advent_1", date(2023, 12, 1), date(2023, 12, 3)),
        ("christmas_eve", date(2026, 12, 24), date(2026, 12, 24)),
        ("christmas_eve", date(2026, 12, 25), date(2027, 12, 24)),
        ("new_year", date(2026, 11, 27), date(2027, 1, 1)),
        ("easter", date(2026, 11, 27), date(2027, 3, 28)),
        ("easter", date(2025, 1, 1), date(2025, 4, 20)),
        ("good_friday", date(2024, 1, 1), date(2024, 3, 29)),
        ("pentecost_monday", date(2026, 1, 1), date(2026, 5, 25)),
    ],
)
def test_holiday_date(key: str, today: date, expected: date) -> None:
    """Holidays fall on the right day, the next one once a year has passed."""
    assert holiday_date(key, today) == expected


@pytest.mark.parametrize(
    ("spoken", "due", "text"),
    [
        ("am ersten Advent um 15 Uhr an den Adventskranz", _at(11, 29, 15), "den Adventskranz"),
        ("an Heiligabend Oma anrufen", _at(12, 24), "Oma anrufen"),
        ("am Heiligen Abend Kirche", _at(12, 24), "Kirche"),
        ("am 4. Advent Plätzchen backen", _at(12, 20), "Plätzchen backen"),
        ("am zweiten Weihnachtsfeiertag Tante besuchen", _at(12, 26), "Tante besuchen"),
        ("an Weihnachten Oma besuchen", _at(12, 25), "Oma besuchen"),
        ("bis Silvester Steuer machen", _at(12, 31), "Steuer machen"),
        ("am Nikolaus Stiefel putzen", _at(12, 6), "Stiefel putzen"),
        ("an Neujahr ausschlafen", _at(1, 1, year=2027), "ausschlafen"),
        ("an Ostern Eier verstecken", _at(3, 28, year=2027), "Eier verstecken"),
        ("Steuer spätestens an Weihnachten machen", _at(12, 25), "Steuer machen"),
        ("bis spätestens Silvester Steuer machen", _at(12, 31), "Steuer machen"),
        ("an Weihnachten an die Geschenke denken", _at(12, 25), "die Geschenke denken"),
    ],
)
def test_german_holiday_is_a_due_date(spoken: str, due: datetime, text: str) -> None:
    """'am ersten Advent' means that Sunday, not today."""
    assert de.extract_spoken_due(spoken, NOW) == (due, text)


@pytest.mark.parametrize(
    "spoken",
    [
        "Silvester Raketen kaufen",
        "Geschenke zu Weihnachten kaufen",
        "Geschenke für Nikolaus besorgen",
        "Brief an Nikolaus schreiben",
        # 'an' names what to think of (review of v1.30.2)
        "erinnere mich an Halloween Kostüm kaufen",
        "an Weihnachten denken",
        "denk an Silvester",
    ],
)
def test_german_holiday_without_preposition_stays_text(spoken: str) -> None:
    """A holiday that only says what the note is about keeps its word."""
    assert de.extract_spoken_due(spoken, NOW) == (None, spoken)


def test_german_reminder_on_a_holiday() -> None:
    """The reminder path no longer falls back to today."""
    due, _text = de.parse_due("erinnere mich am ersten advent um 15 uhr an den kranz", NOW)
    assert due == _at(11, 29, 15)


@pytest.mark.parametrize(
    ("spoken", "due", "text"),
    [
        ("call grandma on Christmas Eve", _at(12, 24), "call grandma"),
        ("on the first Sunday of Advent light a candle", _at(11, 29), "light a candle"),
        ("by New Year's Eve do the taxes", _at(12, 31), "do the taxes"),
        ("decorate on Christmas Day at 5 pm", _at(12, 25, 17), "decorate"),
        ("on New Year's Day sleep in", _at(1, 1, year=2027), "sleep in"),
        ("by New Year’s Eve do taxes", _at(12, 31), "do taxes"),
        ("do taxes at the latest by Christmas", _at(12, 25), "do taxes"),
        ("do taxes no later than Christmas Eve", _at(12, 24), "do taxes"),
    ],
)
def test_english_holiday_is_a_due_date(spoken: str, due: datetime, text: str) -> None:
    """English holidays work the same way."""
    assert en.extract_spoken_due(spoken, NOW) == (due, text)


@pytest.mark.parametrize("spoken", ["buy presents for Christmas", "Christmas Day dinner plan"])
def test_english_holiday_without_preposition_stays_text(spoken: str) -> None:
    """Without 'on', 'by' or 'until' the holiday stays in the note."""
    assert en.extract_spoken_due(spoken, NOW) == (None, spoken)
