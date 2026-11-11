"""Data management and storage for Brainstorm Hub."""
from __future__ import annotations

import asyncio
import contextlib
import hashlib
import json
import logging
import math
import os
import re
import shutil
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from typing import Any, Callable, TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Context, HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    CONF_UI_LEVEL,
    DEFAULT_UI_LEVEL,
    UI_LEVELS,
    ATTR_CATEGORY,
    ATTR_CREATED_AT,
    ATTR_ALEXA_NATIVE,
    ATTR_ASSIGNEE,
    ATTR_CREATED_BY,
    ATTR_MAP_POS,
    ATTR_OWNER,
    ATTR_PIN,
    DRAW_COLORS,
    DRAW_KINDS,
    DRAW_MAX_POINTS,
    DRAW_MAX_STROKES,
    PIN_COLORS,
    ATTR_SHARES,
    ACCESS_OWNER,
    SHARE_ALL,
    SHARE_EDIT,
    SHARE_VIEW,
    ATTR_DEVICE,
    ATTR_DUE,
    ATTR_ECHOS,
    ATTR_TRIGGER,
    ATTR_URGENT_SENT,
    ATTR_ESCALATED,
    ATTR_REMINDED_AT,
    ATTR_ID,
    ATTR_ORDER,
    ATTR_PARENT_ID,
    ATTR_PRIORITY,
    ATTR_RESULT,
    ATTR_DESCRIPTION,
    DESCRIPTION_MAX_LENGTH,
    ATTR_BATTERY,
    ATTR_ATTACHMENTS,
    ATTR_BATTERY_DONE,
    ATTR_COMPLETED_AT,
    ATTR_IN_PROGRESS,
    ATTR_MARKERS,
    ATTR_PROGRESS,
    ATTR_SUBTASKS,
    ATTR_LINKS,
    ATTR_BLOCKED_BY,
    ATTR_FRAME,
    ATTR_NUMBERING,
    ATTR_REPEAT,
    ATTR_REACTIONS,
    ATTR_VOTES,
    ATTR_COMMENTS,
    ATTR_ROUND_BY,
    ATTR_COMMENT_COUNT,
    COMMENT_MAX_LENGTH,
    COMMENTS_MAX,
    EVENT_COMMENT_ADDED,
    REACTIONS,
    ROUND_MAX_MINUTES,
    VOTING_MAX_VOTES,
    ATTR_REPEATED_AS,
    ATTR_REPEAT_CLOSED,
    ATTR_CALLOUT,
    CALLOUT_MAX_LENGTH,
    FRAME_MAX_LENGTH,
    NUMBERING_STYLES,
    REPEAT_MAX_SUBTASKS,
    REPEAT_RULES,
    LINK_LABEL_MAX_LENGTH,
    LINKS_MAX_COUNT,
    ATTR_SHAPE,
    MARKERS,
    NODE_SHAPES,
    PROGRESS_STEPS,
    ATTACHMENT_DIR,
    ATTACHMENT_MAX_COUNT,
    ATTACHMENT_MAX_SIZE,
    ATTACHMENT_RETENTION_DAYS,
    ATTACHMENT_TYPES,
    ATTR_SOURCE,
    ATTR_STATUS,
    ATTR_TAGS,
    ATTR_RAW_TEXT,
    ATTR_TEXT,
    ATTR_TODO_LINK,
    ATTR_SPEC,
    ATTR_BRING_LIST,
    ATTR_UPDATED_AT,
    ATTR_CALENDAR_SYNCED,
    CONF_ALLOWED_ECHOS,
    CONF_PRIVACY_ENABLED,
    CONF_PRIVACY_EXPORT,
    CONF_PRIVACY_OWNER,
    CONF_VOICE_OWNERS,
    CONF_VOICE_MODE,
    CONF_HIDE_EMPTY_CATEGORIES,
    CONF_AI_ENTITY,
    CONF_AI_TEXT_CLEANUP,
    CONF_DELETE_DONE_DAYS,
    CONF_GLOSSARY,
    CONF_REMINDERS_ENABLED,
    CONF_SMART_FORMATTING,
    CONF_VOICE_DUE,
    DEFAULT_HIDE_EMPTY_CATEGORIES,
    DEFAULT_MARKDOWN_PATH,
    DEFAULT_PRIORITY,
    DOMAIN,
    EVENT_IDEA_ADDED,
    EVENT_IDEA_COMPLETED,
    EVENT_IDEA_DELETED,
    EVENT_IDEA_UPDATED,
    EVENT_ROUND_ENDED,
    JSON_EXPORT_FORMAT,
    JSON_EXPORT_VERSION,
    OVERVIEW_ENTITY_ID,
    PRIORITY_HIGH,
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    PRIORITY_URGENT,
    STORAGE_KEY,
    SOURCE_ASSIST_LLM,
    STORAGE_VERSION,
    TYPED_SOURCES,
    VOICE_MODE_NATIVE,
)
from .ai import (
    CLUSTER_MAX_IDEAS,
    CLUSTER_MIN_IDEAS,
    MAP_INPUT_MAX_LENGTH,
    MAP_MAX_NODES,
    MAX_BRANCH_LINES,
    MAX_LOOSE_IDEAS,
    MAX_PARENT_CANDIDATES,
    async_generate_text,
    async_request_text_with_retry,
    clean_summary,
    parse_clusters,
    parse_map_outline,
    parse_parent_suggestions,
    parse_subtask_suggestions,
)
from .languages import CATEGORY_KEYS, get_pack
from .languages.common import CATEGORY_PROJECTS, LanguagePack

if TYPE_CHECKING:
    from .alexa_skill import AlexaSkill
    from .reminders import ReminderManager
    from .todo_sync import TodoSyncManager

_LOGGER = logging.getLogger(__name__)

COLOR_PATTERN = re.compile(r"^#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
ICON_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+:[a-zA-Z0-9_-]+$")
# A tag is a word after #, with at least one letter, so "#1" stays a number.
# The cards find tags the same way.
TAG_PATTERN = re.compile(r"(?:^|(?<=[\s(\[,;]))#((?=[\w-]*[^\W\d_])[\w-]+)")
# A color such as #ff7800 is no tag
COLOR_TAG_PATTERN = re.compile(r"(?=[a-f]*\d)[0-9a-f]{6}(?:[0-9a-f]{2})?", re.IGNORECASE)
# Said aloud, a tag is "hashtag garten"
SPOKEN_TAG_PATTERN = re.compile(r"\bhash\s?tag\s+([^\W\d_][\w-]*)", re.IGNORECASE)
# Config subfolders exports must not write to; 'www' is served without authentication
EXPORT_BLOCKED_DIRS = {"custom_components", "www"}
# The own folder below the config dir that exports and imports use
EXPORT_DIR_NAME = "brainstorm"
# What an imported idea ID may look like; anything else gets a new ID
IMPORT_ID_PATTERN = re.compile(r"[A-Za-z0-9_-]{1,64}")
# How many deleted ideas can be brought back until the next start
MAX_RESTORABLE = 50
# Fields of an idea a JSON import takes over, everything else is left out
IMPORT_FIELDS = (
    ATTR_RAW_TEXT,
    ATTR_DESCRIPTION,
    ATTR_SOURCE,
    ATTR_DEVICE,
    ATTR_RESULT,
    ATTR_ASSIGNEE,
    ATTR_TRIGGER,
    ATTR_MAP_POS,
    ATTR_PIN,
    ATTR_CREATED_BY,
    ATTR_SHAPE,
    ATTR_MARKERS,
    ATTR_PROGRESS,
    ATTR_LINKS,
    ATTR_FRAME,
    ATTR_CALLOUT,
    ATTR_NUMBERING,
    ATTR_REPEAT,
)
# Fields that belong to this Home Assistant and stay out of a JSON export
EXPORT_SKIPPED_FIELDS = (
    # The files themselves are not part of an export
    ATTR_ATTACHMENTS,
    ATTR_IN_PROGRESS,
    ATTR_TODO_LINK,
    ATTR_BRING_LIST,
    ATTR_BATTERY,
    ATTR_BATTERY_DONE,
    ATTR_CALENDAR_SYNCED,
    ATTR_ALEXA_NATIVE,
    # Reactions, votes and comments name users of this Home Assistant
    ATTR_REACTIONS,
    ATTR_VOTES,
    ATTR_COMMENTS,
    ATTR_ROUND_BY,
)
IMPORT_STATUSES = ("active", "completed", "archived")
# Imported fields that must be plain text
IMPORT_TEXT_FIELDS = (
    ATTR_RAW_TEXT,
    ATTR_DESCRIPTION,
    ATTR_SOURCE,
    ATTR_DEVICE,
    ATTR_RESULT,
    ATTR_ASSIGNEE,
    ATTR_CREATED_BY,
)


def _validate_category_style(icon: str | None, color: str | None) -> None:
    """Raise if a category icon or color is malformed."""
    if icon and icon.strip() and not ICON_PATTERN.match(icon.strip()):
        raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="invalid_icon", translation_placeholders={"icon": icon}
        )
    if color and color.strip() and not COLOR_PATTERN.match(color.strip()):
        raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="invalid_color", translation_placeholders={"color": color}
        )





type BrainstormConfigEntry = ConfigEntry[BrainstormStore]


def attachment_name(name: str) -> str:
    """Return a file name without folders or characters that cause trouble."""
    base = Path(str(name or "").replace("\\", "/")).name
    base = re.sub(r"[\x00-\x1f\x7f<>:\"/\\|?*]", "_", base).strip(" .")
    if len(base) > 120:
        stem, suffix = os.path.splitext(base)
        base = stem[: 120 - len(suffix)] + suffix
    return base or "file"


def attachment_folder(idea_id: str) -> str:
    """Return a safe folder name for an idea; imported IDs can be anything."""
    if re.fullmatch(r"[A-Za-z0-9_-]{1,64}", idea_id):
        return idea_id
    return "id-" + hashlib.sha256(idea_id.encode()).hexdigest()[:32]


def _remove_files(paths: list[Path]) -> None:
    """Delete files and the folders they leave empty (blocking I/O)."""
    for path in paths:
        try:
            path.unlink(missing_ok=True)
        except OSError as err:
            _LOGGER.warning("Could not delete attachment %s: %s", path, err)
            continue
        # The folder stays while other files are still in it
        with contextlib.suppress(OSError):
            path.parent.rmdir()


def get_loaded_store(hass: HomeAssistant) -> BrainstormStore | None:
    """Return the store of the loaded config entry, if there is one."""
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    return entries[0].runtime_data if entries else None


