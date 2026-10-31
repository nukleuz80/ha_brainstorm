"""Tests for private ideas per Home Assistant user."""
from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.core import Context, HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import llm
from homeassistant.helpers.entity import DATA_ENTITY_SOURCE
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util
import pytest
from pytest_homeassistant_custom_component.common import async_mock_service
from pytest_homeassistant_custom_component.typing import (
    ClientSessionGenerator,
    WebSocketGenerator,
)

from custom_components.brainstorm.const import OVERVIEW_ENTITY_ID
from custom_components.brainstorm.llm import BrainstormLlmAPI

from .conftest import SetupEntry

TEXT_ATTRIBUTES = (
    "ideas",
    "completed_ideas",
    "recent_ideas",
    "latest_idea",
    "speech_overview",
    "last_action",
)
OWNER = "user-jan"
OTHER = "user-lenja"


async def _private(setup_entry: SetupEntry, **extra: Any) -> Any:
    """Set up with private ideas, one of each user and one from before."""
    entry = await setup_entry(
        stored={
            "ideas": [
                {
                    "id": "oldidea1",
                    "text": "alte geheime idee",
                    "category": "Inbox",
                    "status": "active",
                    "created_at": "2026-01-01T10:00:00+00:00",
                }
            ],
            "categories": ["Inbox", "Alltag"],
        },
        options={"privacy_enabled": True, "privacy_owner": OWNER, **extra},
    )
    store = entry.runtime_data
    await store.async_add_idea("idee von jan", context=Context(user_id=OWNER))
    await store.async_add_idea("idee von lenja", context=Context(user_id=OTHER))
    return entry


def _texts(ideas: list[dict[str, Any]]) -> set[str]:
    """Return the lower-case texts of ideas."""
    return {idea["text"].lower() for idea in ideas}


