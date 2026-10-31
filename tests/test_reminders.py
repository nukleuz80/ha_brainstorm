"""Tests for spoken due dates, reminders, briefing and weekly review."""
from __future__ import annotations

from datetime import datetime, time, timedelta
import json
from pathlib import Path
from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.exceptions import HomeAssistantError
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util
import pytest
from pytest_homeassistant_custom_component.common import async_mock_service
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from custom_components.brainstorm.const import OVERVIEW_ENTITY_ID
from custom_components.brainstorm.nlp import parse_due
from custom_components.brainstorm.reminders import (
    build_reminder_request,
    format_due,
    is_quiet_time,
)

from .conftest import SetupEntry

# A Saturday
NOW = datetime(2026, 10, 31, 10, 0, tzinfo=dt_util.UTC)
PUSH = "notify.mobile_app_phone"
SKILL_ID = "amzn1.ask.skill.mine"


def _at(day_offset: int, hour: int, minute: int = 0) -> datetime:
    """Return a time relative to the test's now."""
    return (NOW + timedelta(days=day_offset)).replace(hour=hour, minute=minute)


@pytest.mark.parametrize(
    ("spoken", "due", "text"),
    [
        ("morgen um 8 an die mülltonnen", _at(1, 8), "die mülltonnen"),
        ("morgen um 8 uhr 30 an die mülltonnen", _at(1, 8, 30), "die mülltonnen"),
        ("morgen um acht an die tonnen", _at(1, 8), "die tonnen"),
        ("morgen früh an die tonnen", _at(1, 8), "die tonnen"),
        ("heute abend an den müll", _at(0, 19), "den müll"),
        ("heute abend um 8 an den müll", _at(0, 20), "den müll"),
        ("übermorgen an den arzt", _at(2, 9), "den arzt"),
        ("um halb neun an den bus", _at(1, 8, 30), "den bus"),
        ("um viertel nach zwölf an das essen", _at(0, 12, 15), "das essen"),
        ("um 14 uhr an das essen", _at(0, 14), "das essen"),
        ("um 14:45 ans essen", _at(0, 14, 45), "essen"),
        ("am montag an die steuer", _at(2, 9), "die steuer"),
        ("am samstag an die steuer", _at(7, 9), "die steuer"),
        ("nächste woche an die steuer", _at(2, 9), "die steuer"),
        ("in zwei stunden an den kuchen", NOW + timedelta(hours=2), "den kuchen"),
        ("in einer stunde an den kuchen", NOW + timedelta(hours=1), "den kuchen"),
        ("in 10 minuten an den kuchen", NOW + timedelta(minutes=10), "den kuchen"),
        ("in drei tagen an den reifen", _at(3, 9), "den reifen"),
        ("am 25.11. an den elternsprechtag", _at(25, 9), "den elternsprechtag"),
        ("am 25. november an den termin", _at(25, 9), "den termin"),
        ("an den termin am 1.2.2027 um 17 uhr", datetime(2027, 2, 1, 17, tzinfo=dt_util.UTC), "den termin"),
        ("die tonnen morgen früh", _at(1, 8), "die tonnen"),
    ],
)
def test_parse_due(spoken: str, due: datetime, text: str) -> None:
    """Test understanding spoken dates and times."""
    assert parse_due(spoken, NOW) == (due, text)


@pytest.mark.parametrize(
    "spoken", ["die tonnen rausstellen", "wir brauchen 8 neue stühle", "kaffee kaufen"]
)
def test_parse_due_without_time(spoken: str) -> None:
    """Test that a text without a time stays as it is."""
    assert parse_due(spoken, NOW) == (None, spoken)


def test_parse_due_invalid_date_is_ignored() -> None:
    """Test that an impossible date does not raise."""
    assert parse_due("am 45.13. an den test", NOW)[0] is None


@pytest.mark.parametrize(
    ("clock", "quiet"),
    [(time(23, 30), True), (time(3, 0), True), (time(7, 0), False), (time(12, 0), False)],
)
def test_quiet_time_spans_midnight(clock: time, quiet: bool) -> None:
    """Test quiet hours across midnight."""
    now = datetime.combine(NOW.date(), clock, dt_util.UTC)
    assert is_quiet_time(now, time(22, 0), time(7, 0)) is quiet


def test_quiet_time_not_set() -> None:
    """Test that missing quiet hours are never quiet."""
    assert not is_quiet_time(NOW, None, None)
    assert not is_quiet_time(NOW, time(8, 0), time(8, 0))


def test_format_due() -> None:
    """Test how a time is spoken."""
    now = dt_util.as_local(NOW)
    assert format_due(now + timedelta(days=1), now).startswith("morgen um ")
    assert "Uhr" in format_due(now + timedelta(days=5), now)


async def _setup(
    hass: HomeAssistant, setup_entry: SetupEntry, **options: Any
) -> tuple[Any, list[ServiceCall], list[ServiceCall]]:
    """Set up reminders with mocked Alexa and phone services."""
    alexa = async_mock_service(hass, "notify", "alexa_media")
    push = async_mock_service(hass, "notify", "mobile_app_phone")
    hass.states.async_set(
        "media_player.kuche", "idle", {"friendly_name": "Echo Küche"}
    )
    entry = await setup_entry(options=options)
    return entry, alexa, push


