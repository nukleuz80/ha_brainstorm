"""Tests for taking over the meal plan of Mealie."""

from __future__ import annotations

from datetime import date
from typing import Any

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.brainstorm.mealie import (
    MealieError,
    async_mealplan_nodes,
    ingredient_text,
    mealie_available,
    recipe_from_mealie,
)

from .conftest import SetupEntry

LASAGNE = {
    "recipe_id": "r1",
    "name": "Lasagne",
    "slug": "lasagne",
    "recipe_yield": "4 Portionen",
    "original_url": "https://example.com/lasagne",
    "ingredients": [
        {"display": "500 g Hackfleisch"},
        {"quantity": 2.0, "unit": "Dosen", "food": "Tomaten", "note": "gehackt"},
        {"quantity": 0, "food": "Salz", "disable_amount": True},
        {"original_text": "1 Packung Lasagneplatten"},
        {"note": "etwas Käse"},
        {},
    ],
    "instructions": [
        {"title": "Soße", "text": "Hackfleisch anbraten."},
        {"text": "Schichten und backen."},
    ],
}


@pytest.fixture(autouse=True)
def _forget_mealie(hass: HomeAssistant) -> Any:
    """Mealie is only pretended, so it must not be unloaded at the end."""
    yield
    for entry in hass.config_entries.async_entries("mealie"):
        entry.mock_state(hass, ConfigEntryState.NOT_LOADED)


def _mealie(
    hass: HomeAssistant,
    meals: list[dict[str, Any]],
    recipes: dict[str, dict[str, Any]] | None = None,
    calls: list[dict[str, Any]] | None = None,
) -> MockConfigEntry:
    """Pretend Mealie is set up, with a meal plan and its recipes."""
    entry = MockConfigEntry(domain="mealie", state=ConfigEntryState.LOADED)
    entry.add_to_hass(hass)

    async def get_mealplan(call: ServiceCall) -> dict[str, Any]:
        if calls is not None:
            calls.append(dict(call.data))
        return {"mealplan": meals}

    async def get_recipe(call: ServiceCall) -> dict[str, Any]:
        recipe = (recipes or {}).get(call.data["recipe_id"])
        if recipe is None:
            raise HomeAssistantError("Recipe not found")
        return {"recipe": recipe}

    hass.services.async_register(
        "mealie", "get_mealplan", get_mealplan, supports_response=SupportsResponse.ONLY
    )
    hass.services.async_register(
        "mealie", "get_recipe", get_recipe, supports_response=SupportsResponse.ONLY
    )
    return entry


def _meal(day: str, recipe: dict[str, Any] | None = None, title: str = "") -> dict[str, Any]:
    return {
        "mealplan_date": date.fromisoformat(day),
        "entry_type": "dinner",
        "title": title,
        "description": "",
        "recipe": recipe,
    }


def test_ingredient_texts() -> None:
    """Mealie's own text comes first, else amount, unit, food and note."""
    texts = [ingredient_text(item) for item in LASAGNE["ingredients"]]
    assert texts == [
        "500 g Hackfleisch",
        "2 Dosen Tomaten (gehackt)",
        "Salz",
        "1 Packung Lasagneplatten",
        "etwas Käse",
        "",
    ]
    assert ingredient_text("  1 Ei ") == "1 Ei"
    assert ingredient_text(None) == ""
    assert ingredient_text({"quantity": 0.5, "food": "Zitrone"}) == "0.5 Zitrone"


def test_recipe_from_mealie() -> None:
    """Steps keep their headings, empty ingredients are left out."""
    recipe = recipe_from_mealie(LASAGNE)
    assert recipe.title == "Lasagne"
    assert len(recipe.ingredients) == 5
    assert recipe.steps == ["Soße:", "Hackfleisch anbraten.", "Schichten und backen."]
    assert recipe.servings == "4 Portionen"
    assert recipe.url == "https://example.com/lasagne"


