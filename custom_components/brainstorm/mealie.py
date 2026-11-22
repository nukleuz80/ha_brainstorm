"""The meal plan of Mealie as notes, with the ingredients of each recipe.

Brainstorm asks the Mealie integration of Home Assistant for the meal plan of
the coming days. The plan becomes one note, every day's meal a subtask below
it, and the ingredients of its recipe subtasks of that. The ingredients can
then go to a Bring list like those of any other recipe.
"""

from __future__ import annotations

from datetime import date, timedelta
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import Context, HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .languages import get_pack
from .outline import NODE_TEXT_MAX_LENGTH, OutlineNode
from .recipe import MAX_INGREDIENTS, MAX_STEPS, Recipe, recipe_description

if TYPE_CHECKING:
    from .store import BrainstormStore

_LOGGER = logging.getLogger(__name__)

MEALIE_DOMAIN = "mealie"
SERVICE_GET_MEALPLAN = "get_mealplan"
SERVICE_GET_RECIPE = "get_recipe"
DEFAULT_MEALIE_DAYS = 7
MEALIE_DAYS_MAX = 14
# More meals than this in one plan are not read
MAX_MEALS = 40

ERR_MEALIE_MISSING = "mealie_missing"
ERR_MEALIE_EMPTY = "mealie_empty"


class MealieError(Exception):
    """The meal plan could not be read; key names the translated reason."""

    def __init__(self, key: str) -> None:
        """Remember the reason."""
        super().__init__(key)
        self.key = key


def mealie_available(hass: HomeAssistant) -> bool:
    """Tell whether the Mealie integration is installed."""
    return hass.services.has_service(MEALIE_DOMAIN, SERVICE_GET_MEALPLAN)


def _entry_id(hass: HomeAssistant, wanted: str | None) -> str:
    """Return the loaded Mealie entry to ask, the wanted one or the first."""
    loaded = [
        entry.entry_id
        for entry in hass.config_entries.async_entries(MEALIE_DOMAIN)
        if entry.state is ConfigEntryState.LOADED
    ]
    if wanted:
        if wanted in loaded:
            return wanted
        raise MealieError(ERR_MEALIE_MISSING)
    if not loaded or not mealie_available(hass):
        raise MealieError(ERR_MEALIE_MISSING)
    return loaded[0]


def _clean(value: Any, limit: int = NODE_TEXT_MAX_LENGTH) -> str:
    return " ".join(str(value or "").split())[:limit]


