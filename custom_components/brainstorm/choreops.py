"""Hand Brainstorm tasks to ChoreOps and tick them off once a parent approves."""

from __future__ import annotations

from datetime import datetime, timedelta
import logging
import re
from typing import TYPE_CHECKING, Any

from homeassistant.const import EVENT_STATE_CHANGED
from homeassistant.core import (
    CALLBACK_TYPE,
    Context,
    Event,
    EventStateChangedData,
    HomeAssistant,
    State,
    callback,
)
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_call_later
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_ASSIGNEE,
    ATTR_CHOREOPS,
    ATTR_CHOREOPS_REWARD,
    ATTR_DESCRIPTION,
    ATTR_HABIT_BONUS,
    ATTR_PRIORITY,
    ATTR_VOTES,
    ATTR_DUE,
    ATTR_STATUS,
    ATTR_TEXT,
    DOMAIN,
    STREAK_MILESTONES,
)

if TYPE_CHECKING:
    from .store import BrainstormStore

_LOGGER = logging.getLogger(__name__)

CHOREOPS_DOMAIN = "choreops"
CHOREOPS_CREATE = "create_chore"
CHOREOPS_REWARD = "create_reward"
CHOREOPS_ADJUST = "manual_adjust_points"
POINTS_PURPOSE = "purpose_points"
HABIT_BONUS_KEEP = 20
REWARD_NAME_MAX = 80
REWARD_COST_MAX = 100000
POINTS_MAX = 10000
SUGGEST_MAX_ITEMS = 30
POINT_KINDS = ("chore", "reward")
# How much more than a normal task a priority is worth
PRIORITY_WEIGHT = {"low": 0.5, "medium": 1.0, "high": 1.5, "urgent": 2.0}
_POINTS_LINE = re.compile(r"\bL\s*(\d+)\b\D{0,12}?(\d{1,6})")
STATUS_SUFFIX = "_chore_status"
CHORE_NAME_MAX = 80
CHORE_LABEL = "brainstorm"
# What a status sensor of ChoreOps shows once a parent approved the chore
DONE_STATES = frozenset({"approved", "completed", "approved_in_part", "completed_in_part"})
CLAIMED_STATES = frozenset({"claimed", "claimed_in_part"})
CHORE_OPEN = "open"
CHORE_CLAIMED = "claimed"
CHORE_APPROVED = "approved"
REFRESH_DELAY = 2
STATUS_COMPLETED = "completed"


def choreops_available(hass: HomeAssistant) -> bool:
    """Tell whether ChoreOps is installed and takes new chores."""
    return hass.services.has_service(CHOREOPS_DOMAIN, CHOREOPS_CREATE)


def rewards_available(hass: HomeAssistant) -> bool:
    """Tell whether ChoreOps takes new rewards."""
    return hass.services.has_service(CHOREOPS_DOMAIN, CHOREOPS_REWARD)


def _round_to(value: float, step: int) -> int:
    return max(step, int(round(value / step)) * step)


def rule_points(idea: dict[str, Any], kind: str, base: int, open_subtasks: int = 0) -> int:
    """Suggest points without AI: by priority and subtasks, or by votes for a wish.

    A chore is worth the default points, more for a high priority and for
    every open subtask. A reward costs about five chores, more the more votes
    the wish got.
    """
    base = max(1, int(base or 10))
    if kind == "reward":
        votes = sum(
            int(n) for n in (idea.get(ATTR_VOTES) or {}).values() if isinstance(n, int)
        )
        step = 10 if base * 5 >= 50 else 5
        return min(REWARD_COST_MAX, _round_to(base * 5 + base * votes / 2, step))
    weight = PRIORITY_WEIGHT.get(str(idea.get(ATTR_PRIORITY) or "medium"), 1.0)
    points = base * weight + base / 2 * min(open_subtasks, 6)
    return min(POINTS_MAX, _round_to(points, 5 if base >= 5 else 1))


def parse_points(text: str | None, count: int, limit: int) -> dict[int, int]:
    """Read lines such as 'L2: 15' as 0-based index -> points, unknown ones left out."""
    found: dict[int, int] = {}
    for line in (text or "").splitlines():
        match = _POINTS_LINE.search(line)
        if not match:
            continue
        index = int(match.group(1)) - 1
        if 0 <= index < count and index not in found:
            found[index] = max(0, min(limit, int(match.group(2))))
    return found


