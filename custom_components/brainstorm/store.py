"""Data management and storage for Brainstorm Hub."""
from __future__ import annotations

import logging
import os
import re
import uuid
from pathlib import Path
from typing import Any, Callable

from homeassistant.core import Context, HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_CATEGORY,
    ATTR_CREATED_AT,
    ATTR_DEVICE,
    ATTR_ID,
    ATTR_ORDER,
    ATTR_PARENT_ID,
    ATTR_PRIORITY,
    ATTR_SOURCE,
    ATTR_STATUS,
    ATTR_TAGS,
    ATTR_TEXT,
    ATTR_UPDATED_AT,
    CONF_ALLOWED_ECHOS,
    CONF_HIDE_EMPTY_CATEGORIES,
    CONF_SMART_FORMATTING,
    DEFAULT_CATEGORIES,
    DEFAULT_HIDE_EMPTY_CATEGORIES,
    DEFAULT_MARKDOWN_PATH,
    DEFAULT_PRIORITY,
    EVENT_IDEA_ADDED,
    EVENT_IDEA_COMPLETED,
    EVENT_IDEA_DELETED,
    EVENT_IDEA_UPDATED,
    OVERVIEW_ENTITY_ID,
    PRIORITY_HIGH,
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    PRIORITY_URGENT,
    STORAGE_KEY,
    STORAGE_VERSION,
)
from .nlp import clean_and_format_idea_text

_LOGGER = logging.getLogger(__name__)

