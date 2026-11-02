"""Rules for languages without their own rules: only keep the text tidy."""
from __future__ import annotations

from datetime import datetime
import re

from .common import (
    NEVER_MATCHES,
    LanguagePack,
    apply_glossary,
    capitalize_first,
    merge_glossary,
)


def format_typed_text(raw_text: str) -> str:
    """Start with a capital letter and otherwise keep what was said or written."""
    text = re.sub(r"\s+", " ", raw_text).strip()
    return capitalize_first(text[:1]) + text[1:] if text else ""


def clean_text(raw_text: str, glossary: dict[str, str] | None = None) -> str:
    """Tidy a spoken text without changing any of its words."""
    return apply_glossary(format_typed_text(raw_text), glossary or {})


def _no_due(text: str, now: datetime) -> tuple[datetime | None, str]:
    """Leave the text alone, as dates cannot be recognized."""
    return None, text


def _build_glossary(custom_terms: str | None, names: list[str]) -> dict[str, str]:
    """Build the spellings from names and the person's own list."""
    return merge_glossary({}, custom_terms, names)


PACK = LanguagePack(
    code="neutral",
    category_names={},
    category_aliases={},
    category_keywords={},
    and_word="&",
    category_stop_words=frozenset(),
    alias_lead=r"^",
    alias_tail=r"(:|\s*,\s*|\s+)(.+)$",
    topic_pattern=NEVER_MATCHES,
    priority_prefixes=(),
    clean_text=clean_text,
    format_typed=format_typed_text,
    extract_due=_no_due,
    parse_due=_no_due,
    strip_reminder_words=lambda text: re.sub(r"\s+", " ", text).strip(" ,."),
    extract_priority=lambda text: (text, None),
    starts_with_verb=lambda text: False,
    build_glossary=_build_glossary,
    validate_ai_rewrite=lambda spoken, rule_text, candidate: None,
)
