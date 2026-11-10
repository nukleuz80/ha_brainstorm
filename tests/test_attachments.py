"""Tests for files attached to ideas."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
import pytest

from custom_components.brainstorm.const import ATTACHMENT_MAX_SIZE
from custom_components.brainstorm.store import attachment_folder, attachment_name

from .conftest import SetupEntry

PNG = b"\x89PNG\r\n\x1a\n" + b"\0" * 64


@pytest.fixture(autouse=True)
def config_in_tmp(hass: HomeAssistant, tmp_path: Path) -> Path:
    """Keep the attachment folder out of the test package."""
    hass.config.config_dir = str(tmp_path)
    return tmp_path


async def _add(hass: HomeAssistant, text: str = "Router spinnt") -> str:
    response = await hass.services.async_call(
        "brainstorm",
        "add_idea",
        {"text": text, "category": "Inbox"},
        blocking=True,
        return_response=True,
    )
    return response["idea"]["id"]


def _form(*files: tuple[str, bytes]) -> aiohttp.FormData:
    form = aiohttp.FormData()
    for name, data in files:
        form.add_field("file", data, filename=name)
    return form


async def test_upload_show_and_delete(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_client: Any, config_in_tmp: Path
) -> None:
    """Test the life of an attachment through the endpoints."""
    entry = await setup_entry()
    store = entry.runtime_data
    idea_id = await _add(hass)
    client = await hass_client()

    resp = await client.post(
        f"/api/brainstorm/attachments/{idea_id}",
        data=_form(("../Fehler 1.png", PNG), ("log.txt", b"line")),
    )
    assert resp.status == 200
    body = await resp.json()
    assert [a["name"] for a in body["added"]] == ["Fehler 1.png", "log.txt"]
    attachments = store.get_idea(idea_id)["attachments"]
    assert [a["type"] for a in attachments] == ["image/png", "text/plain"]
    assert attachments[0]["size"] == len(PNG)
    assert attachments[0]["added_by"]
    files = sorted(p.name for p in (config_in_tmp / "brainstorm_attachments" / idea_id).iterdir())
    assert files == sorted([f"{attachments[0]['id']}.png", f"{attachments[1]['id']}.txt"])

    # The cards read the list from the overview
    overview = store.get_overview_attributes()
    listed = next(i for i in overview["ideas"] if i["id"] == idea_id)
    assert len(listed["attachments"]) == 2

    image = attachments[0]["id"]
    resp = await client.get(f"/api/brainstorm/attachments/{idea_id}/{image}")
    assert resp.status == 200
    assert await resp.read() == PNG
    assert resp.headers["Content-Type"] == "image/png"
    assert resp.headers["Content-Disposition"].startswith("inline;")
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    resp = await client.get(f"/api/brainstorm/attachments/{idea_id}/{attachments[1]['id']}")
    assert resp.headers["Content-Disposition"].startswith("attachment;")

    resp = await client.delete(f"/api/brainstorm/attachments/{idea_id}/{image}")
    assert resp.status == 200
    assert [a["name"] for a in (await resp.json())["attachments"]] == ["log.txt"]
    assert not (config_in_tmp / "brainstorm_attachments" / idea_id / f"{image}.png").exists()
    resp = await client.get(f"/api/brainstorm/attachments/{idea_id}/{image}")
    assert resp.status == 404

    resp = await client.delete(
        f"/api/brainstorm/attachments/{idea_id}/{attachments[1]['id']}"
    )
    assert resp.status == 200
    assert "attachments" not in store.get_idea(idea_id)
    assert not (config_in_tmp / "brainstorm_attachments" / idea_id).exists()


async def test_upload_refusals(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_client: Any
) -> None:
    """Test types, sizes and ideas that cannot take a file."""
    entry = await setup_entry()
    store = entry.runtime_data
    idea_id = await _add(hass)
    client = await hass_client()

    resp = await client.post(
        f"/api/brainstorm/attachments/{idea_id}", data=_form(("evil.svg", b"<svg/>"))
    )
    assert resp.status == 400
    assert (await resp.json())["code"] == "attachment_type"

    resp = await client.post(
        f"/api/brainstorm/attachments/{idea_id}",
        data=_form(("big.png", b"\0" * (ATTACHMENT_MAX_SIZE + 1))),
    )
    assert resp.status == 400
    assert (await resp.json())["code"] == "attachment_too_large"

    resp = await client.post(
        f"/api/brainstorm/attachments/{idea_id}", data=_form(("leer.txt", b""))
    )
    assert (await resp.json())["code"] == "attachment_empty"

    resp = await client.post(
        "/api/brainstorm/attachments/nope", data=_form(("a.png", PNG))
    )
    assert resp.status == 404
    resp = await client.get(f"/api/brainstorm/attachments/{idea_id}/nope")
    assert resp.status == 404
    assert "attachments" not in store.get_idea(idea_id)


async def test_upload_needs_login(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_client_no_auth: Any
) -> None:
    """Test that the files are not public."""
    await setup_entry()
    idea_id = await _add(hass)
    client = await hass_client_no_auth()
    resp = await client.post(
        f"/api/brainstorm/attachments/{idea_id}", data=_form(("a.png", PNG))
    )
    assert resp.status == 401


async def test_private_ideas_hide_their_files(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_admin_user: Any,
    hass_client: Any,
) -> None:
    """Test that only people who may see an idea get its files."""
    other = await hass.auth.async_create_user("Gast")
    entry = await setup_entry(
        options={"privacy_enabled": True, "privacy_owner": other.id}
    )
    store = entry.runtime_data
    idea_id = await _add(hass)
    store.get_idea(idea_id)["owner"] = other.id
    attachment = await store.async_add_attachment(idea_id, "a.png", PNG)

    client = await hass_client()
    resp = await client.get(f"/api/brainstorm/attachments/{idea_id}/{attachment['id']}")
    assert resp.status == 404
    resp = await client.post(
        f"/api/brainstorm/attachments/{idea_id}", data=_form(("b.png", PNG))
    )
    assert resp.status == 404
    resp = await client.delete(
        f"/api/brainstorm/attachments/{idea_id}/{attachment['id']}"
    )
    assert resp.status == 404
    assert len(store.get_idea(idea_id)["attachments"]) == 1


async def test_cleanup_after_thirty_days(
    hass: HomeAssistant, setup_entry: SetupEntry, config_in_tmp: Path
) -> None:
    """Test that files of ideas done long ago go, and others stay."""
    entry = await setup_entry()
    store = entry.runtime_data
    old_id = await _add(hass, "Alt")
    new_id = await _add(hass, "Neu")
    open_id = await _add(hass, "Offen")
    gone_id = await _add(hass, "Gelöscht")
    for idea_id in (old_id, new_id, open_id, gone_id):
        await store.async_add_attachment(idea_id, "shot.png", PNG)
    root = config_in_tmp / "brainstorm_attachments"
    (root / "verwaist").mkdir()
    (root / "verwaist" / "x.png").write_bytes(PNG)

    for idea_id in (old_id, new_id):
        await hass.services.async_call(
            "brainstorm", "update_idea", {"id": idea_id, "status": "completed"}, blocking=True
        )
    assert store.get_idea(new_id)["completed_at"]
    store.get_idea(old_id)["completed_at"] = (
        dt_util.now() - timedelta(days=31)
    ).isoformat()
    # Ideas done before completed_at existed fall back to their last change
    store.get_idea(open_id)["updated_at"] = (dt_util.now() - timedelta(days=90)).isoformat()
    await store.async_delete_idea(gone_id)

    assert await store.async_cleanup_attachments() == 1
    assert "attachments" not in store.get_idea(old_id)
    assert not (root / old_id).exists()
    assert (root / new_id).is_dir()
    assert (root / open_id).is_dir()
    # A deleted idea can still come back with its files
    assert (root / gone_id).is_dir()
    assert not (root / "verwaist").exists()

    restored = await store.async_restore_idea(gone_id)
    assert restored["attachments"]


async def test_reopening_forgets_the_completion(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a reopened idea keeps its files for good."""
    entry = await setup_entry()
    store = entry.runtime_data
    idea_id = await _add(hass)
    await hass.services.async_call(
        "brainstorm", "update_idea", {"id": idea_id, "status": "completed"}, blocking=True
    )
    assert "completed_at" in store.get_idea(idea_id)
    await hass.services.async_call(
        "brainstorm", "update_idea", {"id": idea_id, "status": "active"}, blocking=True
    )
    assert "completed_at" not in store.get_idea(idea_id)

    await store.async_archive_ideas([idea_id])
    assert "completed_at" in store.get_idea(idea_id)


async def test_attachments_stay_out_of_the_json_export(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that an export does not promise files it does not contain."""
    entry = await setup_entry()
    store = entry.runtime_data
    idea_id = await _add(hass)
    await store.async_add_attachment(idea_id, "a.png", PNG)
    exported = store.export_json()
    assert all("attachments" not in idea for idea in exported["ideas"])


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Screenshot 2026-11-05.png", "Screenshot 2026-11-05.png"),
        ("../../etc/passwd.txt", "passwd.txt"),
        ("C:\\Users\\olaf\\log.txt", "log.txt"),
        ('a<b>:"|?*.txt', "a_b______.txt"),
        ("...", "file"),
        ("", "file"),
    ],
)
def test_attachment_names(raw: str, expected: str) -> None:
    """Test that names cannot leave their folder."""
    assert attachment_name(raw) == expected


def test_attachment_folders() -> None:
    """Test that imported IDs with odd characters get a safe folder."""
    assert attachment_folder("ab12cd34") == "ab12cd34"
    odd = attachment_folder("../x")
    assert odd.startswith("id-") and "/" not in odd