async def _due_idea(entry: Any, **fields: Any) -> dict[str, Any]:
    """Add an idea that was due a minute ago."""
    return await entry.runtime_data.async_add_idea(
        "tonnen rausstellen",
        device="Echo Küche",
        due=dt_util.now() - timedelta(minutes=1),
        **fields,
    )


async def test_reminder_goes_to_origin_echo_and_phone_once(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test a due idea on all channels, the event and that it is not repeated."""
    entry, alexa, push = await _setup(
        hass, setup_entry, reminder_alexa="origin", reminder_notify=[PUSH]
    )
    events: list[Any] = []
    hass.bus.async_listen("brainstorm_reminder_due", events.append)
    idea = await _due_idea(entry)

    await entry.runtime_data.reminders.async_check(dt_util.now())
    await hass.async_block_till_done()

    assert alexa[0].data["target"] == ["media_player.kuche"]
    assert "tonnen" in alexa[0].data["message"].lower()
    actions = [a["action"] for a in push[0].data["data"]["actions"]]
    assert actions[0] == f"BRAINSTORM_DONE_{idea['id']}"
    assert len(events) == 1

    await entry.runtime_data.reminders.async_check(dt_util.now())
    await hass.async_block_till_done()
    assert (len(alexa), len(push), len(events)) == (1, 1, 1)


async def test_future_and_completed_ideas_stay_silent(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test ideas that must not remind."""
    entry, alexa, push = await _setup(
        hass, setup_entry, reminder_alexa="origin", reminder_notify=[PUSH]
    )
    store = entry.runtime_data
    await store.async_add_idea("zukunft", due=dt_util.now() + timedelta(hours=1))
    done = await _due_idea(entry)
    await store.async_update_idea(done["id"], status="completed")

    await store.reminders.async_check(dt_util.now())
    await hass.async_block_till_done()

    assert not alexa
    assert not push


async def test_no_channels_still_fires_event(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that people without services can use their own automations."""
    entry, alexa, push = await _setup(hass, setup_entry)
    events: list[Any] = []
    hass.bus.async_listen("brainstorm_reminder_due", events.append)
    await _due_idea(entry)

    await entry.runtime_data.reminders.async_check(dt_util.now())
    await hass.async_block_till_done()

    assert len(events) == 1
    assert not alexa
    assert not push


async def test_phone_waits_for_delay(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that the phone follows the announcement after the waiting time."""
    entry, alexa, push = await _setup(
        hass,
        setup_entry,
        reminder_alexa="origin",
        reminder_notify=[PUSH],
        reminder_delay=15,
    )
    await _due_idea(entry)
    reminders = entry.runtime_data.reminders

    await reminders.async_check(dt_util.now())
    await hass.async_block_till_done()
    assert len(alexa) == 1
    assert not push

    await reminders.async_check(dt_util.now() + timedelta(minutes=16))
    await hass.async_block_till_done()
    assert len(push) == 1
    assert len(alexa) == 1


async def test_phone_is_used_at_once_if_alexa_is_missing(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the fallback when no Echo can be found."""
    entry, _, push = await _setup(
        hass, setup_entry, reminder_alexa="fixed", reminder_notify=[PUSH], reminder_delay=15
    )
    await _due_idea(entry)

    await entry.runtime_data.reminders.async_check(dt_util.now())
    await hass.async_block_till_done()

    assert len(push) == 1


async def test_quiet_hours_hold_back_until_end(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a reminder waits for the end of the quiet hours."""
    entry, alexa, push = await _setup(
        hass,
        setup_entry,
        reminder_alexa="origin",
        reminder_notify=[PUSH],
        quiet_start="22:00:00",
        quiet_end="07:00:00",
    )
    await _due_idea(entry)
    reminders = entry.runtime_data.reminders
    night = dt_util.now().replace(hour=23, minute=0) + timedelta(days=1)

    await reminders.async_check(night)
    await hass.async_block_till_done()
    assert not alexa
    assert not push

    await reminders.async_check(night + timedelta(hours=9))
    await hass.async_block_till_done()
    assert len(alexa) == 1
    assert len(push) == 1


async def test_urgent_idea_reaches_phone_in_quiet_hours(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that urgent ideas break through, but no Echo speaks at night."""
    entry, alexa, push = await _setup(
        hass,
        setup_entry,
        reminder_alexa="origin",
        reminder_notify=[PUSH],
        quiet_start="22:00:00",
        quiet_end="07:00:00",
    )
    await _due_idea(entry, priority="urgent")
    night = dt_util.now().replace(hour=23, minute=0) + timedelta(days=1)

    await entry.runtime_data.reminders.async_check(night)
    await hass.async_block_till_done()

    assert not alexa
    assert len(push) == 1


@pytest.mark.parametrize(
    ("action", "status", "hours"),
    [("DONE", "completed", None), ("SNOOZE", "active", 1)],
)
async def test_phone_buttons(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    action: str,
    status: str,
    hours: int | None,
) -> None:
    """Test the buttons in a phone notification."""
    entry, _, _ = await _setup(hass, setup_entry, reminder_notify=[PUSH])
    idea = await _due_idea(entry)
    reminders = entry.runtime_data.reminders
    await reminders.async_check(dt_util.now())

    hass.bus.async_fire(
        "mobile_app_notification_action",
        {"action": f"BRAINSTORM_{action}_{idea['id']}"},
    )
    await hass.async_block_till_done()

    stored = next(i for i in entry.runtime_data.ideas if i["id"] == idea["id"])
    assert stored["status"] == status
    if hours:
        assert dt_util.parse_datetime(stored["due"]) > dt_util.now()
        assert not stored["reminded_at"]


async def test_digest_once_per_day(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the daily briefing and that it respects its schedule."""
    entry, _, push = await _setup(
        hass,
        setup_entry,
        reminder_notify=[PUSH],
        digest_enabled=True,
        digest_time="08:00:00",
    )
    store = entry.runtime_data
    morning = dt_util.now().replace(hour=8, minute=1, second=0, microsecond=0)
    await store.async_add_idea("tonnen raus", due=morning + timedelta(hours=2))

    await store.reminders.async_check(morning - timedelta(hours=1))
    await hass.async_block_till_done()
    assert not push

    await store.reminders.async_check(morning)
    await store.reminders.async_check(morning + timedelta(minutes=1))
    await hass.async_block_till_done()
    assert len(push) == 1
    assert "tonnen" in push[0].data["message"].lower()


async def test_digest_survives_restart_without_repeating(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a reload does not send the briefing twice."""
    entry, _, push = await _setup(
        hass,
        setup_entry,
        reminder_notify=[PUSH],
        digest_enabled=True,
        digest_time="08:00:00",
    )
    morning = dt_util.now().replace(hour=8, minute=1, second=0, microsecond=0)
    await entry.runtime_data.async_add_idea("tonnen", due=morning + timedelta(hours=2))
    await entry.runtime_data.reminders.async_check(morning)
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    await entry.runtime_data.reminders.async_check(morning + timedelta(minutes=1))
    await hass.async_block_till_done()

    assert len(push) == 1


async def test_weekly_review_only_on_its_day(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the review of long open ideas."""
    now = dt_util.now().replace(hour=18, minute=1, second=0, microsecond=0)
    entry, _, push = await _setup(
        hass,
        setup_entry,
        reminder_notify=[PUSH],
        review_enabled=True,
        review_weekday=str(now.weekday()),
        review_time="18:00:00",
        review_days=21,
    )
    store = entry.runtime_data
    await store.async_add_idea("uralte idee")
    await store.async_add_idea("neue idee")
    store._ideas[store.ideas[0]["id"]]["created_at"] = (  # noqa: SLF001
        now - timedelta(days=30)
    ).isoformat()
    old_text = store.ideas[0]["text"]

    await store.reminders.async_check(now + timedelta(days=1))
    await hass.async_block_till_done()
    assert not push

    await store.reminders.async_check(now)
    await store.reminders.async_check(now + timedelta(minutes=1))
    await hass.async_block_till_done()
    assert len(push) == 1
    assert old_text in push[0].data["message"]
    assert "1 Einträge" in push[0].data["message"]


async def test_service_sets_and_clears_due(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test due dates through the services, also from the text."""
    entry = await setup_entry()
    response = await hass.services.async_call(
        "brainstorm",
        "add_idea",
        {"text": "morgen um 8 an die tonnen", "parse_due": True},
        blocking=True,
        return_response=True,
    )
    idea = response["idea"]
    assert idea["due"]
    assert "morgen" not in idea["text"].lower()
    attributes = hass.states.get(OVERVIEW_ENTITY_ID).attributes
    assert next(i for i in attributes["ideas"] if i["id"] == idea["id"])["due"]

    await hass.services.async_call(
        "brainstorm", "update_idea", {"id": idea["id"], "due": None}, blocking=True
    )
    stored = next(i for i in entry.runtime_data.ideas if i["id"] == idea["id"])
    assert stored["due"] is None


async def test_due_date_in_todo_list(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test setting a due date in a normal to-do list."""
    entry = await setup_entry()
    idea = await entry.runtime_data.async_add_idea("tonnen", category="Alltag")
    entity_id = next(
        state.entity_id
        for state in hass.states.async_all("todo")
        if state.entity_id.endswith("alltag")
    )
    tomorrow = (dt_util.now() + timedelta(days=1)).date()

    await hass.services.async_call(
        "todo",
        "update_item",
        {"item": idea["id"], "due_date": tomorrow.isoformat()},
        target={"entity_id": entity_id},
        blocking=True,
    )

    stored = next(i for i in entry.runtime_data.ideas if i["id"] == idea["id"])
    due = dt_util.as_local(dt_util.parse_datetime(stored["due"]))
    assert due.date() == tomorrow
    assert due.hour == 9
    items = await hass.services.async_call(
        "todo",
        "get_items",
        {},
        target={"entity_id": entity_id},
        blocking=True,
        return_response=True,
    )
    assert items[entity_id]["items"][0]["due"]


async def test_new_due_date_reminds_again(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that moving an idea resets its reminder."""
    entry, _, push = await _setup(hass, setup_entry, reminder_notify=[PUSH])
    idea = await _due_idea(entry)
    store = entry.runtime_data
    await store.reminders.async_check(dt_util.now())

    await store.async_set_due(idea["id"], dt_util.now() - timedelta(seconds=5))
    await store.reminders.async_check(dt_util.now())
    await hass.async_block_till_done()

    assert len(push) == 2


async def _skill(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> tuple[Any, Any]:
    """Return an entry and a function posting to its skill webhook."""
    hass.config.language = "de"
    assert await async_setup_component(hass, "http", {})
    entry = await setup_entry(options={"voice_mode": "skill"})
    client = await hass_client_no_auth()
    url = f"/api/webhook/{entry.runtime_data.alexa_skill._webhook_id}"  # noqa: SLF001

    async def post(action: str, text: str = "") -> dict[str, Any]:
        response = await client.post(
            url, json={"application_id": SKILL_ID, "action": action, "text": text}
        )
        return await response.json()

    return entry, post


async def test_skill_reminder(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test a reminder in one sentence."""
    entry, post = await _skill(hass, setup_entry, hass_client_no_auth)

    reply = await post("remind", "morgen um 8 an die mülltonnen")

    assert reply["speech"].startswith("Okay, ich erinnere dich morgen um 8 Uhr")
    idea = entry.runtime_data.ideas[0]
    assert "morgen" not in idea["text"].lower()
    assert dt_util.as_local(dt_util.parse_datetime(idea["due"])).hour == 8


async def test_skill_reminder_without_time_saves_and_says_so(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test that a missing time is told honestly and the idea is kept."""
    entry, post = await _skill(hass, setup_entry, hass_client_no_auth)

    reply = await post("remind", "an die mülltonnen")

    assert "ohne Erinnerung" in reply["speech"]
    assert entry.runtime_data.ideas[0]["due"] is None


async def test_skill_done_and_snooze(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test completing and moving ideas by voice."""
    entry, post = await _skill(hass, setup_entry, hass_client_no_auth)
    store = entry.runtime_data
    first = await store.async_add_idea("mülltonnen rausstellen")
    second = await store.async_add_idea(
        "kuchen backen", due=dt_util.now() - timedelta(minutes=1)
    )
    assert "gefunden" in (await post("done", "ganz etwas anderes"))["speech"]

    assert "Erledigt" in (await post("done", "mülltonnen"))["speech"]
    assert store._ideas[first["id"]]["status"] == "completed"  # noqa: SLF001

    assert "keine Erinnerung" in (await post("snooze"))["speech"]
    await store.reminders.async_check(dt_util.now())
    assert "wieder" in (await post("snooze"))["speech"]
    stored = store._ideas[second["id"]]  # noqa: SLF001
    assert dt_util.parse_datetime(stored["due"]) > dt_util.now()

    await store.async_mark_reminded(second["id"], escalated=True)
    assert "Erledigt" in (await post("done"))["speech"]
    assert store._ideas[second["id"]]["status"] == "completed"  # noqa: SLF001


async def _options_step(
    hass: HomeAssistant, entry: Any, step: str, **user_input: Any
) -> dict[str, Any]:
    """Open a section of the reminder options and submit it."""
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "reminders"}
    )
    assert result["type"] is FlowResultType.MENU
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": step}
    )
    assert result["step_id"] == step
    return await hass.config_entries.options.async_configure(
        result["flow_id"], user_input
    )


async def test_options_flow_saves_and_clears(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the sections, also clearing a chosen service."""
    async_mock_service(hass, "notify", "mobile_app_phone")
    async_mock_service(hass, "notify", "alexa_media")
    entry = await setup_entry()

    await _options_step(
        hass,
        entry,
        "reminder_general",
        reminders_enabled=True,
        reminder_alexa="origin",
        notify_enabled=True,
        reminder_notify=[PUSH],
    )
    await hass.async_block_till_done()
    assert entry.options["reminder_notify"] == [PUSH]

    await _options_step(hass, entry, "reminder_general", reminder_alexa="off")
    await hass.async_block_till_done()
    assert "reminder_notify" not in entry.options
    assert entry.options["reminders_enabled"] is True

    await _options_step(
        hass, entry, "reminder_schedule", quiet_start="22:00:00", quiet_end="07:00:00"
    )
    await hass.async_block_till_done()
    assert entry.options["quiet_start"] == "22:00:00"
    assert entry.options["quiet_enabled"] is True


@pytest.mark.parametrize(
    ("step", "fields", "key"),
    [
        ("reminder_general", {"reminders_enabled": False}, "reminders_enabled"),
        ("reminder_general", {"notify_enabled": False}, "notify_enabled"),
        ("reminder_general", {"urgent_enabled": True}, "urgent_enabled"),
        ("reminder_schedule", {"quiet_enabled": False}, "quiet_enabled"),
        ("reminder_schedule", {"digest_enabled": True}, "digest_enabled"),
        ("reminder_schedule", {"review_enabled": True}, "review_enabled"),
        ("reminder_lists", {"list_rules_enabled": True}, "list_rules_enabled"),
        ("reminder_places", {"arrival_enabled": True}, "arrival_enabled"),
        ("reminder_places", {"places_enabled": True}, "places_enabled"),
        ("reminder_persons", {"persons_enabled": True}, "persons_enabled"),
        ("reminder_extras", {"calendar_enabled": True}, "calendar_enabled"),
        ("reminder_extras", {"ai_enabled": True}, "ai_enabled"),
        ("reminder_extras", {"native_reminders": True}, "native_reminders"),
    ],
)
async def test_every_feature_has_a_switch(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    step: str,
    fields: dict[str, Any],
    key: str,
) -> None:
    """Test that each feature can be switched in the settings."""
    entry = await setup_entry()
    await _options_step(hass, entry, step, **fields)
    await hass.async_block_till_done()
    assert entry.options[key] == fields[key]


async def test_translations_cover_every_option() -> None:
    """Test that no setting shows up without a label."""
    root = Path(__file__).parent.parent / "custom_components" / "brainstorm"
    english = json.loads((root / "translations" / "en.json").read_text("utf-8"))
    german = json.loads((root / "translations" / "de.json").read_text("utf-8"))
    strings = json.loads((root / "strings.json").read_text("utf-8"))
    assert set(english["options"]["step"]) == set(german["options"]["step"])
    assert english["options"]["step"] == strings["options"]["step"]
    for name, step in german["options"]["step"].items():
        assert set(step.get("data", {})) == set(
            english["options"]["step"][name].get("data", {})
        )


async def test_master_switch_stops_everything(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that nothing happens with reminders switched off."""
    entry, alexa, push = await _setup(
        hass,
        setup_entry,
        reminders_enabled=False,
        reminder_alexa="origin",
        reminder_notify=[PUSH],
    )
    events: list[Any] = []
    hass.bus.async_listen("brainstorm_reminder_due", events.append)
    await _due_idea(entry)

    await entry.runtime_data.reminders.async_check(dt_util.now())
    await hass.async_block_till_done()

    assert not alexa
    assert not push
    assert not events


async def test_notify_switch_keeps_alexa(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test switching off notifications without losing the services."""
    entry, alexa, push = await _setup(
        hass,
        setup_entry,
        notify_enabled=False,
        reminder_alexa="origin",
        reminder_notify=[PUSH],
    )
    await _due_idea(entry)

    await entry.runtime_data.reminders.async_check(dt_util.now())
    await hass.async_block_till_done()

    assert len(alexa) == 1
    assert not push


async def test_quiet_switch_ignores_times(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that switching off quiet hours keeps their times but ignores them."""
    entry, _, push = await _setup(
        hass,
        setup_entry,
        quiet_enabled=False,
        reminder_notify=[PUSH],
        quiet_start="00:00:00",
        quiet_end="23:59:00",
    )
    await _due_idea(entry)

    await entry.runtime_data.reminders.async_check(dt_util.now())
    await hass.async_block_till_done()

    assert len(push) == 1


@pytest.mark.parametrize(
    ("channel", "alexa_calls", "push_calls"),
    [("default", 1, 1), ("alexa", 1, 0), ("notify", 0, 1), ("none", 0, 0)],
)
async def test_list_rule_chooses_channel(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    channel: str,
    alexa_calls: int,
    push_calls: int,
) -> None:
    """Test a private list that only goes to the phone, and the other choices."""
    entry, alexa, push = await _setup(
        hass,
        setup_entry,
        reminder_alexa="origin",
        reminder_notify=[PUSH],
        list_rules_enabled=True,
        list_rules={"Alltag": {"channel": channel}},
    )
    await _due_idea(entry, category="Alltag")

    await entry.runtime_data.reminders.async_check(dt_util.now())
    await hass.async_block_till_done()

    assert (len(alexa), len(push)) == (alexa_calls, push_calls)


async def test_list_rules_switch_ignores_rules(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a rule stops applying when the switch is off."""
    entry, _, push = await _setup(
        hass,
        setup_entry,
        reminder_notify=[PUSH],
        list_rules_enabled=False,
        list_rules={"Alltag": {"channel": "none"}},
    )
    await _due_idea(entry, category="Alltag")

    await entry.runtime_data.reminders.async_check(dt_util.now())
    await hass.async_block_till_done()

    assert len(push) == 1


async def test_list_schedule_once_on_its_days(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test sending a list on chosen weekdays."""
    now = dt_util.now().replace(hour=8, minute=1, second=0, microsecond=0)
    entry, _, push = await _setup(
        hass,
        setup_entry,
        reminder_notify=[PUSH],
        list_rules_enabled=True,
        list_rules={
            "Alltag": {
                "channel": "notify",
                "schedule_enabled": True,
                "schedule_weekdays": [str(now.weekday())],
                "schedule_time": "08:00:00",
            }
        },
    )
    await entry.runtime_data.async_add_idea("milch kaufen", category="Alltag")
    reminders = entry.runtime_data.reminders

    await reminders.async_check(now + timedelta(days=1))
    await hass.async_block_till_done()
    assert not push

    await reminders.async_check(now)
    await reminders.async_check(now + timedelta(minutes=1))
    await hass.async_block_till_done()
    assert len(push) == 1
    assert "milch" in push[0].data["message"].lower()


async def test_urgent_stage(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Test that important open ideas reach the extra services once."""
    entry, _, push = await _setup(
        hass,
        setup_entry,
        reminder_notify=[PUSH],
        urgent_enabled=True,
        urgent_notify=["notify.pushover"],
        urgent_delay=30,
    )
    urgent_calls = async_mock_service(hass, "notify", "pushover")
    await _due_idea(entry, priority="high")
    reminders = entry.runtime_data.reminders

    await reminders.async_check(dt_util.now())
    await reminders.async_check(dt_util.now() + timedelta(minutes=10))
    await hass.async_block_till_done()
    assert not urgent_calls

    await reminders.async_check(dt_util.now() + timedelta(minutes=31))
    await reminders.async_check(dt_util.now() + timedelta(minutes=32))
    await hass.async_block_till_done()
    assert len(urgent_calls) == 1
    assert len(push) == 1


async def test_digest_waits_for_presence(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test a briefing that waits until someone is in the kitchen."""
    entry, _, push = await _setup(
        hass,
        setup_entry,
        reminder_notify=[PUSH],
        digest_enabled=True,
        digest_time="07:00:00",
        digest_presence=["binary_sensor.kuche"],
    )
    hass.states.async_set("binary_sensor.kuche", "off")
    morning = dt_util.now().replace(hour=7, minute=1, second=0, microsecond=0)
    store = entry.runtime_data
    await store.async_add_idea("tonnen", due=morning + timedelta(hours=8))

    await store.reminders.async_check(morning)
    await hass.async_block_till_done()
    assert not push

    hass.states.async_set("binary_sensor.kuche", "on")
    await store.reminders.async_check(morning + timedelta(hours=1))
    await hass.async_block_till_done()
    assert len(push) == 1

    await store.reminders.async_check(morning + timedelta(hours=2))
    await hass.async_block_till_done()
    assert len(push) == 1


def _add_person_and_zones(hass: HomeAssistant) -> None:
    """Add people and places as they look in Home Assistant."""
    hass.states.async_set("person.jan", "not_home", {"friendly_name": "Jan"})
    hass.states.async_set("person.lenja", "not_home", {"friendly_name": "Lenja"})
    hass.states.async_set("zone.home", "0", {"friendly_name": "Zuhause"})
    hass.states.async_set("zone.edeka", "0", {"friendly_name": "Edeka in Sorsum"})


@pytest.mark.parametrize(
    ("spoken", "zone", "person", "text"),
    [
        ("wenn ich heimkomme an den müll", "zone.home", "person.jan", "den müll"),
        ("an den müll wenn ich nach hause komme", "zone.home", "person.jan", "den müll"),
        ("wenn lenja heimkommt an den müll", "zone.home", "person.lenja", "den müll"),
        ("wenn ich bei edeka bin an die milch", "zone.edeka", "person.jan", "die milch"),
        ("beim edeka an die milch", "zone.edeka", "person.jan", "die milch"),
        ("wenn ich im edeka in sorsum bin an brot", "zone.edeka", "person.jan", "brot"),
    ],
)
def test_build_request_places(
    hass: HomeAssistant, spoken: str, zone: str, person: str, text: str
) -> None:
    """Test understanding places and coming home."""
    _add_person_and_zones(hass)
    options = {
        "arrival_enabled": True,
        "places_enabled": True,
        "persons_enabled": True,
        "default_person": "person.jan",
    }

    request = build_reminder_request(hass, options, spoken, NOW)

    assert request.trigger == {"zone": zone, "person": person}
    assert request.text == text
    assert request.due is None


def test_build_request_person_and_time(hass: HomeAssistant) -> None:
    """Test a reminder for someone else."""
    _add_person_and_zones(hass)
    request = build_reminder_request(
        hass, {"persons_enabled": True}, "lenja morgen um 8 an den termin", NOW
    )
    assert request.assignee == "person.lenja"
    assert request.due == _at(1, 8)
    assert request.text == "den termin"


def test_build_request_respects_switches(hass: HomeAssistant) -> None:
    """Test that nothing is understood for features that are switched off."""
    _add_person_and_zones(hass)
    request = build_reminder_request(hass, {}, "wenn ich heimkomme an den müll", NOW)
    assert request.trigger is None
    request = build_reminder_request(hass, {}, "lenja morgen um 8 an den termin", NOW)
    assert request.assignee is None
    request = build_reminder_request(hass, {}, "beim edeka an die milch", NOW)
    assert request.trigger is None


def test_build_request_with_time_keeps_place_in_text(hass: HomeAssistant) -> None:
    """Test that a set time wins and a place stays part of the sentence."""
    _add_person_and_zones(hass)
    request = build_reminder_request(
        hass,
        {"places_enabled": True},
        "morgen um 9 an den termin beim edeka",
        NOW,
    )
    assert request.trigger is None
    assert request.due == _at(1, 9)
    assert "edeka" in request.text


async def test_arrival_reminds_right_person_once(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test a reminder when coming home."""
    _add_person_and_zones(hass)
    entry, alexa, push = await _setup(
        hass,
        setup_entry,
        arrival_enabled=True,
        reminder_alexa="fixed",
        reminder_echos=["media_player.kuche"],
        reminder_notify=[PUSH],
    )
    await entry.runtime_data.async_add_idea(
        "müll rausbringen", trigger={"zone": "zone.home", "person": "person.jan"}
    )

    hass.states.async_set("person.lenja", "home", {"friendly_name": "Lenja"})
    await hass.async_block_till_done()
    assert not push

    hass.states.async_set("person.jan", "home", {"friendly_name": "Jan"})
    await hass.async_block_till_done()
    assert len(push) == 1
    assert len(alexa) == 1

    hass.states.async_set("person.jan", "not_home", {"friendly_name": "Jan"})
    hass.states.async_set("person.jan", "home", {"friendly_name": "Jan"})
    await hass.async_block_till_done()
    assert len(push) == 1


async def test_zone_reminds_on_phone_only(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that no Echo at home speaks for someone at the supermarket."""
    _add_person_and_zones(hass)
    entry, alexa, push = await _setup(
        hass,
        setup_entry,
        places_enabled=True,
        reminder_alexa="fixed",
        reminder_echos=["media_player.kuche"],
        reminder_notify=[PUSH],
    )
    await entry.runtime_data.async_add_idea(
        "milch kaufen", trigger={"zone": "zone.edeka", "person": None}
    )

    hass.states.async_set("person.jan", "Edeka in Sorsum", {"friendly_name": "Jan"})
    await hass.async_block_till_done()

    assert len(push) == 1
    assert not alexa


async def test_list_at_place_once_a_day(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the shopping list when arriving at the supermarket."""
    _add_person_and_zones(hass)
    entry, _, push = await _setup(
        hass,
        setup_entry,
        places_enabled=True,
        reminder_notify=[PUSH],
        list_rules_enabled=True,
        list_rules={
            "Alltag": {"channel": "notify", "zone_enabled": True, "zone": "zone.edeka"}
        },
    )
    await entry.runtime_data.async_add_idea("milch", category="Alltag")

    hass.states.async_set("person.jan", "Edeka in Sorsum", {"friendly_name": "Jan"})
    await hass.async_block_till_done()
    assert len(push) == 1

    hass.states.async_set("person.jan", "not_home", {"friendly_name": "Jan"})
    hass.states.async_set("person.jan", "Edeka in Sorsum", {"friendly_name": "Jan"})
    await hass.async_block_till_done()
    assert len(push) == 1


async def test_arrival_switch_off_stays_silent(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a stored place does nothing with its switch off."""
    _add_person_and_zones(hass)
    entry, _, push = await _setup(
        hass, setup_entry, arrival_enabled=False, reminder_notify=[PUSH]
    )
    await entry.runtime_data.async_add_idea(
        "müll", trigger={"zone": "zone.home", "person": None}
    )

    hass.states.async_set("person.jan", "home", {"friendly_name": "Jan"})
    await hass.async_block_till_done()

    assert not push


async def test_person_gets_own_channels(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test a reminder that goes to someone else's phone and Echo."""
    _add_person_and_zones(hass)
    entry, alexa, push = await _setup(
        hass,
        setup_entry,
        persons_enabled=True,
        reminder_notify=[PUSH],
        reminder_alexa="fixed",
        reminder_echos=["media_player.kuche"],
        person_rules={
            "person.lenja": {
                "notify": ["notify.mobile_app_lenja"],
                "echos": ["media_player.lenja"],
            }
        },
    )
    lenja_calls = async_mock_service(hass, "notify", "mobile_app_lenja")
    await _due_idea(entry, assignee="person.lenja")

    await entry.runtime_data.reminders.async_check(dt_util.now())
    await hass.async_block_till_done()

    assert len(lenja_calls) == 1
    assert not push
    assert alexa[0].data["target"] == ["media_player.lenja"]


async def test_calendar_sync_once(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Test adding a reminder to a calendar, and the switch."""
    calls = async_mock_service(hass, "calendar", "create_event")
    entry = await setup_entry(
        options={"calendar_enabled": True, "calendar_entity": "calendar.familie"}
    )
    store = entry.runtime_data
    await store.async_add_idea("arzt", due=dt_util.now() + timedelta(days=1))

    await store.reminders.async_check(dt_util.now())
    await store.reminders.async_check(dt_util.now())
    await hass.async_block_till_done()

    assert len(calls) == 1
    assert calls[0].data["summary"].lower() == "arzt"
    assert calls[0].data["entity_id"] == "calendar.familie"


async def test_calendar_switch_off(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Test that nothing goes to the calendar when switched off."""
    calls = async_mock_service(hass, "calendar", "create_event")
    entry = await setup_entry(options={"calendar_entity": "calendar.familie"})
    store = entry.runtime_data
    await store.async_add_idea("arzt", due=dt_util.now() + timedelta(days=1))

    await store.reminders.async_check(dt_util.now())
    await hass.async_block_till_done()

    assert not calls


async def test_ai_shortens_briefing_and_falls_back(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the AI summary and that a failure keeps the normal text."""
    entry, _, push = await _setup(
        hass,
        setup_entry,
        reminder_notify=[PUSH],
        digest_enabled=True,
        digest_time="08:00:00",
        ai_enabled=True,
        ai_entity="ai_task.test",
    )
    responses = [{"data": "Kurz: Tonnen."}]

    async def generate(call: ServiceCall) -> dict[str, Any]:
        if not responses:
            raise HomeAssistantError("down")
        return responses.pop()

    hass.services.async_register(
        "ai_task", "generate_data", generate, supports_response=SupportsResponse.ONLY
    )
    store = entry.runtime_data
    morning = dt_util.now().replace(hour=8, minute=1, second=0, microsecond=0)
    await store.async_add_idea("tonnen raus", due=morning + timedelta(hours=2))

    await store.reminders.async_check(morning)
    await hass.async_block_till_done()
    assert push[0].data["message"] == "Kurz: Tonnen."

    store.reminders._last_digest = None  # noqa: SLF001
    await store.reminders.async_check(morning)
    await hass.async_block_till_done()
    assert "tonnen" in push[1].data["message"].lower()


async def test_skill_person_place_and_native(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test the skill's answers for people, places and real Alexa reminders."""
    _add_person_and_zones(hass)
    hass.config.language = "de"
    assert await async_setup_component(hass, "http", {})
    entry = await setup_entry(
        options={
            "voice_mode": "skill",
            "persons_enabled": True,
            "arrival_enabled": True,
            "native_reminders": True,
        }
    )
    client = await hass_client_no_auth()
    url = f"/api/webhook/{entry.runtime_data.alexa_skill._webhook_id}"  # noqa: SLF001

    async def post(action: str, text: str = "") -> dict[str, Any]:
        response = await client.post(
            url, json={"application_id": SKILL_ID, "action": action, "text": text}
        )
        return await response.json()

    reply = await post("remind", "lenja morgen um 8 an den termin")
    assert reply["speech"].startswith("Okay, ich erinnere Lenja morgen um 8 Uhr")
    assert "alexa_reminder" not in reply

    reply = await post("remind", "wenn ich heimkomme an den müll")
    assert "beim Heimkommen" in reply["speech"]
    assert "alexa_reminder" not in reply

    reply = await post("remind", "morgen um 9 an das paket")
    idea_id = reply["alexa_reminder"]["id"]
    assert await post("native_confirm", idea_id) == {"ok": True}
    assert entry.runtime_data._ideas[idea_id]["alexa_native"] is True  # noqa: SLF001


async def test_native_reminder_is_not_spoken_twice(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that Home Assistant stays quiet when Alexa rings by itself."""
    entry, alexa, push = await _setup(
        hass, setup_entry, reminder_alexa="origin", reminder_notify=[PUSH]
    )
    idea = await _due_idea(entry)
    await entry.runtime_data.async_mark_fields(idea["id"], {"alexa_native": True})

    await entry.runtime_data.reminders.async_check(dt_util.now())
    await hass.async_block_till_done()

    assert not alexa
    assert len(push) == 1


async def test_skill_says_reminders_are_off(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test an honest answer with the master switch off."""
    hass.config.language = "de"
    assert await async_setup_component(hass, "http", {})
    entry = await setup_entry(
        options={"voice_mode": "skill", "reminders_enabled": False}
    )
    client = await hass_client_no_auth()
    url = f"/api/webhook/{entry.runtime_data.alexa_skill._webhook_id}"  # noqa: SLF001

    response = await client.post(
        url,
        json={
            "application_id": SKILL_ID,
            "action": "remind",
            "text": "morgen um 8 an die tonnen",
        },
    )

    assert "ausgeschaltet" in (await response.json())["speech"]
    assert entry.runtime_data.ideas[0]["due"] is None


async def test_service_assignee_and_zone(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test people and places through the services."""
    entry = await setup_entry()
    response = await hass.services.async_call(
        "brainstorm",
        "add_idea",
        {"text": "milch", "assignee": "person.jan", "zone": "zone.edeka"},
        blocking=True,
        return_response=True,
    )
    idea_id = response["idea"]["id"]
    stored = entry.runtime_data._ideas[idea_id]  # noqa: SLF001
    assert stored["trigger"] == {"zone": "zone.edeka", "person": "person.jan"}

    await hass.services.async_call(
        "brainstorm", "update_idea", {"id": idea_id, "zone": None}, blocking=True
    )
    assert entry.runtime_data._ideas[idea_id]["trigger"] is None  # noqa: SLF001


def test_notify_service_list_skips_alexa() -> None:
    """Test the channel list, which must not offer Alexa twice."""
    from custom_components.brainstorm.config_flow import (  # noqa: PLC0415
        BrainstormOptionsFlowHandler,
    )

    class _Services:
        def async_services(self) -> dict[str, dict[str, Any]]:
            return {
                "notify": {
                    "alexa_media": {},
                    "alexa_media_kuche": {},
                    "send_message": {},
                    "pushover": {},
                }
            }

    class _States:
        def async_entity_ids(self, domain: str) -> list[str]:
            return ["notify.entity_one"]

    handler = BrainstormOptionsFlowHandler()
    handler.hass = type("H", (), {"services": _Services(), "states": _States()})()

    assert handler._notify_service_options() == [  # noqa: SLF001
        "notify.entity_one",
        "notify.pushover",
    ]
