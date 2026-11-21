"""Recipes from a web address, read from the schema.org data of the page.

Almost every recipe site (Chefkoch, Lecker, EatSmarter, BBC Good Food, ...)
describes its recipe as JSON-LD for search engines. Brainstorm reads title,
servings, time, ingredients and steps from it, without AI and without an
account. The page is loaded with the same checks as a mind map source, so
addresses inside the own network are refused.
"""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass, field
from typing import Any

from homeassistant.core import HomeAssistant

from .const import DESCRIPTION_MAX_LENGTH
from .map_sources import (
    ERR_SOURCE_UNSUPPORTED,
    SourceError,
    async_fetch,
    decode_page,
    is_html,
)
from .outline import NODE_TEXT_MAX_LENGTH, OutlineNode

ERR_NO_RECIPE = "no_recipe"
# More would not be a shopping list any more
MAX_INGREDIENTS = 60
MAX_STEPS = 60
# Nested @graph and mainEntity blocks are never deeper than this
MAX_DEPTH = 6

_LD_JSON = re.compile(
    r"<script[^>]*type\s*=\s*[\"']?application/ld\+json[\"']?[^>]*>(.*?)</script>",
    re.IGNORECASE | re.DOTALL,
)
_TAG = re.compile(r"<[^>]+>")
_DURATION = re.compile(
    r"^P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:\d+(?:\.\d+)?S)?)?$", re.IGNORECASE
)

# Section names that only repeat the label of the steps
GENERIC_SECTIONS = frozenset(
    {"zubereitung", "anleitung", "steps", "instructions", "directions", "method"}
)

LABELS = {
    "de": {
        "servings": "Portionen",
        "time": "Zeit",
        "steps": "Zubereitung",
        "source": "Quelle",
    },
    "en": {
        "servings": "Servings",
        "time": "Time",
        "steps": "Steps",
        "source": "Source",
    },
}


@dataclass
class Recipe:
    """What a recipe page describes."""

    title: str
    ingredients: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)
    servings: str | None = None
    minutes: int | None = None
    url: str | None = None


def _clean(value: Any, limit: int = NODE_TEXT_MAX_LENGTH) -> str:
    """Return plain text without tags, entities and extra spaces."""
    text = html.unescape(_TAG.sub(" ", html.unescape(str(value or ""))))
    text = " ".join(text.split())
    # Empty optional parts leave ", ," behind on some sites
    text = re.sub(r"\s*,(?:\s*,)+", ",", text).replace(" ,", ",")
    return text[:limit]


def _is_recipe(item: dict[str, Any]) -> bool:
    kind = item.get("@type")
    kinds = kind if isinstance(kind, list) else [kind]
    return any(str(k).rsplit("/", 1)[-1].lower() == "recipe" for k in kinds)


def _find_recipe(data: Any, depth: int = 0) -> dict[str, Any] | None:
    """Return the first Recipe in a JSON-LD block, also inside @graph."""
    if depth > MAX_DEPTH:
        return None
    if isinstance(data, list):
        for item in data:
            if found := _find_recipe(item, depth + 1):
                return found
        return None
    if not isinstance(data, dict):
        return None
    if _is_recipe(data):
        return data
    for key in ("@graph", "mainEntity", "mainEntityOfPage", "itemListElement"):
        if key in data and (found := _find_recipe(data[key], depth + 1)):
            return found
    return None


def _steps(value: Any, depth: int = 0) -> list[str]:
    """Return the steps of recipeInstructions in all the shapes sites use."""
    if depth > MAX_DEPTH or value is None:
        return []
    if isinstance(value, str):
        # One text, sometimes with HTML paragraphs or line breaks
        text = re.sub(r"(?i)<\s*(br|/p|/li)\s*/?>", "\n", html.unescape(value))
        return [line for line in (_clean(part) for part in text.split("\n")) if line]
    if isinstance(value, list):
        steps: list[str] = []
        for item in value:
            steps.extend(_steps(item, depth + 1))
        return steps
    if isinstance(value, dict):
        kind = str(value.get("@type") or "").lower()
        if "section" in kind or "itemListElement" in value:
            name = _clean(value.get("name"))
            inner = _steps(value.get("itemListElement"), depth + 1)
            return ([f"{name}:"] if name and inner else []) + inner
        return _steps(value.get("text") or value.get("name"), depth + 1)
    return []


def _first(value: Any) -> Any:
    if isinstance(value, list):
        return next((item for item in value if item not in (None, "")), None)
    return value


