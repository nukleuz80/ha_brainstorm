"""Tests for the time tracking on notes and the Gantt rows."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pytest
from homeassistant.core import Context, HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.util import dt as dt_util

from custom_components.brainstorm import timetrack
from custom_components.brainstorm.statistics import build_statistics

from .conftest import SetupEntry

NOW = dt_util.as_local(datetime(2026, 11, 18, 12, 0, tzinfo=dt_util.UTC))
HOUR = timedelta(hours=1)


def test_start_stop_and_sum() -> None:
    """The log keeps finished spans, the running timer counts along."""
    idea: dict[str, Any] = {"id": "a", "status": "active"}
    assert timetrack.start_timer(idea, NOW - 3 * HOUR, "u1")
    assert not timetrack.start_timer(idea, NOW, "u1")
    assert timetrack.tracked_seconds(idea, NOW) == 3 * 3600
    assert timetrack.stop_timer(idea, NOW - 2 * HOUR)
    assert "timer" not in idea
    assert idea["time_log"][0][2] == "u1"
    assert not timetrack.stop_timer(idea, NOW)

    timetrack.start_timer(idea, NOW - HOUR, "u1")
    assert timetrack.tracked_seconds(idea, NOW) == 2 * 3600
    # Only the time inside the window counts
    assert timetrack.tracked_seconds(idea, NOW, NOW - 30 * timedelta(minutes=1)) == 1800


def test_forgotten_timer_is_capped() -> None:
    """A timer left running counts no longer than twelve hours."""
    idea: dict[str, Any] = {"id": "a"}
    timetrack.start_timer(idea, NOW - 40 * HOUR, None)
    assert timetrack.tracked_seconds(idea, NOW) == 12 * 3600
    timetrack.stop_timer(idea, NOW)
    assert timetrack.tracked_seconds(idea, NOW) == 12 * 3600


def test_summary_and_gantt() -> None:
    """Sums per category and bars from the first work to the due date."""
    work = {
        "id": "w",
        "text": "Bericht",
        "category": "Arbeit",
        "status": "active",
        "created_at": (NOW - 100 * HOUR).isoformat(),
        "due": (NOW + 48 * HOUR).isoformat(),
        "time_log": [[(NOW - 5 * HOUR).isoformat(), (NOW - 3 * HOUR).isoformat(), "u"]],
    }
    home = {
        "id": "h",
        "text": "Garten",
        "category": "Haus",
        "status": "completed",
        "created_at": (NOW - 10 * HOUR).isoformat(),
        "completed_at": (NOW - HOUR).isoformat(),
        "time_log": [
            [(NOW - 4 * HOUR).isoformat(), (NOW - 3.5 * HOUR).isoformat(), "u"]
        ],
    }
    plain = {"id": "p", "text": "Ohne", "category": "Haus", "status": "active"}
    stats = build_statistics([work, home, plain], NOW, {})
    time = stats["time"]
    assert time["total_seconds"] == 2 * 3600 + 1800
    assert time["categories"][0] == {"category": "Arbeit", "seconds": 7200}
    assert [note["id"] for note in time["notes"]] == ["w", "h"]

    gantt = {row["id"]: row for row in stats["gantt"]}
    assert set(gantt) == {"w", "h"}
    assert dt_util.parse_datetime(gantt["w"]["start"]) == NOW - 5 * HOUR
    assert dt_util.parse_datetime(gantt["w"]["end"]) == NOW + 48 * HOUR
    assert gantt["h"]["done"]
    assert dt_util.parse_datetime(gantt["h"]["end"]) == NOW - HOUR


async def _add(hass: HomeAssistant, text: str) -> str:
    response = await hass.services.async_call(
        "brainstorm",
        "add_idea",
        {"text": text, "category": "Inbox"},
        blocking=True,
        return_response=True,
    )
    return response["idea"]["id"]


async def _track(
    hass: HomeAssistant, idea_id: str, user: Any, action: str = "toggle"
) -> dict[str, Any]:
    return await hass.services.async_call(
        "brainstorm",
        "track_time",
        {"id": idea_id, "action": action},
        blocking=True,
        return_response=True,
        context=Context(user_id=user.id),
    )


async def test_track_time_service(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_admin_user: Any
) -> None:
    """One timer per person, stopped when the note is done."""
    entry = await setup_entry()
    store = entry.runtime_data
    first = await _add(hass, "Steuer machen")
    second = await _add(hass, "Keller aufräumen")

    result = await _track(hass, first, hass_admin_user)
    assert result["running"]
    assert store.get_idea(first)["timer"]["by"] == hass_admin_user.id

    listed = next(
        i for i in store.get_overview_attributes()["ideas"] if i["id"] == first
    )
    assert listed["timer"]["by"] == hass_admin_user.id
    assert "time_spent" in listed

    # Starting the second note stops the first
    await _track(hass, second, hass_admin_user, "start")
    assert "timer" not in store.get_idea(first)
    assert store.get_idea(first)["time_log"]
    assert store.get_idea(second)["timer"]

    # Ticking off stops it, and a done note takes no new timer
    await hass.services.async_call(
        "brainstorm",
        "update_idea",
        {"id": second, "status": "completed"},
        blocking=True,
    )
    assert "timer" not in store.get_idea(second)
    with pytest.raises(ServiceValidationError):
        await _track(hass, second, hass_admin_user, "start")

    # Stop on a note without a timer changes nothing
    result = await _track(hass, first, hass_admin_user, "stop")
    assert not result["running"]


def test_broken_log_entries_are_skipped() -> None:
    """Short, unreadable or backwards entries of the log count nothing."""
    idea: dict[str, Any] = {
        "id": "a",
        "status": "active",
        "time_log": [
            "nonsense",
            [NOW.isoformat()],
            ["gestern", NOW.isoformat()],
            [NOW.isoformat(), (NOW - HOUR).isoformat()],
            [(NOW - HOUR).isoformat(), NOW.isoformat(), "u1"],
        ],
    }
    assert timetrack.tracked_seconds(idea, NOW) == 3600
    # Only the part after "since" counts
    assert timetrack.tracked_seconds(idea, NOW, since=NOW - HOUR / 2) == 1800


def test_a_forgotten_timer_counts_at_most_twelve_hours() -> None:
    """A timer left running stops counting after TIMER_MAX, also when stopped."""
    idea: dict[str, Any] = {"id": "a", "status": "active"}
    timetrack.start_timer(idea, NOW - 20 * HOUR, None)
    assert timetrack.tracked_seconds(idea, NOW) == 12 * 3600
    assert timetrack.stop_timer(idea, NOW)
    assert timetrack.tracked_seconds(idea, NOW) == 12 * 3600
    assert not timetrack.stop_timer(idea, NOW)
    assert timetrack.running_since({"timer": "broken"}) is None


def test_the_log_keeps_the_newest_entries() -> None:
    """The log never grows beyond TIME_LOG_MAX entries."""
    idea: dict[str, Any] = {
        "id": "a",
        "time_log": [[None, None]] * timetrack.TIME_LOG_MAX,
    }
    timetrack.start_timer(idea, NOW - HOUR, "u1")
    timetrack.stop_timer(idea, NOW)
    assert len(idea["time_log"]) == timetrack.TIME_LOG_MAX
    assert idea["time_log"][-1][2] == "u1"


def test_summary_lists_the_top_notes() -> None:
    """The summary keeps the busiest notes, sorted, and counts running timers."""
    ideas = [
        {
            "id": f"n{number}",
            "text": f"Notiz {number}",
            "category": "Arbeit" if number % 2 else "Alltag",
            "time_log": [[(NOW - (number + 1) * HOUR).isoformat(), NOW.isoformat()]],
        }
        for number in range(timetrack.TOP_NOTES + 2)
    ]
    ideas.append({"id": "idle", "text": "Nichts", "category": "Alltag"})
    timetrack.start_timer(ideas[0], NOW - HOUR, None)
    summary = timetrack.time_summary(ideas, NOW, None)
    assert len(summary["notes"]) == timetrack.TOP_NOTES
    assert summary["notes"][0]["id"] == f"n{timetrack.TOP_NOTES + 1}"
    assert summary["running"] == 1
    assert {c["category"] for c in summary["categories"]} == {"Arbeit", "Alltag"}
    assert summary["total_seconds"] == sum(c["seconds"] for c in summary["categories"])


def test_gantt_skips_what_does_not_fit() -> None:
    """Archived notes, notes without time and bars that ended earlier stay out."""
    week_ago = NOW - timedelta(days=7)
    ideas = [
        {"id": "archived", "status": "archived", "due": NOW.isoformat()},
        {"id": "nothing", "status": "active"},
        {
            "id": "old",
            "status": "completed",
            "created_at": (week_ago - timedelta(days=3)).isoformat(),
            "completed_at": (week_ago - timedelta(days=1)).isoformat(),
            "due": (week_ago - timedelta(days=2)).isoformat(),
        },
        {
            "id": "backwards",
            "status": "active",
            "created_at": NOW.isoformat(),
            "due": (NOW - timedelta(days=1)).isoformat(),
        },
    ]
    rows = timetrack.gantt_rows(ideas, NOW, week_ago)
    assert [row["id"] for row in rows] == ["backwards"]
    assert rows[0]["start"] < rows[0]["end"]
