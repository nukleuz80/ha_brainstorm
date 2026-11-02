"""Keep the German text rules exactly as they are.

The fixture holds the output of the rules for many sentences. To add sentences, list
them in the sentence file and run this test once with BRAINSTORM_GOLDEN_WRITE=1, then
check the difference before committing it.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any

from homeassistant.core import HomeAssistant

from custom_components.brainstorm.languages.de import (
    clean_and_format_idea_text,
    extract_spoken_due,
    extract_spoken_priority,
    format_typed_text,
    parse_due,
    starts_with_verb,
    strip_reminder_words,
)
from custom_components.brainstorm.store import BrainstormStore

FIXTURES = Path(__file__).parent / "fixtures"
SENTENCES = Path(os.environ.get("BRAINSTORM_GOLDEN_SENTENCES", FIXTURES / "golden_de.txt"))
GOLDEN = Path(os.environ.get("BRAINSTORM_GOLDEN_FILE", FIXTURES / "golden_de.json"))
NOW = datetime(2026, 3, 10, 10, 0, tzinfo=timezone.utc)
CATEGORIES = [
    "Inbox",
    "Smarthome",
    "Haus & Garten",
    "Projekte",
    "Alltag",
    "Brainstorm",
    "Familie",
]


def _due(result: tuple[datetime | None, str]) -> list[str | None]:
    """Make a due date result comparable."""
    return [result[0].isoformat() if result[0] else None, result[1]]


def _outputs(store: BrainstormStore, sentence: str) -> dict[str, Any]:
    """Return everything the rules make of one sentence."""
    return {
        "clean": clean_and_format_idea_text(sentence),
        "typed": format_typed_text(sentence),
        "priority": list(extract_spoken_priority(sentence)),
        "spoken_due": _due(extract_spoken_due(sentence, NOW)),
        "parse_due": _due(parse_due(sentence, NOW)),
        "strip": strip_reminder_words(sentence),
        "verb": starts_with_verb(sentence),
        "spoken": list(store.parse_text_and_category(sentence)),
        "typed_entry": list(store.parse_text_and_category(sentence, spoken=False)),
    }


async def test_german_rules_stay_the_same(hass: HomeAssistant) -> None:
    """Every sentence gives exactly the stored result."""
    hass.config.language = "de"
    store = BrainstormStore(hass, {})
    store._categories = list(CATEGORIES)  # noqa: SLF001
    sentences = [
        line for line in SENTENCES.read_text("utf-8").splitlines() if line.strip()
    ]
    actual = {sentence: _outputs(store, sentence) for sentence in sentences}

    if os.environ.get("BRAINSTORM_GOLDEN_WRITE"):
        GOLDEN.write_text(
            json.dumps(actual, ensure_ascii=False, indent=0, sort_keys=True) + "\n",
            "utf-8",
        )

    expected = json.loads(GOLDEN.read_text("utf-8"))
    different = {
        sentence: {"expected": expected.get(sentence), "actual": outputs}
        for sentence, outputs in actual.items()
        if expected.get(sentence) != outputs
    }
    assert not different, json.dumps(different, ensure_ascii=False, indent=1)
    assert len(sentences) >= 500 or "BRAINSTORM_GOLDEN_SENTENCES" in os.environ
