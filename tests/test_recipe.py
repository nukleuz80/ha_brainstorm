"""Tests for recipes imported from a web page."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import patch

import pytest
import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.brainstorm import map_sources
from custom_components.brainstorm.recipe import (
    Recipe,
    recipe_description,
    recipe_from_html,
    recipe_nodes,
)

from .conftest import SetupEntry

# Shaped like the recipe data of Chefkoch: a list of blocks, HTML entities
CHEFKOCH = {
    "@context": "http://schema.org",
    "@type": "Recipe",
    "name": "Spaghetti Carbonara",
    "recipeYield": "4 Portion(en)",
    "prepTime": "P0DT0H15M",
    "cookTime": "P0DT0H10M",
    "recipeIngredient": [
        "500 g Spaghetti",
        "150 g Speck",
        "4  Eigelb",
        "Salz &amp; Pfeffer",
        "100 g Speck (oder Guanciale, , alternativ Bacon)",
        "",
        "500 g Spaghetti",
    ],
    "recipeInstructions": "Nudeln kochen.<br>Speck anbraten.\nAlles mischen.",
}
# Shaped like WordPress recipe plugins: @graph, sections with HowToStep
GRAPH = {
    "@context": "https://schema.org",
    "@graph": [
        {"@type": "WebPage", "name": "Blog"},
        {
            "@type": ["Recipe", "NewsArticle"],
            "name": "Apple Pie",
            "recipeYield": ["8", "8 slices"],
            "totalTime": "PT1H30M",
            "recipeIngredient": ["3 apples", "1 pie crust"],
            "recipeInstructions": [
                {
                    "@type": "HowToSection",
                    "name": "Filling",
                    "itemListElement": [
                        {"@type": "HowToStep", "text": "Slice the <b>apples</b>."},
                        {"@type": "HowToStep", "text": "Add sugar."},
                    ],
                },
                {"@type": "HowToStep", "text": "Bake for 45 minutes."},
            ],
        },
    ],
}


def page(*blocks: Any) -> str:
    """Return a page with the blocks as JSON-LD scripts."""
    scripts = "".join(
        f'<script type="application/ld+json">{json.dumps(block)}</script>'
        for block in blocks
    )
    return f"<html><head>{scripts}</head><body>Rezept</body></html>"


def test_recipe_like_chefkoch() -> None:
    """Title, cleaned ingredients without doubles, steps, servings and time."""
    recipe = recipe_from_html(
        page([{"@type": "BreadcrumbList"}, CHEFKOCH]), "https://x.de/r"
    )
    assert recipe is not None
    assert recipe.title == "Spaghetti Carbonara"
    assert recipe.ingredients == [
        "500 g Spaghetti",
        "150 g Speck",
        "4 Eigelb",
        "Salz & Pfeffer",
        "100 g Speck (oder Guanciale, alternativ Bacon)",
    ]
    assert recipe.steps == ["Nudeln kochen.", "Speck anbraten.", "Alles mischen."]
    assert recipe.servings == "4 Portion(en)"
    assert recipe.minutes == 25


def test_recipe_in_a_graph_with_sections() -> None:
    """Recipes inside @graph, with a list of types and sections of steps."""
    recipe = recipe_from_html(page({"@type": "Organization"}, GRAPH))
    assert recipe is not None
    assert recipe.title == "Apple Pie"
    assert recipe.steps == [
        "Filling:",
        "Slice the apples .",
        "Add sugar.",
        "Bake for 45 minutes.",
    ]
    assert recipe.servings == "8"
    assert recipe.minutes == 90


def test_pages_without_a_recipe() -> None:
    """No recipe data, broken JSON or a recipe without ingredients give None."""
    assert recipe_from_html("<html><body>Nur Text</body></html>") is None
    assert (
        recipe_from_html('<script type="application/ld+json">{kaputt</script>') is None
    )
    assert recipe_from_html(page({"@type": "Recipe", "name": "Leer"})) is None


def test_description_and_nodes() -> None:
    """Facts first, numbered steps with section titles, the source last."""
    recipe = Recipe(
        title="Apple Pie",
        ingredients=["3 apples", "1 pie crust"],
        steps=["Filling:", "Slice.", "Bake."],
        servings="8",
        minutes=90,
        url="https://example.com/pie",
    )
    text = recipe_description(recipe, "de")
    assert text.splitlines()[0] == "Portionen: 8 · Zeit: 1 h 30 min"
    assert "Zubereitung:\nFilling:\n1. Slice.\n2. Bake." in text
    assert text.endswith("Quelle: https://example.com/pie")
    assert recipe_description(recipe, "en").startswith("Servings: 8 · Time: 1 h 30 min")
    single = Recipe(title="X", ingredients=["a"], steps=["Zubereitung:", "Kochen."])
    assert recipe_description(single, "de") == "Zubereitung:\n1. Kochen."
    long = Recipe(
        title="X", ingredients=["a"], steps=["Schritt " * 200] * 10, url="https://e.com"
    )
    text = recipe_description(long, "de")
    assert len(text) <= 4000 and text.endswith("Quelle: https://e.com")
    nodes = recipe_nodes(recipe, "en")
    assert [(n.text, n.depth) for n in nodes] == [
        ("Apple Pie", 0),
        ("3 apples", 1),
        ("1 pie crust", 1),
    ]


@pytest.fixture
def public_dns() -> Any:
    """Every host name is a public address, without asking a real DNS."""
    with patch.object(map_sources, "async_resolve", return_value=["93.184.216.34"]):
        yield


async def test_import_recipe_service(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    aioclient_mock: AiohttpClientMocker,
    public_dns: Any,
) -> None:
    """The recipe becomes a tagged note with one subtask per ingredient."""
    entry = await setup_entry()
    store = entry.runtime_data
    aioclient_mock.get(
        "https://www.chefkoch.de/rezepte/1/carbonara.html",
        text=page(CHEFKOCH),
        headers={"Content-Type": "text/html; charset=utf-8"},
    )
    result = await hass.services.async_call(
        "brainstorm",
        "import_recipe",
        {
            "url": " https://www.chefkoch.de/rezepte/1/carbonara.html ",
            "category": "Inbox",
        },
        blocking=True,
        return_response=True,
    )
    assert result["title"] == "Spaghetti Carbonara"
    assert result["ingredients"] == 5
    note = store.get_idea(result["id"])
    assert note["category"] == "Inbox"
    assert note["tags"] == ["rezept"]
    assert (
        "Quelle: https://www.chefkoch.de/rezepte/1/carbonara.html"
        in note["description"]
    )
    subtasks = [i for i in store.ideas if i.get("parent_id") == note["id"]]
    assert [i["text"] for i in subtasks][:4] == [
        "500 g Spaghetti",
        "150 g Speck",
        "4 Eigelb",
        "Salz & Pfeffer",
    ]
    assert all(not i["tags"] for i in subtasks)


async def test_import_recipe_errors(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    aioclient_mock: AiohttpClientMocker,
    public_dns: Any,
) -> None:
    """A page without recipe data, a dead page and a private address are refused."""
    await setup_entry()
    aioclient_mock.get(
        "https://example.com/blog",
        text="<html><body>Hallo</body></html>",
        headers={"Content-Type": "text/html"},
    )
    aioclient_mock.get("https://example.com/weg", status=404)
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            "brainstorm",
            "import_recipe",
            {"url": "https://example.com/blog"},
            blocking=True,
        )
    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            "brainstorm",
            "import_recipe",
            {"url": "https://example.com/weg"},
            blocking=True,
        )
    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            "brainstorm",
            "import_recipe",
            {"url": "http://192.168.0.1/rezept"},
            blocking=True,
        )
    with pytest.raises(vol.Invalid):
        await hass.services.async_call(
            "brainstorm", "import_recipe", {"url": "kein Link"}, blocking=True
        )
