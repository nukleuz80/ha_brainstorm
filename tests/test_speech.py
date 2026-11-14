"""Tests for freely spoken text that the AI splits into notes."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.brainstorm.ai import MAX_SPEECH_TASKS, parse_speech_tasks

from .conftest import SetupEntry

AI_OPTIONS = {"ai_entity": "ai_task.test"}


def _register_ai(hass: HomeAssistant, answer: Any) -> list[ServiceCall]:
    """Let the AI give a fixed answer and return the calls it got."""
    calls: list[ServiceCall] = []

    async def generate(call: ServiceCall) -> ServiceResponse:
        calls.append(call)
        return {"data": answer}

    hass.services.async_register(
        "ai_task", "generate_data", generate, supports_response=SupportsResponse.ONLY
    )
    return calls


def _people(hass: HomeAssistant) -> None:
    hass.states.async_set("person.anna", "home", {"friendly_name": "Anna Muster"})
    hass.states.async_set("person.ben", "home", {"friendly_name": "Ben"})


def test_parser_reads_task_due_and_person() -> None:
    """Lines with task, due date and person are read, headings and repeats go."""
    answer = (
        "```\n"
        "Aufgabe | Termin | Person\n"
        "1. Klempner anrufen | 2026-11-16 10:00 | Anna\n"
        "- **Milch kaufen** | 2026-11-20 | -\n"
        "Rasen mähen\n"
        "milch kaufen | - | Ben\n"
        "```"
    )
    assert parse_speech_tasks(answer) == [
        {"text": "Klempner anrufen", "due": "2026-11-16 10:00", "person": "Anna"},
        {"text": "Milch kaufen", "due": "2026-11-20", "person": None},
        {"text": "Rasen mähen", "due": None, "person": None},
    ]
    many = "\n".join(f"Aufgabe {n} | - | -" for n in range(30))
    assert len(parse_speech_tasks(many)) == MAX_SPEECH_TASKS
    assert parse_speech_tasks(None) == []


async def test_ai_splits_with_due_and_person(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """The AI gets today and the people; names become person entities."""
    _people(hass)
    calls = _register_ai(
        hass,
        "Klempner anrufen | 2026-11-16 10:00 | Anna\n"
        "Milch kaufen | 2026-11-20 | Ben\n"
        "Fenster putzen | - | Fremder",
    )
    entry = await setup_entry(options=AI_OPTIONS)
    store = entry.runtime_data
    result = await store.async_split_speech(
        "Anna ruft Montag um zehn den Klempner an, Ben kauft Freitag Milch", "de"
    )
    assert result["ai"] is True
    tasks = result["tasks"]
    assert [t["text"] for t in tasks] == ["Klempner anrufen", "Milch kaufen", "Fenster putzen"]
    assert [t["assignee"] for t in tasks] == ["person.anna", "person.ben", None]
    assert dt_util.parse_datetime(tasks[0]["due"]).hour == 10
    assert dt_util.parse_datetime(tasks[1]["due"]).hour == 9
    assert tasks[2]["due"] is None
    instructions = calls[0].data["instructions"]
    assert "Anna Muster" in instructions and "Ben" in instructions
    assert dt_util.now().strftime("%Y-%m-%d") in instructions
    # Nothing is stored before the person checks the list
    assert store.ideas == []


async def test_without_ai_sentences_are_read_like_reminders(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Without an AI each sentence becomes a task with its spoken due date."""
    _people(hass)
    entry = await setup_entry(options={"persons_enabled": True})
    store = entry.runtime_data
    result = await store.async_split_speech(
        "Anna morgen um 10 Uhr Klempner anrufen. Dann Milch kaufen", "de"
    )
    assert result["ai"] is False
    first, second = result["tasks"]
    assert first["assignee"] == "person.anna"
    due = dt_util.parse_datetime(first["due"])
    assert (due.date(), due.hour) == ((dt_util.now() + timedelta(days=1)).date(), 10)
    assert "Klempner anrufen" in first["text"]
    assert second == {"text": "Milch kaufen", "due": None, "assignee": None}


async def test_ai_without_answer_falls_back(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """An empty AI answer still splits the text sentence by sentence."""
    _register_ai(hass, "")
    entry = await setup_entry(options=AI_OPTIONS)
    result = await entry.runtime_data.async_split_speech("Brot backen; Auto waschen", "de")
    assert result["ai"] is False
    assert [t["text"] for t in result["tasks"]] == ["Brot backen", "Auto waschen"]


async def test_service_creates_the_notes(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """The action creates every task with due date and person at once."""
    _people(hass)
    _register_ai(hass, "Klempner anrufen | 2026-11-16 10:00 | Anna\nMilch kaufen | - | -")
    entry = await setup_entry(options=AI_OPTIONS)
    response = await hass.services.async_call(
        "brainstorm",
        "add_from_speech",
        {"text": "Anna ruft den Klempner an und Milch kaufen", "category": "Projekte"},
        blocking=True,
        return_response=True,
    )
    assert response["ai"] is True
    ideas = {i["text"]: i for i in entry.runtime_data.ideas}
    assert set(ideas) == {"Klempner anrufen", "Milch kaufen"}
    assert ideas["Klempner anrufen"]["assignee"] == "person.anna"
    assert ideas["Klempner anrufen"]["due"].startswith("2026-11-16T10:00")
    assert ideas["Milch kaufen"]["category"] == "Projekte"


async def test_websocket_returns_the_preview(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_ws_client: WebSocketGenerator,
) -> None:
    """The card gets the tasks to check before anything is stored."""
    _register_ai(hass, "Klempner anrufen | - | -")
    entry = await setup_entry(options=AI_OPTIONS)
    client = await hass_ws_client(hass)
    await client.send_json_auto_id(
        {"type": "brainstorm/split_speech", "text": "Klempner anrufen", "language": "de"}
    )
    msg = await client.receive_json()
    assert msg["success"]
    assert msg["result"] == {
        "ai": True,
        "tasks": [{"text": "Klempner anrufen", "due": None, "assignee": None}],
    }
    assert entry.runtime_data.ideas == []
