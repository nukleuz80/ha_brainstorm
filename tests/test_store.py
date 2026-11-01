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


@pytest.mark.parametrize(
    ("text", "explicit", "clean", "priority"),
    [
        ("Regal", "später", "Regal", "low"),
        ("Regal", "irgendwas", "Regal", "medium"),
        ("Regal bauen !dringend", None, "Regal bauen", "urgent"),
        ("Regal bauen !wichtig", None, "Regal bauen", "high"),
        ("Regal bauen !niedrig", None, "Regal bauen", "low"),
        ("Dringend: Regal bauen", None, "Regal bauen", "urgent"),
        ("Wichtig: Regal bauen", None, "Regal bauen", "high"),
        ("Niedrige Priorität: Regal bauen", None, "Regal bauen", "low"),
        ("Normale Priorität: Regal bauen", None, "Regal bauen", "medium"),
        ("Regal bauen", None, "Regal bauen", "medium"),
    ],
)
def test_parse_priority(
    store: BrainstormStore, text: str, explicit: str | None, clean: str, priority: str
) -> None:
    """Test each way to state a priority."""
    assert store.parse_priority(text, explicit) == (clean, priority)


@pytest.mark.parametrize(
    ("text", "explicit", "category", "words"),
    [
        ("Regal bauen", "garten", "Haus & Garten", "regal"),
        ("Regal bauen", "Gibtsnicht", "Inbox", "regal"),
        ("Garten: Beet umgraben", None, "Haus & Garten", "beet"),
        ("Projekt Smarthome neu aufsetzen", None, "Smarthome", "smarthome"),
        ("Projekt Gartenhaus neu aufsetzen", None, "Projekte", "gartenhaus"),
        ("Etwas ganz anderes #alltag", None, "Alltag", "anderes"),
        ("Etwas ganz anderes #garten", None, "Haus & Garten", "anderes"),
        ("Bald den Garten umgraben", None, "Haus & Garten", "umgraben"),
    ],
)
def test_parse_text_and_category_ways(
    store: BrainstormStore, text: str, explicit: str | None, category: str, words: str
) -> None:
    """Test each way to state a category."""
    clean, found, _, _ = store.parse_text_and_category(text, explicit)
    assert found == category
    assert words in clean.lower()


def test_priority_after_a_category_prefix(store: BrainstormStore) -> None:
    """Test that a priority behind the category is found too."""
    clean, category, _, priority = store.parse_text_and_category(
        "Alltag: Dringend: Milch kaufen"
    )
    assert category == "Alltag"
    assert priority == "urgent"
    assert "milch" in clean.lower()


async def test_own_category_is_recognized(store: BrainstormStore) -> None:
    """Test that a category without predefined words is found by its name."""
    await store.async_add_category("Reisen")
    assert store.parse_text_and_category("Reisen: Koffer packen")[1] == "Reisen"


async def test_invalid_text_is_refused(store: BrainstormStore) -> None:
    """Test that a canceled sentence does not become an idea."""
    with pytest.raises(ServiceValidationError, match="abbrechen"):
        await store.async_add_idea("abbrechen")


async def test_broken_listener_does_not_stop_the_others(
    store: BrainstormStore, caplog: pytest.LogCaptureFixture
) -> None:
    """Test that one failing listener leaves the others running."""
    called: list[bool] = []

    def _broken(context: Any = None) -> None:
        raise ValueError("kaputt")

    store.register_listener(_broken)
    store.register_listener(lambda context=None: called.append(True))
    await store.async_add_category("Reisen")
    assert called == [True]
    assert "Error notifying brainstorm listener" in caplog.text


async def test_stored_categories_get_an_inbox(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    """Test that the Inbox comes back if it is missing in the storage."""
    hass_storage["brainstorm.storage"] = {
        "version": 1,
        "minor_version": 1,
        "key": "brainstorm.storage",
        "data": {"categories": ["Alltag"], "ideas": []},
    }
    instance = BrainstormStore(hass, {})
    await instance.async_load()
    assert instance.categories == ["Inbox", "Alltag"]


async def test_set_categories_keeps_inbox_first_and_moves_ideas(
    store: BrainstormStore,
) -> None:
    """Test editing the whole list of categories."""
    idea = await store.async_add_idea("Regal bauen", category="Projekte")
    await store.async_set_categories(["Alltag", "Inbox"])
    assert store.categories == ["Inbox", "Alltag"]
    assert store.get_idea(idea["id"])["category"] == "Inbox"
    await store.async_set_categories(["Alltag"])
    assert store.categories == ["Inbox", "Alltag"]


async def test_updates_of_unknown_ideas_change_nothing(store: BrainstormStore) -> None:
    """Test the quiet way out of reminder bookkeeping for a deleted idea."""
    await store.async_mark_reminded("gibtsnicht", escalated=False)
    await store.async_mark_fields("gibtsnicht", {"a": 1})
    assert store.ideas == []
    assert store.find_open_idea("  ") is None
    assert not await store.async_set_category_style(" ")


async def test_find_open_idea_ignores_completed_ones(store: BrainstormStore) -> None:
    """Test that a finished idea cannot be finished again by voice."""
    idea = await store.async_add_idea("Regal bauen")
    await store.async_update_idea(idea["id"], status="completed")
    assert store.find_open_idea("Regal bauen") is None


async def test_overview_without_ideas(store: BrainstormStore) -> None:
    """Test what is said when there is nothing to say."""
    assert "keine offenen" in store.get_overview_text()
    assert "keine offenen" in store.get_announcement_text()


async def test_announcement_finds_category_with_and(store: BrainstormStore) -> None:
    """Test a spoken category name, where the sign became a word."""
    await store.async_add_idea("Beet umgraben", category="Haus & Garten")
    assert "Beet" in store.get_announcement_text("haus und garten")
    assert store.get_ideas_by_category("Haus & Garten", priority="urgent") == []
    assert store.get_ideas_by_category("Alltag") == []


async def test_parent_chain_without_cycle_is_allowed(store: BrainstormStore) -> None:
    """Test moving an idea below another one that has its own parent."""
    top = await store.async_add_idea("Garage aufräumen")
    middle = await store.async_add_idea("Regal bauen", parent_id=top["id"])
    other = await store.async_add_idea("Licht reparieren")
    updated = await store.async_update_idea(
        other["id"], parent_id=middle["id"], update_parent=True
    )
    assert updated["parent_id"] == middle["id"]
