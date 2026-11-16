"""Track the time spent on notes, and lay them out as a Gantt chart.

A running timer sits on the note as {"since", "by"}; stopping it adds a
[start, end, user] entry to the note's time log. Each person runs at most
one timer, so starting one stops the other.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from homeassistant.util import dt as dt_util

from .const import (
    ATTR_CATEGORY,
    ATTR_COMPLETED_AT,
    ATTR_CREATED_AT,
    ATTR_DUE,
    ATTR_ID,
    ATTR_STATUS,
    ATTR_TEXT,
    ATTR_TIME_LOG,
    ATTR_TIMER,
)

# Old entries go first once a note has this many
TIME_LOG_MAX = 500
# A timer left running longer than this was forgotten, it counts this long
TIMER_MAX = timedelta(hours=12)
GANTT_MAX_ROWS = 40
TOP_NOTES = 10


def _parse(value: Any) -> datetime | None:
    return dt_util.parse_datetime(str(value or "")) if value else None


def running_since(idea: dict[str, Any]) -> datetime | None:
    """Return when the timer of a note started, or None."""
    timer = idea.get(ATTR_TIMER)
    return _parse(timer.get("since")) if isinstance(timer, dict) else None


def _spans(idea: dict[str, Any], now: datetime) -> list[tuple[datetime, datetime]]:
    spans: list[tuple[datetime, datetime]] = []
    for entry in idea.get(ATTR_TIME_LOG) or []:
        if not isinstance(entry, list | tuple) or len(entry) < 2:
            continue
        start, end = _parse(entry[0]), _parse(entry[1])
        if start and end and end > start:
            spans.append((start, end))
    if since := running_since(idea):
        spans.append((since, min(now, since + TIMER_MAX)))
    return spans


def tracked_seconds(
    idea: dict[str, Any], now: datetime, since: datetime | None = None
) -> int:
    """Add up the tracked time of a note, the running timer included."""
    total = 0.0
    for start, end in _spans(idea, now):
        if since is not None:
            start = max(start, since)
        if end > start:
            total += (end - start).total_seconds()
    return int(total)


def start_timer(idea: dict[str, Any], now: datetime, user_id: str | None) -> bool:
    """Start the timer of a note; False when it runs already."""
    if running_since(idea) is not None:
        return False
    idea[ATTR_TIMER] = {"since": now.isoformat(), "by": user_id}
    return True


def stop_timer(idea: dict[str, Any], now: datetime) -> bool:
    """Stop the timer of a note and log its time; False when none ran."""
    timer = idea.pop(ATTR_TIMER, None)
    since = _parse(timer.get("since")) if isinstance(timer, dict) else None
    if since is None:
        return False
    end = min(now, since + TIMER_MAX)
    if end > since:
        log = list(idea.get(ATTR_TIME_LOG) or [])
        log.append([since.isoformat(), end.isoformat(), timer.get("by")])
        idea[ATTR_TIME_LOG] = log[-TIME_LOG_MAX:]
    return True


def time_summary(
    ideas: list[dict[str, Any]], now: datetime, since: datetime | None
) -> dict[str, Any]:
    """Sum up the tracked time since a moment, per category and per note."""
    per_category: dict[str, int] = {}
    per_note: list[dict[str, Any]] = []
    running = 0
    for idea in ideas:
        seconds = tracked_seconds(idea, now, since)
        if seconds <= 0:
            continue
        category = str(idea.get(ATTR_CATEGORY) or "")
        per_category[category] = per_category.get(category, 0) + seconds
        is_running = running_since(idea) is not None
        running += is_running
        per_note.append(
            {
                "id": idea.get(ATTR_ID),
                "text": idea.get(ATTR_TEXT),
                "category": category,
                "seconds": seconds,
                "running": is_running,
            }
        )
    per_note.sort(key=lambda item: -item["seconds"])
    return {
        "total_seconds": sum(per_category.values()),
        "running": running,
        "categories": [
            {"category": name, "seconds": seconds}
            for name, seconds in sorted(per_category.items(), key=lambda i: -i[1])
        ],
        "notes": per_note[:TOP_NOTES],
    }


def gantt_rows(
    ideas: list[dict[str, Any]], now: datetime, since: datetime
) -> list[dict[str, Any]]:
    """Lay out the notes with a due date or tracked time as bars.

    A bar starts with the first tracked time, or else when the note was added,
    and ends at the due date, or when it was done. Bars that ended before
    the window are left out.
    """
    rows: list[dict[str, Any]] = []
    for idea in ideas:
        status = idea.get(ATTR_STATUS)
        if status not in ("active", "completed"):
            continue
        spans = _spans(idea, now)
        due = _parse(idea.get(ATTR_DUE))
        done = _parse(idea.get(ATTR_COMPLETED_AT)) if status == "completed" else None
        if due is None and not spans:
            continue
        created = _parse(idea.get(ATTR_CREATED_AT))
        start = min((s for s, _e in spans), default=None) or created or due
        end = done or due or max((e for _s, e in spans), default=None) or now
        if start is None:
            continue
        if end < start:
            start, end = end, start
        if end < since:
            continue
        rows.append(
            {
                "id": idea.get(ATTR_ID),
                "text": idea.get(ATTR_TEXT),
                "category": idea.get(ATTR_CATEGORY),
                "start": dt_util.as_local(start).isoformat(),
                "end": dt_util.as_local(end).isoformat(),
                "due": dt_util.as_local(due).isoformat() if due else None,
                "done": status == "completed",
                "overdue": status == "active" and due is not None and due < now,
                "seconds": tracked_seconds(idea, now),
            }
        )
    rows.sort(key=lambda row: (row["start"], row["end"]))
    return rows[:GANTT_MAX_ROWS]