class BrainstormStore:
    """Manages brainstorm ideas and categories in persistent storage."""

    def __init__(self, hass: HomeAssistant, options: dict[str, Any] | None = None) -> None:
        """Initialize the store."""
        self.hass = hass
        self.options = options or {}
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._ideas: dict[str, dict[str, Any]] = {}
        # Ideas deleted since the start, so a dashboard can undo the deletion
        self._deleted: dict[str, dict[str, Any]] = {}
        self._categories: list[str] = list(self._pack().default_categories)
        self._category_icons: dict[str, str] = {}
        self._category_colors: dict[str, str] = {}
        self._listeners: list[Callable[[], None]] = []
        self._revision = 0
        self._privacy_enabled = bool(self.options.get(CONF_PRIVACY_ENABLED))
        self._privacy_owner = self.options.get(CONF_PRIVACY_OWNER)
        # Export files are readable by everyone with access to the config folder
        self._auto_export = self.options.get("auto_export_markdown", False) and (
            not self._privacy_enabled or self.options.get(CONF_PRIVACY_EXPORT, False)
        )
        self._markdown_path = self.options.get("markdown_path", DEFAULT_MARKDOWN_PATH)
        self._smart_formatting = self.options.get(CONF_SMART_FORMATTING, True)
        # A date only moves out of the text if it can lead to a reminder
        self._voice_due = self.options.get(CONF_VOICE_DUE, True) and self.options.get(
            CONF_REMINDERS_ENABLED, True
        )
        self._hide_empty_categories = self.options.get(
            CONF_HIDE_EMPTY_CATEGORIES, DEFAULT_HIDE_EMPTY_CATEGORIES
        )
        self._allowed_echos = list(self.options.get(CONF_ALLOWED_ECHOS) or [])
        self._voice_mode = self.options.get(CONF_VOICE_MODE, VOICE_MODE_NATIVE)
        ui_level = self.options.get(CONF_UI_LEVEL, DEFAULT_UI_LEVEL)
        self._ui_level = ui_level if ui_level in UI_LEVELS else DEFAULT_UI_LEVEL
        self._default_category = self.options.get("default_category", "Inbox")
        self._last_action: dict[str, Any] | None = None
        self._ai_tasks: set[asyncio.Task[None]] = set()
        self._category_shares: dict[str, dict[str, dict[str, str]]] = {}
        # Running voting rounds: category -> votes per person, hidden, by, since
        self._voting: dict[str, dict[str, Any]] = {}
        # Hidden brainstorm rounds: category -> since, by, ends_at
        self._rounds: dict[str, dict[str, Any]] = {}
        self._round_timers: dict[str, Callable[[], None]] = {}
        self._drawings: dict[str, list[dict[str, Any]]] = {}
        self._drawing_revs: dict[str, int] = {}
        self.integration_version: str | None = None
        self.alexa_skill: AlexaSkill | None = None
        self.reminders: ReminderManager | None = None
        self.todo_sync: TodoSyncManager | None = None

    @property
    def last_action(self) -> dict[str, Any] | None:
        """Return the most recent action performed."""
        return getattr(self, "_last_action", None)

    @property
    def ui_level(self) -> str:
        """Return how many controls the cards and settings show."""
        return self._ui_level

    @property
    def hide_empty_categories(self) -> bool:
        """Return whether empty categories should be hidden."""
        return self._hide_empty_categories

    @property
    def allowed_echos(self) -> list[str]:
        """Return the Echos allowed for voice input, empty meaning all."""
        return list(self._allowed_echos)

    @property
    def privacy_enabled(self) -> bool:
        """Return whether ideas are private to their owners."""
        return self._privacy_enabled

    @property
    def voice_user_id(self) -> str | None:
        """Return whose ideas voice and briefings may mention, None meaning all."""
        return self._privacy_owner if self._privacy_enabled else None

    def voice_user_for(self, device: str | None) -> str | None:
        """Return whose ideas a device may use, as voices cannot be told apart."""
        if not self._privacy_enabled:
            return None
        owners = self.options.get(CONF_VOICE_OWNERS) or {}
        return owners.get(device or "") or self._privacy_owner

    def owner_of(self, idea: dict[str, Any]) -> str | None:
        """Return the owner of an idea, ideas from before belong to the main user."""
        return idea.get(ATTR_OWNER) or self._privacy_owner

    def access_level(self, idea: dict[str, Any], user_id: str | None) -> str | None:
        """Return what a user may do with an idea, None being the system."""
        if self.hidden_in_round(idea, user_id):
            return None
        if not self._privacy_enabled or user_id is None:
            return ACCESS_OWNER
        owner = self.owner_of(idea)
        if owner == user_id:
            return ACCESS_OWNER
        category_shares = self._category_shares.get(owner or "", {}).get(
            idea.get(ATTR_CATEGORY) or "", {}
        )
        levels = {
            (idea.get(ATTR_SHARES) or {}).get(user_id),
            (idea.get(ATTR_SHARES) or {}).get(SHARE_ALL),
            category_shares.get(user_id),
            category_shares.get(SHARE_ALL),
        }
        if SHARE_EDIT in levels:
            return SHARE_EDIT
        return SHARE_VIEW if SHARE_VIEW in levels else None

    def can_access(self, idea: dict[str, Any], user_id: str | None) -> bool:
        """Return whether a user may see an idea."""
        return self.access_level(idea, user_id) is not None

    def can_edit(self, idea: dict[str, Any], user_id: str | None) -> bool:
        """Return whether a user may change or complete an idea."""
        return self.access_level(idea, user_id) in (ACCESS_OWNER, SHARE_EDIT)

    def is_owner(self, idea: dict[str, Any], user_id: str | None) -> bool:
        """Return whether a user may delete and share an idea."""
        return self.access_level(idea, user_id) == ACCESS_OWNER

    def owner_for_new_idea(
        self, user_id: str | None, category: str, parent: dict[str, Any] | None
    ) -> str | None:
        """Return who owns a new idea, a shared list keeping it for its owner."""
        if not self._privacy_enabled or user_id is None:
            return user_id
        # A subtask belongs to whoever owns its parent, else that owner would not see it
        if parent is not None and self.can_edit(parent, user_id):
            return self.owner_of(parent)
        # Only a list shared with this user personally counts, not one shared with all
        owners = {
            owner
            for owner, categories in self._category_shares.items()
            if owner != user_id
            and (categories.get(category) or {}).get(user_id) == SHARE_EDIT
        }
        return owners.pop() if len(owners) == 1 else user_id

    def is_shared_with_all(self, idea: dict[str, Any]) -> bool:
        """Return whether every Home Assistant user may see an idea."""
        category_shares = self._category_shares.get(self.owner_of(idea) or "", {}).get(
            idea.get(ATTR_CATEGORY) or "", {}
        )
        return SHARE_ALL in (idea.get(ATTR_SHARES) or {}) or SHARE_ALL in category_shares

    def _person_user(self, person: str | None) -> str | None:
        """Return the Home Assistant user of a person."""
        state = self.hass.states.get(person) if person else None
        return state.attributes.get("user_id") if state else None

    async def async_set_idea_shares(
        self,
        idea_ids: list[str],
        shares: dict[str, str | None],
        user_id: str | None,
    ) -> int:
        """Change who may see several ideas at once, returning how many changed."""
        ideas = [self._ideas[idea_id] for idea_id in idea_ids if idea_id in self._ideas]
        if any(not self.is_owner(idea, user_id) for idea in ideas):
            raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="owner_only_share"
        )
        for idea in ideas:
            current = dict(idea.get(ATTR_SHARES) or {})
            for target, level in shares.items():
                if level is None:
                    current.pop(target, None)
                else:
                    current[target] = level
            idea[ATTR_SHARES] = current
        await self.async_save()
        self._notify_listeners()
        return len(ideas)

    async def async_set_category_shares(
        self, owner: str, category: str, shares: dict[str, str | None]
    ) -> None:
        """Change who may see all of one owner's ideas in a category."""
        owner_shares = self._category_shares.setdefault(owner, {})
        current = dict(owner_shares.get(category) or {})
        for target, level in shares.items():
            if level is None:
                current.pop(target, None)
            else:
                current[target] = level
        owner_shares[category] = current
        await self.async_save()
        self._notify_listeners()

    def visible_ideas(self, user_id: str | None = None) -> list[dict[str, Any]]:
        """Return the ideas a user may see."""
        return [idea for idea in self.ideas if self.can_access(idea, user_id)]

    def get_idea(self, idea_id: str) -> dict[str, Any] | None:
        """Return an idea by its ID."""
        return self._ideas.get(idea_id)

    def get_public_attributes(self) -> dict[str, Any]:
        """Return what every Home Assistant user may read while ideas are private."""
        return {
            "privacy": True,
            # Without it the sensor would stay the same and the cards would not reload
            "revision": self._revision,
            "categories": self.categories,
            "category_icons": self.category_icons,
            "category_colors": self.category_colors,
            "hide_empty_categories": self.hide_empty_categories,
            "allowed_echos": self.allowed_echos,
            "voice_mode": self.voice_mode,
            "ai_subtasks": self.ai_subtasks_available,
            "ui_level": self.ui_level,
        }

    def get_overview_attributes(self, user_id: str | None = None) -> dict[str, Any]:
        """Return the statistics and ideas a user may see."""
        visible = self.visible_ideas(user_id)
        if user_id is None:
            # The shared sensor shows no note of a running hidden round
            visible = [
                i
                for i in visible
                if not (i.get(ATTR_ROUND_BY) and i.get(ATTR_CATEGORY) in self._rounds)
            ]
        active_ideas = [i for i in visible if i.get(ATTR_STATUS) == "active"]
        completed_ideas = [i for i in visible if i.get(ATTR_STATUS) == "completed"]

        counts_by_cat = {
            cat: len([i for i in active_ideas if i.get(ATTR_CATEGORY) == cat])
            for cat in self.categories
        }
        counts_by_prio = {
            prio: len(
                [i for i in active_ideas if i.get(ATTR_PRIORITY, DEFAULT_PRIORITY) == prio]
            )
            for prio in ("urgent", "high", "medium", "low")
        }

        progress_of = _subtask_progress(visible)
        visible_by_id = {str(i.get(ATTR_ID)): i for i in visible}
        blocked_by = _blocked_by(visible)

        def summary(idea: dict[str, Any]) -> dict[str, Any]:
            return {
                "text": idea.get(ATTR_TEXT),
                "category": idea.get(ATTR_CATEGORY),
                "priority": idea.get(ATTR_PRIORITY, DEFAULT_PRIORITY),
                "created_at": idea.get(ATTR_CREATED_AT),
                "source": idea.get(ATTR_SOURCE),
                "device": idea.get(ATTR_DEVICE),
            }

        def details(idea: dict[str, Any]) -> dict[str, Any]:
            result = {
                **summary(idea),
                "id": idea.get(ATTR_ID),
                "status": idea.get(ATTR_STATUS),
                "parent_id": idea.get(ATTR_PARENT_ID),
                "order": idea.get(ATTR_ORDER),
            }
            if note := idea.get(ATTR_BRING_LIST):
                result[ATTR_BRING_LIST] = note.get("entity")
            if self._privacy_enabled:
                access = self.access_level(idea, user_id)
                result["access"] = access
                result["owner"] = self.owner_of(idea)
                # Only the owner needs to know who else can see an idea
                if access == ACCESS_OWNER:
                    result[ATTR_SHARES] = idea.get(ATTR_SHARES) or {}
                if author := idea.get(ATTR_CREATED_BY):
                    result[ATTR_CREATED_BY] = author
            if position := idea.get(ATTR_MAP_POS):
                result[ATTR_MAP_POS] = position
            if pin := idea.get(ATTR_PIN):
                result[ATTR_PIN] = pin
            if shape := idea.get(ATTR_SHAPE):
                result[ATTR_SHAPE] = shape
            if note := idea.get(ATTR_RESULT):
                result[ATTR_RESULT] = note
            if description := idea.get(ATTR_DESCRIPTION):
                result[ATTR_DESCRIPTION] = description
            if attachments := idea.get(ATTR_ATTACHMENTS):
                result[ATTR_ATTACHMENTS] = [dict(a) for a in attachments]
            if working := idea.get(ATTR_IN_PROGRESS):
                result[ATTR_IN_PROGRESS] = dict(working)
            if tags := idea.get(ATTR_TAGS):
                result[ATTR_TAGS] = list(tags)
            if markers := idea.get(ATTR_MARKERS):
                result[ATTR_MARKERS] = list(markers)
            if progress := idea.get(ATTR_PROGRESS):
                result[ATTR_PROGRESS] = progress
            if subtasks := progress_of.get(str(idea.get(ATTR_ID))):
                result[ATTR_SUBTASKS] = subtasks
            if links := [
                dict(link)
                for link in idea.get(ATTR_LINKS) or []
                if link.get("to") in visible_by_id
            ]:
                result[ATTR_LINKS] = links
            if waits := blocked_by.get(str(idea.get(ATTR_ID))):
                result[ATTR_BLOCKED_BY] = waits
            if frame := idea.get(ATTR_FRAME):
                result[ATTR_FRAME] = frame
            if callout := idea.get(ATTR_CALLOUT):
                result[ATTR_CALLOUT] = callout
            if numbering := idea.get(ATTR_NUMBERING):
                result[ATTR_NUMBERING] = numbering
            if repeat := idea.get(ATTR_REPEAT):
                result[ATTR_REPEAT] = repeat
            if reactions := idea.get(ATTR_REACTIONS):
                result[ATTR_REACTIONS] = {k: list(v) for k, v in reactions.items()}
            if comments := idea.get(ATTR_COMMENTS):
                result[ATTR_COMMENT_COUNT] = len(comments)
            if votes := idea.get(ATTR_VOTES):
                round_ = self._voting.get(str(idea.get(ATTR_CATEGORY)))
                if round_ and round_.get("hidden"):
                    # Hidden until the round ends: only your own points
                    mine = votes.get(user_id or "")
                    if mine:
                        result[ATTR_VOTES] = {user_id: mine}
                    result["votes_hidden"] = True
                else:
                    result[ATTR_VOTES] = dict(votes)
            return result

        last_action = self.last_action
        if self._privacy_enabled and last_action is not None:
            # A deleted idea has no owner any more, so its action stays hidden
            acted_on = self._ideas.get(str(last_action.get("id")))
            if acted_on is None or not self.can_access(acted_on, user_id):
                last_action = None

        return {
            "speech_overview": self.get_announcement_text(user_id=user_id),
            "last_action": last_action,
            "active_count": len(active_ideas),
            "completed_count": len(completed_ideas),
            "categories": self.categories,
            "category_icons": self.category_icons,
            "category_colors": self.category_colors,
            "active_categories": [c for c in self.categories if counts_by_cat[c] > 0],
            "hide_empty_categories": self.hide_empty_categories,
            "allowed_echos": self.allowed_echos,
            "voice_mode": self.voice_mode,
            "ai_subtasks": self.ai_subtasks_available,
            "ui_level": self.ui_level,
            "category_counts": counts_by_cat,
            "priority_counts": counts_by_prio,
            "latest_idea": summary(active_ideas[0]) if active_ideas else None,
            "recent_ideas": [summary(i) for i in active_ideas[:5]],
            "ideas": [
                {
                    **details(i),
                    "due": i.get(ATTR_DUE),
                    "assignee": i.get(ATTR_ASSIGNEE),
                    "trigger": i.get(ATTR_TRIGGER),
                    "echos": i.get(ATTR_ECHOS),
                    "raw_text": i.get(ATTR_RAW_TEXT),
                }
                for i in active_ideas
            ],
            "completed_ideas": [details(i) for i in completed_ideas[:50]],
            "category_shares": self._category_shares.get(user_id or "", {}),
            "voting": {
                category: {
                    **round_,
                    "used": self.votes_used(category, user_id),
                }
                for category, round_ in self._voting.items()
            },
            "rounds": {
                category: {**round_, "hidden_count": self.round_hidden_count(category, user_id)}
                for category, round_ in self._rounds.items()
            },
            # The strokes come by WebSocket; this tells the cards when to fetch them
            "drawing_revs": {
                category: self._drawing_revs.get(category, 0)
                for category in self._drawings
            },
        }

    @property
    def voice_mode(self) -> str:
        """Return how Alexa voice input reaches Brainstorm."""
        return self._voice_mode

    @property
    def categories(self) -> list[str]:
        """Return the list of categories."""
        return list(self._categories)

    @property
    def category_icons(self) -> dict[str, str]:
        """Return the dictionary of category icons."""
        return dict(self._category_icons)

    @property
    def category_colors(self) -> dict[str, str]:
        """Return the dictionary of category color hex values."""
        return dict(self._category_colors)

    @property
    def _fallback_category(self) -> str:
        """Return the category for ideas without a valid category."""
        if self._default_category in self._categories:
            return self._default_category
        return "Inbox"

    @property
    def category_counts(self) -> dict[str, int]:
        """Return the number of active ideas per category."""
        counts = {cat: 0 for cat in self._categories}
        for idea in self._ideas.values():
            cat = idea.get(ATTR_CATEGORY)
            if idea.get(ATTR_STATUS) == "active" and cat in counts:
                counts[cat] += 1
        return counts

    @property
    def ideas(self) -> list[dict[str, Any]]:
        """Return all ideas sorted by custom order or creation date descending."""
        ordered = [i for i in self._ideas.values() if i.get(ATTR_ORDER) is not None]
        unordered = [i for i in self._ideas.values() if i.get(ATTR_ORDER) is None]

        ordered.sort(key=lambda x: x.get(ATTR_ORDER, 0))
        unordered.sort(key=lambda x: x.get(ATTR_CREATED_AT, ""), reverse=True)
        return ordered + unordered

    def register_listener(self, listener: Callable[..., Any]) -> Callable[[], None]:
        """Register a callback for updates."""
        self._listeners.append(listener)

        def remove_listener():
            if listener in self._listeners:
                self._listeners.remove(listener)

        return remove_listener

    def _notify_listeners(self, context: Context | None = None) -> None:
        """Notify all registered listeners of a change."""
        self._revision += 1
        # Iterate over a copy, a listener can remove entities and their listeners
        for listener in list(self._listeners):
            if listener not in self._listeners:
                continue
            try:
                try:
                    listener(context)
                except TypeError:
                    listener()
            except Exception as err:
                _LOGGER.exception("Error notifying brainstorm listener: %s", err)

    async def async_load(self) -> None:
        """Load ideas and categories from storage."""
        data = await self._store.async_load()
        if data:
            self._ideas = {}
            for item in data.get("ideas", []):
                if ATTR_PRIORITY not in item:
                    item[ATTR_PRIORITY] = DEFAULT_PRIORITY
                self._ideas[item[ATTR_ID]] = item
            # The stored list is authoritative, so removed defaults stay removed
            loaded_cats = data.get("categories")
            if loaded_cats:
                self._categories = list(loaded_cats)
                if "Inbox" not in self._categories:
                    self._categories.insert(0, "Inbox")
            self._category_icons = data.get("category_icons", {})
            self._category_colors = data.get("category_colors", {})
            self._category_shares = data.get("category_shares", {})
            self._voting = data.get("voting", {})
            self._rounds = data.get("rounds", {})
            self._drawings = data.get("drawings", {})
            for category in list(self._rounds):
                self._schedule_round_end(category)
            _LOGGER.debug(
                "Loaded %d ideas and %d categories from storage",
                len(self._ideas),
                len(self._categories),
            )
        else:
            _LOGGER.debug("No existing brainstorm storage found, initialized defaults")
        self._notify_listeners()

    async def async_save(self) -> None:
        """Save ideas and categories to storage."""
        data = {
            "categories": self._categories,
            "category_icons": self._category_icons,
            "category_colors": self._category_colors,
            "category_shares": self._category_shares,
            "voting": self._voting,
            "rounds": self._rounds,
            "drawings": self._drawings,
            "ideas": list(self._ideas.values()),
        }
        await self._store.async_save(data)
        if self._auto_export:
            # The data is already persisted, so a failed export must not fail the action
            try:
                await self.async_export_to_markdown()
            except (OSError, HomeAssistantError) as err:
                _LOGGER.error("Brainstorm auto-export to Markdown failed: %s", err)

    def _pack(self, language: str | None = None) -> LanguagePack:
        """Return the language of a request, or the one of Home Assistant."""
        return get_pack(language or self.hass.config.language)

    def parse_priority(
        self,
        text: str,
        explicit_priority: str | None = None,
        language: str | None = None,
    ) -> tuple[str, str]:
        """Extract priority from explicit value, tags, prefixes, or return medium as default."""
        if explicit_priority:
            e = str(explicit_priority).strip().lower()
            if e in ("urgent", "dringend", "sofort", "notfall", "highest"):
                return text, PRIORITY_URGENT
            if e in ("high", "hoch", "wichtig", "prio1", "1"):
                return text, PRIORITY_HIGH
            if e in ("low", "niedrig", "prio3", "3", "später"):
                return text, PRIORITY_LOW
            return text, PRIORITY_MEDIUM

        clean = text.strip()

        # Priority tags anywhere (e.g. !urgent, !high, !low, !wichtig)
        tag_match = re.search(
            r"(?:^|\s)(!(?:urgent|dringend|notfall|sofort|high|hoch|wichtig|prio1|1|low|niedrig|prio3|3|medium|mittel|normal|prio2|2))(?:\s|$)",
            clean,
            re.IGNORECASE,
        )
        if tag_match:
            tag = tag_match.group(1).lower().lstrip("!")
            clean = re.sub(re.escape(tag_match.group(0).strip()), "", clean).strip()
            if tag in ("urgent", "dringend", "notfall", "sofort"):
                return clean, PRIORITY_URGENT
            if tag in ("high", "hoch", "wichtig", "prio1", "1"):
                return clean, PRIORITY_HIGH
            if tag in ("low", "niedrig", "prio3", "3"):
                return clean, PRIORITY_LOW
            return clean, PRIORITY_MEDIUM

        for pattern, priority in self._pack(language).priority_prefixes:
            if match := pattern.match(clean):
                return match.group(1).strip(), priority

        return clean, PRIORITY_MEDIUM

    def _glossary(self, pack: LanguagePack) -> dict[str, str]:
        """Return the spellings for spoken text, including people and categories."""
        names = [state.name for state in self.hass.states.async_all("person")]
        return pack.build_glossary(
            self.options.get(CONF_GLOSSARY), [*names, *self._categories]
        )

    def _schedule_ai_cleanup(
        self, idea_id: str, spoken_text: str, rule_text: str, pack: LanguagePack
    ) -> None:
        """Let an AI improve a stored note, without making anyone wait for it."""
        entity = self.options.get(CONF_AI_ENTITY)
        if (
            not self.options.get(CONF_AI_TEXT_CLEANUP)
            or not entity
            or pack.ai_cleanup_prompt is None
        ):
            return
        task = self.hass.async_create_background_task(
            self._async_ai_cleanup(entity, idea_id, spoken_text, rule_text, pack),
            f"brainstorm_ai_cleanup_{idea_id}",
        )
        self._ai_tasks.add(task)
        task.add_done_callback(self._ai_tasks.discard)

    async def _async_ai_cleanup(
        self,
        entity: str,
        idea_id: str,
        spoken_text: str,
        rule_text: str,
        pack: LanguagePack,
    ) -> None:
        """Replace the text of a note if the AI's version passes all checks."""
        instructions = pack.ai_cleanup_prompt(spoken_text, rule_text)
        candidate = await async_generate_text(self.hass, entity, instructions)
        idea = self._ideas.get(idea_id)
        # The person may have changed the note in the meantime
        if candidate is None or idea is None or idea.get(ATTR_TEXT) != rule_text:
            return
        improved = pack.validate_ai_rewrite(spoken_text, rule_text, candidate)
        if improved is None:
            _LOGGER.debug("Ignoring the AI text for %s: %s", idea_id, candidate)
            return
        if improved != rule_text:
            await self.async_mark_fields(idea_id, {ATTR_TEXT: improved})

    @property
    def ai_subtasks_available(self) -> bool:
        """Return whether an AI task entity can suggest subtasks."""
        return bool(self.options.get(CONF_AI_ENTITY))

    async def async_suggest_subtasks(
        self, idea: dict[str, Any], language: str | None = None
    ) -> list[str] | None:
        """Ask the AI for subtasks of an idea, None when it gave nothing usable.

        Nothing is stored: the person picks what to keep first. Raises
        AIUnavailableError when the AI did not answer, even when asked twice.
        """
        entity = self.options.get(CONF_AI_ENTITY)
        if not entity:
            return None
        pack = self._pack(language)
        children = [
            item.get(ATTR_TEXT) or ""
            for item in self._ideas.values()
            if item.get(ATTR_PARENT_ID) == idea.get(ATTR_ID)
            and item.get(ATTR_STATUS) == "active"
        ]
        instructions = pack.msg(
            "subtasks_prompt",
            text=idea.get(ATTR_TEXT) or "",
            category=idea.get(ATTR_CATEGORY) or "",
            existing=", ".join(children) if children else "–",
        )
        answer = await async_request_text_with_retry(self.hass, entity, instructions)
        suggestions = parse_subtask_suggestions(
            answer, [idea.get(ATTR_TEXT) or "", *children]
        )
        return suggestions or None

    async def async_summarize_branch(
        self, idea: dict[str, Any], user_id: str | None, language: str | None = None
    ) -> str | None:
        """Ask the AI for a short summary of a note and everything below it.

        Nothing is stored: the person decides whether it becomes the description.
        Raises AIUnavailableError when the AI did not answer, even when asked twice.
        """
        entity = self.options.get(CONF_AI_ENTITY)
        if not entity:
            return None
        pack = self._pack(language)
        lines: list[str] = []
        seen: set[str] = set()

        def walk(parent_id: str, depth: int) -> None:
            for child in self.children_of(parent_id):
                if child[ATTR_ID] in seen or len(lines) >= MAX_BRANCH_LINES:
                    continue
                seen.add(child[ATTR_ID])
                if not self.can_access(child, user_id):
                    continue
                line = f"{'  ' * depth}- {child.get(ATTR_TEXT) or ''}"
                if child.get(ATTR_STATUS) == "completed":
                    line += " ✓"
                if description := (child.get(ATTR_DESCRIPTION) or "").strip():
                    line += f" ({' '.join(description.split())[:200]})"
                lines.append(line)
                walk(child[ATTR_ID], depth + 1)

        walk(idea[ATTR_ID], 0)
        if not lines:
            return None
        instructions = pack.msg(
            "branch_summary_prompt",
            text=idea.get(ATTR_TEXT) or "",
            outline="\n".join(lines),
        )
        answer = await async_request_text_with_retry(self.hass, entity, instructions)
        return clean_summary(answer, DESCRIPTION_MAX_LENGTH)

    async def async_generate_map(
        self, text: str, language: str | None = None
    ) -> list[dict[str, Any]] | None:
        """Ask the AI for a mind map from a topic or a pasted text.

        Returns nodes with text and depth, the title first; nothing is stored,
        the person picks what to keep. Raises AIUnavailableError when the AI did
        not answer, even when asked twice.
        """
        entity = self.options.get(CONF_AI_ENTITY)
        text = (text or "").strip()[:MAP_INPUT_MAX_LENGTH]
        if not entity or not text:
            return None
        instructions = self._pack(language).msg(
            "map_prompt", text=text, limit=MAP_MAX_NODES
        )
        answer = await async_request_text_with_retry(self.hass, entity, instructions)
        return parse_map_outline(answer) or None

    async def async_suggest_parents(
        self, category: str, user_id: str | None, language: str | None = None
    ) -> list[dict[str, Any]] | None:
        """Ask the AI where loose notes of a category belong.

        Loose are main notes without subtasks; each may get another note of the
        category as its parent. Nothing is stored. Raises AIUnavailableError when
        the AI did not answer, even when asked twice.
        """
        entity = self.options.get(CONF_AI_ENTITY)
        if not entity:
            return None
        pack = self._pack(language)
        notes = [
            idea
            for idea in self.visible_ideas(user_id)
            if idea.get(ATTR_CATEGORY) == category
            and idea.get(ATTR_STATUS) == "active"
        ]
        parents = {idea.get(ATTR_PARENT_ID) for idea in notes}
        loose = self.loose_ideas(category, user_id)[:MAX_LOOSE_IDEAS]
        # Notes with subtasks first, they are the likely homes
        candidates = sorted(notes, key=lambda idea: idea[ATTR_ID] not in parents)
        candidates = candidates[:MAX_PARENT_CANDIDATES]
        if not loose or len(candidates) < 2:
            return None
        instructions = pack.msg(
            "parents_prompt",
            category=category,
            candidates="\n".join(
                f"K{index}: {idea.get(ATTR_TEXT) or ''}"
                for index, idea in enumerate(candidates, 1)
            ),
            loose="\n".join(
                f"L{index}: {idea.get(ATTR_TEXT) or ''}"
                for index, idea in enumerate(loose, 1)
            ),
        )
        answer = await async_request_text_with_retry(self.hass, entity, instructions)
        suggestions: list[dict[str, Any]] = []
        chosen: dict[str, str] = {}
        for loose_index, candidate_index in parse_parent_suggestions(
            answer, len(loose), len(candidates)
        ):
            idea, parent = loose[loose_index], candidates[candidate_index]
            # Not below itself, and loose notes not below each other in a ring
            step, ring = parent[ATTR_ID], False
            while step:
                if step == idea[ATTR_ID]:
                    ring = True
                    break
                step = chosen.get(step)
            if ring:
                continue
            chosen[idea[ATTR_ID]] = parent[ATTR_ID]
            suggestions.append(
                {
                    "idea_id": idea[ATTR_ID],
                    "text": idea.get(ATTR_TEXT) or "",
                    "parent_id": parent[ATTR_ID],
                    "parent_text": parent.get(ATTR_TEXT) or "",
                }
            )
        return suggestions

    def loose_ideas(self, category: str, user_id: str | None) -> list[dict[str, Any]]:
        """Return the main notes of a category without subtasks this user may move."""
        notes = [
            idea
            for idea in self.visible_ideas(user_id)
            if idea.get(ATTR_CATEGORY) == category
            and idea.get(ATTR_STATUS) == "active"
        ]
        parents = {idea.get(ATTR_PARENT_ID) for idea in notes}
        return [
            idea
            for idea in notes
            if not idea.get(ATTR_PARENT_ID) or idea.get(ATTR_PARENT_ID) not in self._ideas
            if idea[ATTR_ID] not in parents and self.can_edit(idea, user_id)
        ]

    async def async_cluster_ideas(
        self, category: str, user_id: str | None, language: str | None = None
    ) -> list[dict[str, Any]] | None:
        """Ask the AI to group the loose notes of a category into themes.

        Returns themes with a suggested title and their notes; None when there
        are too few loose notes. Nothing is stored. Raises AIUnavailableError
        when the AI did not answer, even when asked twice.
        """
        entity = self.options.get(CONF_AI_ENTITY)
        if not entity:
            return None
        loose = self.loose_ideas(category, user_id)[:CLUSTER_MAX_IDEAS]
        if len(loose) < CLUSTER_MIN_IDEAS:
            return None
        instructions = self._pack(language).msg(
            "cluster_prompt",
            category=category,
            loose="\n".join(
                f"L{index}: {idea.get(ATTR_TEXT) or ''}"
                for index, idea in enumerate(loose, 1)
            ),
        )
        answer = await async_request_text_with_retry(self.hass, entity, instructions)
        return [
            {
                "title": title,
                "ideas": [
                    {"idea_id": loose[i][ATTR_ID], "text": loose[i].get(ATTR_TEXT) or ""}
                    for i in members
                ],
            }
            for title, members in parse_clusters(answer, len(loose))
        ]

    async def async_group_ideas(
        self, title: str, idea_ids: list[str], context: Context | None = None
    ) -> dict[str, Any]:
        """Put notes of one category below a new note with this title.

        The new note takes the place of the first of them; the notes keep
        their order and their subtasks.
        """
        ideas = [self._ideas[i] for i in dict.fromkeys(idea_ids) if i in self._ideas]
        category = ideas[0].get(ATTR_CATEGORY) or self._fallback_category
        author = context.user_id if context else None
        if any(idea.get(ATTR_ORDER) is None for idea in ideas):
            # Give every note a place first, as the cards show them now
            for index, item in enumerate(self.ideas):
                item[ATTR_ORDER] = index
        top = ideas[0].get(ATTR_PARENT_ID)
        now_iso = dt_util.now().isoformat()
        group: dict[str, Any] = {
            ATTR_ID: uuid.uuid4().hex[:8],
            ATTR_TEXT: title,
            ATTR_CATEGORY: category,
            ATTR_PRIORITY: DEFAULT_PRIORITY,
            ATTR_PARENT_ID: top if top in self._ideas else None,
            ATTR_ORDER: min(int(idea[ATTR_ORDER]) for idea in ideas),
            ATTR_SOURCE: "dashboard",
            ATTR_DEVICE: None,
            ATTR_TAGS: [],
            ATTR_STATUS: "active",
            ATTR_CREATED_AT: now_iso,
            ATTR_UPDATED_AT: now_iso,
            ATTR_DUE: None,
            ATTR_ASSIGNEE: None,
            ATTR_TRIGGER: None,
            ATTR_OWNER: self.owner_for_new_idea(author, category, None),
            ATTR_SHARES: {},
        }
        if author and group[ATTR_OWNER] != author:
            group[ATTR_CREATED_BY] = author
        self._ideas[group[ATTR_ID]] = group
        for idea in ideas:
            idea[ATTR_PARENT_ID] = group[ATTR_ID]
            idea[ATTR_UPDATED_AT] = now_iso
        await self.async_save()
        act_context = context or Context()
        self.hass.bus.async_fire(
            EVENT_IDEA_ADDED, {**group, "entity_id": OVERVIEW_ENTITY_ID}, context=act_context
        )
        for idea in ideas:
            self.hass.bus.async_fire(
                EVENT_IDEA_UPDATED,
                {**idea, "entity_id": OVERVIEW_ENTITY_ID},
                context=act_context,
            )
        self._notify_listeners(context=act_context)
        return group

    def async_cancel_ai_tasks(self) -> None:
        """Stop AI work and round timers that still run when the integration unloads."""
        for task in self._ai_tasks:
            task.cancel()
        for cancel in self._round_timers.values():
            cancel()
        self._round_timers.clear()

    def parse_text_and_category(
        self,
        text: str,
        explicit_category: str | None = None,
        explicit_priority: str | None = None,
        spoken: bool = True,
        language: str | None = None,
    ) -> tuple[str, str, list[str], str]:
        """Parse raw text to extract category, clean text, hashtags and priority."""
        pack = self._pack(language)
        clean_text, resolved_prio = self.parse_priority(
            text, explicit_priority, language
        )
        category: str | None = None

        # Build dynamic alias and keyword lookup for all registered categories
        active_aliases: dict[str, list[str]] = {}
        active_keywords: dict[str, list[str]] = {}

        # A category of its own wins over a standard alias with its name, so that
        # 'Einkauf' does not end up in 'Alltag' once the person created 'Einkauf'
        own_names = {c.strip().lower() for c in self._categories}
        for cat in self._categories:
            if cat.lower() == "inbox":
                continue
            key = CATEGORY_KEYS.get(cat)
            cat_clean = cat.strip().lower()
            aliases = [
                a
                for a in pack.category_aliases.get(key, [])
                if a == cat_clean or a not in own_names
            ]
            if cat_clean not in aliases:
                aliases.append(cat_clean)
            if "&" in cat_clean:
                aliases.append(cat_clean.replace("&", pack.and_word).strip())
            active_aliases[cat] = aliases

            kws = [
                k
                for k in pack.category_keywords.get(key, [])
                if k == cat_clean or k not in own_names
            ]
            for word in re.findall(r"[a-zA-Z0-9äöüÄÖÜß]{3,}", cat_clean):
                if word not in kws and word not in pack.category_stop_words:
                    kws.append(word)
            active_keywords[cat] = kws

        # 0. Check explicit category if provided
        if explicit_category and explicit_category.strip() and explicit_category.lower() != "auto":
            exp = explicit_category.strip()
            # Direct match
            for c in self._categories:
                if c.lower() == exp.lower():
                    category = c
                    break
            # Alias match
            if not category:
                for cat_name, aliases in active_aliases.items():
                    if exp.lower() in [a.lower() for a in aliases]:
                        category = cat_name
                        break
            if not category:
                category = exp

        # Extract hashtags, a spoken "hashtag garten" becomes "#garten"
        clean_text = SPOKEN_TAG_PATTERN.sub(lambda m: f"#{m.group(1).lower()}", clean_text)
        written_tags = [
            tag for tag in TAG_PATTERN.findall(clean_text) if not COLOR_TAG_PATTERN.fullmatch(tag)
        ]
        tags = list(dict.fromkeys(tag.lower() for tag in written_tags))

        # 1. Prefix: 'Kategorie: Der eigentliche Text' or '[Kategorie] Der eigentliche Text'
        if not category:
            match_prefix = re.match(
                r"^(?:\[([a-zA-Z0-9äöüÄÖÜß\s\-_&]{2,30})\]:?|"
                r"([a-zA-Z0-9äöüÄÖÜß\s\-_&]{2,30}):)\s*(.+)$",
                clean_text,
                re.IGNORECASE,
            )
            if match_prefix:
                cand = (match_prefix.group(1) or match_prefix.group(2)).strip()
                rem_text = match_prefix.group(3).strip()
                for c in self._categories:
                    if c.lower() == cand.lower():
                        category = c
                        clean_text = rem_text
                        break
                if not category:
                    for cat_name, aliases in active_aliases.items():
                        if cand.lower() in [a.lower() for a in aliases]:
                            category = cat_name
                            clean_text = rem_text
                            break

        # 2. Compound Project / Topic Prefix:
        # e.g. 'Projekt Brainstorm erweitern' -> Category: 'Brainstorm', Text: 'Brainstorm erweitern'
        # or 'Projekt Gartenhaus bauen' -> Category: 'Projekte', Text: 'Gartenhaus bauen'
        if not category:
            match_compound = pack.topic_pattern.match(clean_text)
            if match_compound:
                target_cand = match_compound.group(1).strip()
                rem_content = match_compound.group(2).strip()
                # Check if target_cand matches an active category (e.g. Brainstorm)
                for cat_name, aliases in active_aliases.items():
                    if target_cand.lower() in [a.lower() for a in aliases]:
                        category = cat_name
                        clean_text = f"{target_cand.capitalize()} {rem_content}"
                        break
                projects = next(
                    (c for c in self._categories if CATEGORY_KEYS.get(c) == CATEGORY_PROJECTS),
                    None,
                )
                if not category and projects:
                    category = projects
                    clean_text = f"{target_cand} {rem_content}"

        # 3. Prepositional / Leading Indicator phrases:
        # e.g. 'für den Garten ...', 'im Garten ...', 'fürs Smarthome ...', 'für Brainstorm ...'
        if not category:
            for cat_name, aliases in active_aliases.items():
                for alias in sorted(aliases, key=len, reverse=True):
                    pattern = f"{pack.alias_lead}{re.escape(alias)}{pack.alias_tail}"
                    m = re.match(pattern, clean_text, re.IGNORECASE)
                    if m:
                        category = cat_name
                        remainder = m.group(2).strip()
                        # After a plain space, a single remaining word usually needs
                        # the alias to make sense ('Haus streichen'), and a verb
                        # shows the alias is the subject ('Garten muss gemäht werden').
                        is_subject = not m.group(1).strip() and pack.starts_with_verb(
                            remainder
                        )
                        # 'für den Einkauf Duschgel' names the list, so only
                        # 'Duschgel' is the note
                        has_lead = not clean_text.lower().startswith(alias)
                        if not is_subject and (
                            has_lead
                            or m.group(1).strip()
                            or len(remainder.split()) > 1
                        ):
                            clean_text = remainder
                        break
                if category:
                    break

        # 4. Hashtags matching
        if not category and tags:
            for tag in tags:
                for c in self._categories:
                    if c.lower() == tag.lower():
                        category = c
                        break
                if not category:
                    for cat_name, aliases in active_aliases.items():
                        if tag.lower() in [a.lower() for a in aliases]:
                            category = cat_name
                            break
                if category:
                    break

        # 5. Contextual Keyword & Semantic Scoring
        if not category:
            lower_text = clean_text.lower()
            words = set(re.findall(r"[a-zA-Z0-9äöüÄÖÜß]+", lower_text))
            scores: dict[str, int] = {c: 0 for c in self._categories if c.lower() != "inbox"}

            for cat_name, kws in active_keywords.items():
                cat_aliases = active_aliases.get(cat_name, [cat_name.lower()])
                # High priority if an alias is directly mentioned in the sentence
                for alias in cat_aliases:
                    if alias in words:
                        scores[cat_name] += 12
                    elif " " in alias and alias in lower_text:
                        scores[cat_name] += 10

                for kw in kws:
                    if " " in kw:
                        if kw in lower_text:
                            scores[cat_name] += 4
                    else:
                        if kw in words:
                            scores[cat_name] += 3
                        elif any(w.startswith(kw) or w.endswith(kw) for w in words if len(w) > 4 and len(kw) > 3):
                            scores[cat_name] += 1

            if scores:
                best_cat = max(scores, key=scores.get)
                if scores[best_cat] > 0:
                    category = best_cat

        # Fallback to the configured default category
        if not category or category not in self._categories:
            category = self._fallback_category

        # 6. Check priority once more if still medium (in case priority keyword appeared after stripped category prefix)
        if resolved_prio == PRIORITY_MEDIUM and not explicit_priority:
            clean_text, detected_prio = self.parse_priority(
                clean_text, language=language
            )
            if detected_prio != PRIORITY_MEDIUM:
                resolved_prio = detected_prio

        if (
            spoken
            and self._smart_formatting
            and resolved_prio == PRIORITY_MEDIUM
            and not explicit_priority
        ):
            clean_text, spoken_prio = pack.extract_priority(clean_text)
            resolved_prio = spoken_prio or resolved_prio

        # 7. Smart NLP Text Normalization, a typed text only gets its typos fixed.
        # The tags of a spoken sentence wait at its end, so they do not break it up.
        if self._smart_formatting:
            spoken_tags: list[str] = []
            if spoken and tags:
                # Each tag once, spelled as written
                spoken_tags = [
                    f"#{tag}" for tag in {t.lower(): t for t in reversed(written_tags)}.values()
                ][::-1]
                clean_text = TAG_PATTERN.sub(
                    lambda m: m.group(0) if COLOR_TAG_PATTERN.fullmatch(m.group(1)) else "",
                    clean_text,
                )
                clean_text = re.sub(r"\s{2,}", " ", clean_text).strip()
            formatted = (
                pack.clean_text(clean_text, self._glossary(pack))
                if spoken
                else pack.format_typed(clean_text)
            )
            if formatted:
                clean_text = formatted
            if spoken_tags:
                clean_text = " ".join([clean_text, *spoken_tags]).strip()

        return clean_text, category, tags, resolved_prio

    async def async_add_idea(
        self,
        text: str,
        category: str | None = None,
        priority: str | None = None,
        source: str = "manual",
        tags: list[str] | None = None,
        device: str | None = None,
        parent_id: str | None = None,
        context: Context | None = None,
        due: datetime | None = None,
        assignee: str | None = None,
        trigger: dict[str, str | None] | None = None,
        owner: str | None = None,
        shares: dict[str, str] | None = None,
        language: str | None = None,
        spoken: bool | None = None,
        verbatim: bool = False,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Add a new brainstorm idea.

        A verbatim idea keeps its text and category exactly as given, as an
        item taken over from another list must not be renamed there.
        """
        pack = self._pack(language)
        raw_check = (text or "").strip().lower()
        if not raw_check or raw_check in {
            "none",
            "responsenone",
            "responseno",
            "null",
            "undefined",
            "abbrechen",
            "stop",
            "stopp",
            "cancel",
        }:
            raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="invalid_text", translation_placeholders={"text": str(text)}
        )

        if verbatim:
            spoken = False
        elif spoken is None:
            spoken = source not in TYPED_SOURCES
        if (
            spoken
            and self._smart_formatting
            and self._voice_due
            and due is None
            and trigger is None
        ):
            spoken_due, remaining = pack.extract_due(text.strip(), dt_util.now())
            if spoken_due is not None:
                due = spoken_due
                raw_text, text = text.strip(), remaining
            else:
                raw_text = text.strip()
        else:
            raw_text = text.strip()

        if verbatim:
            resolved_cat = (category or "").strip() or self._fallback_category
            if resolved_cat not in self._categories:
                self._categories.append(resolved_cat)
            clean_text, parsed_tags = raw_text, []
            resolved_prio = self.parse_priority("", priority, language)[1]
        else:
            clean_text, resolved_cat, parsed_tags, resolved_prio = (
                self.parse_text_and_category(
                    text, category, priority, spoken=spoken, language=language
                )
            )

        all_tags = list(set((tags or []) + parsed_tags))
        now_iso = dt_util.now().isoformat()
        idea_id = uuid.uuid4().hex[:8]

        author = owner or (context.user_id if context else None)
        resolved_parent = None
        if parent_id and parent_id.strip() in self._ideas:
            resolved_parent = parent_id.strip()

        ordered_vals = [i.get(ATTR_ORDER) for i in self._ideas.values() if i.get(ATTR_ORDER) is not None]
        min_order = min(ordered_vals, default=0) if ordered_vals else 0
        new_order = min_order - 1 if ordered_vals else 0

        idea = {
            ATTR_ID: idea_id,
            ATTR_TEXT: clean_text,
            ATTR_CATEGORY: resolved_cat,
            ATTR_PRIORITY: resolved_prio,
            ATTR_PARENT_ID: resolved_parent,
            ATTR_ORDER: new_order,
            ATTR_SOURCE: source,
            ATTR_DEVICE: (device or "").strip() if device else None,
            ATTR_TAGS: all_tags,
            ATTR_STATUS: "active",
            ATTR_CREATED_AT: now_iso,
            ATTR_UPDATED_AT: now_iso,
            ATTR_DUE: due.isoformat() if due else None,
            ATTR_ASSIGNEE: assignee,
            ATTR_TRIGGER: trigger,
            ATTR_OWNER: self.owner_for_new_idea(
                author,
                resolved_cat,
                self._ideas.get(resolved_parent) if resolved_parent else None,
            ),
            ATTR_SHARES: shares or {},
        }
        if description and description.strip():
            idea[ATTR_DESCRIPTION] = description.strip()
        # Keeps what was really said, so a bad shortening can be undone
        if raw_text != clean_text:
            idea[ATTR_RAW_TEXT] = raw_text
        # Written into someone else's list, so its owner can see who it was
        if author and idea[ATTR_OWNER] != author:
            idea[ATTR_CREATED_BY] = author
        # During a hidden round only its author sees the new note
        if author and resolved_cat in self._rounds:
            idea[ATTR_ROUND_BY] = author
        # Someone who is meant to be reminded also has to see the idea
        if assignee_user := self._person_user(assignee):
            idea[ATTR_SHARES].setdefault(assignee_user, SHARE_EDIT)

        act_context = context or Context()
        self._last_action = {
            "action": "added",
            "id": idea_id,
            "text": clean_text,
            "category": resolved_cat,
            "priority": resolved_prio,
            "source": source,
            "device": (device or "").strip() if device else None,
            "timestamp": now_iso,
            "description": f"{pack.msg('log_added')}: \"{clean_text}\" ({resolved_cat})",
        }

        self._ideas[idea_id] = idea
        await self.async_save()

        if spoken and self._smart_formatting and source != SOURCE_ASSIST_LLM:
            self._schedule_ai_cleanup(idea_id, text.strip(), clean_text, pack)

        # Fire event for automations and logbook with entity_id and context
        event_data = {
            **idea,
            "entity_id": OVERVIEW_ENTITY_ID,
        }
        self.hass.bus.async_fire(EVENT_IDEA_ADDED, event_data, context=act_context)
        self._notify_listeners(context=act_context)
        _LOGGER.info(
            "Brainstorm idea [%s] added in category '%s' (prio: %s, parent: %s, device: %s)",
            idea_id,
            resolved_cat,
            resolved_prio,
            resolved_parent,
            device,
        )
        return idea

    def _creates_parent_cycle(self, idea_id: str, parent_id: str) -> bool:
        """Return whether making parent_id the parent of idea_id creates a cycle."""
        seen: set[str] = set()
        current: str | None = parent_id
        while current and current not in seen:
            if current == idea_id:
                return True
            seen.add(current)
            current = self._ideas.get(current, {}).get(ATTR_PARENT_ID)
        return False

    async def async_update_idea(
        self,
        idea_id: str,
        text: str | None = None,
        category: str | None = None,
        priority: str | None = None,
        status: str | None = None,
        device: str | None = None,
        parent_id: str | None = None,
        update_parent: bool = False,
        order: int | None = None,
        context: Context | None = None,
        due: datetime | None = None,
        update_due: bool = False,
        result: str | None = None,
        update_result: bool = False,
        description: str | None = None,
        update_description: bool = False,
        in_progress: bool | None = None,
        shape: str | None = None,
        update_shape: bool = False,
        markers: list[str] | None = None,
        update_markers: bool = False,
        progress: int | None = None,
        update_progress: bool = False,
        links: list[dict[str, Any]] | None = None,
        update_links: bool = False,
        frame: str | None = None,
        update_frame: bool = False,
        callout: str | None = None,
        update_callout: bool = False,
        numbering: str | None = None,
        update_numbering: bool = False,
        repeat: str | None = None,
        update_repeat: bool = False,
    ) -> dict[str, Any] | None:
        """Update an existing idea.

        The result note says what came of an idea, usually when it is ticked
        off. It stays when the idea is reopened, and an empty one removes it.
        """
        if idea_id not in self._ideas:
            _LOGGER.warning("Brainstorm idea %s not found for update", idea_id)
            return None

        if (
            update_parent
            and parent_id
            and parent_id.strip() not in ("", "none")
            and parent_id.strip() not in self._ideas
        ):
            raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="parent_not_found", translation_placeholders={"id": parent_id}
        )

        if update_parent and parent_id and self._creates_parent_cycle(
            idea_id, parent_id.strip()
        ):
            raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="parent_cycle", translation_placeholders={"id": parent_id}
        )

        idea = self._ideas[idea_id]
        newly_completed = status == "completed" and idea.get(ATTR_STATUS) != "completed"
        reopened = status == "active" and idea.get(ATTR_STATUS) in ("completed", "archived")
        if text is not None:
            idea[ATTR_TEXT] = text.strip()
        if category is not None:
            cat_clean = category.strip()
            if cat_clean not in self._categories:
                self._categories.append(cat_clean)
            # Its place on the map of the old list means nothing in the new one
            if idea.get(ATTR_CATEGORY) != cat_clean:
                idea.pop(ATTR_MAP_POS, None)
                idea.pop(ATTR_PIN, None)
            idea[ATTR_CATEGORY] = cat_clean
        if priority is not None:
            _, normalized_prio = self.parse_priority("", priority)
            idea[ATTR_PRIORITY] = normalized_prio
        if status is not None:
            idea[ATTR_STATUS] = status
            if newly_completed:
                idea[ATTR_COMPLETED_AT] = dt_util.now().isoformat()
            elif status == "active":
                idea.pop(ATTR_COMPLETED_AT, None)
        if in_progress and not idea.get(ATTR_IN_PROGRESS):
            mark: dict[str, Any] = {"since": dt_util.now().isoformat()}
            if context is not None and context.user_id:
                mark["by"] = context.user_id
            idea[ATTR_IN_PROGRESS] = mark
        elif in_progress is False:
            idea.pop(ATTR_IN_PROGRESS, None)
        # Work on an idea ends when it is done
        if idea.get(ATTR_STATUS) in ("completed", "archived"):
            idea.pop(ATTR_IN_PROGRESS, None)
        if device is not None:
            idea[ATTR_DEVICE] = device.strip() if device else None
        if order is not None:
            idea[ATTR_ORDER] = int(order)
        if update_due:
            new_due = due.isoformat() if due else None
            if new_due != idea.get(ATTR_DUE):
                idea[ATTR_DUE] = new_due
                idea[ATTR_REMINDED_AT] = None
                idea[ATTR_ESCALATED] = False
                idea[ATTR_URGENT_SENT] = False
                idea[ATTR_ALEXA_NATIVE] = False
        if update_result:
            if result and result.strip():
                idea[ATTR_RESULT] = result.strip()
            else:
                idea.pop(ATTR_RESULT, None)
        if update_description:
            if description and description.strip():
                idea[ATTR_DESCRIPTION] = description.strip()
            else:
                idea.pop(ATTR_DESCRIPTION, None)
        if update_shape:
            if shape in NODE_SHAPES:
                idea[ATTR_SHAPE] = shape
            else:
                idea.pop(ATTR_SHAPE, None)
        if update_markers:
            if cleaned := _clean_markers(markers):
                idea[ATTR_MARKERS] = cleaned
            else:
                idea.pop(ATTR_MARKERS, None)
        if update_progress:
            if cleaned_progress := _clean_progress(progress):
                idea[ATTR_PROGRESS] = cleaned_progress
            else:
                idea.pop(ATTR_PROGRESS, None)
        if update_links:
            if cleaned_links := _clean_links(links, idea_id, set(self._ideas)):
                idea[ATTR_LINKS] = cleaned_links
            else:
                idea.pop(ATTR_LINKS, None)
        if update_frame:
            if cleaned_frame := _clean_short_text(frame, FRAME_MAX_LENGTH):
                idea[ATTR_FRAME] = cleaned_frame
            else:
                idea.pop(ATTR_FRAME, None)
        if update_callout:
            if cleaned_callout := _clean_short_text(callout, CALLOUT_MAX_LENGTH):
                idea[ATTR_CALLOUT] = cleaned_callout
            else:
                idea.pop(ATTR_CALLOUT, None)
        if update_numbering:
            if numbering in NUMBERING_STYLES:
                idea[ATTR_NUMBERING] = numbering
            else:
                idea.pop(ATTR_NUMBERING, None)
        if update_repeat:
            if repeat in REPEAT_RULES:
                idea[ATTR_REPEAT] = repeat
            else:
                idea.pop(ATTR_REPEAT, None)
        repeated: dict[str, Any] | None = None
        if newly_completed and idea.get(ATTR_REPEAT) in REPEAT_RULES:
            repeated = self._repeat_idea(idea)
        elif reopened and idea.get(ATTR_REPEATED_AS):
            self._take_back_repeat(idea)
        if update_parent:
            if not parent_id or parent_id.strip() in ("", "none"):
                idea[ATTR_PARENT_ID] = None
            else:
                idea[ATTR_PARENT_ID] = parent_id.strip()

        now_iso = dt_util.now().isoformat()
        idea[ATTR_UPDATED_AT] = now_iso

        act_context = context or Context()
        action_type = "completed" if newly_completed else "updated"
        pack = self._pack()
        action_desc = (
            f"{pack.msg('log_completed')}: \"{idea.get(ATTR_TEXT)}\" ({idea.get(ATTR_CATEGORY)})"
            if newly_completed
            else f"{pack.msg('log_updated')}: \"{idea.get(ATTR_TEXT)}\" ({idea.get(ATTR_CATEGORY)})"
        )
        self._last_action = {
            "action": action_type,
            "id": idea_id,
            "text": idea.get(ATTR_TEXT),
            "category": idea.get(ATTR_CATEGORY),
            "priority": idea.get(ATTR_PRIORITY),
            "status": status or idea.get(ATTR_STATUS),
            "timestamp": now_iso,
            "description": action_desc,
        }

        await self.async_save()

        event_name = EVENT_IDEA_COMPLETED if newly_completed else EVENT_IDEA_UPDATED
        event_data = {
            **idea,
            "entity_id": OVERVIEW_ENTITY_ID,
        }
        self.hass.bus.async_fire(event_name, event_data, context=act_context)
        if repeated is not None:
            self.hass.bus.async_fire(
                EVENT_IDEA_ADDED,
                {**repeated, "entity_id": OVERVIEW_ENTITY_ID},
                context=act_context,
            )
        self._notify_listeners(context=act_context)
        return idea

    def _repeat_idea(self, idea: dict[str, Any]) -> dict[str, Any]:
        """Add the next round of a repeating idea that was just ticked off.

        The new idea is due at the next date of the rule, after now, and its
        subtasks come along open again. The done idea remembers it and gives
        the rule to it, so reopening the done one can take the new one back.
        """
        now = dt_util.now()
        old_due = dt_util.parse_datetime(str(idea.get(ATTR_DUE) or ""))
        if old_due is not None:
            old_due = dt_util.as_local(old_due)
        new_due = next_repeat_due(old_due, idea[ATTR_REPEAT], now)
        shift = new_due - (old_due or new_due)
        now_iso = now.isoformat()
        copied = (
            ATTR_TEXT, ATTR_CATEGORY, ATTR_PRIORITY, ATTR_SOURCE, ATTR_DEVICE,
            ATTR_TAGS, ATTR_ASSIGNEE, ATTR_TRIGGER, ATTR_OWNER, ATTR_DESCRIPTION,
            ATTR_SHAPE, ATTR_MARKERS, ATTR_FRAME, ATTR_CALLOUT, ATTR_NUMBERING,
            ATTR_MAP_POS, ATTR_PIN, ATTR_ORDER, ATTR_CREATED_BY,
        )

        def clone(source: dict[str, Any], parent: str | None, due: datetime | None) -> dict[str, Any]:
            new_id = uuid.uuid4().hex[:8]
            while new_id in self._ideas:
                new_id = uuid.uuid4().hex[:8]
            new = {key: source[key] for key in copied if key in source}
            new.update(
                {
                    ATTR_ID: new_id,
                    ATTR_PARENT_ID: parent,
                    ATTR_STATUS: "active",
                    ATTR_CREATED_AT: now_iso,
                    ATTR_UPDATED_AT: now_iso,
                    ATTR_DUE: due.isoformat() if due else None,
                    ATTR_SHARES: dict(source.get(ATTR_SHARES) or {}),
                }
            )
            self._ideas[new_id] = new
            return new

        parent = idea.get(ATTR_PARENT_ID)
        if parent and self._ideas.get(parent, {}).get(ATTR_STATUS) not in (None, "active"):
            parent = None
        first = clone(idea, parent, new_due)
        first[ATTR_REPEAT] = idea.pop(ATTR_REPEAT)
        idea[ATTR_REPEATED_AS] = first[ATTR_ID]
        # The subtasks, all levels, open again and moved by the same time
        queue = [(idea[ATTR_ID], first[ATTR_ID])]
        count = 0
        closed: list[str] = []
        while queue and count < REPEAT_MAX_SUBTASKS:
            old_parent, new_parent = queue.pop(0)
            for child in list(self._ideas.values()):
                if child.get(ATTR_PARENT_ID) != old_parent or child.get(ATTR_STATUS) == "archived":
                    continue
                if count >= REPEAT_MAX_SUBTASKS:
                    break
                child_due = dt_util.parse_datetime(str(child.get(ATTR_DUE) or ""))
                moved = dt_util.as_local(child_due) + shift if child_due else None
                new_child = clone(child, new_parent, moved)
                queue.append((child[ATTR_ID], new_child[ATTR_ID]))
                count += 1
                # The open subtasks of this round end with it, the new round has its own
                if child.get(ATTR_STATUS) == "active":
                    child[ATTR_STATUS] = "completed"
                    child[ATTR_COMPLETED_AT] = now_iso
                    child.pop(ATTR_IN_PROGRESS, None)
                    closed.append(child[ATTR_ID])
        if closed:
            idea[ATTR_REPEAT_CLOSED] = closed
        _LOGGER.info(
            "Brainstorm idea [%s] repeats %s as [%s], due %s",
            idea[ATTR_ID],
            first[ATTR_REPEAT],
            first[ATTR_ID],
            first[ATTR_DUE],
        )
        return first

    def _take_back_repeat(self, idea: dict[str, Any]) -> None:
        """Remove the next round of a reopened idea, unless work began on it."""
        new_id = idea.pop(ATTR_REPEATED_AS, None)
        closed = idea.pop(ATTR_REPEAT_CLOSED, None) or []
        new = self._ideas.get(new_id) if new_id else None
        if new is None or new.get(ATTR_STATUS) != "active":
            return
        for child_id in closed:
            child = self._ideas.get(child_id)
            if child is not None and child.get(ATTR_STATUS) == "completed":
                child[ATTR_STATUS] = "active"
                child.pop(ATTR_COMPLETED_AT, None)
        idea[ATTR_REPEAT] = new.get(ATTR_REPEAT, idea.get(ATTR_REPEAT))
        removed = {new_id}
        changed = True
        while changed:
            changed = False
            for other_id, other in list(self._ideas.items()):
                if other_id not in removed and other.get(ATTR_PARENT_ID) in removed:
                    removed.add(other_id)
                    changed = True
        for other_id in removed:
            self._ideas.pop(other_id, None)

    async def async_set_due(
        self, idea_id: str, due: datetime | None, context: Context | None = None
    ) -> dict[str, Any] | None:
        """Set or clear when an idea is due."""
        return await self.async_update_idea(
            idea_id, due=due, update_due=True, context=context
        )

    async def async_mark_reminded(self, idea_id: str, escalated: bool) -> None:
        """Remember that a reminder went out, without a new activity entry."""
        idea = self._ideas.get(idea_id)
        if idea is None:
            return
        if not idea.get(ATTR_REMINDED_AT):
            idea[ATTR_REMINDED_AT] = dt_util.now().isoformat()
        idea[ATTR_ESCALATED] = escalated
        await self.async_save()
        self._notify_listeners()

    async def async_mark_fields(self, idea_id: str, fields: dict[str, Any]) -> None:
        """Store reminder details of an idea, without a new activity entry."""
        idea = self._ideas.get(idea_id)
        if idea is None:
            return
        idea.update(fields)
        await self.async_save()
        self._notify_listeners()

    async def async_set_links(self, links: dict[str, dict[str, Any] | None]) -> None:
        """Store the to-do list items ideas are linked to, saving only once."""
        await self.async_set_fields(
            {idea_id: {ATTR_TODO_LINK: link} for idea_id, link in links.items()}
        )

    async def async_set_fields(self, updates: dict[str, dict[str, Any]]) -> None:
        """Store sync details of several ideas, saving only once.

        None removes a field. Only a changed amount is shown in the cards, so
        the cards are only told when one changed.
        """
        changed = visible = False
        for idea_id, fields in updates.items():
            idea = self._ideas.get(idea_id)
            if idea is None:
                continue
            for key, value in fields.items():
                if idea.get(key) == value:
                    continue
                if value is None:
                    idea.pop(key, None)
                else:
                    idea[key] = value
                changed = True
                visible = visible or key == ATTR_SPEC
        if changed:
            await self.async_save()
        if visible:
            self._notify_listeners()

    async def async_archive_ideas(self, idea_ids: list[str]) -> int:
        """Archive several ideas at once, unlinked from their lists.

        Archived ideas leave every view of the cards. The item on a linked
        list stays where it is.
        """
        now_iso = dt_util.now().isoformat()
        archived = 0
        for idea_id in idea_ids:
            idea = self._ideas.get(idea_id)
            if idea is None or idea.get(ATTR_STATUS) == "archived":
                continue
            idea[ATTR_STATUS] = "archived"
            idea[ATTR_UPDATED_AT] = now_iso
            idea.setdefault(ATTR_COMPLETED_AT, now_iso)
            idea.pop(ATTR_IN_PROGRESS, None)
            idea.pop(ATTR_TODO_LINK, None)
            idea.pop(ATTR_SPEC, None)
            archived += 1
        if archived:
            await self.async_save()
            self._notify_listeners()
        return archived

    # Attachments

    @property
    def attachment_root(self) -> Path:
        """Return the folder that holds the attachments of all ideas."""
        return Path(self.hass.config.path(ATTACHMENT_DIR))

    def attachment_file(self, idea_id: str, attachment_id: str) -> Path | None:
        """Return the file of an attachment the store knows, or None."""
        idea = self._ideas.get(idea_id)
        if idea is None:
            return None
        for attachment in idea.get(ATTR_ATTACHMENTS) or []:
            if attachment.get(ATTR_ID) == attachment_id:
                return self._attachment_path(idea_id, attachment)
        return None

    def _attachment_path(self, idea_id: str, attachment: dict[str, Any]) -> Path:
        """Return where an attachment lies; names come only from the store."""
        suffix = Path(str(attachment.get("name") or "")).suffix.lower()
        if suffix not in ATTACHMENT_TYPES:
            suffix = ""
        return (
            self.attachment_root
            / attachment_folder(idea_id)
            / f"{attachment[ATTR_ID]}{suffix}"
        )

    async def async_add_attachment(
        self,
        idea_id: str,
        name: str,
        data: bytes,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """Store a file with an idea and return its entry."""
        idea = self._ideas.get(idea_id)
        if idea is None:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="idea_not_found",
                translation_placeholders={"id": idea_id},
            )
        clean_name = attachment_name(name)
        suffix = Path(clean_name).suffix.lower()
        if suffix not in ATTACHMENT_TYPES:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="attachment_type",
                translation_placeholders={"name": clean_name},
            )
        if not data:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="attachment_empty",
                translation_placeholders={"name": clean_name},
            )
        if len(data) > ATTACHMENT_MAX_SIZE:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="attachment_too_large",
                translation_placeholders={
                    "name": clean_name,
                    "max": str(ATTACHMENT_MAX_SIZE // (1024 * 1024)),
                },
            )
        attachments = list(idea.get(ATTR_ATTACHMENTS) or [])
        if len(attachments) >= ATTACHMENT_MAX_COUNT:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="attachment_too_many",
                translation_placeholders={"max": str(ATTACHMENT_MAX_COUNT)},
            )
        attachment = {
            ATTR_ID: uuid.uuid4().hex,
            "name": clean_name,
            "type": ATTACHMENT_TYPES[suffix],
            "size": len(data),
            "added_at": dt_util.now().isoformat(),
        }
        if user_id:
            attachment["added_by"] = user_id
        path = self._attachment_path(idea_id, attachment)

        def _write() -> None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)

        try:
            await self.hass.async_add_executor_job(_write)
        except OSError as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="attachment_write_failed",
                translation_placeholders={"error": str(err)},
            ) from err
        # The idea may have changed while the file was written
        idea = self._ideas.get(idea_id)
        if idea is None:
            await self.hass.async_add_executor_job(_remove_files, [path])
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="idea_not_found",
                translation_placeholders={"id": idea_id},
            )
        idea[ATTR_ATTACHMENTS] = [*(idea.get(ATTR_ATTACHMENTS) or []), attachment]
        idea[ATTR_UPDATED_AT] = dt_util.now().isoformat()
        await self.async_save()
        self._notify_listeners()
        return attachment

    async def async_remove_attachment(self, idea_id: str, attachment_id: str) -> bool:
        """Delete one attachment of an idea, with its file."""
        idea = self._ideas.get(idea_id)
        if idea is None:
            return False
        attachments = idea.get(ATTR_ATTACHMENTS) or []
        found = next((a for a in attachments if a.get(ATTR_ID) == attachment_id), None)
        if found is None:
            return False
        remaining = [a for a in attachments if a is not found]
        if remaining:
            idea[ATTR_ATTACHMENTS] = remaining
        else:
            idea.pop(ATTR_ATTACHMENTS, None)
        idea[ATTR_UPDATED_AT] = dt_util.now().isoformat()
        await self.hass.async_add_executor_job(
            _remove_files, [self._attachment_path(idea_id, found)]
        )
        await self.async_save()
        self._notify_listeners()
        return True

    async def async_cleanup_attachments(self) -> int:
        """Delete the attachments of ideas done for a while, and orphaned files.

        Ideas deleted since the start keep their files, so undo brings them
        back complete. Returns the number of attachments removed from ideas.
        """
        limit = dt_util.now() - timedelta(days=ATTACHMENT_RETENTION_DAYS)
        expired: list[Path] = []
        removed = 0
        for idea_id, idea in self._ideas.items():
            attachments = idea.get(ATTR_ATTACHMENTS)
            if not attachments or idea.get(ATTR_STATUS) not in ("completed", "archived"):
                continue
            done_at = dt_util.parse_datetime(
                str(idea.get(ATTR_COMPLETED_AT) or idea.get(ATTR_UPDATED_AT) or "")
            )
            if done_at is None or dt_util.as_local(done_at) > limit:
                continue
            expired.extend(self._attachment_path(idea_id, a) for a in attachments)
            removed += len(attachments)
            idea.pop(ATTR_ATTACHMENTS)
        keep = {
            attachment_folder(idea_id)
            for idea_id, idea in (
                *self._ideas.items(),
                *((i, d["idea"]) for i, d in self._deleted.items()),
            )
            if idea.get(ATTR_ATTACHMENTS)
        }
        root = self.attachment_root

        def _cleanup() -> None:
            _remove_files(expired)
            if not root.is_dir():
                return
            for folder in root.iterdir():
                if folder.is_dir() and folder.name not in keep:
                    shutil.rmtree(folder, ignore_errors=True)

        await self.hass.async_add_executor_job(_cleanup)
        if removed:
            _LOGGER.debug("Removed %d attachments of ideas done long ago", removed)
            await self.async_save()
            self._notify_listeners()
        return removed

    def done_ideas(
        self, older_than_days: int = 0, user_id: str | None = None
    ) -> list[str]:
        """Return the IDs of ideas done at least this many days ago.

        Done means ticked off or archived. With a user, only the ideas this
        user owns count, as only the owner may delete an idea.
        """
        limit = dt_util.now() - timedelta(days=max(older_than_days, 0))
        found: list[str] = []
        for idea_id, idea in self._ideas.items():
            if idea.get(ATTR_STATUS) not in ("completed", "archived"):
                continue
            if user_id is not None and not self.is_owner(idea, user_id):
                continue
            if older_than_days > 0:
                done_at = dt_util.parse_datetime(
                    str(idea.get(ATTR_COMPLETED_AT) or idea.get(ATTR_UPDATED_AT) or "")
                )
                if done_at is None or dt_util.as_local(done_at) > limit:
                    continue
            found.append(idea_id)
        return found

    async def async_delete_done(
        self,
        older_than_days: int = 0,
        user_id: str | None = None,
        context: Context | None = None,
    ) -> int:
        """Delete ideas done at least this many days ago, in one save.

        0 days deletes everything done. Open subtasks of a deleted idea stay
        as main tasks. Each deleted idea fires the usual event, so a linked
        to-do list drops its item too. Returns how many were deleted.
        """
        idea_ids = set(self.done_ideas(older_than_days, user_id))
        if not idea_ids:
            return 0
        act_context = context or Context()
        removed = [self._ideas.pop(idea_id) for idea_id in idea_ids]
        for item in self._ideas.values():
            if item.get(ATTR_PARENT_ID) in idea_ids:
                item[ATTR_PARENT_ID] = None
        await self.async_save()
        for idea in removed:
            self.hass.bus.async_fire(
                EVENT_IDEA_DELETED,
                {**idea, "entity_id": OVERVIEW_ENTITY_ID},
                context=act_context,
            )
        self._notify_listeners(context=act_context)
        _LOGGER.info("Deleted %d Brainstorm ideas that were done", len(removed))
        # Their attachments go with them
        await self.async_cleanup_attachments()
        return len(removed)

    async def async_delete_done_by_setting(self) -> int:
        """Delete what the setting says has been done long enough."""
        days = int(self.options.get(CONF_DELETE_DONE_DAYS) or 0)
        if days <= 0:
            return 0
        return await self.async_delete_done(days)

    def deleted_idea(self, idea_id: str) -> dict[str, Any] | None:
        """Return an idea deleted since the start, as it would come back."""
        deleted = self._deleted.get(idea_id)
        return deleted["idea"] if deleted else None

    async def async_set_map_positions(
        self,
        positions: dict[str, dict[str, float] | None],
        user_id: str | None,
    ) -> int:
        """Keep where ideas sit on the mind map, returning how many changed.

        A position is relative to the center of the map, so it fits every screen.
        None removes it, letting the map place the idea on its own again. Ideas
        the user may not change keep their position.
        """
        changed = 0
        for idea_id, position in positions.items():
            idea = self._ideas.get(idea_id)
            if idea is None or not self.can_edit(idea, user_id):
                continue
            if position is None:
                if idea.pop(ATTR_MAP_POS, None) is not None:
                    changed += 1
                continue
            value = {"x": round(position["x"], 1), "y": round(position["y"], 1)}
            if idea.get(ATTR_MAP_POS) != value:
                idea[ATTR_MAP_POS] = value
                changed += 1
        if changed:
            # Moving a note on the map is no change of the note itself
            await self.async_save()
            self._notify_listeners()
        return changed

    def drawing(self, category: str) -> list[dict[str, Any]]:
        """Return the strokes drawn on the map of a category."""
        return list(self._drawings.get(self._known_category(category), []))

    def _known_category(self, category: str) -> str:
        """Return the category as it is spelled here, or raise."""
        wanted = category.strip().lower()
        for existing in self._categories:
            if existing.lower() == wanted:
                return existing
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="category_not_found",
            translation_placeholders={"category": category},
        )

    async def async_add_stroke(
        self,
        category: str,
        kind: str,
        points: list[list[float]],
        color: str,
        width: int,
    ) -> dict[str, Any]:
        """Add a stroke, an arrow or an ellipse to the map of a category.

        Points are relative to the center of the map, like the places of the
        notes. An arrow and an ellipse keep only their first two points.
        """
        name = self._known_category(category)
        strokes = self._drawings.setdefault(name, [])
        if len(strokes) >= DRAW_MAX_STROKES:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="drawing_full",
                translation_placeholders={"max": str(DRAW_MAX_STROKES)},
            )
        stroke = _clean_stroke(
            {
                "id": uuid.uuid4().hex[:8],
                "kind": kind,
                "color": color,
                "width": width,
                "points": points,
            }
        )
        if stroke is None:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="drawing_invalid"
            )
        strokes.append(stroke)
        self._drawing_revs[name] = self._drawing_revs.get(name, 0) + 1
        await self.async_save()
        self._notify_listeners()
        return stroke

    async def async_delete_strokes(
        self, category: str, stroke_ids: list[str] | None = None
    ) -> int:
        """Remove strokes of a category, all of them without IDs."""
        name = self._known_category(category)
        strokes = self._drawings.get(name, [])
        keep = (
            []
            if stroke_ids is None
            else [stroke for stroke in strokes if stroke["id"] not in stroke_ids]
        )
        removed = len(strokes) - len(keep)
        if not removed:
            return 0
        if keep:
            self._drawings[name] = keep
        else:
            self._drawings.pop(name, None)
        # The counter stays, so the cards notice the empty map
        self._drawing_revs[name] = self._drawing_revs.get(name, 0) + 1
        await self.async_save()
        self._notify_listeners()
        return removed

    async def async_set_pins(
        self,
        pins: dict[str, dict[str, Any] | None],
        user_id: str | None,
    ) -> int:
        """Keep where notes sit on the pinboard and their colour.

        Returns how many changed. None takes a note off the board, so it goes
        back to the free row. Without a colour the note keeps the one it has,
        an empty colour removes it. Notes the user may not change stay put.
        """
        changed = 0
        for idea_id, pin in pins.items():
            idea = self._ideas.get(idea_id)
            if idea is None or not self.can_edit(idea, user_id):
                continue
            if pin is None:
                if idea.pop(ATTR_PIN, None) is not None:
                    changed += 1
                continue
            old = idea.get(ATTR_PIN) or {}
            value: dict[str, Any] = {
                "x": round(pin["x"], 1),
                "y": round(pin["y"], 1),
            }
            color = pin.get("color", old.get("color"))
            if color in PIN_COLORS:
                value["color"] = color
            if old != value:
                idea[ATTR_PIN] = value
                changed += 1
        if changed:
            # Moving a note on the board is no change of the note itself
            await self.async_save()
            self._notify_listeners()
        return changed

    def find_open_idea(
        self, spoken: str, user_id: str | None = None
    ) -> dict[str, Any] | None:
        """Find the active idea a person most likely means."""
        wanted = spoken.strip().lower()
        if not wanted:
            return None
        best: dict[str, Any] | None = None
        best_score = 0.0
        for idea in self.visible_ideas(user_id):
            if idea.get(ATTR_STATUS) != "active":
                continue
            text = str(idea.get(ATTR_TEXT, "")).lower()
            score = 1.0 if wanted in text else SequenceMatcher(None, wanted, text).ratio()
            if score > best_score:
                best, best_score = idea, score
        return best if best_score >= 0.6 else None

    def next_due_idea(self) -> dict[str, Any] | None:
        """Return the active idea whose reminder comes next."""
        upcoming = [
            idea
            for idea in self.ideas
            if idea.get(ATTR_STATUS) == "active"
            and idea.get(ATTR_DUE)
            and not idea.get(ATTR_REMINDED_AT)
        ]
        return min(upcoming, key=lambda idea: idea[ATTR_DUE], default=None)

    def last_reminded_idea(self, user_id: str | None = None) -> dict[str, Any] | None:
        """Return the active idea that was most recently reminded of."""
        reminded = [
            idea
            for idea in self.visible_ideas(user_id)
            if idea.get(ATTR_STATUS) == "active" and idea.get(ATTR_REMINDED_AT)
        ]
        return max(reminded, key=lambda idea: idea[ATTR_REMINDED_AT], default=None)

    def get_overview_text(
        self, user_id: str | None = None, language: str | None = None
    ) -> str:
        """Generate a short spoken overview instead of reading every idea."""
        pack = self._pack(language)
        parts = []
        total = 0
        for category in self._categories:
            count = len(
                [
                    idea
                    for idea in self.visible_ideas(user_id)
                    if idea.get(ATTR_STATUS) == "active"
                    and idea.get(ATTR_CATEGORY) == category
                ]
            )
            if count:
                total += count
                parts.append(
                    pack.msg(
                        "overview_part",
                        count=count,
                        category=pack.spoken_category(category),
                    )
                )
        if not parts:
            return pack.msg("overview_empty")
        return pack.msg("overview", total=total, parts=", ".join(parts))

    async def async_import_outline(
        self,
        nodes: list[Any],
        category: str | None,
        parent_id: str | None = None,
        context: Context | None = None,
    ) -> list[dict[str, Any]]:
        """Add a tree of notes from an outline in one go, in its order.

        Each node has text, depth, description and done; a node hangs below
        the last node before it with a smaller depth, depth 0 below parent_id.
        """
        if not nodes:
            return []
        parent = self._ideas.get(parent_id) if parent_id else None
        resolved_cat = (
            parent.get(ATTR_CATEGORY)
            if parent
            else (category or "").strip() or self._fallback_category
        )
        if resolved_cat not in self._categories:
            self._categories.append(resolved_cat)
        author = context.user_id if context else None
        ordered_vals = [
            i.get(ATTR_ORDER) for i in self._ideas.values() if i.get(ATTR_ORDER) is not None
        ]
        start = (min(ordered_vals) if ordered_vals else 0) - len(nodes)
        now_iso = dt_util.now().isoformat()
        added: list[dict[str, Any]] = []
        chain: list[dict[str, Any]] = []
        for index, node in enumerate(nodes):
            del chain[node.depth :]
            above = chain[-1] if chain else parent
            idea: dict[str, Any] = {
                ATTR_ID: uuid.uuid4().hex[:8],
                ATTR_TEXT: node.text,
                ATTR_CATEGORY: resolved_cat,
                ATTR_PRIORITY: DEFAULT_PRIORITY,
                ATTR_PARENT_ID: above[ATTR_ID] if above else None,
                ATTR_ORDER: start + index,
                ATTR_SOURCE: "import",
                ATTR_DEVICE: None,
                ATTR_TAGS: [],
                ATTR_STATUS: "completed" if node.done else "active",
                ATTR_CREATED_AT: now_iso,
                ATTR_UPDATED_AT: now_iso,
                ATTR_DUE: None,
                ATTR_ASSIGNEE: None,
                ATTR_TRIGGER: None,
                ATTR_OWNER: self.owner_for_new_idea(author, resolved_cat, above),
                ATTR_SHARES: {},
            }
            if node.done:
                idea[ATTR_COMPLETED_AT] = now_iso
            if node.description:
                idea[ATTR_DESCRIPTION] = node.description
            if author and idea[ATTR_OWNER] != author:
                idea[ATTR_CREATED_BY] = author
            self._ideas[idea[ATTR_ID]] = idea
            chain.append(idea)
            added.append(idea)
        await self.async_save()
        act_context = context or Context()
        for idea in added:
            self.hass.bus.async_fire(
                EVENT_IDEA_ADDED,
                {**idea, "entity_id": OVERVIEW_ENTITY_ID},
                context=act_context,
            )
        self._notify_listeners(context=act_context)
        _LOGGER.info(
            "Brainstorm imported %d notes from an outline into '%s'",
            len(added),
            resolved_cat,
        )
        return added

    def children_of(
        self, parent_id: str | None, category: str | None = None
    ) -> list[dict[str, Any]]:
        """Return the subtasks of a note, or the main notes of a category, in order.

        Archived notes stay where they are.
        """
        result = []
        for idea in self.ideas:
            if idea.get(ATTR_STATUS) == "archived":
                continue
            parent = idea.get(ATTR_PARENT_ID)
            if parent_id:
                if parent == parent_id:
                    result.append(idea)
            elif idea.get(ATTR_CATEGORY) == category and (
                not parent or parent not in self._ideas
            ):
                result.append(idea)
        return result

    async def async_sort_ideas(
        self,
        idea_ids: list[str],
        by: str,
        reverse: bool = False,
        manual: list[str] | None = None,
    ) -> int:
        """Sort notes among the places they already take in the order.

        Notes before, after or between them keep their place. Ties keep
        their order, notes without a due date come last either way. A manual
        order puts the notes it names first, in its order, the others after.
        """
        ids = [i for i in idea_ids if i in self._ideas]
        if len(ids) < 2:
            return len(ids)
        if any(self._ideas[i].get(ATTR_ORDER) is None for i in ids):
            # Give every note a place first, as the cards show them now
            for index, idea in enumerate(self.ideas):
                idea[ATTR_ORDER] = index
        slots = sorted(int(self._ideas[i][ATTR_ORDER]) for i in ids)
        current = sorted(ids, key=lambda i: int(self._ideas[i][ATTR_ORDER]))
        rank = {
            PRIORITY_URGENT: 0,
            PRIORITY_HIGH: 1,
            PRIORITY_MEDIUM: 2,
            PRIORITY_LOW: 3,
        }

        def key(idea_id: str) -> Any:
            idea = self._ideas[idea_id]
            if by == "priority":
                return rank.get(str(idea.get(ATTR_PRIORITY)), 2)
            if by == "created":
                return str(idea.get(ATTR_CREATED_AT) or "")
            if by == "votes":
                # Most points first, so the winners lead
                return -sum((idea.get(ATTR_VOTES) or {}).values())
            return str(idea.get(ATTR_TEXT) or "").casefold()

        if manual is not None:
            place = {idea_id: index for index, idea_id in enumerate(manual)}
            ordered = sorted(current, key=lambda i: place.get(i, len(place)))
        elif by == "due":
            dated = [i for i in current if self._ideas[i].get(ATTR_DUE)]
            undated = [i for i in current if not self._ideas[i].get(ATTR_DUE)]
            dated.sort(key=lambda i: str(self._ideas[i][ATTR_DUE]), reverse=reverse)
            ordered = dated + undated
        else:
            ordered = sorted(current, key=key, reverse=reverse)
        now_iso = dt_util.now().isoformat()
        for slot, idea_id in zip(slots, ordered, strict=True):
            if self._ideas[idea_id].get(ATTR_ORDER) != slot:
                self._ideas[idea_id][ATTR_ORDER] = slot
                self._ideas[idea_id][ATTR_UPDATED_AT] = now_iso
        await self.async_save()
        self._notify_listeners()
        return len(ids)

    def _require_viewer(self, idea_id: str, user_id: str | None) -> dict[str, Any]:
        """Return an idea a person may see, for reacting and voting."""
        idea = self._ideas.get(idea_id)
        if idea is None:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="idea_not_found",
                translation_placeholders={"id": idea_id},
            )
        if not user_id:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="needs_user"
            )
        if not self.can_access(idea, user_id):
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="no_access_idea",
                translation_placeholders={"id": idea_id},
            )
        return idea

    async def async_react(
        self,
        idea_id: str,
        reaction: str,
        user_id: str | None,
        active: bool | None = None,
    ) -> dict[str, list[str]]:
        """Switch a reaction of a person on a note, returning all reactions.

        Seeing a note is enough to react to it. Without active the reaction
        toggles.
        """
        idea = self._require_viewer(idea_id, user_id)
        reactions: dict[str, list[str]] = {
            key: list(users)
            for key, users in (idea.get(ATTR_REACTIONS) or {}).items()
            if key in REACTIONS
        }
        users = reactions.get(reaction, [])
        on = user_id not in users if active is None else active
        if on and user_id not in users:
            users.append(str(user_id))
        elif not on and user_id in users:
            users.remove(user_id)
        if users:
            reactions[reaction] = users
        else:
            reactions.pop(reaction, None)
        if reactions:
            idea[ATTR_REACTIONS] = reactions
        else:
            idea.pop(ATTR_REACTIONS, None)
        await self.async_save()
        self._notify_listeners()
        return reactions

    def votes_used(self, category: str, user_id: str | None) -> int:
        """Return how many votes a person gave in the open notes of a category."""
        if not user_id:
            return 0
        return sum(
            int((idea.get(ATTR_VOTES) or {}).get(user_id, 0))
            for idea in self._ideas.values()
            if idea.get(ATTR_CATEGORY) == category
            and idea.get(ATTR_STATUS) == "active"
        )

    @property
    def voting(self) -> dict[str, dict[str, Any]]:
        """Return the running voting rounds by category."""
        return {category: dict(round_) for category, round_ in self._voting.items()}

    async def async_vote(
        self, idea_id: str, user_id: str | None, delta: int
    ) -> dict[str, Any]:
        """Give a note more or fewer points in the running round of its list.

        Each person has the votes the round grants and may put several on one
        note. Taking points back is always possible.
        """
        idea = self._require_viewer(idea_id, user_id)
        category = str(idea.get(ATTR_CATEGORY))
        round_ = self._voting.get(category)
        if round_ is None:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="no_voting_round",
                translation_placeholders={"category": category},
            )
        if idea.get(ATTR_STATUS) != "active":
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="idea_not_active",
                translation_placeholders={"id": idea_id},
            )
        votes: dict[str, int] = dict(idea.get(ATTR_VOTES) or {})
        mine = int(votes.get(str(user_id), 0))
        allowed = int(round_.get("votes", 1))
        if delta > 0 and self.votes_used(category, user_id) + delta > allowed:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="no_votes_left",
                translation_placeholders={"votes": str(allowed)},
            )
        mine = max(0, mine + delta)
        if mine:
            votes[str(user_id)] = mine
        else:
            votes.pop(str(user_id), None)
        if votes:
            idea[ATTR_VOTES] = votes
        else:
            idea.pop(ATTR_VOTES, None)
        await self.async_save()
        self._notify_listeners()
        return {
            "votes": mine,
            "used": self.votes_used(category, user_id),
            "allowed": allowed,
        }

    async def async_start_voting(
        self,
        category: str,
        votes: int,
        hidden: bool,
        clear: bool,
        user_id: str | None,
    ) -> dict[str, Any]:
        """Start a voting round in a category, optionally without old points."""
        if category not in self._categories:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="category_not_found",
                translation_placeholders={"category": category},
            )
        if clear:
            for idea in self._ideas.values():
                if idea.get(ATTR_CATEGORY) == category:
                    idea.pop(ATTR_VOTES, None)
        round_ = {
            "votes": max(1, min(VOTING_MAX_VOTES, int(votes))),
            "hidden": bool(hidden),
            "since": dt_util.now().isoformat(),
        }
        if user_id:
            round_["by"] = user_id
        self._voting[category] = round_
        await self.async_save()
        self._notify_listeners()
        return dict(round_)

    async def async_end_voting(
        self, category: str, user_id: str | None
    ) -> list[dict[str, Any]]:
        """End the round of a category and return its notes ranked by points."""
        if self._voting.pop(category, None) is None:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="no_voting_round",
                translation_placeholders={"category": category},
            )
        await self.async_save()
        self._notify_listeners()
        ranked = [
            {
                ATTR_ID: idea[ATTR_ID],
                ATTR_TEXT: idea.get(ATTR_TEXT),
                "points": sum((idea.get(ATTR_VOTES) or {}).values()),
                "voters": len(idea.get(ATTR_VOTES) or {}),
            }
            for idea in self._ideas.values()
            if idea.get(ATTR_CATEGORY) == category
            and idea.get(ATTR_STATUS) == "active"
            and idea.get(ATTR_VOTES)
            and self.can_access(idea, user_id)
        ]
        ranked.sort(key=lambda item: -item["points"])
        return ranked

    @property
    def rounds(self) -> dict[str, dict[str, Any]]:
        """Return the running hidden brainstorm rounds by category."""
        return {category: dict(round_) for category, round_ in self._rounds.items()}

    def hidden_in_round(self, idea: dict[str, Any], user_id: str | None) -> bool:
        """Tell whether a note of someone else is still hidden from this user."""
        author = idea.get(ATTR_ROUND_BY)
        return bool(
            author
            and user_id is not None
            and author != user_id
            and idea.get(ATTR_CATEGORY) in self._rounds
        )

    def round_hidden_count(self, category: str, user_id: str | None) -> int:
        """Count the notes of others this user cannot see yet in a round."""
        return sum(
            1
            for idea in self._ideas.values()
            if idea.get(ATTR_CATEGORY) == category
            and idea.get(ATTR_STATUS) == "active"
            and self.hidden_in_round(idea, user_id)
        )

    async def async_start_round(
        self, category: str, minutes: int, user_id: str | None
    ) -> dict[str, Any]:
        """Start a hidden brainstorm round, or return the one already running.

        Until it ends, each person sees only their own new notes of the
        category. With minutes it ends by itself.
        """
        if category not in self._categories:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="category_not_found",
                translation_placeholders={"category": category},
            )
        if (running := self._rounds.get(category)) is not None:
            return dict(running)
        now = dt_util.now()
        round_: dict[str, Any] = {"since": now.isoformat()}
        if user_id:
            round_["by"] = user_id
        minutes = max(0, min(ROUND_MAX_MINUTES, int(minutes)))
        if minutes:
            round_["ends_at"] = (now + timedelta(minutes=minutes)).isoformat()
        self._rounds[category] = round_
        self._schedule_round_end(category)
        await self.async_save()
        self._notify_listeners()
        return dict(round_)

    async def async_end_round(self, category: str) -> int:
        """End the hidden round of a category, show all its notes and count them."""
        if self._rounds.pop(category, None) is None:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="no_hidden_round",
                translation_placeholders={"category": category},
            )
        if cancel := self._round_timers.pop(category, None):
            cancel()
        revealed = 0
        for idea in self._ideas.values():
            if idea.get(ATTR_CATEGORY) == category and idea.pop(ATTR_ROUND_BY, None):
                revealed += 1
        await self.async_save()
        self.hass.bus.async_fire(
            EVENT_ROUND_ENDED, {"category": category, "revealed": revealed}
        )
        self._notify_listeners()
        return revealed

    def _schedule_round_end(self, category: str) -> None:
        """End a round with a time limit when its time is up."""
        if cancel := self._round_timers.pop(category, None):
            cancel()
        ends_at = dt_util.parse_datetime(str(self._rounds[category].get("ends_at") or ""))
        if ends_at is None:
            return

        async def _end(_now: datetime) -> None:
            self._round_timers.pop(category, None)
            if category in self._rounds:
                await self.async_end_round(category)

        self._round_timers[category] = async_track_point_in_utc_time(
            self.hass, _end, dt_util.as_utc(ends_at)
        )

    def get_comments(self, idea_id: str, user_id: str | None) -> list[dict[str, Any]]:
        """Return the comments of a note a person may see, oldest first."""
        idea = self._require_viewer(idea_id, user_id)
        return [dict(comment) for comment in idea.get(ATTR_COMMENTS) or []]

    async def async_add_comment(
        self,
        idea_id: str,
        text: str,
        user_id: str | None,
        mentions: list[str] | None = None,
        context: Context | None = None,
    ) -> dict[str, Any]:
        """Add a comment of a person to a note; seeing the note is enough."""
        idea = self._require_viewer(idea_id, user_id)
        text = (text or "").strip()[:COMMENT_MAX_LENGTH]
        if not text:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="comment_empty"
            )
        comments = list(idea.get(ATTR_COMMENTS) or [])
        if len(comments) >= COMMENTS_MAX:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="too_many_comments",
                translation_placeholders={"count": str(COMMENTS_MAX)},
            )
        comment: dict[str, Any] = {
            ATTR_ID: uuid.uuid4().hex[:8],
            "by": user_id,
            "at": dt_util.now().isoformat(),
            ATTR_TEXT: text,
        }
        if mentions:
            comment["mentions"] = list(mentions)
        comments.append(comment)
        idea[ATTR_COMMENTS] = comments
        await self.async_save()
        self.hass.bus.async_fire(
            EVENT_COMMENT_ADDED,
            {
                "idea_id": idea[ATTR_ID],
                "idea_text": idea.get(ATTR_TEXT),
                ATTR_CATEGORY: idea.get(ATTR_CATEGORY),
                "comment_id": comment[ATTR_ID],
                ATTR_TEXT: text,
                "by": user_id,
                "mentions": list(mentions or []),
                "entity_id": OVERVIEW_ENTITY_ID,
            },
            context=context or Context(user_id=user_id),
        )
        self._notify_listeners()
        return dict(comment)

    async def async_delete_comment(
        self, idea_id: str, comment_id: str, user_id: str | None
    ) -> None:
        """Remove a comment; its author or whoever may change the note may."""
        idea = self._require_viewer(idea_id, user_id)
        comments = list(idea.get(ATTR_COMMENTS) or [])
        comment = next((c for c in comments if c.get(ATTR_ID) == comment_id), None)
        if comment is None:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="comment_not_found",
                translation_placeholders={"id": comment_id},
            )
        if comment.get("by") != user_id and not self.can_edit(idea, user_id):
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="comment_not_yours",
                translation_placeholders={"id": comment_id},
            )
        comments.remove(comment)
        if comments:
            idea[ATTR_COMMENTS] = comments
        else:
            idea.pop(ATTR_COMMENTS, None)
        await self.async_save()
        self._notify_listeners()

    async def async_reorder_ideas(self, idea_ids: list[str]) -> bool:
        """Update order of ideas based on the provided list of IDs."""
        for idx, idea_id in enumerate(idea_ids):
            if idea_id in self._ideas:
                self._ideas[idea_id][ATTR_ORDER] = idx
                self._ideas[idea_id][ATTR_UPDATED_AT] = dt_util.now().isoformat()
        await self.async_save()
        self._notify_listeners()
        return True

    async def async_delete_idea(
        self, idea_id: str, context: Context | None = None
    ) -> bool:
        """Delete an idea by ID."""
        if idea_id not in self._ideas:
            return False

        deleted_idea = self._ideas.pop(idea_id)
        # Unparent any direct subtasks of the deleted idea
        orphans = []
        for item in self._ideas.values():
            if item.get(ATTR_PARENT_ID) == idea_id:
                item[ATTR_PARENT_ID] = None
                orphans.append(item[ATTR_ID])
        self._deleted.pop(idea_id, None)
        self._deleted[idea_id] = {
            "idea": deleted_idea,
            "orphans": orphans,
            "user_id": context.user_id if context else None,
        }
        while len(self._deleted) > MAX_RESTORABLE:
            del self._deleted[next(iter(self._deleted))]

        now_iso = dt_util.now().isoformat()
        act_context = context or Context()
        pack = self._pack()
        self._last_action = {
            "action": "deleted",
            "id": idea_id,
            "text": deleted_idea.get(ATTR_TEXT),
            "category": deleted_idea.get(ATTR_CATEGORY),
            "timestamp": now_iso,
            "description": f"{pack.msg('log_deleted')}: \"{deleted_idea.get(ATTR_TEXT)}\" ({deleted_idea.get(ATTR_CATEGORY)})",
        }

        await self.async_save()
        event_data = {
            **deleted_idea,
            "entity_id": OVERVIEW_ENTITY_ID,
        }
        self.hass.bus.async_fire(EVENT_IDEA_DELETED, event_data, context=act_context)
        self._notify_listeners(context=act_context)
        return True

    def can_restore(self, idea_id: str, user_id: str | None) -> bool:
        """Tell whether this user may bring back a deleted idea."""
        deleted = self._deleted.get(idea_id)
        if deleted is None or idea_id in self._ideas:
            return False
        return user_id is None or deleted["user_id"] in (None, user_id)

    async def async_restore_idea(
        self, idea_id: str, user_id: str | None = None
    ) -> dict[str, Any] | None:
        """Bring back an idea deleted since the start, with its subtasks."""
        if not self.can_restore(idea_id, user_id):
            return None
        deleted = self._deleted.pop(idea_id)
        idea = deleted["idea"]
        if idea.get(ATTR_CATEGORY) not in self._categories:
            idea[ATTR_CATEGORY] = self._categories[0] if self._categories else idea.get(ATTR_CATEGORY)
        parent = idea.get(ATTR_PARENT_ID)
        if parent and parent not in self._ideas:
            idea[ATTR_PARENT_ID] = None
        self._ideas[idea_id] = idea
        # Subtasks that nobody has moved elsewhere in the meantime hang on it again
        for orphan_id in deleted["orphans"]:
            orphan = self._ideas.get(orphan_id)
            if orphan is not None and not orphan.get(ATTR_PARENT_ID):
                orphan[ATTR_PARENT_ID] = idea_id

        pack = self._pack()
        self._last_action = {
            "action": "restored",
            "id": idea_id,
            "text": idea.get(ATTR_TEXT),
            "category": idea.get(ATTR_CATEGORY),
            "timestamp": dt_util.now().isoformat(),
            "description": f"{pack.msg('log_restored')}: \"{idea.get(ATTR_TEXT)}\" ({idea.get(ATTR_CATEGORY)})",
        }
        await self.async_save()
        self._notify_listeners()
        return idea

    async def async_add_category(
        self,
        category_name: str,
        icon: str | None = None,
        color: str | None = None,
    ) -> bool:
        """Add a new category."""
        _validate_category_style(icon, color)
        clean_name = category_name.strip()
        if not clean_name or any(c.lower() == clean_name.lower() for c in self._categories):
            return False
        self._categories.append(clean_name)
        if icon and icon.strip():
            self._category_icons[clean_name] = icon.strip()
        if color and color.strip():
            self._category_colors[clean_name] = color.strip()
        await self.async_save()
        self._notify_listeners()
        return True

    async def async_remove_category(self, category_name: str) -> bool:
        """Remove a category and reassign ideas to Inbox."""
        clean_name = category_name.strip()
        if clean_name not in self._categories or clean_name == "Inbox":
            return False

        self._categories.remove(clean_name)
        self._category_icons.pop(clean_name, None)
        self._category_colors.pop(clean_name, None)
        self._drawings.pop(clean_name, None)
        # Move remaining ideas to Inbox
        for idea in self._ideas.values():
            if idea.get(ATTR_CATEGORY) == clean_name:
                idea[ATTR_CATEGORY] = "Inbox"
                idea[ATTR_UPDATED_AT] = dt_util.now().isoformat()

        await self.async_save()
        self._notify_listeners()
        return True

    async def async_set_category_style(
        self,
        category_name: str,
        icon: str | None = None,
        color: str | None = None,
        reset: bool = False,
    ) -> bool:
        """Set custom icon and/or color for a category."""
        clean_name = category_name.strip()
        if not clean_name:
            return False

        if reset:
            self._category_icons.pop(clean_name, None)
            self._category_colors.pop(clean_name, None)
        else:
            _validate_category_style(icon, color)
            if icon is not None:
                clean_icon = icon.strip()
                if clean_icon:
                    self._category_icons[clean_name] = clean_icon
                else:
                    self._category_icons.pop(clean_name, None)

            if color is not None:
                clean_color = color.strip()
                if clean_color:
                    self._category_colors[clean_name] = clean_color
                else:
                    self._category_colors.pop(clean_name, None)

        await self.async_save()
        self._notify_listeners()
        return True

    async def async_set_categories(self, new_categories: list[str]) -> bool:
        """Set full list of categories and safely migrate any removed categories to Inbox."""
        cleaned: list[str] = []
        for cat in new_categories:
            c = cat.strip()
            if c and c not in cleaned:
                cleaned.append(c)

        if "Inbox" not in cleaned:
            cleaned.insert(0, "Inbox")
        elif cleaned[0] != "Inbox":
            cleaned.remove("Inbox")
            cleaned.insert(0, "Inbox")

        self._categories = cleaned

        # Reassign ideas from deleted categories to Inbox
        for idea in self._ideas.values():
            if idea.get(ATTR_CATEGORY) not in self._categories:
                idea[ATTR_CATEGORY] = "Inbox"
                idea[ATTR_UPDATED_AT] = dt_util.now().isoformat()

        await self.async_save()
        self._notify_listeners()
        return True

    def get_ideas_by_category(
        self,
        category: str | None = None,
        status: str | None = "active",
        priority: str | None = None,
        user_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Filter ideas by category, status and priority."""
        results = []
        for idea in self.visible_ideas(user_id):
            if category and idea.get(ATTR_CATEGORY) != category:
                continue
            if status and idea.get(ATTR_STATUS) != status:
                continue
            if priority and idea.get(ATTR_PRIORITY, DEFAULT_PRIORITY) != priority:
                continue
            results.append(idea)
        return results

    def get_announcement_text(
        self,
        category: str | None = None,
        user_id: str | None = None,
        language: str | None = None,
    ) -> str:
        """Generate a concise, natural spoken text of the active ideas."""
        pack = self._pack(language)
        active_ideas = [
            i for i in self.visible_ideas(user_id) if i.get(ATTR_STATUS) == "active"
        ]

        def _format_items(items: list[str]) -> str:
            return pack.join(
                [it.strip().rstrip(".!,;:") for it in items if it and it.strip()]
            )

        # If a specific category was requested
        if category and str(category).strip() and str(category).strip().lower() not in ["all", "alle", "none"]:
            clean_cat = str(category).strip().lower()
            # Match case-insensitively or with common variations (e.g. haus und garten / garten)
            matched = None
            for c in self._categories:
                c_norm = c.lower().replace("&", pack.and_word).strip()
                if c.lower() == clean_cat or c_norm == clean_cat:
                    matched = c
                    break
                if clean_cat in pack.garden_words and pack.garden_match in c.lower():
                    matched = c
                    break

            target_cat = matched or str(category).strip()
            cat_ideas = [
                i.get(ATTR_TEXT, "")
                for i in active_ideas
                if (i.get(ATTR_CATEGORY) or "").lower() == target_cat.lower()
            ]
            spoken_cat = pack.spoken_category(target_cat)
            if not cat_ideas:
                return pack.msg("category_empty", category=spoken_cat)
            return pack.msg(
                "category_items",
                category=spoken_cat,
                count=pack.count_entries(len(cat_ideas)),
                items=_format_items(cat_ideas),
            )

        # All categories
        if not active_ideas:
            return pack.msg("overview_empty")

        parts = []
        for cat in self._categories:
            cat_ideas = [
                i.get(ATTR_TEXT, "")
                for i in active_ideas
                if i.get(ATTR_CATEGORY) == cat
            ]
            if not cat_ideas:
                continue
            parts.append(
                pack.msg(
                    "category_items",
                    category=pack.spoken_category(cat),
                    count=pack.count_entries(len(cat_ideas)),
                    items=_format_items(cat_ideas),
                )
            )

        return " ".join(parts)

    def _export_roots(self, config_dir: Path) -> list[Path]:
        """Return the folders below the config dir that files may go to (blocking I/O)."""
        roots = [config_dir / EXPORT_DIR_NAME]
        configured = Path(self._markdown_path)
        if not configured.is_absolute():
            configured = config_dir / configured
        configured = configured.resolve()
        if configured.is_relative_to(config_dir):
            parts = configured.relative_to(config_dir).parts
            if (
                parts
                and parts[0] not in EXPORT_BLOCKED_DIRS
                and not parts[0].startswith(".")
            ):
                roots.append(configured)
        return roots

    def _validate_export_dir(self, export_dir: str) -> None:
        """Allow the own export folder and allowlisted external dirs only (blocking I/O).

        Below the config dir, files only go to the Brainstorm folder or the
        configured Markdown folder, so no other integration's files can be
        overwritten.
        """
        config_dir = Path(self.hass.config.config_dir).resolve()
        target = Path(export_dir).resolve()
        if target.is_relative_to(config_dir):
            if any(target.is_relative_to(root) for root in self._export_roots(config_dir)):
                return
        elif self.hass.config.is_allowed_path(str(target)):
            return
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="export_not_allowed",
            translation_placeholders={
                "path": export_dir,
                "folder": str(config_dir / EXPORT_DIR_NAME),
            },
        )

    async def async_export_to_markdown(self, target_dir: str | None = None) -> None:
        """Export all categories and ideas into readable Markdown files."""
        export_dir = target_dir or self._markdown_path

        # Group ideas by category in the event loop; the executor must not iterate
        # over store state that the loop can change at the same time.
        by_cat: dict[str, list[dict[str, Any]]] = {c: [] for c in self._categories}
        for idea in self.ideas:
            cat = idea.get(ATTR_CATEGORY, "Inbox")
            if cat not in by_cat:
                by_cat[cat] = []
            by_cat[cat].append(dict(idea))

        pack = self._pack()

        def _do_export():
            self._validate_export_dir(export_dir)
            os.makedirs(export_dir, exist_ok=True)

            for cat, items in by_cat.items():
                safe_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", cat).lower()
                filepath = os.path.join(export_dir, f"{safe_name}.md")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"# Brainstorming: {cat}\n\n")
                    active = [i for i in items if i.get(ATTR_STATUS) == "active"]
                    completed = [
                        i for i in items if i.get(ATTR_STATUS) in ("completed", "archived")
                    ]

                    f.write(f"{pack.msg('export_active')}\n")
                    if not active:
                        f.write(f"{pack.msg('export_none')}\n\n")
                    else:
                        for item in active:
                            created = item.get(ATTR_CREATED_AT, "")[:16].replace("T", " ")
                            src = item.get(ATTR_SOURCE, "")
                            dev = item.get(ATTR_DEVICE, "")
                            if src and dev:
                                src_str = f" `[{src} ({dev})]`"
                            elif src:
                                src_str = f" `[{src}]`"
                            elif dev:
                                src_str = f" `[{dev}]`"
                            else:
                                src_str = ""
                            prio = item.get(ATTR_PRIORITY, DEFAULT_PRIORITY)
                            if prio == PRIORITY_URGENT:
                                prio_str = f" `[{pack.msg('prio_urgent')}]`"
                            elif prio == PRIORITY_HIGH:
                                prio_str = f" `[{pack.msg('prio_high')}]`"
                            elif prio == PRIORITY_LOW:
                                prio_str = f" `[{pack.msg('prio_low')}]`"
                            else:
                                prio_str = ""
                            f.write(f"- [ ] {item.get(ATTR_TEXT)}{prio_str}{src_str} _({created})_\n")
                            if description := item.get(ATTR_DESCRIPTION):
                                for line in str(description).splitlines():
                                    f.write(f"  > {line}\n")
                            for attachment in item.get(ATTR_ATTACHMENTS) or []:
                                f.write(f"  - 📎 {attachment.get('name')}\n")
                        f.write("\n")

                    if completed:
                        f.write(f"{pack.msg('export_done')}\n")
                        for item in completed:
                            f.write(f"- [x] ~~{item.get(ATTR_TEXT)}~~\n")
                        f.write("\n")

        await self.hass.async_add_executor_job(_do_export)


    def export_json(
        self, user_id: str | None = None, category: str | None = None
    ) -> dict[str, Any]:
        """Return the ideas this user may see, with their categories, as JSON data."""
        ideas = [
            {k: v for k, v in idea.items() if k not in EXPORT_SKIPPED_FIELDS}
            for idea in self.visible_ideas(user_id)
            if category is None
            or (idea.get(ATTR_CATEGORY) or "").lower() == category.strip().lower()
        ]
        if category is None:
            categories = list(self._categories)
        else:
            categories = [
                c for c in self._categories if c.lower() == category.strip().lower()
            ] or [category.strip()]
        return {
            "format": JSON_EXPORT_FORMAT,
            "version": JSON_EXPORT_VERSION,
            "integration_version": self.integration_version,
            "exported_at": dt_util.now().isoformat(),
            "categories": categories,
            "category_icons": {
                c: i for c, i in self._category_icons.items() if c in categories
            },
            "category_colors": {
                c: v for c, v in self._category_colors.items() if c in categories
            },
            "drawings": {
                c: strokes for c, strokes in self._drawings.items() if c in categories
            },
            "ideas": ideas,
        }

    def resolve_json_path(self, path: str, must_exist: bool = False) -> str:
        """Check a JSON file path like an export folder (blocking I/O)."""
        target = Path(path)
        if not target.is_absolute():
            target = Path(self.hass.config.config_dir) / target
        if target.suffix.lower() != ".json":
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="json_path_invalid",
                translation_placeholders={"path": path},
            )
        self._validate_export_dir(str(target.parent))
        if must_exist and not target.is_file():
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="json_file_missing",
                translation_placeholders={"path": path},
            )
        return str(target)

    async def async_write_json(self, path: str, data: dict[str, Any]) -> str:
        """Write JSON export data to a file below the config folder."""
        text = json.dumps(data, ensure_ascii=False, indent=2)

        def _write() -> str:
            target = self.resolve_json_path(path)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "w", encoding="utf-8") as file:
                file.write(text)
            return target

        return await self.hass.async_add_executor_job(_write)

    async def async_read_json(self, path: str) -> Any:
        """Read JSON export data from a file below the config folder."""

        def _read() -> Any:
            target = self.resolve_json_path(path, must_exist=True)
            with open(target, encoding="utf-8") as file:
                return json.load(file)

        try:
            return await self.hass.async_add_executor_job(_read)
        except ValueError as err:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="json_invalid",
                translation_placeholders={"error": str(err)},
            ) from err

    async def async_import_json(
        self,
        data: Any,
        user_id: str | None,
        known_users: set[str],
        keep_owners: bool,
    ) -> dict[str, Any]:
        """Add the ideas of a JSON export that are not here yet.

        Ideas whose ID exists are skipped, so importing the same file twice
        changes nothing. Owners and shares only stay for users of this Home
        Assistant, and owners only when the importing user may keep them.
        """
        if (
            not isinstance(data, dict)
            or data.get("format") != JSON_EXPORT_FORMAT
            or not isinstance(data.get("ideas"), list)
        ):
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="json_not_brainstorm"
            )
        if int(data.get("version") or 0) > JSON_EXPORT_VERSION:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="json_too_new",
                translation_placeholders={"version": str(data.get("version"))},
            )

        added_categories: list[str] = []

        def _ensure_category(name: Any) -> str | None:
            if not isinstance(name, str) or not name.strip():
                return None
            name = name.strip()
            for existing in self._categories:
                if existing.lower() == name.lower():
                    return existing
            self._categories.append(name)
            added_categories.append(name)
            return name

        for name in data.get("categories") or []:
            _ensure_category(name)

        now_iso = dt_util.now().isoformat()
        new_ideas: dict[str, dict[str, Any]] = {}
        skipped = 0
        for item in data["ideas"]:
            text = item.get(ATTR_TEXT) if isinstance(item, dict) else None
            if not isinstance(text, str) or not text.strip():
                skipped += 1
                continue
            raw_id = item.get(ATTR_ID)
            if isinstance(raw_id, str) and IMPORT_ID_PATTERN.fullmatch(raw_id.strip()):
                idea_id = raw_id.strip()
                if idea_id in self._ideas or idea_id in new_ideas:
                    skipped += 1
                    continue
            else:
                # An unusual ID could carry markup into the cards
                idea_id = uuid.uuid4().hex[:8]
                while idea_id in self._ideas or idea_id in new_ideas:
                    idea_id = uuid.uuid4().hex[:8]
            category = _ensure_category(item.get(ATTR_CATEGORY)) or self._fallback_category
            status = item.get(ATTR_STATUS)
            due = dt_util.parse_datetime(str(item.get(ATTR_DUE) or ""))
            owner = item.get(ATTR_OWNER)
            if not (keep_owners and owner in known_users):
                owner = user_id
            raw_shares = item.get(ATTR_SHARES)
            shares = {
                who: level
                for who, level in (
                    raw_shares.items() if isinstance(raw_shares, dict) else []
                )
                if (who == SHARE_ALL or who in known_users)
                and level in (SHARE_VIEW, SHARE_EDIT)
            }
            tags = item.get(ATTR_TAGS)
            order = item.get(ATTR_ORDER)
            idea: dict[str, Any] = {
                ATTR_ID: idea_id,
                ATTR_TEXT: text.strip(),
                ATTR_CATEGORY: category,
                ATTR_PRIORITY: self.parse_priority(
                    "", str(item.get(ATTR_PRIORITY) or DEFAULT_PRIORITY)
                )[1],
                ATTR_PARENT_ID: _clean_import_id(item.get(ATTR_PARENT_ID)),
                ATTR_ORDER: order if isinstance(order, int) else None,
                ATTR_SOURCE: "manual",
                ATTR_DEVICE: None,
                ATTR_TAGS: [t for t in tags if isinstance(t, str)]
                if isinstance(tags, list)
                else [],
                ATTR_STATUS: status if status in IMPORT_STATUSES else "active",
                ATTR_CREATED_AT: str(item.get(ATTR_CREATED_AT) or now_iso),
                ATTR_UPDATED_AT: str(item.get(ATTR_UPDATED_AT) or now_iso),
                ATTR_DUE: due.isoformat() if due else None,
                ATTR_ASSIGNEE: None,
                ATTR_TRIGGER: None,
                ATTR_OWNER: owner,
                ATTR_SHARES: shares,
            }
            # Only the expected kinds of values come in, nothing a card could
            # mistake for markup or styles
            for field in IMPORT_FIELDS:
                value = item.get(field)
                if value is None:
                    continue
                if field in IMPORT_TEXT_FIELDS and not isinstance(value, str):
                    continue
                idea[field] = value
            if ATTR_MAP_POS in idea:
                if position := _clean_map_pos(idea[ATTR_MAP_POS]):
                    idea[ATTR_MAP_POS] = position
                else:
                    idea.pop(ATTR_MAP_POS)
            if ATTR_PIN in idea:
                if pin := _clean_pin(idea[ATTR_PIN]):
                    idea[ATTR_PIN] = pin
                else:
                    idea.pop(ATTR_PIN)
            if idea.get(ATTR_TRIGGER) is not None:
                trigger = idea[ATTR_TRIGGER]
                if not (
                    isinstance(trigger, dict)
                    and isinstance(trigger.get("zone"), str)
                    and isinstance(trigger.get("person"), (str, type(None)))
                ):
                    idea[ATTR_TRIGGER] = None
                else:
                    idea[ATTR_TRIGGER] = {
                        "zone": trigger["zone"],
                        "person": trigger.get("person"),
                    }
            if idea.get(ATTR_SHAPE) not in (None, *NODE_SHAPES):
                idea.pop(ATTR_SHAPE)
            if ATTR_MARKERS in idea:
                if cleaned := _clean_markers(idea[ATTR_MARKERS]):
                    idea[ATTR_MARKERS] = cleaned
                else:
                    idea.pop(ATTR_MARKERS)
            if ATTR_PROGRESS in idea:
                if cleaned_progress := _clean_progress(idea[ATTR_PROGRESS]):
                    idea[ATTR_PROGRESS] = cleaned_progress
                else:
                    idea.pop(ATTR_PROGRESS)
            for field, limit in ((ATTR_FRAME, FRAME_MAX_LENGTH), (ATTR_CALLOUT, CALLOUT_MAX_LENGTH)):
                if field in idea:
                    if cleaned_text := _clean_short_text(idea[field], limit):
                        idea[field] = cleaned_text
                    else:
                        idea.pop(field)
            if ATTR_NUMBERING in idea and idea[ATTR_NUMBERING] not in NUMBERING_STYLES:
                idea.pop(ATTR_NUMBERING)
            if ATTR_REPEAT in idea and idea[ATTR_REPEAT] not in REPEAT_RULES:
                idea.pop(ATTR_REPEAT)
            new_ideas[idea_id] = idea
        known = set(new_ideas) | set(self._ideas)
        for idea_id, idea in new_ideas.items():
            if ATTR_LINKS in idea:
                if cleaned_links := _clean_links(idea[ATTR_LINKS], idea_id, known):
                    idea[ATTR_LINKS] = cleaned_links
                else:
                    idea.pop(ATTR_LINKS)

        for name, value in (data.get("category_icons") or {}).items():
            if name in self._categories and name not in self._category_icons:
                try:
                    _validate_category_style(value, None)
                except ServiceValidationError:
                    continue
                self._category_icons[name] = value
        for name, value in (data.get("category_colors") or {}).items():
            if name in self._categories and name not in self._category_colors:
                try:
                    _validate_category_style(None, value)
                except ServiceValidationError:
                    continue
                self._category_colors[name] = value

        drawn = 0
        raw_drawings = data.get("drawings")
        for name, strokes in (raw_drawings if isinstance(raw_drawings, dict) else {}).items():
            category = next(
                (c for c in self._categories if isinstance(name, str) and c.lower() == name.strip().lower()),
                None,
            )
            if category is None or not isinstance(strokes, list):
                continue
            current = self._drawings.setdefault(category, [])
            known = {stroke["id"] for stroke in current}
            for raw in strokes:
                stroke = _clean_stroke(raw)
                if stroke is None or stroke["id"] in known or len(current) >= DRAW_MAX_STROKES:
                    continue
                current.append(stroke)
                known.add(stroke["id"])
                drawn += 1
            if not current:
                self._drawings.pop(category)
            else:
                self._drawing_revs[category] = self._drawing_revs.get(category, 0) + 1

        self._ideas.update(new_ideas)
        # A parent that came neither with the file nor exists here is dropped
        for idea_id, idea in new_ideas.items():
            parent = idea.get(ATTR_PARENT_ID)
            if parent and (
                parent not in self._ideas
                or self._creates_parent_cycle(idea_id, parent)
            ):
                idea[ATTR_PARENT_ID] = None

        if new_ideas or added_categories or drawn:
            pack = self._pack()
            self._last_action = {
                "action": "imported",
                "count": len(new_ideas),
                "timestamp": now_iso,
                "description": pack.msg("log_imported", count=len(new_ideas)),
            }
            await self.async_save()
            self._notify_listeners()
        return {
            "added": len(new_ideas),
            "skipped": skipped,
            "categories_added": added_categories,
        }