def _quantity(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return ""
    if number <= 0:
        return ""
    return f"{number:g}"


def ingredient_text(item: Any) -> str:
    """Return an ingredient of Mealie the way it reads on a shopping list."""
    if isinstance(item, str):
        return _clean(item)
    if not isinstance(item, dict):
        return ""
    for key in ("display", "original_text"):
        if text := _clean(item.get(key)):
            return text
    parts = [
        "" if item.get("disable_amount") else _quantity(item.get("quantity")),
        _clean(item.get("unit")),
        _clean(item.get("food")),
    ]
    text = " ".join(part for part in parts if part)
    note = _clean(item.get("note"))
    if note:
        text = f"{text} ({note})" if text else note
    return text or _clean(item.get("title"))


def _day(value: Any) -> date | None:
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _steps(instructions: Any) -> list[str]:
    steps: list[str] = []
    for step in instructions if isinstance(instructions, list) else []:
        if not isinstance(step, dict):
            continue
        if title := _clean(step.get("title")):
            steps.append(f"{title}:")
        if text := _clean(step.get("text"), 2000):
            steps.append(text)
    return steps[:MAX_STEPS]


def recipe_from_mealie(data: dict[str, Any]) -> Recipe:
    """Turn a recipe of Mealie into a Brainstorm recipe."""
    ingredients = [
        text
        for text in (ingredient_text(item) for item in data.get("ingredients") or [])
        if text
    ][:MAX_INGREDIENTS]
    return Recipe(
        title=_clean(data.get("name")),
        ingredients=ingredients,
        steps=_steps(data.get("instructions")),
        servings=_clean(data.get("recipe_yield"), 40) or None,
        url=_clean(data.get("original_url"), 500) or None,
    )


async def _async_call(
    hass: HomeAssistant, service: str, data: dict[str, Any]
) -> dict[str, Any]:
    response = await hass.services.async_call(
        MEALIE_DOMAIN, service, data, blocking=True, return_response=True
    )
    return response if isinstance(response, dict) else {}


async def async_mealplan_nodes(
    hass: HomeAssistant,
    days: int,
    language: str | None,
    entry_id: str | None = None,
    today: date | None = None,
) -> tuple[list[OutlineNode], int]:
    """Read the meal plan of the coming days as an outline.

    Return the nodes and the number of meals. A recipe that cannot be read
    keeps its name without ingredients.
    """
    entry = _entry_id(hass, entry_id)
    start = today or dt_util.now().date()
    end = start + timedelta(days=max(1, min(days, MEALIE_DAYS_MAX)) - 1)
    try:
        plan = await _async_call(
            hass,
            SERVICE_GET_MEALPLAN,
            {
                "config_entry_id": entry,
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
            },
        )
    except HomeAssistantError as err:
        _LOGGER.warning("Could not read the meal plan of Mealie: %s", err)
        raise MealieError(ERR_MEALIE_MISSING) from err

    meals = [
        meal for meal in plan.get("mealplan") or [] if isinstance(meal, dict)
    ][:MAX_MEALS]
    meals.sort(key=lambda meal: _day(meal.get("mealplan_date")) or end)
    pack = get_pack(language)

    def label(day: date) -> str:
        return pack.msg("mealplan_date", day=day.day, month=day.month)

    nodes = [
        OutlineNode(
            text=pack.msg("mealplan_title", start=label(start), end=label(end)),
            depth=0,
        )
    ]
    count = 0
    for meal in meals:
        recipe_data = meal.get("recipe") if isinstance(meal.get("recipe"), dict) else None
        name = _clean((recipe_data or {}).get("name")) or _clean(meal.get("title"))
        if not name:
            continue
        day = _day(meal.get("mealplan_date"))
        text = f"{label(day)} · {name}" if day else name
        recipe: Recipe | None = None
        recipe_id = (recipe_data or {}).get("recipe_id") or (recipe_data or {}).get("slug")
        if recipe_id:
            try:
                answer = await _async_call(
                    hass,
                    SERVICE_GET_RECIPE,
                    {"config_entry_id": entry, "recipe_id": str(recipe_id)},
                )
            except HomeAssistantError as err:
                _LOGGER.warning("Could not read the Mealie recipe %s: %s", name, err)
            else:
                if isinstance(answer.get("recipe"), dict):
                    recipe = recipe_from_mealie(answer["recipe"])
        description = (
            recipe_description(recipe, language)
            if recipe is not None
            else _clean(meal.get("description"), 2000) or None
        )
        nodes.append(
            OutlineNode(text=text[:NODE_TEXT_MAX_LENGTH], depth=1, description=description)
        )
        if recipe is not None:
            nodes.extend(OutlineNode(text=item, depth=2) for item in recipe.ingredients)
        count += 1
    if not count:
        raise MealieError(ERR_MEALIE_EMPTY)
    return nodes, count


async def async_import_mealplan(
    hass: HomeAssistant,
    store: BrainstormStore,
    days: int,
    category: str | None,
    entry_id: str | None = None,
    context: Context | None = None,
) -> dict[str, Any]:
    """Add the meal plan of Mealie as notes and return what was added."""
    try:
        nodes, meals = await async_mealplan_nodes(
            hass, days, hass.config.language, entry_id
        )
    except MealieError as err:
        raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key=err.key
        ) from err
    language = hass.config.language
    tag = "essensplan" if (language or "").lower().startswith("de") else "mealplan"
    added = await store.async_import_outline(
        nodes, category, None, context, tags=[tag]
    )
    return {"id": added[0]["id"], "title": nodes[0].text, "meals": meals}
