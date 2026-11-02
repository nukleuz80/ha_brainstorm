"""Tests for the language packs."""
from __future__ import annotations

import ast
import copy
from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Any

import pytest
from homeassistant.core import HomeAssistant

from custom_components.brainstorm.const import STORAGE_KEY
from custom_components.brainstorm.languages import PACKS, get_pack
from custom_components.brainstorm.languages.common import LanguagePack
from custom_components.brainstorm.languages.neutral import PACK as NEUTRAL
from custom_components.brainstorm.store import BrainstormStore

NOW = datetime(2026, 3, 10, 10, 0, tzinfo=timezone.utc)
GERMAN_TEXT = re.compile(
    r"[äöüßÄÖÜ]|\b(?:Idee|Ideen|Eintrag|Einträge|Notiz|Kategorie|Erinnerung|Termin|"
    r"Heute|Morgen|nicht|wurde)\b"
)
# Words people may write in any language, like a !dringend tag
ALLOWED_GERMAN = {"später"}
# The settings hold their menu labels next to each other in both languages
SHOWS_BOTH_LANGUAGES = {"config_flow.py"}


@pytest.mark.parametrize(
    ("language", "code"),
    [("de", "de"), ("de-AT", "de"), ("DE_ch", "de"), ("xx", "neutral"), (None, "neutral")],
)
def test_get_pack(language: str | None, code: str) -> None:
    """A regional language finds its pack, an unknown one the neutral rules."""
    assert get_pack(language).code == code


@pytest.mark.parametrize("pack", [*PACKS.values(), NEUTRAL], ids=lambda pack: pack.code)
def test_every_pack_handles_any_text(pack: LanguagePack) -> None:
    """No pack fails on text of any kind, including foreign letters and empty text."""
    for text in ("", "   ", "Ça va très bien?", "買い物 リスト", "!!!", "a"):
        pack.clean_text(text, None)
        pack.format_typed(text)
        pack.extract_due(text, NOW)
        pack.parse_due(text, NOW)
        pack.strip_reminder_words(text)
        pack.extract_priority(text)
        pack.starts_with_verb(text)
        pack.validate_ai_rewrite(text, text, text)


@pytest.mark.parametrize("pack", PACKS.values(), ids=lambda pack: pack.code)
def test_every_pack_describes_the_same_categories(pack: LanguagePack) -> None:
    """Aliases and keywords exist for the standard categories of every pack."""
    assert set(pack.category_aliases) == set(pack.category_names)
    assert set(pack.category_keywords) == set(pack.category_names)
    assert pack.ai_cleanup_prompt is not None


@pytest.mark.parametrize("pack", PACKS.values(), ids=lambda pack: pack.code)
def test_every_pack_has_all_messages(pack: LanguagePack) -> None:
    """A text missing in one language would fail at the moment it is needed."""
    assert set(pack.messages) == set(PACKS["de"].messages)
    for key, text in pack.messages.items():
        assert re.findall(r"{(\w+)}", text) == re.findall(
            r"{(\w+)}", PACKS["de"].messages[key]
        ) or sorted(re.findall(r"{(\w+)}", text)) == sorted(
            re.findall(r"{(\w+)}", PACKS["de"].messages[key])
        ), key


def test_no_german_text_outside_of_the_language_packs() -> None:
    """Anything a person reads comes from a language pack or a translation."""
    root = Path(__file__).parents[1] / "custom_components/brainstorm"
    found = []
    for path in root.glob("*.py"):
        tree = ast.parse(path.read_text("utf-8"))
        docstrings = {
            id(node.body[0].value)
            for node in ast.walk(tree)
            if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef)
            and node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
        }
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Constant)
                and isinstance(node.value, str)
                and id(node) not in docstrings
                and GERMAN_TEXT.search(node.value)
                and node.value not in ALLOWED_GERMAN
                and "a-zA-Z" not in node.value
                and path.name not in SHOWS_BOTH_LANGUAGES
            ):
                found.append((path.name, node.lineno, node.value[:60]))
    assert not found


async def test_unknown_language_leaves_words_alone(hass: HomeAssistant) -> None:
    """Rules of another language are never applied to a foreign text."""
    hass.config.language = "fr"
    store = BrainstormStore(hass, {})
    text, category, _, priority = store.parse_text_and_category(
        "il faut acheter du lait demain"
    )
    assert text == "Il faut acheter du lait demain"
    assert category == "Inbox"
    assert priority == "medium"
    assert get_pack(hass.config.language).extract_due(text, NOW) == (None, text)


async def test_request_language_wins_over_home_assistant(hass: HomeAssistant) -> None:
    """A request in another language uses that language's rules."""
    hass.config.language = "fr"
    store = BrainstormStore(hass, {})
    store._categories = ["Inbox", "Haus & Garten"]  # noqa: SLF001
    text, category, _, _ = store.parse_text_and_category(
        "der rasen muss gemäht werden", language="de"
    )
    assert text == "Rasen mähen"
    assert category == "Haus & Garten"


async def test_tags_work_in_every_language(hass: HomeAssistant) -> None:
    """The written priority tags are not bound to a language."""
    hass.config.language = "fr"
    store: Any = BrainstormStore(hass, {})
    assert store.parse_priority("Regal !dringend")[1] == "urgent"
    assert store.parse_priority("Regal !urgent")[1] == "urgent"


async def test_service_accepts_a_language(hass: HomeAssistant, setup_entry: Any) -> None:
    """An automation can state the language of its text."""
    hass.config.language = "de"
    await setup_entry()
    response = await hass.services.async_call(
        "brainstorm",
        "add_idea",
        {"text": "the lawn has to be mowed", "source": "assist", "language": "en"},
        blocking=True,
        return_response=True,
    )
    assert response["idea"]["text"] == "Mow lawn"


@pytest.mark.parametrize("language", ["de", "en", "fr"])
async def test_stored_data_stays_untouched_in_every_language(
    hass: HomeAssistant, hass_storage: dict[str, Any], language: str
) -> None:
    """Loading and saving in any language changes no category and no entry."""
    hass.config.language = language
    stored = {
        "categories": ["Inbox", "Smarthome", "Haus & Garten", "Projekte", "Alltag", "Axis"],
        "category_icons": {"Axis": "mdi:axis"},
        "category_colors": {"Axis": "#123456"},
        "category_shares": {},
        "ideas": [
            {
                "id": "abc",
                "text": "der rasen muss gemäht werden",
                "category": "Haus & Garten",
                "priority": "high",
                "status": "active",
                "source": "alexa",
                "created_at": "2026-01-01T10:00:00+00:00",
                "updated_at": "2026-01-01T10:00:00+00:00",
                "tags": [],
            }
        ],
    }
    hass_storage[STORAGE_KEY] = {
        "version": 1,
        "minor_version": 1,
        "key": STORAGE_KEY,
        "data": copy.deepcopy(stored),
    }
    store = BrainstormStore(hass, {})
    await store.async_load()
    await store.async_add_category("Neu")
    await store.async_remove_category("Neu")

    assert store.categories == stored["categories"]
    assert store.ideas == stored["ideas"]
    await hass.async_block_till_done()
    saved = hass_storage[STORAGE_KEY]
    assert saved["version"] == 1
    assert saved["data"]["categories"] == stored["categories"]
    assert saved["data"]["ideas"] == stored["ideas"]
