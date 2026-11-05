"""Data management and storage for Brainstorm Hub."""
from __future__ import annotations

import asyncio
import contextlib
import hashlib
import json
import logging
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
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_CATEGORY,
    ATTR_CREATED_AT,
    ATTR_ALEXA_NATIVE,
    ATTR_ASSIGNEE,
    ATTR_CREATED_BY,
    ATTR_MAP_POS,
    ATTR_OWNER,
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
    ATTR_BATTERY,
    ATTR_ATTACHMENTS,
    ATTR_BATTERY_DONE,
    ATTR_COMPLETED_AT,
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
    async_generate_text,
    async_request_text_with_retry,
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
# Config subfolders exports must not write to; 'www' is served without authentication
EXPORT_BLOCKED_DIRS = {"custom_components", "www"}
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
    ATTR_CREATED_BY,
)
# Fields that belong to this Home Assistant and stay out of a JSON export
EXPORT_SKIPPED_FIELDS = (
    # The files themselves are not part of an export
    ATTR_ATTACHMENTS,
    ATTR_TODO_LINK,
    ATTR_BRING_LIST,
    ATTR_BATTERY,
    ATTR_BATTERY_DONE,
    ATTR_CALENDAR_SYNCED,
    ATTR_ALEXA_NATIVE,
)
IMPORT_STATUSES = ("active", "completed", "archived")


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
        self._default_category = self.options.get("default_category", "Inbox")
        self._last_action: dict[str, Any] | None = None
        self._ai_tasks: set[asyncio.Task[None]] = set()
        self._category_shares: dict[str, dict[str, dict[str, str]]] = {}
        self.integration_version: str | None = None
        self.alexa_skill: AlexaSkill | None = None
        self.reminders: ReminderManager | None = None
        self.todo_sync: TodoSyncManager | None = None

    @property
    def last_action(self) -> dict[str, Any] | None:
        """Return the most recent action performed."""
        return getattr(self, "_last_action", None)

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
        }

    def get_overview_attributes(self, user_id: str | None = None) -> dict[str, Any]:
        """Return the statistics and ideas a user may see."""
        visible = self.visible_ideas(user_id)
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
            if note := idea.get(ATTR_RESULT):
                result[ATTR_RESULT] = note
            if description := idea.get(ATTR_DESCRIPTION):
                result[ATTR_DESCRIPTION] = description
            if attachments := idea.get(ATTR_ATTACHMENTS):
                result[ATTR_ATTACHMENTS] = [dict(a) for a in attachments]
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

    def async_cancel_ai_tasks(self) -> None:
        """Stop AI work that is still running when the integration unloads."""
        for task in self._ai_tasks:
            task.cancel()

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

        # Extract hashtags
        tags = re.findall(r"#([a-zA-Z0-9äöüÄÖÜß_-]+)", clean_text)

        # 1. Prefix: 'Kategorie: Der eigentliche Text' or '[Kategorie] Der eigentliche Text'
        if not category:
            match_prefix = re.match(
                r"^\[?([a-zA-Z0-9äöüÄÖÜß\s\-_&]{2,30})\]?:\s*(.+)$",
                clean_text,
                re.IGNORECASE,
            )
            if match_prefix:
                cand = match_prefix.group(1).strip()
                rem_text = match_prefix.group(2).strip()
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

        # 7. Smart NLP Text Normalization, a typed text only gets its typos fixed
        if self._smart_formatting:
            formatted = (
                pack.clean_text(clean_text, self._glossary(pack))
                if spoken
                else pack.format_typed(clean_text)
            )
            if formatted:
                clean_text = formatted

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
        if text is not None:
            idea[ATTR_TEXT] = text.strip()
        if category is not None:
            cat_clean = category.strip()
            if cat_clean not in self._categories:
                self._categories.append(cat_clean)
            # Its place on the map of the old list means nothing in the new one
            if idea.get(ATTR_CATEGORY) != cat_clean:
                idea.pop(ATTR_MAP_POS, None)
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
        self._notify_listeners(context=act_context)
        return idea

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

    def _validate_export_dir(self, export_dir: str) -> None:
        """Allow config subfolders and allowlisted external dirs only (blocking I/O)."""
        config_dir = Path(self.hass.config.config_dir).resolve()
        target = Path(export_dir).resolve()
        if target.is_relative_to(config_dir):
            parts = target.relative_to(config_dir).parts
            if (
                parts
                and parts[0] not in EXPORT_BLOCKED_DIRS
                and not parts[0].startswith(".")
            ):
                return
        elif self.hass.config.is_allowed_path(str(target)):
            return
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="export_not_allowed",
            translation_placeholders={"path": export_dir},
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
            idea_id = str(item.get(ATTR_ID) or "").strip() or uuid.uuid4().hex[:8]
            if idea_id in self._ideas or idea_id in new_ideas:
                skipped += 1
                continue
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
                ATTR_PARENT_ID: item.get(ATTR_PARENT_ID) or None,
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
            for field in IMPORT_FIELDS:
                if item.get(field) is not None:
                    idea[field] = item[field]
            new_ideas[idea_id] = idea

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

        self._ideas.update(new_ideas)
        # A parent that came neither with the file nor exists here is dropped
        for idea_id, idea in new_ideas.items():
            parent = idea.get(ATTR_PARENT_ID)
            if parent and (
                parent not in self._ideas
                or self._creates_parent_cycle(idea_id, parent)
            ):
                idea[ATTR_PARENT_ID] = None

        if new_ideas or added_categories:
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
