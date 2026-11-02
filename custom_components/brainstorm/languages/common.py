"""What a language has to offer, and the helpers all languages share."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime
from difflib import SequenceMatcher
import re
from typing import Any

# Neutral names of the standard categories, so stored names need no translating
CATEGORY_HOME_GARDEN = "home_garden"
CATEGORY_SMARTHOME = "smarthome"
CATEGORY_PROJECTS = "projects"
CATEGORY_DAILY = "daily"
CATEGORY_BRAINSTORM = "brainstorm"

# The standard categories of a new installation outside of a language with its own
ENGLISH_CATEGORIES: tuple[str, ...] = (
    "Inbox",
    "Smart Home",
    "House & Garden",
    "Projects",
    "Daily Life",
)

NEVER_MATCHES = re.compile(r"(?!)")


@dataclass(frozen=True)
class ReminderWords:
    """Regular expression parts of 'when I get home' and 'when I am at the shop'."""

    me: tuple[str, ...]
    others: tuple[str, ...]
    when: str
    home: str
    place: str
    place_lead: str
    place_end: str


@dataclass(frozen=True)
class LanguagePack:
    """The rules and words of one language."""

    code: str
    # Standard categories
    default_categories: tuple[str, ...]
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
    # What Brainstorm says and writes
    messages: dict[str, str]
    format_due: Callable[[datetime, date], str]
    count_entries: Callable[[int], str]
    reminder_words: ReminderWords
    # Alexa: the voice model and the command words that are not part of a note
    skill_model: dict[str, Any]
    voice_prefixes: tuple[str, ...]
    voice_suffixes: tuple[str, ...]
    # Words for the house and garden list, and the word that shows a category is one
    garden_words: tuple[str, ...]
    garden_match: str
    # None means this language has no AI step
    ai_cleanup_prompt: Callable[[str, str], str] | None = field(default=None)

    def msg(self, key: str, **values: object) -> str:
        """Return a text of this language with its values filled in."""
        return self.messages[key].format(**values)

    def join(self, items: list[str]) -> str:
        """Return items as a spoken list: 'a, b and c'."""
        if len(items) < 2:
            return "".join(items)
        return f"{', '.join(items[:-1])} {self.messages['and']} {items[-1]}"

    def spoken_category(self, category: str) -> str:
        """Return a category name the way it can be read aloud."""
        return category.replace("&", self.and_word)


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


def _has_similar_word(word: str, others: set[str], threshold: float) -> bool:
    """Return whether a word or a close spelling of it is among other words."""
    return word in others or any(
        SequenceMatcher(None, word, other).ratio() >= threshold for other in others
    )


def validate_rewrite(
    spoken: str,
    rule_text: str,
    candidate: str,
    negation: re.Pattern[str],
    allowed_words: frozenset[str],
    letters: str,
) -> str | None:
    """Return the AI's text if it only shortens what was said, otherwise None.

    It may not be longer than the spoken text, add a word or number, change a
    negation, or lose most of what the rules kept.
    """

    def words_of(text: str) -> list[str]:
        """Return the lowercase words of a text."""
        return re.findall(letters, text.lower())

    text = candidate.strip().strip("\"'„“”‚‘’").rstrip(".!").strip()
    if not text or "\n" in text or len(text) > max(len(spoken), len(rule_text)):
        return None

    source = f"{spoken} {rule_text}"
    source_words = set(words_of(source))
    joined = "".join(words_of(spoken))
    for word in words_of(text):
        if (
            len(word) >= 3
            and word not in allowed_words
            and word not in joined
            and not _has_similar_word(word, source_words, 0.7)
        ):
            return None

    if not set(re.findall(r"\d+", text)) <= set(re.findall(r"\d+", source)):
        return None
    if bool(negation.search(spoken)) != bool(negation.search(text)):
        return None

    kept_words = {word for word in words_of(rule_text) if len(word) >= 4}
    answer_words = set(words_of(text))
    found = sum(_has_similar_word(word, answer_words, 0.7) for word in kept_words)
    if kept_words and found / len(kept_words) < 0.6:
        return None
    return text
