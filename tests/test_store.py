"""Tests for the Brainstorm store."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError

from custom_components.brainstorm.const import (
    DEFAULT_CATEGORIES,
    EVENT_IDEA_COMPLETED,
    EVENT_IDEA_UPDATED,
)
from custom_components.brainstorm.store import BrainstormStore


@pytest.fixture
async def store(hass: HomeAssistant, hass_storage: dict[str, Any]) -> BrainstormStore:
    """Return a loaded store."""
    instance = BrainstormStore(hass, {})
    await instance.async_load()
    return instance


async def _reload(hass: HomeAssistant, store: BrainstormStore) -> BrainstormStore:
    """Save the store and load a new instance from storage."""
    await store._store.async_save(  # noqa: SLF001
        {
            "categories": store.categories,
            "category_icons": store.category_icons,
            "category_colors": store.category_colors,
            "ideas": store.ideas,
        }
    )
    instance = BrainstormStore(hass, {})
    await instance.async_load()
    return instance


async def test_removed_default_category_stays_removed(
    hass: HomeAssistant, store: BrainstormStore
) -> None:
    """Test that a removed default category does not come back."""
    assert await store.async_remove_category("Alltag")
    reloaded = await _reload(hass, store)
    assert "Alltag" not in reloaded.categories


async def test_category_order_survives_reload(
    hass: HomeAssistant, store: BrainstormStore
) -> None:
    """Test that a custom category order is kept."""
    await store.async_set_categories(["Inbox", "Zeta", "Alpha"])
    reloaded = await _reload(hass, store)
    assert reloaded.categories == ["Inbox", "Zeta", "Alpha"]


async def test_fresh_store_has_defaults(store: BrainstormStore) -> None:
    """Test the default categories of a new store."""
    assert store.categories == DEFAULT_CATEGORIES


@pytest.mark.parametrize(
    ("text", "expected_text", "expected_category"),
    [
        ("Haus streichen", "Haus streichen", "Haus & Garten"),
        ("Familie besuchen", "Familie besuchen", "Alltag"),
        ("Garten Zaun reparieren", "Zaun reparieren", "Haus & Garten"),
        ("Garten: Blumen pflanzen", "Blumen pflanzen", "Haus & Garten"),
        ("für den Garten Tomaten düngen", "Tomaten düngen", "Haus & Garten"),
        ("Haus, streichen", "Streichen", "Haus & Garten"),
    ],
)
async def test_parse_text_and_category(
    store: BrainstormStore, text: str, expected_text: str, expected_category: str
) -> None:
    """Test that category words are only stripped when text remains meaningful."""
    assert store.parse_text_and_category(text)[:2] == (expected_text, expected_category)


async def test_failing_auto_export_does_not_abort_add(
    hass: HomeAssistant, tmp_path: Path
) -> None:
    """Test that the action still completes if the auto-export fails."""
    hass.config.config_dir = str(tmp_path)
    (tmp_path / "blocker").touch()
    store = BrainstormStore(
        hass,
        {"auto_export_markdown": True, "markdown_path": str(tmp_path / "blocker/x")},
    )
    await store.async_load()
    calls: list[Any] = []
    store.register_listener(lambda *args: calls.append(args))

    await store.async_add_idea("Rasen mähen vorne")

    assert len(store.ideas) == 1
    assert calls


@pytest.mark.parametrize(
    ("relative", "allowed"),
    [
        ("brainstorm", True),
        ("a/b", True),
        ("", False),
        ("../outside", False),
        ("custom_components/brainstorm", False),
        ("www/notes", False),
        (".storage", False),
    ],
)
async def test_export_path_inside_config(
    hass: HomeAssistant,
    store: BrainstormStore,
    tmp_path: Path,
    relative: str,
    allowed: bool,
) -> None:
    """Test which folders below the config dir can be exported to."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    hass.config.config_dir = str(config_dir)
    target = config_dir / relative

    if allowed:
        await store.async_export_to_markdown(str(target))
        assert (target / "inbox.md").exists()
    else:
        with pytest.raises(ServiceValidationError):
            await store.async_export_to_markdown(str(target))
        assert not (target / "inbox.md").exists()


