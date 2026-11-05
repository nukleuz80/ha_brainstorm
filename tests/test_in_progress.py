"""Tests for the mark that someone is working on an idea."""

from __future__ import annotations

from typing import Any

from homeassistant.core import Context, HomeAssistant

from .conftest import SetupEntry


async def _add(hass: HomeAssistant) -> str:
    response = await hass.services.async_call(
        "brainstorm",
        "add_idea",
        {"text": "Anhänge bauen", "category": "Inbox"},
        blocking=True,
        return_response=True,
    )
    return response["idea"]["id"]


async def _update(hass: HomeAssistant, context: Context | None = None, **data: Any) -> None:
    await hass.services.async_call(
        "brainstorm", "update_idea", data, blocking=True, context=context
    )


async def test_mark_and_unmark(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_admin_user: Any
) -> None:
    """Test that the mark keeps who started and when."""
    entry = await setup_entry()
    store = entry.runtime_data
    idea_id = await _add(hass)

    await _update(hass, Context(user_id=hass_admin_user.id), id=idea_id, in_progress=True)
    mark = store.get_idea(idea_id)["in_progress"]
    assert mark["by"] == hass_admin_user.id
    since = mark["since"]

    # Marking again keeps the start
    await _update(hass, id=idea_id, in_progress=True)
    assert store.get_idea(idea_id)["in_progress"]["since"] == since

    # Other changes leave it alone
    await _update(hass, id=idea_id, text="Anhänge bauen (v1.7.9)")
    assert store.get_idea(idea_id)["in_progress"]["since"] == since

    listed = next(i for i in store.get_overview_attributes()["ideas"] if i["id"] == idea_id)
    assert listed["in_progress"]["by"] == hass_admin_user.id

    response = await hass.services.async_call(
        "brainstorm", "get_ideas", {}, blocking=True, return_response=True
    )
    assert next(i for i in response["ideas"] if i["id"] == idea_id)["in_progress"]

    await _update(hass, id=idea_id, in_progress=False)
    assert "in_progress" not in store.get_idea(idea_id)


async def test_ticking_off_ends_the_work(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a done or archived idea is no longer in progress."""
    entry = await setup_entry()
    store = entry.runtime_data
    done_id = await _add(hass)
    archived_id = await _add(hass)
    for idea_id in (done_id, archived_id):
        await _update(hass, id=idea_id, in_progress=True)

    await _update(hass, id=done_id, status="completed", result="fertig")
    assert "in_progress" not in store.get_idea(done_id)

    # Done ideas cannot be marked
    await _update(hass, id=done_id, in_progress=True)
    assert "in_progress" not in store.get_idea(done_id)

    await store.async_archive_ideas([archived_id])
    assert "in_progress" not in store.get_idea(archived_id)


async def test_mark_stays_out_of_the_export(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a JSON export does not carry the mark to another home."""
    entry = await setup_entry()
    store = entry.runtime_data
    idea_id = await _add(hass)
    await _update(hass, id=idea_id, in_progress=True)
    assert all("in_progress" not in idea for idea in store.export_json()["ideas"])