def _minutes(value: Any) -> int | None:
    """Return the minutes of an ISO 8601 duration like PT1H30M."""
    match = _DURATION.match(str(_first(value) or "").strip())
    if not match or not any(match.groups()):
        return None
    days, hours, minutes = (int(part or 0) for part in match.groups())
    total = days * 1440 + hours * 60 + minutes
    return total or None


def _servings(value: Any) -> str | None:
    text = _clean(_first(value), 60)
    return text or None


def recipe_from_html(page: str, url: str | None = None) -> Recipe | None:
    """Return the recipe a page describes, or None without recipe data."""
    for block in _LD_JSON.findall(page):
        try:
            data = json.loads(block.strip(), strict=False)
        except ValueError:
            continue
        item = _find_recipe(data)
        if item is None:
            continue
        title = _clean(item.get("name") or item.get("headline"))
        ingredients = [
            text
            for text in (
                _clean(entry)
                for entry in (
                    item.get("recipeIngredient") or item.get("ingredients") or []
                )
                if isinstance(entry, (str, int, float))
            )
            if text
        ]
        if isinstance(item.get("recipeIngredient"), str):
            ingredients = [_clean(item["recipeIngredient"])]
        if not title or not ingredients:
            continue
        minutes = _minutes(item.get("totalTime"))
        if minutes is None:
            parts = [_minutes(item.get(key)) for key in ("prepTime", "cookTime")]
            minutes = sum(part for part in parts if part) or None
        return Recipe(
            title=title,
            ingredients=list(dict.fromkeys(ingredients))[:MAX_INGREDIENTS],
            steps=_steps(item.get("recipeInstructions"))[:MAX_STEPS],
            servings=_servings(item.get("recipeYield")),
            minutes=minutes,
            url=url,
        )
    return None


def _duration_text(minutes: int) -> str:
    hours, rest = divmod(minutes, 60)
    if not hours:
        return f"{rest} min"
    return f"{hours} h {rest} min" if rest else f"{hours} h"


def recipe_description(recipe: Recipe, language: str | None) -> str:
    """Return the note text below the title: facts, steps and the source."""
    labels = LABELS["de" if (language or "").lower().startswith("de") else "en"]
    facts = []
    if recipe.servings:
        facts.append(f"{labels['servings']}: {recipe.servings}")
    if recipe.minutes:
        facts.append(f"{labels['time']}: {_duration_text(recipe.minutes)}")
    parts = [" · ".join(facts)] if facts else []
    steps = recipe.steps
    if steps and steps[0][:-1].strip().lower() in GENERIC_SECTIONS:
        # A heading like "Zubereitung" says what the label says already
        steps = steps[1:]
    numbered = []
    count = 0
    for step in steps:
        if step.endswith(":"):
            numbered.append(f"\n{step}")
            continue
        count += 1
        numbered.append(f"{count}. {step}")
    if numbered:
        parts.append(f"{labels['steps']}:\n" + "\n".join(numbered).strip("\n"))
    source = f"{labels['source']}: {recipe.url}" if recipe.url else ""
    text = "\n\n".join(parts)
    room = DESCRIPTION_MAX_LENGTH - len(source) - 4
    if len(text) > room:
        text = text[: max(0, room - 1)].rstrip() + "…"
    return "\n\n".join(part for part in (text, source) if part)


def recipe_nodes(recipe: Recipe, language: str | None) -> list[OutlineNode]:
    """Return the recipe as a note with one subtask per ingredient."""
    nodes = [
        OutlineNode(
            text=recipe.title,
            depth=0,
            description=recipe_description(recipe, language),
        )
    ]
    nodes.extend(OutlineNode(text=item, depth=1) for item in recipe.ingredients)
    return nodes


async def async_recipe_from_url(hass: HomeAssistant, address: str) -> Recipe:
    """Load a recipe page and return its recipe."""
    kind, data, content_type = await async_fetch(
        hass, address, accept="text/html,application/xhtml+xml,*/*;q=0.5"
    )
    if not is_html(kind, data):
        raise SourceError(ERR_SOURCE_UNSUPPORTED, f"Cannot read {kind or 'this file'}")
    page = decode_page(data, content_type)
    recipe = await hass.async_add_executor_job(recipe_from_html, page, address.strip())
    if recipe is None:
        raise SourceError(ERR_NO_RECIPE, "The page has no recipe data")
    return recipe
