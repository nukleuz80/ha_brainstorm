"""What a language has to offer, and the helpers all languages share."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
import re

# Neutral names of the standard categories, so stored names need no translating
CATEGORY_HOME_GARDEN = "home_garden"
CATEGORY_SMARTHOME = "smarthome"
CATEGORY_PROJECTS = "projects"
CATEGORY_DAILY = "daily"
CATEGORY_BRAINSTORM = "brainstorm"

NEVER_MATCHES = re.compile(r"(?!)")


@dataclass(frozen=True)
class LanguagePack:
    """The rules and words of one language."""

    code: str
    # Standard categories
    category_names: dict[str, str]
    category_aliases: dict[str, list[str]]
    category_keywords: dict[str, list[str]]
    and_word: str
    category_stop_words: frozenset[str]
    # Regular expression parts around a category name at the start of a text
    alias_lead: str
    alias_tail: str
    topic_pattern: re.Pattern[str]
    # Priority words in front of a text, first match wins
    priority_prefixes: tuple[tuple[re.Pattern[str], str], ...]
    # Rules for text
    clean_text: Callable[[str, dict[str, str] | None], str]
    format_typed: Callable[[str], str]
    extract_due: Callable[[str, datetime], tuple[datetime | None, str]]
    parse_due: Callable[[str, datetime], tuple[datetime | None, str]]
    strip_reminder_words: Callable[[str], str]
    extract_priority: Callable[[str], tuple[str, str | None]]
    starts_with_verb: Callable[[str], bool]
    build_glossary: Callable[[str | None, list[str]], dict[str, str]]
    validate_ai_rewrite: Callable[[str, str, str], str | None]
    # None means this language has no AI step
    ai_cleanup_prompt: Callable[[str, str], str] | None = field(default=None)


def capitalize_first(word: str) -> str:
    """Uppercase the first letter and keep spellings like 'WLAN' or 'iPhone'."""
    if any(c.isupper() for c in word):
        return word
    return word[:1].upper() + word[1:]


def merge_glossary(
    builtin: dict[str, str],
    custom_terms: str | None,
    names: list[str],
    sentence_word: re.Pattern[str] = NEVER_MATCHES,
) -> dict[str, str]:
    """Build the spellings to enforce from names and the person's own list.

    A line of the list is a term ('Lenia') or a correction ('fehler = Richtig').
    The person's own entries win over everything else.
    """
    glossary = dict(builtin)
    for name in names:
        clean_name = name.strip()
        if len(clean_name) < 3 or sentence_word.fullmatch(clean_name):
            continue
        glossary.setdefault(clean_name.lower(), clean_name)
        first_name = clean_name.split()[0]
        if len(first_name) >= 3 and not sentence_word.fullmatch(first_name):
            glossary.setdefault(first_name.lower(), first_name)
    for line in re.split(r"[\n;]", custom_terms or ""):
        wrong, separator, right = line.partition("=")
        if not wrong.strip():
            continue
        glossary[wrong.strip().lower()] = right.strip() if separator else wrong.strip()
    return {wrong: right for wrong, right in glossary.items() if right}


def apply_glossary(text: str, glossary: dict[str, str]) -> str:
    """Put each known term into its proper spelling, longest terms first."""
    if not glossary:
        return text
    pattern = "|".join(
        re.escape(term) for term in sorted(glossary, key=len, reverse=True)
    )
    return re.sub(
        rf"(?<![\w-])(?:{pattern})(?![\w-])",
        lambda match: glossary[match.group(0).lower()],
        text,
        flags=re.IGNORECASE,
    )
