"""Tests for the texts of the dashboard cards."""
from __future__ import annotations

import json
from pathlib import Path
import re

WWW = Path(__file__).parents[1] / "www"
MANIFEST = Path(__file__).parents[1] / "custom_components/brainstorm/manifest.json"
USED = re.compile(r"""\bt\(\s*(?:"((?:[^"\\]|\\.)*)"|'((?:[^'\\]|\\.)*)')""")
CHOICE = re.compile(r"""t\(item\.access === "view" \? "([^"]+)" : "([^"]+)\"""")


def _dictionary() -> dict[str, str]:
    """Return the English dictionary of the cards."""
    source = (WWW / "brainstorm-i18n.js").read_text("utf-8")
    block = source[source.index("en: {") + 5 : source.index("  },\n};")]
    return json.loads("{" + block.rstrip().rstrip(",") + "}")


def _used_texts() -> set[str]:
    """Return every text the cards ask for."""
    used: set[str] = set()
    for card in ("brainstorm-card.js", "brainstorm-mindmap-card.js", "brainstorm-i18n.js"):
        source = (WWW / card).read_text("utf-8")
        for double, single in USED.findall(source):
            used.add(double.replace('\\"', '"') if double else single)
        for choice in CHOICE.findall(source):
            used.update(choice)
    return used


def test_every_card_text_has_a_translation() -> None:
    """A missing translation would show German text to everyone else."""
    assert _used_texts() - set(_dictionary()) == set()


def test_no_unused_translations() -> None:
    """Translations of texts that are gone only mislead."""
    assert set(_dictionary()) - _used_texts() == set()


def test_translations_keep_their_values() -> None:
    """A translation shows the same values as the German text."""
    for german, english in _dictionary().items():
        assert sorted(re.findall(r"{(\w+)}", german)) == sorted(
            re.findall(r"{(\w+)}", english)
        ), german


def test_cards_load_the_texts_of_their_own_version() -> None:
    """An old cached file with new cards would break them."""
    version = json.loads(MANIFEST.read_text("utf-8"))["version"]
    for card in ("brainstorm-card.js", "brainstorm-mindmap-card.js"):
        assert f'"./brainstorm-i18n.js?v={version}"' in (WWW / card).read_text("utf-8")


def test_cards_show_idea_texts_only_through_the_safe_formatter() -> None:
    """Texts and result notes are escaped and formatted in one place."""
    for card, name in (
        ("brainstorm-card.js", "item"),
        ("brainstorm-mindmap-card.js", "idea"),
    ):
        source = (WWW / card).read_text("utf-8")
        assert f"formatText({name}.text)" in source
        assert f"formatText({name}.result)" in source
        assert f"_escapeHtml({name}.result)" not in source
        assert f"_escapeHtml({name}.text)" not in source


def test_formatter_only_links_web_and_mail_addresses() -> None:
    """A javascript: or data: link must never become a link."""
    source = (WWW / "brainstorm-i18n.js").read_text("utf-8")
    assert '["http:", "https:", "mailto:"].includes(parsed.protocol)' in source
    assert 'rel="noopener noreferrer"' in source
