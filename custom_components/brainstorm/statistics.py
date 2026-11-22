"""Numbers for the statistics view: done per week, lead time and who did it."""

from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timedelta
from statistics import median
from typing import Any

from homeassistant.util import dt as dt_util

from .const import (
    ATTR_CATEGORY,
    ATTR_CHOREOPS,
    ATTR_COMPLETED_AT,
    ATTR_COMPLETED_BY,
    ATTR_CREATED_AT,
    ATTR_DUE,
    ATTR_STATUS,
)
from .timetrack import gantt_rows, time_summary

DEFAULT_WEEKS = 8
MAX_WEEKS = 52


def _moment(value: Any) -> datetime | None:
    parsed = dt_util.parse_datetime(str(value or ""))
    return dt_util.as_local(parsed) if parsed is not None else None


def _week_start(day: date) -> date:
    return day - timedelta(days=day.weekday())


def statistics_window(now: datetime, weeks: int = DEFAULT_WEEKS) -> datetime:
    """Return the start of the first week the statistics cover."""
    weeks = max(1, min(MAX_WEEKS, int(weeks)))
    first = _week_start(dt_util.as_local(now).date()) - timedelta(weeks=weeks - 1)
    return dt_util.start_of_local_day(first)


def done_by(idea: dict[str, Any], names: dict[str, str]) -> str | None:
    """Return who ticked an idea off, by the HA user or the ChoreOps person."""
    if (user := idea.get(ATTR_COMPLETED_BY)) and names.get(str(user)):
        return names[str(user)]
    chore = idea.get(ATTR_CHOREOPS)
    if isinstance(chore, dict) and chore.get("done_by"):
        return str(chore["done_by"])
    return None


def build_statistics(
    ideas: list[dict[str, Any]],
    now: datetime,
    names: dict[str, str],
    weeks: int = DEFAULT_WEEKS,
    category: str | None = None,
) -> dict[str, Any]:
    """Return the statistics of the given ideas over the last weeks."""
    weeks = max(1, min(MAX_WEEKS, int(weeks)))
    local_now = dt_util.as_local(now)
    first = _week_start(local_now.date()) - timedelta(weeks=weeks - 1)
    rows = {
        first + timedelta(weeks=index): {"completed": 0, "added": 0}
        for index in range(weeks)
    }
    chosen = [
        idea for idea in ideas if not category or idea.get(ATTR_CATEGORY) == category
    ]
    lead_hours: list[float] = []
    people: Counter[str] = Counter()
    unknown = 0
    categories: dict[str, dict[str, int]] = {}
    open_count = overdue = 0
    for idea in chosen:
        status = idea.get(ATTR_STATUS)
        cat = str(idea.get(ATTR_CATEGORY) or "")
        row = categories.setdefault(cat, {"completed": 0, "open": 0})
        created = _moment(idea.get(ATTR_CREATED_AT))
        if created is not None and (week := _week_start(created.date())) in rows:
            rows[week]["added"] += 1
        if status == "active":
            open_count += 1
            row["open"] += 1
            due = _moment(idea.get(ATTR_DUE))
            if due is not None and due < local_now:
                overdue += 1
            continue
        if status not in ("completed", "archived"):
            continue
        done = _moment(idea.get(ATTR_COMPLETED_AT))
        if done is None or (week := _week_start(done.date())) not in rows:
            continue
        rows[week]["completed"] += 1
        row["completed"] += 1
        if created is not None and done >= created:
            lead_hours.append((done - created).total_seconds() / 3600)
        if (person := done_by(idea, names)) is not None:
            people[person] += 1
        else:
            unknown += 1
    window = dt_util.start_of_local_day(first)
    return {
        "time": time_summary(chosen, now, window),
        "gantt": gantt_rows(chosen, now, window),
        "weeks": [
            {
                "start": start.isoformat(),
                "week": start.isocalendar().week,
                **counts,
            }
            for start, counts in rows.items()
        ],
        "completed": sum(row["completed"] for row in rows.values()),
        "added": sum(row["added"] for row in rows.values()),
        "open": open_count,
        "overdue": overdue,
        "lead_time": {
            "count": len(lead_hours),
            "median_hours": round(median(lead_hours), 1) if lead_hours else None,
            "average_hours": (
                round(sum(lead_hours) / len(lead_hours), 1) if lead_hours else None
            ),
        },
        "people": [
            {"name": name, "completed": count} for name, count in people.most_common()
        ],
        "unknown": unknown,
        "categories": sorted(
            (
                {"category": cat, **counts}
                for cat, counts in categories.items()
                if counts["completed"] or counts["open"]
            ),
            key=lambda item: (-item["completed"], -item["open"], item["category"]),
        ),
    }