def _clean_map_pos(value: Any) -> dict[str, float] | None:
    """Return an imported mind map position if both coordinates are numbers."""
    if not isinstance(value, dict):
        return None
    x, y = value.get("x"), value.get("y")
    if not all(
        isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)
        for v in (x, y)
    ):
        return None
    return {"x": round(float(x), 1), "y": round(float(y), 1)}


def _clean_points(value: Any) -> list[list[float]] | None:
    """Return the points of a stroke if they are pairs of sane numbers."""
    if not isinstance(value, list) or not 2 <= len(value) <= DRAW_MAX_POINTS:
        return None
    points: list[list[float]] = []
    for point in value:
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            return None
        if not all(
            isinstance(v, (int, float)) and not isinstance(v, bool)
            and math.isfinite(v) and abs(v) <= 1e5
            for v in point
        ):
            return None
        points.append([round(float(point[0]), 1), round(float(point[1]), 1)])
    return points


def _clean_stroke(value: Any) -> dict[str, Any] | None:
    """Return an imported stroke with known kind, colour and width only."""
    if not isinstance(value, dict):
        return None
    stroke_id = _clean_import_id(value.get("id"))
    points = _clean_points(value.get("points"))
    kind = value.get("kind")
    color = value.get("color")
    width = value.get("width")
    if (
        stroke_id is None
        or points is None
        or kind not in DRAW_KINDS
        or color not in DRAW_COLORS
        or not isinstance(width, int)
        or isinstance(width, bool)
        or not 1 <= width <= 16
    ):
        return None
    if kind != "pen":
        points = points[:2]
    return {"id": stroke_id, "kind": kind, "color": color, "width": width, "points": points}