async def test_mealplan_becomes_an_outline(hass: HomeAssistant) -> None:
    """A note for the plan, a subtask per meal, the ingredients below it."""
    calls: list[dict[str, Any]] = []
    entry = _mealie(
        hass,
        [
            _meal("2026-11-25", title="Reste essen"),
            _meal("2026-11-24", {"recipe_id": "r1", "name": "Lasagne"}),
            _meal("2026-11-26", {"recipe_id": "gone", "name": "Suppe"}),
            _meal("2026-11-27"),
        ],
        {"r1": LASAGNE},
        calls,
    )
    assert mealie_available(hass)

    nodes, meals = await async_mealplan_nodes(hass, 7, "de", today=date(2026, 11, 23))

    assert calls == [
        {
            "config_entry_id": entry.entry_id,
            "start_date": "2026-11-23",
            "end_date": "2026-11-29",
        }
    ]
    assert meals == 3
    assert nodes[0].text == "Essensplan 23.11. – 29.11."
    assert nodes[0].depth == 0
    assert [(n.text, n.depth) for n in nodes[1:3]] == [
        ("24.11. · Lasagne", 1),
        ("500 g Hackfleisch", 2),
    ]
    assert "Portionen: 4 Portionen" in nodes[1].description
    assert "1. Hackfleisch anbraten." in nodes[1].description
    texts = [n.text for n in nodes if n.depth == 1]
    # A recipe that cannot be read keeps its name, a meal without anything is left out
    assert texts == ["24.11. · Lasagne", "25.11. · Reste essen", "26.11. · Suppe"]


async def test_english_labels_and_limits(hass: HomeAssistant) -> None:
    """English dates, and the days stay between 1 and 14."""
    calls: list[dict[str, Any]] = []
    _mealie(hass, [_meal("2026-11-23", title="Pizza")], calls=calls)
    nodes, _ = await async_mealplan_nodes(hass, 30, "en", today=date(2026, 11, 23))
    assert nodes[0].text == "Meal plan 11/23 – 12/06"
    assert nodes[1].text == "11/23 · Pizza"
    await async_mealplan_nodes(hass, 0, "en", today=date(2026, 11, 23))
    assert calls[-1]["end_date"] == "2026-11-23"


async def test_errors(hass: HomeAssistant) -> None:
    """Without Mealie, with an unknown entry or an empty plan nothing is added."""
    with pytest.raises(MealieError) as err:
        await async_mealplan_nodes(hass, 7, "de")
    assert err.value.key == "mealie_missing"

    _mealie(hass, [])
    with pytest.raises(MealieError) as err:
        await async_mealplan_nodes(hass, 7, "de", entry_id="unknown")
    assert err.value.key == "mealie_missing"
    with pytest.raises(MealieError) as err:
        await async_mealplan_nodes(hass, 7, "de")
    assert err.value.key == "mealie_empty"


async def test_the_action_adds_the_plan(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """brainstorm.import_mealplan adds the tree, tagged, in the chosen category."""
    entry = await setup_entry(options={"mealie_days": 3})
    store = entry.runtime_data
    today = dt_util.now().date().isoformat()
    _mealie(hass, [_meal(today, {"recipe_id": "r1", "name": "Lasagne"})], {"r1": LASAGNE})

    response = await hass.services.async_call(
        "brainstorm",
        "import_mealplan",
        {"category": "Alltag"},
        blocking=True,
        return_response=True,
    )
    assert response["meals"] == 1
    plan = store.get_idea(response["id"])
    assert plan["category"] == "Alltag"
    assert plan["tags"] == ["essensplan"]
    meal = next(i for i in store.ideas if i.get("parent_id") == plan["id"])
    assert meal["text"].endswith("· Lasagne")
    assert len([i for i in store.ideas if i.get("parent_id") == meal["id"]]) == 5


async def test_the_action_explains_a_missing_mealie(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Without Mealie the action says why."""
    await setup_entry()
    with pytest.raises(ServiceValidationError) as err:
        await hass.services.async_call(
            "brainstorm", "import_mealplan", {}, blocking=True, return_response=True
        )
    assert err.value.translation_key == "mealie_missing"


async def test_settings_page(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """The page appears with Mealie, saves the days and takes the plan over."""
    today = dt_util.now().date().isoformat()
    entry = await setup_entry()
    _mealie(hass, [_meal(today, title="Pizza")])

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert "integrations" in result["menu_options"]
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "integrations"}
    )
    assert "mealie" in result["menu_options"]
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "mealie"}
    )
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"mealie_days": 5, "mealie_category": "Alltag", "mealie_import": True},
    )
    assert result["step_id"] == "integrations"
    assert "Pizza" not in result["description_placeholders"]["notice"]
    assert "1" in result["description_placeholders"]["notice"]
    assert entry.options["mealie_days"] == 5
    assert entry.options["mealie_category"] == "Alltag"
    assert any(i["text"].endswith("· Pizza") for i in entry.runtime_data.ideas)
