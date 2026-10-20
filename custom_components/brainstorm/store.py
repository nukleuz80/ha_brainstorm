"""Data management and storage for Brainstorm Hub."""
from __future__ import annotations

import logging
import os
import re
import uuid
from typing import Any, Callable

from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_CATEGORY,
    ATTR_CREATED_AT,
    ATTR_ID,
    ATTR_SOURCE,
    ATTR_STATUS,
    ATTR_TAGS,
    ATTR_TEXT,
    ATTR_UPDATED_AT,
    CONF_SMART_FORMATTING,
    DEFAULT_CATEGORIES,
    DEFAULT_MARKDOWN_PATH,
    DOMAIN,
    EVENT_IDEA_ADDED,
    EVENT_IDEA_COMPLETED,
    EVENT_IDEA_DELETED,
    EVENT_IDEA_UPDATED,
    STORAGE_KEY,
    STORAGE_VERSION,
)
from .nlp import clean_and_format_idea_text

_LOGGER = logging.getLogger(__name__)


CATEGORY_ALIASES: dict[str, list[str]] = {
    "Haus & Garten": [
        "haus & garten",
        "haus und garten",
        "garten",
        "haus",
        "gartenarbeit",
        "gartenbereich",
        "balkon",
        "terrasse",
        "terasse",
    ],
    "Smarthome": [
        "smarthome",
        "smart home",
        "hausautomation",
        "homeautomation",
        "home assistant",
        "homeassistant",
    ],
    "Projekte": ["projekte", "projekt", "basteln", "werkstatt", "bauprojekt"],
    "Alltag": ["alltag", "haushalt", "erledigungen", "einkauf", "familie"],
}

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Haus & Garten": [
        "garten",
        "rasen",
        "rasenmähen",
        "rasensprengen",
        "mähen",
        "sprengen",
        "blume",
        "blumen",
        "sonnenblume",
        "sonnenblumen",
        "rose",
        "rosen",
        "pflanze",
        "pflanzen",
        "beet",
        "hochbeet",
        "hecke",
        "heckenschere",
        "unkraut",
        "gießen",
        "wässern",
        "balkon",
        "terrasse",
        "terasse",
        "baum",
        "bäume",
        "ast",
        "äste",
        "schneiden",
        "laub",
        "kompost",
        "dünger",
        "düngen",
        "gewächshaus",
        "pool",
        "poolpumpe",
        "poolroboter",
        "zaun",
        "schuppen",
        "dachrinne",
        "gartenhaus",
        "trampolin",
        "vogelhaus",
        "grill",
        "sandkasten",
        "bewässerung",
        "bewässern",
        "tomate",
        "tomaten",
    ],
    "Smarthome": [
        "smarthome",
        "smart home",
        "home assistant",
        "homeassistant",
        "automation",
        "automatisieren",
        "shelly",
        "zigbee",
        "zha",
        "z2m",
        "zigbee2mqtt",
        "esphome",
        "esp32",
        "esp8266",
        "tasmota",
        "mqtt",
        "bwm",
        "bewegungsmelder",
        "präsenzmelder",
        "präsenz",
        "sensor",
        "sensoren",
        "temperatur",
        "feuchtigkeit",
        "luftfeuchtigkeit",
        "licht",
        "lichter",
        "beleuchtung",
        "lampe",
        "lampen",
        "dimmen",
        "dimmer",
        "steckdose",
        "steckdosen",
        "schalter",
        "relais",
        "frigate",
        "kamera",
        "kameras",
        "dashboard",
        "lovelace",
        "tablet",
        "wlan",
        "wifi",
        "netzwerk",
        "router",
        "fritzbox",
        "blueprint",
        "yaml",
        "alexa",
        "echo",
        "thermostat",
        "heizkörper",
        "heizung",
        "bkw",
        "balkonkraftwerk",
        "wechselrichter",
        "inverter",
        "stromzähler",
        "powercalc",
    ],
    "Projekte": [
        "projekt",
        "projekte",
        "bauen",
        "basteln",
        "umbau",
        "umbauen",
        "renovieren",
        "renovierung",
        "streichen",
        "lackieren",
        "abschleifen",
        "schleifen",
        "bohren",
        "bohrer",
        "sägen",
        "kreissäge",
        "werkstatt",
        "werkzeug",
        "3d-druck",
        "3d druck",
        "drucken",
        "filament",
        "löten",
        "lötkolben",
        "schrauben",
        "dübel",
        "holz",
        "brett",
        "bretter",
        "latte",
        "latten",
        "metall",
        "konstruieren",
        "designen",
        "reparieren",
        "reparatur",
        "werkbank",
    ],
    "Alltag": [
        "alltag",
        "haushalt",
        "einkaufen",
        "einkauf",
        "einkaufsliste",
        "supermarkt",
        "kaufen",
        "besorgen",
        "mitbringen",
        "apotheke",
        "medikament",
        "kinder",
        "kind",
        "flughafen",
        "bahnhof",
        "schule",
        "kita",
        "kindergarten",
        "arzt",
        "zahnarzt",
        "termin",
        "rechnung",
        "bezahlen",
        "überweisen",
        "brief",
        "post",
        "paket",
        "abholen",
        "abgeben",
        "wäsche",
        "waschen",
        "bügeln",
        "trockner",
        "spülmaschine",
        "wischen",
        "saugen",
        "staubsauger",
        "putzen",
        "fenster",
        "müll",
        "biotonne",
        "restmüll",
        "altpapier",
        "gelber sack",
        "müllabfuhr",
        "auto waschen",
        "tüv",
        "tanken",
        "ölwechsel",
        "tierarzt",
        "futter",
        "kochen",
        "rezept",
        "backen",
        "geburtstag",
        "geschenk",
        "brot",
        "milch",
        "mittagessen",
        "abendessen",
    ],
}