def _clean_pin(value: Any) -> dict[str, Any] | None:
    """Return an imported pinboard place, with its colour if it is a known one."""
    position = _clean_map_pos(value)
    if position is None:
        return None
    if value.get("color") in PIN_COLORS:
        position["color"] = value["color"]
    return position


def _clean_import_id(value: Any) -> str | None:
    """Return an imported reference to an idea if it looks like an ID."""
    if isinstance(value, str) and IMPORT_ID_PATTERN.fullmatch(value.strip()):
        return value.strip()
    return None


def _clean_markers(markers: Any) -> list[str]:
    """Return the known markers of a list once each, in their fixed order."""
    if not isinstance(markers, list):
        return []
    return [marker for marker in MARKERS if marker in markers]


def next_repeat_due(due: datetime | None, rule: str, now: datetime) -> datetime:
    """Return when a repeating idea is due next, always after now.

    Without a due date the idea comes back on the next day of the rule at
    09:00. A monthly or yearly date that does not exist in the next month,
    such as the 31st, falls on its last day.
    """
    if due is None:
        due = now.replace(hour=9, minute=0, second=0, microsecond=0)
    anchor_day = due.day

    def step(current: datetime, times: int) -> datetime:
        if rule == "daily":
            return current + timedelta(days=times)
        if rule == "weekly":
            return current + timedelta(weeks=times)
        if rule == "biweekly":
            return current + timedelta(weeks=2 * times)
        if rule == "weekdays":
            result = current
            for _ in range(times):
                result += timedelta(days=1)
                while result.weekday() >= 5:
                    result += timedelta(days=1)
            return result
        months = times * (12 if rule == "yearly" else 1)
        index = current.year * 12 + current.month - 1 + months
        year, month = divmod(index, 12)
        month += 1
        last = (datetime(year + month // 12, month % 12 + 1, 1) - timedelta(days=1)).day
        return current.replace(year=year, month=month, day=min(anchor_day, last))

    result = step(due, 1)
    # A late tick jumps over the rounds that passed meanwhile
    for _ in range(4000):
        if result > now:
            break
        result = step(result, 1)
    return result


def _clean_progress(progress: Any) -> int | None:
    """Return a progress step above 0, or None for none or nonsense."""
    if isinstance(progress, bool):
        return None
    try:
        value = int(progress)
    except (TypeError, ValueError):
        return None
    return value if value in PROGRESS_STEPS and value > 0 else None


def _subtask_progress(ideas: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    """Return how far the subtasks of each note with subtasks are.

    "done" and "total" count the direct subtasks, archived ones not at all.
    "percent" rolls up like MindManager: a ticked off note counts 100, one
    with subtasks the mean of them, any other its own progress.
    """
    children: dict[str, list[dict[str, Any]]] = {}
    for idea in ideas:
        parent = idea.get(ATTR_PARENT_ID)
        if parent and idea.get(ATTR_STATUS) != "archived":
            children.setdefault(str(parent), []).append(idea)
    percents: dict[str, float] = {}

    def percent(idea: dict[str, Any], seen: frozenset[str]) -> float:
        idea_id = str(idea.get(ATTR_ID))
        if idea_id in percents:
            return percents[idea_id]
        if idea.get(ATTR_STATUS) == "completed":
            value = 100.0
        elif (subtasks := children.get(idea_id)) and idea_id not in seen:
            inner = seen | {idea_id}
            value = sum(percent(child, inner) for child in subtasks) / len(subtasks)
        else:
            value = float(_clean_progress(idea.get(ATTR_PROGRESS)) or 0)
        percents[idea_id] = value
        return value

    result: dict[str, dict[str, int]] = {}
    for idea in ideas:
        idea_id = str(idea.get(ATTR_ID))
        if not (subtasks := children.get(idea_id)):
            continue
        result[idea_id] = {
            "done": sum(1 for child in subtasks if child.get(ATTR_STATUS) == "completed"),
            "total": len(subtasks),
            "percent": round(percent(idea, frozenset())),
        }
    return result


def _clean_short_text(value: Any, limit: int) -> str | None:
    """Return a one-line text cut to its limit, or None when it is empty."""
    if not isinstance(value, str):
        return None
    text = " ".join(value.split())
    return text[:limit] or None


def _clean_links(links: Any, own_id: str, known: set[str]) -> list[dict[str, Any]]:
    """Return the links to other known notes, one per target, at most 20."""
    if not isinstance(links, list):
        return []
    cleaned: list[dict[str, Any]] = []
    targets: set[str] = set()
    for link in links:
        if not isinstance(link, dict):
            continue
        target = link.get("to")
        if not isinstance(target, str) or target == own_id or target in targets:
            continue
        if target not in known:
            continue
        item: dict[str, Any] = {"to": target}
        if label := _clean_short_text(link.get("label"), LINK_LABEL_MAX_LENGTH):
            item["label"] = label
        if link.get("blocks") is True:
            item["blocks"] = True
        cleaned.append(item)
        targets.add(target)
        if len(cleaned) >= LINKS_MAX_COUNT:
            break
    return cleaned


def _blocked_by(ideas: list[dict[str, Any]]) -> dict[str, list[dict[str, str]]]:
    """Return for each note the open notes that block it."""
    ids = {str(i.get(ATTR_ID)) for i in ideas}
    result: dict[str, list[dict[str, str]]] = {}
    for idea in ideas:
        if idea.get(ATTR_STATUS) != "active":
            continue
        for link in idea.get(ATTR_LINKS) or []:
            target = link.get("to")
            if link.get("blocks") and target in ids:
                result.setdefault(target, []).append(
                    {"id": str(idea.get(ATTR_ID)), "text": str(idea.get(ATTR_TEXT) or "")}
                )
    return result