async def test_export_to_external_dir_needs_allowlist(
    hass: HomeAssistant, store: BrainstormStore, tmp_path: Path
) -> None:
    """Test that external folders must be in allowlist_external_dirs."""
    hass.config.config_dir = str(tmp_path / "config")
    external = tmp_path / "external"
    external.mkdir()

    with pytest.raises(ServiceValidationError):
        await store.async_export_to_markdown(str(external))

    hass.config.allowlist_external_dirs = {str(external)}
    await store.async_export_to_markdown(str(external))
    assert (external / "inbox.md").exists()


@pytest.mark.parametrize(
    "kwargs",
    [{"color": 'red"><img src=x onerror=alert(1)>'}, {"color": "red"}, {"icon": 'x"><b'}],
)
async def test_invalid_style_rejected(
    store: BrainstormStore, kwargs: dict[str, str]
) -> None:
    """Test that malformed icons and colors are not stored."""
    with pytest.raises(ServiceValidationError):
        await store.async_set_category_style("Inbox", **kwargs)
    with pytest.raises(ServiceValidationError):
        await store.async_add_category("Neu", **kwargs)
    assert not store.category_colors
    assert not store.category_icons
    assert "Neu" not in store.categories


async def test_valid_style_stored_and_cleared(store: BrainstormStore) -> None:
    """Test storing and clearing a valid style."""
    await store.async_set_category_style("Inbox", icon="mdi:home", color="#06b6d4")
    assert store.category_colors == {"Inbox": "#06b6d4"}
    assert store.category_icons == {"Inbox": "mdi:home"}
    await store.async_set_category_style("Inbox", icon="", color="")
    assert not store.category_colors
    assert not store.category_icons


async def test_parent_cycle_rejected(store: BrainstormStore) -> None:
    """Test that a parent cycle is rejected and nothing changes."""
    first = await store.async_add_idea("Erste Notiz hier")
    second = await store.async_add_idea("Zweite Notiz hier", parent_id=first["id"])

    with pytest.raises(ServiceValidationError):
        await store.async_update_idea(
            first["id"], text="Geändert", parent_id=second["id"], update_parent=True
        )
    with pytest.raises(ServiceValidationError):
        await store.async_update_idea(
            first["id"], parent_id=first["id"], update_parent=True
        )
    assert first["parent_id"] is None
    assert first["text"] == "Erste Notiz hier"


async def test_completed_event_fires_only_on_transition(
    hass: HomeAssistant, store: BrainstormStore
) -> None:
    """Test that editing a completed idea does not complete it again."""
    events: list[str] = []

    @callback
    def _record(event: Event) -> None:
        events.append(event.event_type)

    hass.bus.async_listen(EVENT_IDEA_COMPLETED, _record)
    hass.bus.async_listen(EVENT_IDEA_UPDATED, _record)
    idea = await store.async_add_idea("Rasen mähen vorne")

    await store.async_update_idea(idea["id"], status="completed")
    await store.async_update_idea(idea["id"], text="Neu", status="completed")
    await hass.async_block_till_done()

    assert events == [EVENT_IDEA_COMPLETED, EVENT_IDEA_UPDATED]


async def test_default_category_is_used(hass: HomeAssistant, hass_storage: dict) -> None:
    """Test the default category option and its fallback."""
    store = BrainstormStore(hass, {"default_category": "Projekte"})
    await store.async_load()
    assert (await store.async_add_idea("xyz abc"))["category"] == "Projekte"
    await store.async_remove_category("Projekte")
    assert (await store.async_add_idea("xyz def"))["category"] == "Inbox"


async def test_archived_ideas_are_exported_as_done(
    hass: HomeAssistant, store: BrainstormStore, tmp_path: Path
) -> None:
    """Test that archived ideas appear in the done section."""
    hass.config.config_dir = str(tmp_path)
    idea = await store.async_add_idea("Alte Notiz hier")
    await store.async_update_idea(idea["id"], status="archived")
    await store.async_export_to_markdown(str(tmp_path / "out"))
    assert "~~Alte Notiz hier~~" in (tmp_path / "out/inbox.md").read_text("utf-8")