async def test_switch_off_changes_nothing(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that without the switch everyone sees everything as before."""
    entry = await setup_entry()
    store = entry.runtime_data
    await store.async_add_idea("idee von lenja", context=Context(user_id=OTHER))

    attributes = hass.states.get(OVERVIEW_ENTITY_ID).attributes
    assert "privacy" not in attributes
    assert _texts(attributes["ideas"]) == {"idee von lenja"}
    assert store.can_access(store.ideas[0], OWNER)
    assert store.get_ideas_by_category(user_id=OWNER)


async def test_sensor_holds_no_private_text(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the sensor, which every Home Assistant user can read."""
    await _private(setup_entry)

    state = hass.states.get(OVERVIEW_ENTITY_ID)

    assert state.attributes["privacy"] is True
    for attribute in TEXT_ATTRIBUTES:
        assert attribute not in state.attributes
    assert "geheim" not in str(state.as_dict())
    assert "idee von" not in str(state.as_dict())
    assert state.attributes["categories"]


async def test_each_user_gets_only_own_ideas(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    """Test the WebSocket command with two real users."""
    assert await async_setup_component(hass, "websocket_api", {})
    entry = await _private(setup_entry)
    store = entry.runtime_data
    refresh = hass.auth.async_validate_access_token(hass_read_only_access_token)
    reader_id = refresh.user.id
    await store.async_add_idea("idee vom leser", context=Context(user_id=reader_id))

    client = await hass_ws_client(hass, hass_read_only_access_token)
    await client.send_json_auto_id({"type": "brainstorm/ideas"})
    result = (await client.receive_json())["result"]

    assert _texts(result["ideas"]) == {"idee vom leser"}
    assert result["active_count"] == 1
    assert "geheim" not in str(result)
    assert "idee von" not in str(result)


async def test_old_ideas_belong_to_main_user(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that ideas from before privacy go to the main user."""
    entry = await _private(setup_entry)
    store = entry.runtime_data

    assert _texts(store.visible_ideas(OWNER)) == {"alte geheime idee", "idee von jan"}
    assert _texts(store.visible_ideas(OTHER)) == {"idee von lenja"}
    assert len(store.visible_ideas(None)) == 3
    overview = store.get_overview_attributes(OTHER)
    assert overview["category_counts"]["Inbox"] <= 1
    assert "geheim" not in overview["speech_overview"]


@pytest.mark.parametrize(
    ("service", "data"),
    [
        ("update_idea", {"id": "oldidea1", "text": "gehackt"}),
        ("delete_idea", {"id": "oldidea1"}),
        ("reorder_ideas", {"idea_ids": ["oldidea1"]}),
    ],
)
async def test_services_protect_foreign_ideas(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    service: str,
    data: dict[str, Any],
) -> None:
    """Test that nobody can change someone else's private idea."""
    entry = await _private(setup_entry)

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            "brainstorm", service, data, blocking=True, context=Context(user_id=OTHER)
        )

    stored = entry.runtime_data.get_idea("oldidea1")
    assert stored["text"] == "alte geheime idee"


async def test_owner_can_change_own_idea(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the normal case for the owner, and automations without a user."""
    entry = await _private(setup_entry)

    await hass.services.async_call(
        "brainstorm",
        "update_idea",
        {"id": "oldidea1", "text": "geändert"},
        blocking=True,
        context=Context(user_id=OWNER),
    )
    assert entry.runtime_data.get_idea("oldidea1")["text"] == "geändert"

    await hass.services.async_call(
        "brainstorm", "update_idea", {"id": "oldidea1", "text": "automation"}, blocking=True
    )
    assert entry.runtime_data.get_idea("oldidea1")["text"] == "automation"


async def test_read_services_are_filtered(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test reading ideas and announcements through services."""
    await _private(setup_entry)

    response = await hass.services.async_call(
        "brainstorm",
        "get_ideas",
        {},
        blocking=True,
        return_response=True,
        context=Context(user_id=OTHER),
    )
    assert _texts(response["ideas"]) == {"idee von lenja"}

    response = await hass.services.async_call(
        "brainstorm",
        "get_announcement",
        {},
        blocking=True,
        return_response=True,
        context=Context(user_id=OTHER),
    )
    assert "lenja" in response["speech"].lower()
    assert "geheim" not in response["speech"].lower()

    # Without a user it is spoken in a room, so only the main user's ideas count
    response = await hass.services.async_call(
        "brainstorm", "get_announcement", {}, blocking=True, return_response=True
    )
    assert "geheim" in response["speech"].lower()
    assert "lenja" not in response["speech"].lower()


@pytest.mark.parametrize(
    ("service", "data"),
    [("remove_category", {"name": "Alltag"}), ("export_markdown", {})],
)
async def test_shared_actions_need_an_admin(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_read_only_access_token: str,
    service: str,
    data: dict[str, Any],
) -> None:
    """Test actions that could reveal or move the ideas of others."""
    await _private(setup_entry)
    refresh = hass.auth.async_validate_access_token(hass_read_only_access_token)

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            "brainstorm",
            service,
            data,
            blocking=True,
            context=Context(user_id=refresh.user.id),
        )


async def test_todo_lists_hide_private_ideas(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the lists, which every user can read."""
    await _private(setup_entry)
    entity_id = next(
        state.entity_id
        for state in hass.states.async_all("todo")
        if state.entity_id.endswith("inbox")
    )

    items = await hass.services.async_call(
        "todo",
        "get_items",
        {},
        target={"entity_id": entity_id},
        blocking=True,
        return_response=True,
    )

    assert items[entity_id]["items"] == []


async def test_logbook_hides_text(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the logbook description, which every user can read."""
    from custom_components.brainstorm.logbook import _visible_text  # noqa: PLC0415

    await _private(setup_entry)
    assert _visible_text(hass, {"text": "geheim"}) == "Privater Eintrag"


async def test_logbook_keeps_text_without_privacy(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that nothing changes in the logbook with the switch off."""
    from custom_components.brainstorm.logbook import _visible_text  # noqa: PLC0415

    await setup_entry()
    assert _visible_text(hass, {"text": "offen"}) == "offen"


async def test_auto_export_stops_unless_allowed(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the files, which everyone with folder access can read."""
    entry = await setup_entry(
        options={
            "privacy_enabled": True,
            "privacy_owner": OWNER,
            "auto_export_markdown": True,
        }
    )
    assert not entry.runtime_data._auto_export  # noqa: SLF001


async def test_auto_export_can_be_allowed(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that exporting stays possible when someone wants it."""
    entry = await setup_entry(
        options={
            "privacy_enabled": True,
            "privacy_owner": OWNER,
            "auto_export_markdown": True,
            "privacy_export": True,
        }
    )
    assert entry.runtime_data._auto_export  # noqa: SLF001


async def _tool(hass: HomeAssistant, name: str, args: dict[str, Any], user: str) -> Any:
    """Call a Brainstorm tool like Assist does for a user."""
    context = llm.LLMContext(
        platform="test",
        context=Context(user_id=user),
        language="de",
        assistant="conversation",
        device_id=None,
    )
    instance = await BrainstormLlmAPI(hass).async_get_api_instance(context)
    tool = next(t for t in instance.tools if t.name == name)
    return await tool.async_call(
        hass, llm.ToolInput(tool_name=name, tool_args=args), context
    )


async def test_assist_tools_are_filtered(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that Assist only works with what the asking user may see."""
    entry = await _private(setup_entry)
    instance = await BrainstormLlmAPI(hass).async_get_api_instance(
        llm.LLMContext(
            platform="test",
            context=Context(user_id=OTHER),
            language="de",
            assistant="conversation",
            device_id=None,
        )
    )
    names = {tool.name for tool in instance.tools}
    query = next(n for n in names if "categor" not in n and ("get" in n or "list" in n))
    complete = next(n for n in names if "complete" in n)
    delete = next(n for n in names if "delete" in n)

    result = await _tool(hass, query, {}, OTHER)
    assert "geheim" not in str(result).lower()
    assert "lenja" in str(result).lower()

    await _tool(hass, complete, {"id": "oldidea1"}, OTHER)
    await _tool(hass, complete, {"idea_id": "oldidea1"}, OTHER)
    await _tool(hass, delete, {"id": "oldidea1"}, OTHER)
    await _tool(hass, delete, {"idea_id": "oldidea1"}, OTHER)
    stored = entry.runtime_data.get_idea("oldidea1")
    assert stored is not None
    assert stored["status"] == "active"


async def test_voice_and_briefing_only_mention_main_user(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test everything spoken aloud, which others could overhear."""
    hass.config.language = "de"
    assert await async_setup_component(hass, "http", {})
    entry = await _private(setup_entry, voice_mode="skill")
    store = entry.runtime_data
    client = await hass_client_no_auth()
    url = f"/api/webhook/{store.alexa_skill._webhook_id}"  # noqa: SLF001

    response = await client.post(
        url, json={"application_id": "a", "action": "read_all", "text": ""}
    )
    speech = (await response.json())["speech"].lower()
    assert "jan" in speech
    assert "lenja" not in speech

    await store.async_add_idea("arztbesuch planen", context=Context(user_id=OTHER))
    response = await client.post(
        url, json={"application_id": "a", "action": "done", "text": "arztbesuch"}
    )
    assert "gefunden" in (await response.json())["speech"]

    # New ideas by voice go to the main user
    response = await client.post(
        url, json={"application_id": "a", "action": "capture", "text": "per stimme"}
    )
    assert response.status == 200
    spoken = next(i for i in store.ideas if "stimme" in i["text"].lower())
    assert store.owner_of(spoken) == OWNER


async def test_foreign_reminder_goes_only_to_its_owner(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a private reminder does not reach the main user's phone."""
    jan_phone = async_mock_service(hass, "notify", "mobile_app_jan")
    lenja_phone = async_mock_service(hass, "notify", "mobile_app_lenja")
    alexa = async_mock_service(hass, "notify", "alexa_media")
    hass.states.async_set("person.lenja", "home", {"user_id": OTHER})
    entry = await _private(
        setup_entry,
        reminder_notify=["notify.mobile_app_jan"],
        reminder_alexa="fixed",
        reminder_echos=["media_player.kuche"],
        person_rules={"person.lenja": {"notify": ["notify.mobile_app_lenja"]}},
    )
    store = entry.runtime_data
    past = dt_util.now() - timedelta(minutes=1)
    await store.async_add_idea(
        "arzt von lenja", due=past, context=Context(user_id=OTHER)
    )

    await store.reminders.async_check(dt_util.now())
    await hass.async_block_till_done()

    assert len(lenja_phone) == 1
    assert not jan_phone
    assert not alexa


async def test_foreign_reminder_without_channels_stays_silent(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a person without channels gets nothing, rather than a leak."""
    jan_phone = async_mock_service(hass, "notify", "mobile_app_jan")
    entry = await _private(setup_entry, reminder_notify=["notify.mobile_app_jan"])
    store = entry.runtime_data
    await store.async_add_idea(
        "arzt von lenja",
        due=dt_util.now() - timedelta(minutes=1),
        context=Context(user_id=OTHER),
    )

    await store.reminders.async_check(dt_util.now())
    await hass.async_block_till_done()

    assert not jan_phone


async def test_options_require_main_user(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_admin_user: Any,
) -> None:
    """Test the switch, which needs someone to own the existing ideas."""
    entry = await setup_entry()
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "privacy"}
    )
    assert result["step_id"] == "privacy"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"privacy_enabled": True}
    )
    assert result["errors"] == {"privacy_owner": "owner_required"}
    assert "privacy_enabled" not in entry.options

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"privacy_enabled": True, "privacy_owner": hass_admin_user.id},
    )
    await hass.async_block_till_done()
    assert result["step_id"] == "init"
    assert entry.options["privacy_owner"] == hass_admin_user.id
    assert hass.states.get(OVERVIEW_ENTITY_ID).attributes["privacy"] is True


async def _share(hass: HomeAssistant, user: str | None, **data: Any) -> Any:
    """Call the share service as a user."""
    return await hass.services.async_call(
        "brainstorm",
        "share",
        data,
        blocking=True,
        return_response=True,
        context=Context(user_id=user),
    )


async def test_share_single_idea_with_levels(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test viewing and editing a shared idea, and taking it back."""
    entry = await _private(setup_entry)
    store = entry.runtime_data
    third = "user-sava"

    await _share(hass, OWNER, ids=["oldidea1"], shares={OTHER: "view", third: "edit"})
    idea = store.get_idea("oldidea1")
    assert store.access_level(idea, OTHER) == "view"
    assert store.access_level(idea, third) == "edit"
    assert "alte geheime idee" in _texts(store.visible_ideas(OTHER))

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            "brainstorm",
            "update_idea",
            {"id": "oldidea1", "text": "geändert"},
            blocking=True,
            context=Context(user_id=OTHER),
        )
    await hass.services.async_call(
        "brainstorm",
        "update_idea",
        {"id": "oldidea1", "status": "completed"},
        blocking=True,
        context=Context(user_id=third),
    )
    assert store.get_idea("oldidea1")["status"] == "completed"

    # Deleting and passing on stay with the owner
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            "brainstorm",
            "delete_idea",
            {"id": "oldidea1"},
            blocking=True,
            context=Context(user_id=third),
        )
    with pytest.raises(ServiceValidationError):
        await _share(hass, third, ids=["oldidea1"], shares={"all": "view"})

    await _share(hass, OWNER, ids=["oldidea1"], shares={OTHER: None})
    assert store.access_level(store.get_idea("oldidea1"), OTHER) is None


async def test_share_several_ideas_at_once(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test sharing more than one idea in one call."""
    entry = await _private(setup_entry)
    store = entry.runtime_data
    second = await store.async_add_idea("noch eine", context=Context(user_id=OWNER))

    response = await _share(
        hass, OWNER, ids=["oldidea1", second["id"]], shares={OTHER: "view"}
    )

    assert response["changed"] == 2
    assert {"alte geheime idee", second["text"].lower()} <= _texts(
        store.visible_ideas(OTHER)
    )


async def test_cannot_share_foreign_idea_among_own(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that one foreign idea stops the whole call, changing nothing."""
    entry = await _private(setup_entry)
    store = entry.runtime_data
    mine = await store.async_add_idea("meine", context=Context(user_id=OTHER))

    with pytest.raises(ServiceValidationError):
        await _share(hass, OTHER, ids=[mine["id"], "oldidea1"], shares={"x": "view"})

    assert not store.get_idea(mine["id"]).get("shares")


async def test_share_category_includes_later_ideas_and_survives_reload(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test sharing a whole category of one owner."""
    entry = await _private(setup_entry)
    store = entry.runtime_data
    await store.async_add_idea(
        "einkaufen", category="Alltag", context=Context(user_id=OWNER)
    )
    await store.async_add_idea(
        "lenjas alltag", category="Alltag", context=Context(user_id=OTHER)
    )

    await _share(hass, OWNER, category="Alltag", shares={OTHER: "view"})
    await store.async_add_idea(
        "später dazu", category="Alltag", context=Context(user_id=OWNER)
    )
    assert {"einkaufen", "später dazu"} <= _texts(store.visible_ideas(OTHER))
    assert "alte geheime idee" not in _texts(store.visible_ideas(OTHER))
    # Someone else's ideas in the same category are not part of the share
    assert "lenjas alltag" not in _texts(store.visible_ideas("user-sava"))

    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert "einkaufen" in _texts(entry.runtime_data.visible_ideas(OTHER))

    await _share(hass, OWNER, category="Alltag", shares={OTHER: None})
    assert "einkaufen" not in _texts(entry.runtime_data.visible_ideas(OTHER))


async def test_share_needs_privacy_and_a_target(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the errors of the share service."""
    await setup_entry()
    with pytest.raises(ServiceValidationError):
        await _share(hass, OWNER, ids=["a"], shares={OTHER: "view"})


async def test_share_needs_exactly_one_target(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that either ideas or a category have to be named."""
    await _private(setup_entry)
    with pytest.raises(ServiceValidationError):
        await _share(hass, OWNER, shares={OTHER: "view"})
    with pytest.raises(ServiceValidationError):
        await _share(hass, OWNER, ids=["oldidea1"], category="Alltag", shares={})


async def test_todo_lists_show_what_is_shared_with_all(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_admin_user: Any
) -> None:
    """Test the normal lists with sharing."""
    entry = await _private(setup_entry)
    entity_id = next(
        state.entity_id
        for state in hass.states.async_all("todo")
        if state.entity_id.endswith("inbox")
    )

    async def items() -> list[dict[str, Any]]:
        result = await hass.services.async_call(
            "todo",
            "get_items",
            {},
            target={"entity_id": entity_id},
            blocking=True,
            return_response=True,
        )
        return result[entity_id]["items"]

    assert await items() == []
    await _share(hass, OWNER, ids=["oldidea1"], shares={"all": "view"})
    assert [i["summary"].lower() for i in await items()] == ["alte geheime idee"]

    # Read-only for others, also through the list
    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            "todo",
            "update_item",
            {"item": "oldidea1", "rename": "geändert"},
            target={"entity_id": entity_id},
            blocking=True,
            context=Context(user_id=hass_admin_user.id),
        )

    # A new entry on a list is meant for everyone who reads that list
    await hass.services.async_call(
        "todo",
        "add_item",
        {"item": "für alle"},
        target={"entity_id": entity_id},
        blocking=True,
        context=Context(user_id=hass_admin_user.id),
    )
    assert "für alle" in [i["summary"].lower() for i in await items()]
    assert "für alle" in _texts(entry.runtime_data.visible_ideas("user-sava"))


async def test_reminder_for_person_shares_idea(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that someone who is reminded of an idea can also see it."""
    hass.states.async_set("person.lenja", "home", {"user_id": OTHER})
    entry = await _private(setup_entry)
    store = entry.runtime_data

    idea = await store.async_add_idea(
        "termin", assignee="person.lenja", context=Context(user_id=OWNER)
    )
    assert store.access_level(store.get_idea(idea["id"]), OTHER) == "edit"

    second = await store.async_add_idea("zweiter", context=Context(user_id=OWNER))
    await hass.services.async_call(
        "brainstorm",
        "update_idea",
        {"id": second["id"], "assignee": "person.lenja"},
        blocking=True,
        context=Context(user_id=OWNER),
    )
    assert store.access_level(store.get_idea(second["id"]), OTHER) == "edit"


async def test_websocket_reports_access_and_people(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
    hass_owner_user: Any,
) -> None:
    """Test what the card gets: rights, owner's name and who can be chosen."""
    assert await async_setup_component(hass, "websocket_api", {})
    entry = await setup_entry(
        options={"privacy_enabled": True, "privacy_owner": hass_owner_user.id}
    )
    store = entry.runtime_data
    refresh = hass.auth.async_validate_access_token(hass_read_only_access_token)
    reader = refresh.user
    own = await store.async_add_idea("von besitzer", context=Context(user_id=hass_owner_user.id))
    await store.async_set_idea_shares([own["id"]], {reader.id: "view"}, hass_owner_user.id)

    client = await hass_ws_client(hass, hass_read_only_access_token)
    await client.send_json_auto_id({"type": "brainstorm/ideas"})
    result = (await client.receive_json())["result"]

    idea = result["ideas"][0]
    assert idea["access"] == "view"
    assert idea["owner_name"] == hass_owner_user.name
    # Who else can see it stays with the owner
    assert "shares" not in idea
    assert result["current_user"] == reader.id
    assert reader.id not in [u["id"] for u in result["share_users"]]
    assert hass_owner_user.id in [u["id"] for u in result["share_users"]]


async def test_no_extra_fields_without_privacy(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that nothing about owners appears in the public sensor when off."""
    entry = await setup_entry()
    await entry.runtime_data.async_add_idea("offen", context=Context(user_id=OTHER))

    idea = hass.states.get(OVERVIEW_ENTITY_ID).attributes["ideas"][0]

    assert "owner" not in idea
    assert "access" not in idea


async def _voice_setup(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_client_no_auth: ClientSessionGenerator
) -> tuple[Any, Any]:
    """Set up two Echos that are already known, one assigned to Lenja."""
    hass.config.language = "de"
    assert await async_setup_component(hass, "http", {})
    entry = await _private(
        setup_entry,
        voice_mode="skill",
        voice_owners={"Echo Lenja": OTHER},
    )
    store = entry.runtime_data
    store.alexa_skill._devices = {  # noqa: SLF001
        "d-lenja": {"name": "Echo Lenja", "entity_id": None, "custom": True},
        "d-kuche": {"name": "Echo Küche", "entity_id": None, "custom": True},
    }
    client = await hass_client_no_auth()
    url = f"/api/webhook/{store.alexa_skill._webhook_id}"  # noqa: SLF001

    async def post(device: str, action: str, text: str = "") -> dict[str, Any]:
        response = await client.post(
            url,
            json={
                "application_id": "a",
                "device_id": device,
                "action": action,
                "text": text,
            },
        )
        return await response.json()

    return entry, post


async def test_skill_uses_person_of_the_echo(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test ideas and read-outs per Echo."""
    entry, post = await _voice_setup(hass, setup_entry, hass_client_no_auth)
    store = entry.runtime_data

    await post("d-lenja", "capture", "hausaufgaben machen")
    await post("d-kuche", "capture", "steuer abgeben")
    lenja = next(i for i in store.ideas if "hausaufgaben" in i["text"].lower())
    jan = next(i for i in store.ideas if "steuer" in i["text"].lower())
    assert store.owner_of(lenja) == OTHER
    assert store.owner_of(jan) == OWNER

    speech = (await post("d-lenja", "read_all"))["speech"].lower()
    assert "hausaufgaben" in speech
    assert "steuer" not in speech
    assert "geheim" not in speech
    speech = (await post("d-kuche", "read_all"))["speech"].lower()
    assert "steuer" in speech
    assert "hausaufgaben" not in speech

    assert "gefunden" in (await post("d-lenja", "done", "steuer abgeben"))["speech"]
    assert store.get_idea(jan["id"])["status"] == "active"
    assert "Erledigt" in (await post("d-lenja", "done", "hausaufgaben"))["speech"]


async def test_native_voice_uses_person_of_the_echo(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the automation path, which passes the Echo as the device."""
    entry = await _private(setup_entry, voice_owners={"Echo Lenja": OTHER})
    store = entry.runtime_data

    response = await hass.services.async_call(
        "brainstorm",
        "add_idea",
        {"text": "hausaufgaben machen", "source": "alexa", "device": "Echo Lenja"},
        blocking=True,
        return_response=True,
    )
    assert store.owner_of(store.get_idea(response["idea"]["id"])) == OTHER

    response = await hass.services.async_call(
        "brainstorm",
        "get_announcement",
        {"device": "Echo Lenja"},
        blocking=True,
        return_response=True,
    )
    assert "hausaufgaben" in response["speech"].lower()
    assert "geheim" not in response["speech"].lower()


async def test_assist_without_user_only_gets_main_user(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test a voice satellite, where nobody is logged in."""
    await _private(setup_entry)
    context = llm.LLMContext(
        platform="test",
        context=Context(),
        language="de",
        assistant="conversation",
        device_id=None,
    )
    instance = await BrainstormLlmAPI(hass).async_get_api_instance(context)
    tool = next(t for t in instance.tools if t.name == "brainstorm_get_ideas")

    result = await tool.async_call(
        hass, llm.ToolInput(tool_name=tool.name, tool_args={}), context
    )

    assert "lenja" not in str(result).lower()
    assert "jan" in str(result).lower()


async def test_reminder_of_assigned_echo_speaks_there(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a person's reminder may use the Echo it came from."""
    alexa = async_mock_service(hass, "notify", "alexa_media")
    hass.states.async_set(
        "media_player.lenja", "idle", {"friendly_name": "Echo Lenja"}
    )
    hass.data.setdefault(DATA_ENTITY_SOURCE, {})["media_player.lenja"] = {
        "domain": "alexa_media",
        "custom_component": True,
    }
    entry = await _private(
        setup_entry,
        reminder_alexa="origin",
        voice_owners={"Echo Lenja": OTHER},
    )
    store = entry.runtime_data
    await store.async_add_idea(
        "arzt",
        device="Echo Lenja",
        owner=OTHER,
        due=dt_util.now() - timedelta(minutes=1),
    )

    await store.reminders.async_check(dt_util.now())
    await hass.async_block_till_done()

    assert alexa[0].data["target"] == ["media_player.lenja"]


async def test_options_assign_and_remove_echo(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_admin_user: Any
) -> None:
    """Test assigning a device to a person and removing it again."""
    entry = await _private(setup_entry)

    async def open_step() -> dict[str, Any]:
        result = await hass.config_entries.options.async_init(entry.entry_id)
        return await hass.config_entries.options.async_configure(
            result["flow_id"], {"next_step_id": "privacy_voice"}
        )

    result = await open_step()
    assert result["step_id"] == "privacy_voice"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"device": "Echo Lenja", "voice_user": hass_admin_user.id}
    )
    await hass.async_block_till_done()
    assert result["step_id"] == "privacy_voice"
    assert entry.options["voice_owners"] == {"Echo Lenja": hass_admin_user.id}
    assert "Echo Lenja" in result["description_placeholders"]["assignments"]

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"device": "Echo Lenja"}
    )
    await hass.async_block_till_done()
    assert entry.options["voice_owners"] == {}