def match_user(name: str | None, users: list[str]) -> str | None:
    """Return the ChoreOps user for a Brainstorm person, by name or first name."""
    wanted = " ".join(str(name or "").split()).casefold()
    if not wanted:
        return None
    for user in users:
        if user.casefold() == wanted:
            return user
    first = wanted.split(" ")[0]
    matches = [user for user in users if user.casefold().split(" ")[0] == first]
    return matches[0] if len(matches) == 1 else None


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    return dt_util.parse_datetime(value)


class ChoreOpsBridge:
    """Watch the ChoreOps status of handed over tasks."""

    def __init__(
        self,
        hass: HomeAssistant,
        store: BrainstormStore,
        default_points: int = 10,
        streak_bonus: int = 0,
    ) -> None:
        """Initialize the bridge."""
        self.hass = hass
        self.store = store
        self.default_points = default_points
        self.streak_bonus = streak_bonus
        self.users: list[str] = []
        # Status sensor -> idea it reports for
        self._entities: dict[str, str] = {}
        self._unsubs: list[CALLBACK_TYPE] = []
        self._refresh_timer: CALLBACK_TYPE | None = None

    @property
    def available(self) -> bool:
        """Tell whether ChoreOps takes chores right now."""
        return choreops_available(self.hass)

    async def async_start(self) -> None:
        """Find the status sensors and listen to them."""
        self._unsubs.append(
            self.hass.bus.async_listen(
                EVENT_STATE_CHANGED, self._state_changed, event_filter=self._tracked
            )
        )
        self._unsubs.append(
            self.hass.bus.async_listen(
                er.EVENT_ENTITY_REGISTRY_UPDATED, self._registry_changed
            )
        )
        self._refresh()

    @callback
    def async_stop(self) -> None:
        """Stop listening."""
        while self._unsubs:
            self._unsubs.pop()()
        if self._refresh_timer is not None:
            self._refresh_timer()
            self._refresh_timer = None

    @callback
    def _tracked(self, event_data: EventStateChangedData) -> bool:
        return event_data["entity_id"] in self._entities

    @callback
    def _registry_changed(self, event: Event[er.EventEntityRegistryUpdatedData]) -> None:
        # ChoreOps adds the sensors of a new chore a moment after creating it
        entity_id = event.data.get("entity_id", "")
        if not entity_id.startswith("sensor.") or self._refresh_timer is not None:
            return
        self._refresh_timer = async_call_later(
            self.hass, REFRESH_DELAY, self._delayed_refresh
        )

    @callback
    def _delayed_refresh(self, _now: datetime) -> None:
        self._refresh_timer = None
        self._refresh()

    @callback
    def _refresh(self) -> None:
        """Read the ChoreOps users and the status sensors of handed over tasks."""
        chores = {
            str(info["chore_id"]): idea_id
            for idea_id, info in self._handed_over().items()
        }
        users: set[str] = set()
        entities: dict[str, str] = {}
        for entry in er.async_get(self.hass).entities.values():
            if entry.platform != CHOREOPS_DOMAIN or entry.domain != "sensor":
                continue
            state = self.hass.states.get(entry.entity_id)
            if state is not None and isinstance(name := state.attributes.get("user_name"), str):
                users.add(name)
            unique_id = str(entry.unique_id)
            if not unique_id.endswith(STATUS_SUFFIX):
                continue
            for chore_id, idea_id in chores.items():
                if unique_id.endswith(f"_{chore_id}{STATUS_SUFFIX}"):
                    entities[entry.entity_id] = idea_id
        changed_users = sorted(users, key=str.casefold) != self.users
        self.users = sorted(users, key=str.casefold)
        self._entities = entities
        # What happened while Home Assistant was off counts as well
        for entity_id, idea_id in entities.items():
            if state := self.hass.states.get(entity_id):
                self._apply(idea_id, state)
        if changed_users:
            self.store.notify_choreops_changed()

    def points(self) -> dict[str, float]:
        """Return the points of every ChoreOps person, by name."""
        result: dict[str, float] = {}
        for entry in er.async_get(self.hass).entities.values():
            if entry.platform != CHOREOPS_DOMAIN or entry.domain != "sensor":
                continue
            state = self.hass.states.get(entry.entity_id)
            if state is None or state.attributes.get("purpose") != POINTS_PURPOSE:
                continue
            name = state.attributes.get("user_name")
            try:
                value = float(state.state)
            except (TypeError, ValueError):
                continue
            if isinstance(name, str):
                result[name] = value
        return dict(sorted(result.items(), key=lambda item: item[0].casefold()))

    def open_chores(self) -> list[dict[str, Any]]:
        """Return the handed over tasks that are not approved yet."""
        return [
            {
                "id": idea_id,
                "text": (self.store.get_idea(idea_id) or {}).get(ATTR_TEXT),
                "user": info.get("user"),
                "points": info.get("points"),
                "status": info.get("status"),
            }
            for idea_id, info in self._handed_over().items()
        ]

    async def async_habit_bonus(
        self, idea_id: str, reason: str, context: Context | None = None
    ) -> int | None:
        """Give bonus points once the streak of a habit reaches a milestone.

        reason holds {days} and {text}. A milestone counts once per streak,
        a new streak after a break may earn it again.
        """
        from .store import habit_summary  # noqa: PLC0415

        idea = self.store.get_idea(idea_id)
        if self.streak_bonus <= 0 or idea is None or not self.available:
            return None
        summary = habit_summary(idea)
        if summary is None or not summary["today"]:
            return None
        streak = summary["streak"]
        if streak not in STREAK_MILESTONES:
            return None
        if not self.users:
            self._refresh()
        user = match_user(idea.get(ATTR_ASSIGNEE), self.users)
        if user is None:
            return None
        start = dt_util.now().date() - timedelta(days=streak - 1)
        key = f"{start.isoformat()}:{streak}"
        earned = [str(k) for k in idea.get(ATTR_HABIT_BONUS) or []]
        if key in earned:
            return None
        text = " ".join(str(idea.get(ATTR_TEXT) or "").split())
        await self.hass.services.async_call(
            CHOREOPS_DOMAIN,
            CHOREOPS_ADJUST,
            {
                "user_name": user,
                "amount": self.streak_bonus,
                "reason": reason.format(days=streak, text=text)[:200],
            },
            blocking=True,
            context=context,
        )
        await self.store.async_set_fields(
            {idea_id: {ATTR_HABIT_BONUS: [*earned, key][-HABIT_BONUS_KEEP:]}}
        )
        _LOGGER.info("ChoreOps streak bonus for %s: %s days", user, streak)
        return self.streak_bonus

    def _handed_over(self) -> dict[str, dict[str, Any]]:
        return {
            idea["id"]: idea[ATTR_CHOREOPS]
            for idea in self.store.ideas
            if isinstance(idea.get(ATTR_CHOREOPS), dict)
            and idea[ATTR_CHOREOPS].get("chore_id")
            and idea[ATTR_CHOREOPS].get("status") != CHORE_APPROVED
        }

    @callback
    def _state_changed(self, event: Event[EventStateChangedData]) -> None:
        idea_id = self._entities.get(event.data["entity_id"])
        if idea_id and (state := event.data["new_state"]) is not None:
            self._apply(idea_id, state)

    @callback
    def _apply(self, idea_id: str, state: State) -> None:
        idea = self.store.get_idea(idea_id)
        info = idea.get(ATTR_CHOREOPS) if idea else None
        if not isinstance(info, dict) or info.get("status") == CHORE_APPROVED:
            return
        if state.state in DONE_STATES:
            since = _parse_time(info.get("since"))
            approved = _parse_time(
                state.attributes.get("last_approved") or state.attributes.get("last_completed")
            )
            # A status left from an older chore of the same name does not count
            if since is not None and approved is not None and approved < since:
                return
            self.hass.async_create_task(
                self.store.async_choreops_update(
                    idea_id,
                    CHORE_APPROVED,
                    done_by=state.attributes.get("user_name"),
                    points=state.attributes.get("chore_points_earned"),
                )
            )
        elif state.state in CLAIMED_STATES and info.get("status") != CHORE_CLAIMED:
            self.hass.async_create_task(
                self.store.async_choreops_update(
                    idea_id, CHORE_CLAIMED, done_by=state.attributes.get("user_name")
                )
            )
        elif (
            state.state not in CLAIMED_STATES
            and state.state not in ("unavailable", "unknown")
            and info.get("status") == CHORE_CLAIMED
        ):
            # A parent turned the report down, the task is open again
            self.hass.async_create_task(
                self.store.async_choreops_update(idea_id, CHORE_OPEN)
            )

    async def async_hand_over(
        self,
        idea: dict[str, Any],
        user: str | None,
        points: int | None,
        context: Context | None = None,
    ) -> dict[str, Any]:
        """Create a chore for a Brainstorm task and remember it."""
        if not self.available:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="choreops_missing"
            )
        if idea.get(ATTR_STATUS) == STATUS_COMPLETED:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="choreops_done"
            )
        current = idea.get(ATTR_CHOREOPS)
        if isinstance(current, dict) and current.get("status") != CHORE_APPROVED:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="choreops_already"
            )
        if points is None:
            points = self.default_points
        if not self.users:
            self._refresh()
        wanted = user or idea.get(ATTR_ASSIGNEE)
        target = match_user(wanted, self.users)
        if target is None:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="choreops_no_user",
                translation_placeholders={
                    "name": str(wanted or "–"),
                    "users": ", ".join(self.users) or "–",
                },
            )
        text = " ".join(str(idea.get(ATTR_TEXT) or "").split())
        data: dict[str, Any] = {
            "name": text[:CHORE_NAME_MAX],
            "assigned_user_names": [target],
            "points": points,
            "labels": [CHORE_LABEL],
            "frequency": "none",
        }
        if description := idea.get(ATTR_DESCRIPTION):
            data["description"] = str(description)[:500]
        if due := _parse_time(idea.get(ATTR_DUE)):
            data["due_date"] = due.isoformat()
        # ChoreOps checks itself whether the caller may create chores
        response = await self.hass.services.async_call(
            CHOREOPS_DOMAIN,
            CHOREOPS_CREATE,
            data,
            blocking=True,
            context=context,
            return_response=True,
        )
        chore_id = (response or {}).get("id") if isinstance(response, dict) else None
        if not chore_id:
            raise HomeAssistantError(
                translation_domain=DOMAIN, translation_key="choreops_failed"
            )
        info = {
            "chore_id": str(chore_id),
            "user": target,
            "points": points,
            "status": CHORE_OPEN,
            "since": dt_util.utcnow().isoformat(),
        }
        await self.store.async_choreops_set(idea["id"], info)
        self._refresh()
        return info

    async def async_make_reward(
        self,
        idea: dict[str, Any],
        cost: int,
        users: list[str] | None = None,
        name: str | None = None,
        context: Context | None = None,
    ) -> dict[str, Any]:
        """Create a ChoreOps reward from a wish and remember it on the note."""
        if not rewards_available(self.hass):
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="choreops_missing"
            )
        if isinstance(idea.get(ATTR_CHOREOPS_REWARD), dict):
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="choreops_reward_already"
            )
        if not self.users:
            self._refresh()
        targets: list[str] = []
        for wanted in users or []:
            target = match_user(wanted, self.users)
            if target is None:
                raise ServiceValidationError(
                    translation_domain=DOMAIN,
                    translation_key="choreops_no_user",
                    translation_placeholders={
                        "name": str(wanted),
                        "users": ", ".join(self.users) or "–",
                    },
                )
            if target not in targets:
                targets.append(target)
        text = " ".join(str(name or idea.get(ATTR_TEXT) or "").split())
        data: dict[str, Any] = {
            "name": text[:REWARD_NAME_MAX],
            "cost": cost,
            "labels": [CHORE_LABEL],
            # Without a choice every person may redeem it
            "assigned_user_names": targets or ["*"],
        }
        if description := idea.get(ATTR_DESCRIPTION):
            data["description"] = str(description)[:500]
        response = await self.hass.services.async_call(
            CHOREOPS_DOMAIN,
            CHOREOPS_REWARD,
            data,
            blocking=True,
            context=context,
            return_response=True,
        )
        reward_id = (response or {}).get("id") if isinstance(response, dict) else None
        if not reward_id:
            raise HomeAssistantError(
                translation_domain=DOMAIN, translation_key="choreops_failed"
            )
        info = {
            "reward_id": str(reward_id),
            "name": data["name"],
            "cost": cost,
            "users": targets,
            "since": dt_util.utcnow().isoformat(),
        }
        await self.store.async_choreops_reward_set(idea["id"], info)
        return info
