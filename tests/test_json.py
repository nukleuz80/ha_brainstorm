"""Tests for exporting and importing ideas as JSON."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from homeassistant.core import Context, HomeAssistant
from homeassistant.exceptions import ServiceValidationError

from custom_components.brainstorm.const import DOMAIN

from .conftest import SetupEntry

STORED = {
    "categories": ["Inbox", "Einkauf", "Projekte"],
    "category_icons": {"Einkauf": "mdi:cart"},
    "category_colors": {"Einkauf": "#ff8800"},
    "ideas": [
        {
            "id": "parent01",
            "text": "Garage aufräumen",
            "category": "Projekte",
            "priority": "high",
            "status": "active",
            "created_at": "2026-11-01T10:00:00+01:00",
            "map_pos": {"x": 10, "y": 20},
            "todo_link": {"entity": "todo.bring", "uid": "abc"},
        },
        {
            "id": "child001",
            "text": "Regal bauen",
            "category": "Projekte",
            "parent_id": "parent01",
            "status": "completed",
            "due": "2026-11-10T09:00:00+01:00",
        },
        {"id": "milk0001", "text": "Milch", "category": "Einkauf", "status": "active"},
    ],
}


async def _call(hass: HomeAssistant, action: str, **data: Any) -> dict[str, Any]:
    """Call an action and return its response."""
    return await hass.services.async_call(
        DOMAIN, action, data, blocking=True, return_response=True
    )


async def test_export_holds_ideas_and_categories(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that the export has everything needed to bring the ideas back."""
    await setup_entry(stored=STORED)
    data = await _call(hass, "export_json")
    assert data["format"] == "brainstorm_hub"
    assert data["version"] == 1
    assert data["categories"] == ["Inbox", "Einkauf", "Projekte"]
    assert data["category_icons"] == {"Einkauf": "mdi:cart"}
    assert {i["id"] for i in data["ideas"]} == {"parent01", "child001", "milk0001"}
    parent = next(i for i in data["ideas"] if i["id"] == "parent01")
    # The link belongs to this Home Assistant's lists
    assert "todo_link" not in parent
    assert parent["map_pos"] == {"x": 10, "y": 20}
    json.dumps(data)

    only = await _call(hass, "export_json", category="einkauf")
    assert only["categories"] == ["Einkauf"]
    assert [i["id"] for i in only["ideas"]] == ["milk0001"]
    assert only["category_colors"] == {"Einkauf": "#ff8800"}