COLOR_PATTERN = re.compile(r"^#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
ICON_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+:[a-zA-Z0-9_-]+$")
# Config subfolders exports must not write to; 'www' is served without authentication
EXPORT_BLOCKED_DIRS = {"custom_components", "www"}


def _validate_category_style(icon: str | None, color: str | None) -> None:
    """Raise if a category icon or color is malformed."""
    if icon and icon.strip() and not ICON_PATTERN.match(icon.strip()):
        raise ServiceValidationError(f"Ungültiges Icon: {icon}")
    if color and color.strip() and not COLOR_PATTERN.match(color.strip()):
        raise ServiceValidationError(f"Ungültige Farbe (Hex erwartet): {color}")


CATEGORY_ALIASES: dict[str, list[str]] = {
    "Haus & Garten": [
        "haus & garten",
        "haus und garten",
        "haus & gartenbereich",
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
        "iot",
    ],
    "Projekte": [
        "projekte",
        "projekt",
        "bauprojekte",
        "bauprojekt",
        "bastelprojekte",
        "bastelprojekt",
        "basteln",
        "werkstatt",
        "diy",
    ],
    "Alltag": [
        "alltag",
        "haushalt",
        "erledigungen",
        "erledigung",
        "einkauf",
        "einkäufe",
        "familie",
        "privat",
        "persönlich",
    ],
    "Brainstorm": [
        "brainstorm",
        "brainstorming",
        "brain storm",
        "brain-storm",
        "brainstorm hub",
        "brainstorm app",
        "mindmap",
        "mind map",
    ],
}

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Brainstorm": [
        "brainstorm",
        "brainstorming",
        "mindmap",
        "synapse",
        "synapsen",
        "gedanken",
        "geistesblitz",
        "ideenkarte",
        "ideensammlung",
        "kartendarstellung",
        "visualisierung",
        "radial",
        "app",
        "notiz-app",
        "logbuch",
        "funktion",
        "karten",
    ],
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
        "erweitern",
        "feature",
        "entwicklung",
        "entwickeln",
        "programmieren",
        "implementieren",
        "konzept",
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
        self._category_icons: dict[str, str] = {}
        self._category_colors: dict[str, str] = {}
        self._listeners: list[Callable[[], None]] = []
        self._auto_export = self.options.get("auto_export_markdown", False)
        self._markdown_path = self.options.get("markdown_path", DEFAULT_MARKDOWN_PATH)
        self._smart_formatting = self.options.get(CONF_SMART_FORMATTING, True)
        self._hide_empty_categories = self.options.get(
            CONF_HIDE_EMPTY_CATEGORIES, DEFAULT_HIDE_EMPTY_CATEGORIES
        )
        self._allowed_echos = list(self.options.get(CONF_ALLOWED_ECHOS) or [])
        self._default_category = self.options.get("default_category", "Inbox")
        self._last_action: dict[str, Any] | None = None
        self.integration_version: str | None = None

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
            "ideas": list(self._ideas.values()),
        }
        await self._store.async_save(data)
        if self._auto_export:
            # The data is already persisted, so a failed export must not fail the action
            try:
                await self.async_export_to_markdown()
            except (OSError, HomeAssistantError) as err:
                _LOGGER.error("Brainstorm auto-export to Markdown failed: %s", err)

    def parse_priority(
        self, text: str, explicit_priority: str | None = None
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

        # Urgent prefixes
        m_urg = re.match(
            r"^(?:dringend|sofort|eilig|asap|notfall|höchste\s+priorität|prio\s+dringend|prio\s+sofort)(?::|\s+|,)\s*(.+)$",
            clean,
            re.IGNORECASE,
        )
        if m_urg:
            return m_urg.group(1).strip(), PRIORITY_URGENT

        # High prefixes
        m_high = re.match(
            r"^(?:wichtig|hohe\s+priorität|priorität\s+hoch|prio\s+1|prio\s+hoch)(?::|\s+|,)\s*(.+)$",
            clean,
            re.IGNORECASE,
        )
        if m_high:
            return m_high.group(1).strip(), PRIORITY_HIGH

        # Low prefixes
        m_low = re.match(
            r"^(?:niedrige\s+priorität|priorität\s+niedrig|prio\s+3|prio\s+niedrig|wenn\s+zeit(?:\s+ist)?|später\s+mal|irgendwann|optional)(?::|\s+|,)\s*(.+)$",
            clean,
            re.IGNORECASE,
        )
        if m_low:
            return m_low.group(1).strip(), PRIORITY_LOW

        # Medium prefixes
        m_med = re.match(
            r"^(?:normale\s+priorität|mittlere\s+priorität|priorität\s+normal|priorität\s+mittel|prio\s+2|prio\s+mittel)(?::|\s+|,)\s*(.+)$",
            clean,
            re.IGNORECASE,
        )
        if m_med:
            return m_med.group(1).strip(), PRIORITY_MEDIUM

        return clean, PRIORITY_MEDIUM

    def parse_text_and_category(
        self,
        text: str,
        explicit_category: str | None = None,
        explicit_priority: str | None = None,
    ) -> tuple[str, str, list[str], str]:
        """Parse raw text to extract category, clean text, hashtags and priority."""
        clean_text, resolved_prio = self.parse_priority(text, explicit_priority)
        category: str | None = None

        # Build dynamic alias and keyword lookup for all registered categories
        active_aliases: dict[str, list[str]] = {}
        active_keywords: dict[str, list[str]] = {}

        for cat in self._categories:
            if cat.lower() == "inbox":
                continue
            aliases = list(CATEGORY_ALIASES.get(cat, []))
            cat_clean = cat.strip().lower()
            if cat_clean not in aliases:
                aliases.append(cat_clean)
            if "&" in cat_clean:
                aliases.append(cat_clean.replace("&", "und").strip())
            active_aliases[cat] = aliases

            kws = list(CATEGORY_KEYWORDS.get(cat, []))
            for word in re.findall(r"[a-zA-Z0-9äöüÄÖÜß]{3,}", cat_clean):
                if word not in kws and word not in ("und", "der", "die", "das"):
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
            match_compound = re.match(
                r"^(?:im\s+|in\s+|für\s+|beim\s+)?(?:projekt|thema|bereich)\s+([a-zA-Z0-9äöüÄÖÜß\-_&]{2,30})(?::|\s+dass\s+|\s+ich\s+|\s+wir\s+|\s*,\s*|\s+)(.+)$",
                clean_text,
                re.IGNORECASE,
            )
            if match_compound:
                target_cand = match_compound.group(1).strip()
                rem_content = match_compound.group(2).strip()
                # Check if target_cand matches an active category (e.g. Brainstorm)
                for cat_name, aliases in active_aliases.items():
                    if target_cand.lower() in [a.lower() for a in aliases]:
                        category = cat_name
                        clean_text = f"{target_cand.capitalize()} {rem_content}"
                        break
                if not category and "Projekte" in self._categories:
                    category = "Projekte"
                    clean_text = f"{target_cand} {rem_content}"

        # 3. Prepositional / Leading Indicator phrases:
        # e.g. 'für den Garten ...', 'im Garten ...', 'fürs Smarthome ...', 'für Brainstorm ...'
        if not category:
            for cat_name, aliases in active_aliases.items():
                for alias in sorted(aliases, key=len, reverse=True):
                    pattern = (
                        rf"^(?:(?:für|fürs|im|in\s+der|in\s+dem|auf\s+der|auf\s+dem|am|beim|zum|zur)\s+"
                        rf"(?:den\s+|das\s+|die\s+|dem\s+)?)?{re.escape(alias)}"
                        rf"(:|\s+dass\s+|\s+ich\s+|\s+wir\s+|\s*,\s*|\s+)(.+)$"
                    )
                    m = re.match(pattern, clean_text, re.IGNORECASE)
                    if m:
                        category = cat_name
                        remainder = m.group(2).strip()
                        # After a plain space, a single remaining word usually needs
                        # the alias to make sense ('Haus streichen'), so keep the text.
                        if m.group(1).strip() or len(remainder.split()) > 1:
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
            clean_text, detected_prio = self.parse_priority(clean_text)
            if detected_prio != PRIORITY_MEDIUM:
                resolved_prio = detected_prio

        # 7. Smart NLP Text Normalization
        if self._smart_formatting:
            formatted = clean_and_format_idea_text(clean_text)
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

        clean_text, resolved_cat, parsed_tags, resolved_prio = self.parse_text_and_category(
            text, category, priority
        )

        all_tags = list(set((tags or []) + parsed_tags))
        now_iso = dt_util.now().isoformat()
        idea_id = uuid.uuid4().hex[:8]

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
        }

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
            "description": f"Idee erfasst: \"{clean_text}\" ({resolved_cat})",
        }

        self._ideas[idea_id] = idea
        await self.async_save()

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
    ) -> dict[str, Any] | None:
        """Update an existing idea."""
        if idea_id not in self._ideas:
            _LOGGER.warning("Brainstorm idea %s not found for update", idea_id)
            return None

        if update_parent and parent_id and self._creates_parent_cycle(
            idea_id, parent_id.strip()
        ):
            raise ServiceValidationError(
                f"Idee '{parent_id}' kann nicht übergeordnet werden (Zyklus)."
            )

        idea = self._ideas[idea_id]
        newly_completed = status == "completed" and idea.get(ATTR_STATUS) != "completed"
        if text is not None:
            idea[ATTR_TEXT] = text.strip()
        if category is not None:
            cat_clean = category.strip()
            if cat_clean not in self._categories:
                self._categories.append(cat_clean)
            idea[ATTR_CATEGORY] = cat_clean
        if priority is not None:
            _, normalized_prio = self.parse_priority("", priority)
            idea[ATTR_PRIORITY] = normalized_prio
        if status is not None:
            idea[ATTR_STATUS] = status
        if device is not None:
            idea[ATTR_DEVICE] = device.strip() if device else None
        if order is not None:
            idea[ATTR_ORDER] = int(order)
        if update_parent:
            if not parent_id or parent_id.strip() in ("", "none"):
                idea[ATTR_PARENT_ID] = None
            else:
                clean_pid = parent_id.strip()
                if clean_pid in self._ideas:
                    idea[ATTR_PARENT_ID] = clean_pid

        now_iso = dt_util.now().isoformat()
        idea[ATTR_UPDATED_AT] = now_iso

        act_context = context or Context()
        action_type = "completed" if newly_completed else "updated"
        action_desc = (
            f"Idee erledigt: \"{idea.get(ATTR_TEXT)}\" ({idea.get(ATTR_CATEGORY)})"
            if newly_completed
            else f"Idee geändert: \"{idea.get(ATTR_TEXT)}\" ({idea.get(ATTR_CATEGORY)})"
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
        for item in self._ideas.values():
            if item.get(ATTR_PARENT_ID) == idea_id:
                item[ATTR_PARENT_ID] = None

        now_iso = dt_util.now().isoformat()
        act_context = context or Context()
        self._last_action = {
            "action": "deleted",
            "id": idea_id,
            "text": deleted_idea.get(ATTR_TEXT),
            "category": deleted_idea.get(ATTR_CATEGORY),
            "timestamp": now_iso,
            "description": f"Idee gelöscht: \"{deleted_idea.get(ATTR_TEXT)}\" ({deleted_idea.get(ATTR_CATEGORY)})",
        }

        await self.async_save()
        event_data = {
            **deleted_idea,
            "entity_id": OVERVIEW_ENTITY_ID,
        }
        self.hass.bus.async_fire(EVENT_IDEA_DELETED, event_data, context=act_context)
        self._notify_listeners(context=act_context)
        return True

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
    ) -> list[dict[str, Any]]:
        """Filter ideas by category, status and priority."""
        results = []
        for idea in self.ideas:
            if category and idea.get(ATTR_CATEGORY) != category:
                continue
            if status and idea.get(ATTR_STATUS) != status:
                continue
            if priority and idea.get(ATTR_PRIORITY, DEFAULT_PRIORITY) != priority:
                continue
            results.append(idea)
        return results

    def get_announcement_text(self, category: str | None = None) -> str:
        """Generate a concise, natural German TTS speech text of active ideas."""
        active_ideas = [i for i in self.ideas if i.get(ATTR_STATUS) == "active"]

        def _format_count(n: int) -> str:
            words = {
                1: "einen",
                2: "zwei",
                3: "drei",
                4: "vier",
                5: "fünf",
                6: "sechs",
                7: "sieben",
                8: "acht",
                9: "neun",
                10: "zehn",
            }
            if n == 1:
                return "einen Eintrag"
            return f"{words.get(n, str(n))} Einträge"

        def _format_items(items: list[str]) -> str:
            clean = [it.strip().rstrip(".!,;:") for it in items if it and it.strip()]
            if not clean:
                return ""
            if len(clean) == 1:
                return clean[0]
            if len(clean) == 2:
                return f"{clean[0]} und {clean[1]}"
            return f"{', '.join(clean[:-1])} und {clean[-1]}"

        # If a specific category was requested
        if category and str(category).strip() and str(category).strip().lower() not in ["all", "alle", "none"]:
            clean_cat = str(category).strip().lower()
            # Match case-insensitively or with common variations (e.g. haus und garten / garten)
            matched = None
            for c in self._categories:
                c_norm = c.lower().replace("&", "und").strip()
                if c.lower() == clean_cat or c_norm == clean_cat:
                    matched = c
                    break
                if clean_cat in ["garten", "haus"] and "garten" in c.lower():
                    matched = c
                    break

            target_cat = matched or str(category).strip()
            cat_ideas = [
                i.get(ATTR_TEXT, "")
                for i in active_ideas
                if (i.get(ATTR_CATEGORY) or "").lower() == target_cat.lower()
            ]
            spoken_cat = target_cat.replace("&", "und")
            if not cat_ideas:
                return f"In der Kategorie {spoken_cat} gibt es aktuell keine offenen Einträge."
            return f"{spoken_cat} hat {_format_count(len(cat_ideas))}: {_format_items(cat_ideas)}."

        # All categories
        if not active_ideas:
            return "Du hast aktuell keine offenen Notizen in Brainstorm."

        parts = []
        for cat in self._categories:
            cat_ideas = [
                i.get(ATTR_TEXT, "")
                for i in active_ideas
                if i.get(ATTR_CATEGORY) == cat
            ]
            if not cat_ideas:
                continue
            spoken_cat = cat.replace("&", "und")
            parts.append(
                f"{spoken_cat} hat {_format_count(len(cat_ideas))}: {_format_items(cat_ideas)}."
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
            f"Export nach '{export_dir}' ist nicht erlaubt. Erlaubt sind Unterordner "
            "des Config-Verzeichnisses und allowlist_external_dirs."
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

                    f.write("## Aktive Ideen\n")
                    if not active:
                        f.write("_Keine aktiven Ideen_\n\n")
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
                                prio_str = " `[🔥 Dringend]`"
                            elif prio == PRIORITY_HIGH:
                                prio_str = " `[🔴 Hoch]`"
                            elif prio == PRIORITY_LOW:
                                prio_str = " `[🟢 Niedrig]`"
                            else:
                                prio_str = ""
                            f.write(f"- [ ] {item.get(ATTR_TEXT)}{prio_str}{src_str} _({created})_\n")
                        f.write("\n")

                    if completed:
                        f.write("## Erledigt / Archiviert\n")
                        for item in completed:
                            f.write(f"- [x] ~~{item.get(ATTR_TEXT)}~~\n")
                        f.write("\n")

        await self.hass.async_add_executor_job(_do_export)

