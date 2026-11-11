"""Tests for reactions and voting rounds."""

from __future__ import annotations

from typing import Any

from homeassistant.core import Context, HomeAssistant
from homeassistant.exceptions import ServiceValidationError
import pytest

from .conftest import SetupEntry

OLAF = "user-olaf"
FRIDA = "user-frida"


async def _call(
    hass: HomeAssistant, service: str, user: str | None = OLAF, **data: Any
) -> Any:
    return await hass.services.async_call(
        "brainstorm",
        service,
        data,
        blocking=True,
        return_response=True,
        context=Context(user_id=user),
    )


async def _add(hass: HomeAssistant, text: str, category: str = "Alltag") -> str:
    response = await _call(hass, "add_idea", text=text, category=category)
    return response["idea"]["id"]


async def test_reactions_toggle_per_user(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that each person switches their own reaction."""
    entry = await setup_entry()
    store = entry.runtime_data
    idea_id = await _add(hass, "Grillabend")

    response = await _call(hass, "react", id=idea_id, reaction="heart")
    assert response["reactions"] == {"heart": [OLAF]}
    await _call(hass, "react", FRIDA, id=idea_id, reaction="heart")
    await _call(hass, "react", FRIDA, id=idea_id, reaction="laugh", active=True)
    assert store.get_idea(idea_id)["reactions"] == {
        "heart": [OLAF, FRIDA],
        "laugh": [FRIDA],
    }

    # Toggling again takes it back, switching on twice keeps one
    await _call(hass, "react", id=idea_id, reaction="heart")
    await _call(hass, "react", FRIDA, id=idea_id, reaction="laugh", active=True)
    assert store.get_idea(idea_id)["reactions"] == {
        "heart": [FRIDA],
        "laugh": [FRIDA],
    }
    await _call(hass, "react", FRIDA, id=idea_id, reaction="heart", active=False)
    await _call(hass, "react", FRIDA, id=idea_id, reaction="laugh", active=False)
    assert "reactions" not in store.get_idea(idea_id)

    with pytest.raises(ServiceValidationError):
        await _call(hass, "react", None, id=idea_id, reaction="like")
    with pytest.raises(ServiceValidationError):
        await _call(hass, "react", id="missing", reaction="like")


async def test_voting_round_budget_and_ranking(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a round grants votes per person and ranks by points."""
    entry = await setup_entry()
    store = entry.runtime_data
    zoo = await _add(hass, "Zoo")
    lake = await _add(hass, "Badesee")
    museum = await _add(hass, "Museum")
    other = await _add(hass, "Rasen mähen", "Inbox")

    with pytest.raises(ServiceValidationError):
        await _call(hass, "vote", id=zoo)

    await _call(hass, "start_voting", category="Alltag", votes=3)
    await _call(hass, "vote", id=zoo, delta=2)
    response = await _call(hass, "vote", id=lake)
    assert response == {"success": True, "votes": 1, "used": 3, "allowed": 3}
    with pytest.raises(ServiceValidationError):
        await _call(hass, "vote", id=museum)
    # Another list has no round
    with pytest.raises(ServiceValidationError):
        await _call(hass, "vote", id=other)

    # Taking one back frees it
    await _call(hass, "vote", id=zoo, delta=-1)
    await _call(hass, "vote", id=museum)
    await _call(hass, "vote", FRIDA, id=lake, delta=3)

    overview = store.get_overview_attributes(OLAF)
    assert overview["voting"]["Alltag"]["used"] == 3
    assert overview["voting"]["Alltag"]["votes"] == 3
    listed = {i["id"]: i for i in overview["ideas"]}
    assert listed[lake]["votes"] == {OLAF: 1, FRIDA: 3}

    response = await _call(hass, "end_voting", category="Alltag")
    assert [item["id"] for item in response["ranking"]] == [lake, zoo, museum]
    assert response["ranking"][0]["points"] == 4
    assert response["ranking"][0]["voters"] == 2
    assert "Alltag" not in store.voting
    # The points stay for sorting
    await _call(hass, "sort_children", category="Alltag", by="votes")
    order = [i["id"] for i in store.ideas if i["category"] == "Alltag"]
    # Zoo and museum tie with one point each and keep their order
    assert order[0] == lake

    with pytest.raises(ServiceValidationError):
        await _call(hass, "end_voting", category="Alltag")

    # A new round can start without the old points
    await _call(hass, "start_voting", category="Alltag", votes=2, clear=True)
    assert not any(store.get_idea(i).get("votes") for i in (zoo, lake, museum))
    with pytest.raises(ServiceValidationError):
        await _call(hass, "start_voting", category="Gibt es nicht")


async def test_hidden_round_shows_only_own_votes(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a hidden round hides the votes of others until it ends."""
    entry = await setup_entry()
    store = entry.runtime_data
    idea_id = await _add(hass, "Pizza")
    await _call(hass, "start_voting", category="Alltag", votes=5, hidden=True)
    await _call(hass, "vote", id=idea_id, delta=2)
    await _call(hass, "vote", FRIDA, id=idea_id, delta=1)

    mine = next(i for i in store.get_overview_attributes(OLAF)["ideas"] if i["id"] == idea_id)
    assert mine["votes"] == {OLAF: 2}
    assert mine["votes_hidden"] is True
    hers = next(i for i in store.get_overview_attributes(FRIDA)["ideas"] if i["id"] == idea_id)
    assert hers["votes"] == {FRIDA: 1}

    await _call(hass, "end_voting", category="Alltag")
    after = next(i for i in store.get_overview_attributes(FRIDA)["ideas"] if i["id"] == idea_id)
    assert after["votes"] == {OLAF: 2, FRIDA: 1}
    assert "votes_hidden" not in after


async def test_round_survives_a_restart(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_storage: dict[str, Any]
) -> None:
    """Test that a running round and the votes are stored."""
    entry = await setup_entry()
    idea_id = await _add(hass, "Kino")
    await _call(hass, "start_voting", category="Alltag", votes=4)
    await _call(hass, "vote", id=idea_id)
    stored = hass_storage["brainstorm.storage"]["data"]
    assert stored["voting"]["Alltag"]["votes"] == 4
    assert stored["voting"]["Alltag"]["by"] == OLAF

    store = entry.runtime_data
    await store.async_load()
    assert store.voting["Alltag"]["votes"] == 4
    assert store.get_idea(idea_id)["votes"] == {OLAF: 1}


async def test_votes_and_reactions_stay_out_of_exports(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that user IDs of this installation do not travel in a JSON export."""
    await setup_entry()
    idea_id = await _add(hass, "Ausflug")
    await _call(hass, "react", id=idea_id, reaction="like")
    await _call(hass, "start_voting", category="Alltag")
    await _call(hass, "vote", id=idea_id)
    response = await _call(hass, "export_json")
    exported = next(i for i in response["ideas"] if i["id"] == idea_id)
    assert "reactions" not in exported
    assert "votes" not in exported


async def test_viewers_may_react_but_strangers_not(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that seeing a private note is enough to react and vote."""
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox", "Alltag"]},
        options={"privacy_enabled": True, "privacy_owner": OLAF},
    )
    store = entry.runtime_data
    idea_id = await _add(hass, "Geheimer Plan")

    with pytest.raises(ServiceValidationError):
        await _call(hass, "react", FRIDA, id=idea_id, reaction="like")

    await _call(hass, "share", ids=[idea_id], shares={FRIDA: "view"})
    await _call(hass, "react", FRIDA, id=idea_id, reaction="like")
    await _call(hass, "start_voting", category="Alltag")
    await _call(hass, "vote", FRIDA, id=idea_id)
    assert store.get_idea(idea_id)["votes"] == {FRIDA: 1}
    assert store.get_idea(idea_id)["reactions"] == {"like": [FRIDA]}