async def test_export_and_import_move_ideas_to_another_home(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that an export brings everything back into an empty Brainstorm."""
    entry = await setup_entry(stored=STORED)
    data = await _call(hass, "export_json")
    store = entry.runtime_data
    for idea in list(store.ideas):
        await store.async_delete_idea(idea["id"])
    await store.async_remove_category("Einkauf")
    store._category_icons.clear()

    result = await _call(hass, "import_json", data=data)
    assert result == {"added": 3, "skipped": 0, "categories_added": ["Einkauf"]}
    child = store.get_idea("child001")
    assert child["parent_id"] == "parent01"
    assert child["status"] == "completed"
    assert child["due"].startswith("2026-11-10T09:00")
    assert store.get_idea("parent01")["priority"] == "high"
    assert store.category_icons["Einkauf"] == "mdi:cart"

    # Importing the same file again changes nothing
    again = await _call(hass, "import_json", data=data)
    assert again == {"added": 0, "skipped": 3, "categories_added": []}
    assert len(store.ideas) == 3


async def test_import_cleans_up_what_does_not_fit(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that broken entries, unknown parents and cycles are handled."""
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox"]})
    store = entry.runtime_data
    data = {
        "format": "brainstorm_hub",
        "version": 1,
        "category_icons": {"Neu": "not an icon"},
        "ideas": [
            {"id": "a", "text": "A", "category": "Neu", "parent_id": "b"},
            {"id": "b", "text": "B", "category": "Neu", "parent_id": "a"},
            {"id": "c", "text": "C", "parent_id": "nirgends", "priority": "dringend"},
            {"id": "d", "text": "  "},
            {"text": "Ohne ID", "status": "unbekannt", "tags": ["x", 3]},
            "kein Objekt",
        ],
    }
    result = await _call(hass, "import_json", data=data)
    assert result["added"] == 4
    assert result["skipped"] == 2
    assert result["categories_added"] == ["Neu"]
    assert "Neu" not in store.category_icons
    assert not (store.get_idea("a")["parent_id"] and store.get_idea("b")["parent_id"])
    assert store.get_idea("c")["parent_id"] is None
    assert store.get_idea("c")["category"] == "Inbox"
    assert store.get_idea("c")["priority"] == "urgent"
    no_id = next(i for i in store.ideas if i["text"] == "Ohne ID")
    assert no_id["status"] == "active"
    assert no_id["tags"] == ["x"]


@pytest.mark.parametrize(
    ("data", "key"),
    [
        ({"ideas": []}, "json_not_brainstorm"),
        ({"format": "brainstorm_hub", "ideas": "x"}, "json_not_brainstorm"),
        ({"format": "brainstorm_hub", "version": 99, "ideas": []}, "json_too_new"),
    ],
)
async def test_import_refuses_foreign_data(
    hass: HomeAssistant, setup_entry: SetupEntry, data: dict[str, Any], key: str
) -> None:
    """Test that only exports of Brainstorm can be imported."""
    await setup_entry()
    with pytest.raises(ServiceValidationError) as err:
        await _call(hass, "import_json", data=data)
    assert err.value.translation_key == key


async def test_import_needs_exactly_one_source(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that data and a path cannot both be given or both be missing."""
    await setup_entry()
    for data in ({}, {"data": {}, "path": "x.json"}):
        with pytest.raises(ServiceValidationError) as err:
            await _call(hass, "import_json", **data)
        assert err.value.translation_key == "json_source_missing"


async def test_export_to_a_file_and_back(
    hass: HomeAssistant, setup_entry: SetupEntry, tmp_path: Path
) -> None:
    """Test writing the export to a file and importing that file."""
    hass.config.config_dir = str(tmp_path)
    entry = await setup_entry(stored=STORED)
    result = await _call(hass, "export_json", path="brainstorm/backup.json")
    target = tmp_path / "brainstorm" / "backup.json"
    assert result["path"] == str(target)
    assert json.loads(target.read_text("utf-8"))["format"] == "brainstorm_hub"

    store = entry.runtime_data
    await store.async_delete_idea("milk0001")
    imported = await _call(hass, "import_json", path=str(target))
    assert imported["added"] == 1
    assert store.get_idea("milk0001")["text"] == "Milch"


@pytest.mark.parametrize(
    ("path", "key"),
    [
        ("brainstorm/backup.txt", "json_path_invalid"),
        ("www/backup.json", "export_not_allowed"),
        ("node-red/flows.json", "export_not_allowed"),
        ("zigbee2mqtt/coordinator_backup.json", "export_not_allowed"),
        (".storage/backup.json", "export_not_allowed"),
        ("brainstorm/missing.json", "json_file_missing"),
    ],
)
async def test_file_paths_are_checked(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    tmp_path: Path,
    path: str,
    key: str,
) -> None:
    """Test that only JSON files in allowed folders are read and written."""
    hass.config.config_dir = str(tmp_path)
    await setup_entry()
    action = "import_json" if "missing" in path else "export_json"
    with pytest.raises(ServiceValidationError) as err:
        await _call(hass, action, path=path)
    assert err.value.translation_key == key


async def test_a_broken_file_is_reported(
    hass: HomeAssistant, setup_entry: SetupEntry, tmp_path: Path
) -> None:
    """Test that a file that is no JSON gives a clear error."""
    hass.config.config_dir = str(tmp_path)
    (tmp_path / "brainstorm").mkdir()
    (tmp_path / "brainstorm" / "kaputt.json").write_text("{nicht json", "utf-8")
    await setup_entry()
    with pytest.raises(ServiceValidationError) as err:
        await _call(hass, "import_json", path="brainstorm/kaputt.json")
    assert err.value.translation_key == "json_invalid"


async def test_privacy_limits_export_and_owners(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_admin_user: Any, hass_read_only_user: Any
) -> None:
    """Test that only visible ideas leave and owners stay only for admins."""
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox"]},
        options={"privacy_enabled": True, "privacy_owner": hass_admin_user.id},
    )
    store = entry.runtime_data
    await store.async_add_idea("geheim", context=Context(user_id=hass_admin_user.id))
    await store.async_add_idea("meins", context=Context(user_id=hass_read_only_user.id))

    data = await hass.services.async_call(
        DOMAIN,
        "export_json",
        {},
        blocking=True,
        return_response=True,
        context=Context(user_id=hass_read_only_user.id),
    )
    assert [i["text"] for i in data["ideas"]] == ["Meins"]

    # Writing a file needs an admin while privacy is on
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN,
            "export_json",
            {"path": "brainstorm/x.json"},
            blocking=True,
            return_response=True,
            context=Context(user_id=hass_read_only_user.id),
        )

    foreign = {
        "format": "brainstorm_hub",
        "version": 1,
        "ideas": [
            {
                "id": "x1",
                "text": "Von Admin",
                "owner": hass_admin_user.id,
                "shares": {"all": "view", "fremd": "edit", hass_admin_user.id: "boss"},
            },
            {"id": "x2", "text": "Von Fremd", "owner": "unbekannt"},
        ],
    }
    await hass.services.async_call(
        DOMAIN,
        "import_json",
        {"data": foreign},
        blocking=True,
        return_response=True,
        context=Context(user_id=hass_read_only_user.id),
    )
    assert store.get_idea("x1")["owner"] == hass_read_only_user.id
    assert store.get_idea("x1")["shares"] == {"all": "view"}
    assert store.get_idea("x2")["owner"] == hass_read_only_user.id

    foreign["ideas"][0]["id"] = "x3"
    await hass.services.async_call(
        DOMAIN,
        "import_json",
        {"data": foreign},
        blocking=True,
        return_response=True,
        context=Context(user_id=hass_admin_user.id),
    )
    assert store.get_idea("x3")["owner"] == hass_admin_user.id


@pytest.mark.parametrize(
    ("action", "data"),
    [
        ("export_json", {"path": "brainstorm/x.json"}),
        ("export_markdown", {"path": "brainstorm/md"}),
        ("import_json", {"path": "brainstorm/x.json"}),
    ],
)
async def test_files_need_an_admin_without_privacy(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_read_only_user: Any,
    tmp_path: Path,
    action: str,
    data: dict[str, Any],
) -> None:
    """Test that only admins may name a file, even with privacy off."""
    hass.config.config_dir = str(tmp_path)
    await setup_entry(stored=STORED)
    with pytest.raises(ServiceValidationError) as err:
        await hass.services.async_call(
            DOMAIN,
            action,
            data,
            blocking=True,
            return_response=action != "export_markdown",
            context=Context(user_id=hass_read_only_user.id),
        )
    assert err.value.translation_key == "admin_only"
    assert not (tmp_path / "brainstorm").exists()


async def test_files_are_fine_for_admins(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_admin_user: Any, tmp_path: Path
) -> None:
    """Test that an admin can still write an export file."""
    hass.config.config_dir = str(tmp_path)
    await setup_entry(stored=STORED)
    result = await hass.services.async_call(
        DOMAIN,
        "export_json",
        {"path": "brainstorm/x.json"},
        blocking=True,
        return_response=True,
        context=Context(user_id=hass_admin_user.id),
    )
    assert result["path"] == str(tmp_path / "brainstorm" / "x.json")


async def test_unusual_ids_get_a_new_id(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that imported IDs with markup are replaced, and so are their parents."""
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox"]})
    bad = '"><img src=x onerror=alert(1)>'
    result = await _call(
        hass,
        "import_json",
        data={
            "format": "brainstorm_hub",
            "version": 1,
            "ideas": [
                {"id": bad, "text": "Böse"},
                {"id": "gut_1", "text": "Gut", "parent_id": bad},
                {"id": 12345, "text": "Zahl"},
                {
                    "id": "pos1",
                    "text": "Position",
                    "map_pos": {"x": "1;color:red", "y": 2},
                    "trigger": "zone.home",
                    "source": {"x": 1},
                },
            ],
        },
    )
    assert result["added"] == 4
    store = entry.runtime_data
    ids = {i["id"] for i in store.ideas}
    assert bad not in ids
    assert all(i.isalnum() or "_" in i for i in ids)
    assert store.get_idea("gut_1")["parent_id"] is None
    position = store.get_idea("pos1")
    assert "map_pos" not in position
    assert position["trigger"] is None
    assert position["source"] == "manual"