class BrainstormStore:
    """Manages brainstorm ideas and categories in persistent storage."""

    def __init__(self, hass: HomeAssistant, options: dict[str, Any] | None = None) -> None:
        """Initialize the store."""
        self.hass = hass
        self.options = options or {}
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._ideas: dict[str, dict[str, Any]] = {}
        self._categories: list[str] = list(DEFAULT_CATEGORIES)
        self._listeners: list[Callable[[], None]] = []
        self._auto_export = self.options.get("auto_export_markdown", False)
        self._markdown_path = self.options.get("markdown_path", DEFAULT_MARKDOWN_PATH)
        self._smart_formatting = self.options.get(CONF_SMART_FORMATTING, True)

    def update_options(self, options: dict[str, Any]) -> None:
        """Update options dynamically."""
        self.options = options
        self._auto_export = options.get("auto_export_markdown", False)
        self._markdown_path = options.get("markdown_path", DEFAULT_MARKDOWN_PATH)
        self._smart_formatting = options.get(CONF_SMART_FORMATTING, True)

    @property
    def categories(self) -> list[str]:
        """Return the list of categories."""
        return list(self._categories)

    @property
    def ideas(self) -> list[dict[str, Any]]:
        """Return all ideas sorted by creation date descending."""
        return sorted(
            self._ideas.values(),
            key=lambda x: x.get(ATTR_CREATED_AT, ""),
            reverse=True,
        )

    def register_listener(self, listener: Callable[[], None]) -> Callable[[], None]:
        """Register a callback for updates."""
        self._listeners.append(listener)

        def remove_listener():
            if listener in self._listeners:
                self._listeners.remove(listener)

        return remove_listener

    def _notify_listeners(self) -> None:
        """Notify all registered listeners of a change."""
        for listener in self._listeners:
            try:
                listener()
            except Exception as err:
                _LOGGER.exception("Error notifying brainstorm listener: %s", err)

    async def async_load(self) -> None:
        """Load ideas and categories from storage."""
        data = await self._store.async_load()
        if data:
            self._ideas = {item[ATTR_ID]: item for item in data.get("ideas", [])}
            loaded_cats = data.get("categories", [])
            for cat in loaded_cats:
                if cat not in self._categories:
                    self._categories.append(cat)
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
            "ideas": list(self._ideas.values()),
        }
        await self._store.async_save(data)
        if self._auto_export:
            await self.async_export_to_markdown()

    def parse_text_and_category(
        self, text: str, explicit_category: str | None = None
    ) -> tuple[str, str, list[str]]:
        """Parse raw text to extract category, clean text and hashtags using multi-tier heuristics."""
        clean_text = text.strip()
        category: str | None = None

        # 0. Check explicit category if provided
        if explicit_category and explicit_category.strip() and explicit_category.lower() != "auto":
            exp = explicit_category.strip()
            # Direct match
            for c in self._categories:
                if c.lower() == exp.lower():
                    category = c
                    break
            # Alias match (e.g. 'Garten' -> 'Haus & Garten')
            if not category:
                for cat_name, aliases in CATEGORY_ALIASES.items():
                    if cat_name in self._categories and exp.lower() in [a.lower() for a in aliases]:
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
                # Direct match with existing categories
                for c in self._categories:
                    if c.lower() == cand.lower():
                        category = c
                        clean_text = rem_text
                        break
                # Alias match (e.g. 'Garten' -> 'Haus & Garten')
                if not category:
                    for cat_name, aliases in CATEGORY_ALIASES.items():
                        if cat_name in self._categories and cand.lower() in [a.lower() for a in aliases]:
                            category = cat_name
                            clean_text = rem_text
                            break

        # 2. Prepositional Indicator phrases:
        # e.g. 'für den Garten ...', 'im Garten ...', 'in der Werkstatt ...', 'fürs Smarthome ...'
        if not category:
            for cat_name, aliases in CATEGORY_ALIASES.items():
                if cat_name not in self._categories:
                    continue
                for alias in sorted(aliases, key=len, reverse=True):
                    pattern = (
                        rf"^(?:(?:für|fürs|im|in\s+der|in\s+dem|auf\s+der|auf\s+dem|am)\s+"
                        rf"(?:den\s+|das\s+|die\s+|dem\s+)?)?{re.escape(alias)}"
                        rf"(?::|\s+dass\s+|\s+ich\s+|\s+wir\s+|\s*,\s*|\s+)(.+)$"
                    )
                    m = re.match(pattern, clean_text, re.IGNORECASE)
                    if m:
                        category = cat_name
                        clean_text = m.group(1).strip()
                        break
                if category:
                    break

        # 3. Hashtags matching
        if not category and tags:
            for tag in tags:
                for c in self._categories:
                    if c.lower() == tag.lower():
                        category = c
                        break
                if not category:
                    for cat_name, aliases in CATEGORY_ALIASES.items():
                        if cat_name in self._categories and tag.lower() in [a.lower() for a in aliases]:
                            category = cat_name
                            break
                if category:
                    break

        # 4. Contextual Keyword Scoring (Semantic matching)
        if not category:
            lower_text = clean_text.lower()
            words = re.findall(r"[a-zA-Z0-9äöüÄÖÜß]+", lower_text)
            scores: dict[str, int] = {c: 0 for c in self._categories}

            for cat_name, kws in CATEGORY_KEYWORDS.items():
                if cat_name in self._categories:
                    for kw in kws:
                        if " " in kw:
                            if kw in lower_text:
                                scores[cat_name] += 3
                        else:
                            if kw in words:
                                scores[cat_name] += 2
                            elif any(w.startswith(kw) or w.endswith(kw) for w in words if len(w) > 4 and len(kw) > 3):
                                scores[cat_name] += 1

            best_cat = max(scores, key=scores.get)
            if scores[best_cat] > 0:
                category = best_cat

        # Fallback to Inbox
        if not category or category not in self._categories:
            category = "Inbox"

        # 5. Smart NLP Text Normalization
        if self._smart_formatting:
            formatted = clean_and_format_idea_text(clean_text)
            if formatted:
                clean_text = formatted

        return clean_text, category, tags

    async def async_add_idea(
        self,
        text: str,
        category: str | None = None,
        source: str = "manual",
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Add a new brainstorm idea."""
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
        }:
            _LOGGER.warning("Ignored empty or invalid idea text: %s", text)
            raise ServiceValidationError(f"Ungültiger oder leerer Notiz-Text: {text}")

        clean_text, resolved_cat, parsed_tags = self.parse_text_and_category(text, category)

        all_tags = list(set((tags or []) + parsed_tags))
        now_iso = dt_util.now().isoformat()
        idea_id = uuid.uuid4().hex[:8]

        # Ensure category is in valid categories (never auto-create rogue categories)
        if resolved_cat not in self._categories:
            resolved_cat = "Inbox"

        idea = {
            ATTR_ID: idea_id,
            ATTR_TEXT: clean_text,
            ATTR_CATEGORY: resolved_cat,
            ATTR_SOURCE: source,
            ATTR_TAGS: all_tags,
            ATTR_STATUS: "active",
            ATTR_CREATED_AT: now_iso,
            ATTR_UPDATED_AT: now_iso,
        }

        self._ideas[idea_id] = idea
        await self.async_save()
        self._notify_listeners()

        # Fire event for automations (e.g. Alexa TTS confirmation or mobile push)
        self.hass.bus.async_fire(EVENT_IDEA_ADDED, idea)
        _LOGGER.info("Brainstorm idea [%s] added in category '%s'", idea_id, resolved_cat)
        return idea
        return idea

    async def async_update_idea(
        self,
        idea_id: str,
        text: str | None = None,
        category: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any] | None:
        """Update an existing idea."""
        if idea_id not in self._ideas:
            _LOGGER.warning("Brainstorm idea %s not found for update", idea_id)
            return None

        idea = self._ideas[idea_id]
        if text is not None:
            idea[ATTR_TEXT] = text.strip()
        if category is not None:
            cat_clean = category.strip()
            if cat_clean not in self._categories:
                self._categories.append(cat_clean)
            idea[ATTR_CATEGORY] = cat_clean
        if status is not None:
            idea[ATTR_STATUS] = status

        idea[ATTR_UPDATED_AT] = dt_util.now().isoformat()
        await self.async_save()
        self._notify_listeners()

        event_name = (
            EVENT_IDEA_COMPLETED
            if status == "completed"
            else EVENT_IDEA_UPDATED
        )
        self.hass.bus.async_fire(event_name, idea)
        return idea

    async def async_delete_idea(self, idea_id: str) -> bool:
        """Delete an idea by ID."""
        if idea_id not in self._ideas:
            return False

        deleted_idea = self._ideas.pop(idea_id)
        await self.async_save()
        self._notify_listeners()
        self.hass.bus.async_fire(EVENT_IDEA_DELETED, deleted_idea)
        return True

    async def async_add_category(self, category_name: str) -> bool:
        """Add a new category."""
        clean_name = category_name.strip()
        if not clean_name or clean_name in self._categories:
            return False
        self._categories.append(clean_name)
        await self.async_save()
        self._notify_listeners()
        return True

    async def async_remove_category(self, category_name: str) -> bool:
        """Remove a category and reassign ideas to Inbox."""
        clean_name = category_name.strip()
        if clean_name not in self._categories or clean_name == "Inbox":
            return False

        self._categories.remove(clean_name)
        # Move remaining ideas to Inbox
        for idea in self._ideas.values():
            if idea.get(ATTR_CATEGORY) == clean_name:
                idea[ATTR_CATEGORY] = "Inbox"
                idea[ATTR_UPDATED_AT] = dt_util.now().isoformat()

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
        self, category: str | None = None, status: str | None = "active"
    ) -> list[dict[str, Any]]:
        """Filter ideas by category and status."""
        results = []
        for idea in self.ideas:
            if category and idea.get(ATTR_CATEGORY) != category:
                continue
            if status and idea.get(ATTR_STATUS) != status:
                continue
            results.append(idea)
        return results

    async def async_export_to_markdown(self, target_dir: str | None = None) -> None:
        """Export all categories and ideas into readable Markdown files."""
        export_dir = target_dir or self._markdown_path

        def _do_export():
            os.makedirs(export_dir, exist_ok=True)
            # Group active ideas by category
            by_cat: dict[str, list[dict[str, Any]]] = {c: [] for c in self._categories}
            for idea in self.ideas:
                cat = idea.get(ATTR_CATEGORY, "Inbox")
                if cat not in by_cat:
                    by_cat[cat] = []
                by_cat[cat].append(idea)

            for cat, items in by_cat.items():
                safe_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", cat).lower()
                filepath = os.path.join(export_dir, f"{safe_name}.md")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"# Brainstorming: {cat}\n\n")
                    active = [i for i in items if i.get(ATTR_STATUS) == "active"]
                    completed = [i for i in items if i.get(ATTR_STATUS) == "completed"]

                    f.write("## Aktive Ideen\n")
                    if not active:
                        f.write("_Keine aktiven Ideen_\n\n")
                    else:
                        for item in active:
                            created = item.get(ATTR_CREATED_AT, "")[:16].replace("T", " ")
                            src = item.get(ATTR_SOURCE, "")
                            src_str = f" `[{src}]`" if src else ""
                            f.write(f"- [ ] {item.get(ATTR_TEXT)}{src_str} _({created})_\n")
                        f.write("\n")

                    if completed:
                        f.write("## Erledigt / Archiviert\n")
                        for item in completed:
                            f.write(f"- [x] ~~{item.get(ATTR_TEXT)}~~\n")
                        f.write("\n")

        await self.hass.async_add_executor_job(_do_export)

