"""Tests for the connection to the user's own Alexa skill."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import io
import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import DATA_ENTITY_SOURCE
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util
import pytest
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from custom_components.brainstorm import alexa_display
from custom_components.brainstorm import alexa_skill
from custom_components.brainstorm.languages.de import PACK as GERMAN
from custom_components.brainstorm.alexa_skill import clean_voice_text
from custom_components.brainstorm.const import OVERVIEW_ENTITY_ID
from custom_components.brainstorm.reminders import ReminderRequest

from .conftest import SetupEntry

SKILL_ID = "amzn1.ask.skill.mine"
DEVICE_ID = "amzn1.ask.device.kitchen"
ECHO_NAME = "Echo Show Küche"
ECHO_ENTITY = "media_player.echo_show_kuche"


async def _setup_skill(
    hass: HomeAssistant, setup_entry: SetupEntry, voice_mode: str = "skill"
) -> Any:
    """Set up the integration in a voice mode."""
    assert await async_setup_component(hass, "http", {})
    return await setup_entry(options={"voice_mode": voice_mode})


async def _post(
    hass_client_no_auth: ClientSessionGenerator, entry: Any, payload: Any
) -> Any:
    """Call the secret webhook without any authentication, like the skill does."""
    client = await hass_client_no_auth()
    skill = entry.runtime_data.alexa_skill
    return await client.post(f"/api/webhook/{skill._webhook_id}", json=payload)  # noqa: SLF001


async def test_skill_stores_idea_and_answers(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test that an idea is stored and Alexa gets one answer."""
    entry = await _setup_skill(hass, setup_entry)

    response = await _post(
        hass_client_no_auth,
        entry,
        {"application_id": SKILL_ID, "text": "wir brauchen neue blumenerde"},
    )

    assert response.status == 200
    assert (await response.json())["speech"].startswith(("Saved", "Gespeichert"))
    ideas = [i for i in entry.runtime_data.ideas if i["source"] == "alexa_skill"]
    assert len(ideas) == 1
    assert entry.runtime_data.alexa_skill.is_linked
    assert entry.runtime_data.alexa_skill.last_request["text"] == ideas[0]["text"]


async def test_other_skill_is_rejected(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test that only the first skill stays linked."""
    entry = await _setup_skill(hass, setup_entry)
    await _post(hass_client_no_auth, entry, {"application_id": SKILL_ID, "text": "abc def"})

    response = await _post(
        hass_client_no_auth, entry, {"application_id": "other", "text": "boese idee"}
    )

    assert response.status == 403
    assert not [i for i in entry.runtime_data.ideas if i["text"].lower() == "boese idee"]


async def test_invalid_requests_are_rejected(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test bad payloads, which must not link a skill either."""
    entry = await _setup_skill(hass, setup_entry)

    for payload in ([], {"text": "abc"}, {"application_id": SKILL_ID}):
        response = await _post(hass_client_no_auth, entry, payload)
        assert response.status == 400
    assert not entry.runtime_data.alexa_skill.is_linked


async def test_text_is_limited_and_empty_text_fails_cleanly(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test long and useless texts."""
    entry = await _setup_skill(hass, setup_entry)

    await _post(hass_client_no_auth, entry, {"application_id": SKILL_ID, "text": "x" * 900})
    assert all(len(i["text"]) <= 500 for i in entry.runtime_data.ideas)

    count = len(entry.runtime_data.ideas)
    response = await _post(hass_client_no_auth, entry, {"application_id": SKILL_ID, "text": "  "})
    assert response.status == 200
    assert not (await response.json())["speech"].startswith(("Saved", "Gespeichert"))
    assert len(entry.runtime_data.ideas) == count


async def test_native_mode_keeps_webhook_closed(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test that the default mode accepts nothing from a skill."""
    assert await async_setup_component(hass, "http", {})
    entry = await setup_entry()
    assert hass.states.get(OVERVIEW_ENTITY_ID).attributes["voice_mode"] == "native"

    response = await _post(
        hass_client_no_auth, entry, {"application_id": SKILL_ID, "text": "abc def"}
    )

    assert await response.text() == ""
    assert not entry.runtime_data.ideas


async def test_reload_keeps_secret_and_unload_closes_webhook(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test the webhook lifecycle."""
    entry = await _setup_skill(hass, setup_entry)
    secret = entry.runtime_data.alexa_skill._webhook_id  # noqa: SLF001
    await _post(hass_client_no_auth, entry, {"application_id": SKILL_ID, "text": "abc def"})

    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    skill = entry.runtime_data.alexa_skill
    assert skill._webhook_id == secret  # noqa: SLF001
    assert skill.is_linked
    response = await _post(
        hass_client_no_auth, entry, {"application_id": "other", "text": "abc def"}
    )
    assert response.status == 403

    await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    client = await hass_client_no_auth()
    response = await client.post(f"/api/webhook/{secret}", json={})
    assert await response.text() == ""


async def test_options_flow_shows_code_and_resets(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test choosing the mode, getting the code and replacing the secret."""
    hass.config.external_url = "https://home.example.org"
    assert await async_setup_component(hass, "http", {})
    entry = await setup_entry()
    old_secret = entry.runtime_data.alexa_skill._webhook_id  # noqa: SLF001

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "alexa_skill"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"voice_mode": "both"}
    )
    assert result["step_id"] == "alexa_skill_setup"
    fields = {str(k): k for k in result["data_schema"].schema}
    code = fields["skill_code"].description["suggested_value"]
    assert f'"https://home.example.org/api/webhook/{old_secret}"' in code
    assert "CaptureIdeaIntent" in fields["interaction_model"].description["suggested_value"]

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"reset_skill": True, "skill_code": code}
    )
    assert result["type"] is FlowResultType.MENU
    await hass.async_block_till_done()

    assert entry.options["voice_mode"] == "both"
    assert "skill_code" not in entry.options
    assert entry.runtime_data.alexa_skill._webhook_id != old_secret  # noqa: SLF001
    assert hass.states.get(OVERVIEW_ENTITY_ID).attributes["voice_mode"] == "both"


async def test_options_flow_without_public_url(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a missing public address is explained instead of failing."""
    assert await async_setup_component(hass, "http", {})
    entry = await setup_entry()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "alexa_skill"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"voice_mode": "skill"}
    )

    assert result["errors"] == {"base": "no_public_url"}
    assert "skill_code" not in {str(k) for k in result["data_schema"].schema}


async def _open_skill_setup(hass: HomeAssistant, entry: Any) -> dict[str, Any]:
    """Open the setup step of the options flow."""
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "alexa_skill"}
    )
    return await hass.config_entries.options.async_configure(
        result["flow_id"], {"voice_mode": "skill"}
    )


async def test_options_flow_uses_home_assistant_cloud_address(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a Home Assistant Cloud address is enough for the skill."""
    assert await async_setup_component(hass, "http", {})
    entry = await setup_entry()

    with patch(
        "homeassistant.helpers.network._get_cloud_url",
        return_value="https://abc.ui.nabu.casa",
    ):
        result = await _open_skill_setup(hass, entry)

    assert not result["errors"]
    secret = entry.runtime_data.alexa_skill._webhook_id  # noqa: SLF001
    fields = {str(k): k for k in result["data_schema"].schema}
    code = fields["skill_code"].description["suggested_value"]
    assert f'"https://abc.ui.nabu.casa/api/webhook/{secret}"' in code


async def test_options_flow_rejects_unencrypted_address(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that the secret address is never offered without HTTPS."""
    hass.config.external_url = "http://home.example.org"
    assert await async_setup_component(hass, "http", {})
    entry = await setup_entry()

    result = await _open_skill_setup(hass, entry)

    assert result["errors"] == {"base": "no_public_url"}


def _run_skill_code(
    reply: bytes | Exception,
    request_data: dict[str, Any] | None = None,
    interfaces: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], list[Any]]:
    """Run the generated skill code like Alexa would, with a fake network."""
    from custom_components.brainstorm.alexa_skill import SKILL_CODE_TEMPLATE  # noqa: PLC0415

    namespace: dict[str, Any] = {}
    code = SKILL_CODE_TEMPLATE.replace("__WEBHOOK_URL__", "https://home.example.org/x")
    exec(code, namespace)  # noqa: S102
    requests: list[Any] = []

    def fake_urlopen(request: Any, timeout: int) -> Any:
        requests.append(request)
        if isinstance(reply, Exception):
            raise reply
        return io.BytesIO(reply)

    event = {
        "context": {
            "System": {
                "application": {"applicationId": SKILL_ID},
                "device": {
                    "deviceId": DEVICE_ID,
                    "supportedInterfaces": interfaces or {},
                },
            }
        },
        "request": {"locale": "de-DE"}
        | (
            request_data
            or {
                "type": "IntentRequest",
                "intent": {
                    "name": "CaptureIdeaIntent",
                    "slots": {"text": {"value": "kellerlicht dimmen"}},
                },
            }
        ),
    }
    with patch("urllib.request.urlopen", fake_urlopen):
        return namespace["lambda_handler"](event, None), requests


@pytest.mark.parametrize(
    ("intent", "key"),
    [("AMAZON.FallbackIntent", "skill_fallback"), ("AMAZON.HelpIntent", "skill_help")],
)
def test_skill_code_explains_unknown_sentences(intent: str, key: str) -> None:
    """Test that a sentence Alexa could not place asks for a command word."""
    result, requests = _run_skill_code(
        b"", {"type": "IntentRequest", "intent": {"name": intent}}
    )

    assert requests == []
    assert result["response"]["outputSpeech"]["text"] == GERMAN.messages[key]
    assert result["response"]["shouldEndSession"] is False


def test_skill_model_has_natural_sentences() -> None:
    """Test that the model takes sentences people say without a command word."""
    model = GERMAN.skill_model["interactionModel"]["languageModel"]
    samples = {
        intent["name"]: intent["samples"] for intent in model["intents"]
    }
    for sample in ("wir brauchen {text}", "nokia {text}", "dass {text}"):
        assert sample in samples["CaptureIdeaIntent"]
    assert "zeige mir die liste {category}" in samples["ShowIdeasIntent"]
    assert "erinnere mich am {text}" in samples["ReminderIntent"]
    every = [s for intent in samples.values() for s in intent]
    assert len(every) == len(set(every))


def test_skill_code_speaks_answer_from_home_assistant() -> None:
    """Test that the generated code forwards the text and speaks the reply."""
    result, requests = _run_skill_code(b'{"speech": "Gespeichert."}')

    assert result["response"]["outputSpeech"]["text"] == "Gespeichert."
    assert json.loads(requests[0].data) == _capture_payload(
        display=False, locale="de-DE"
    )


@pytest.mark.parametrize(
    ("spoken", "expected"),
    [
        ("kellerlicht dimmen", "kellerlicht dimmen"),
        # The category parser needs the preposition to see a list name
        ("für den garten tomaten düngen", "für den garten tomaten düngen"),
        ("testidee zwei auf meine to do liste", "testidee zwei"),
        ("ein buch auf die liste", "ein buch"),
        ("erinnere mich an den müll", "den müll"),
        ("neue idee kaffee kochen", "kaffee kochen"),
    ],
)
def test_clean_voice_text(spoken: str, expected: str) -> None:
    """Test that spoken text is cleaned like in the native capture."""
    assert clean_voice_text(spoken, GERMAN) == expected


def _add_echo(hass: HomeAssistant, entity_id: str = ECHO_ENTITY, name: str = ECHO_NAME) -> None:
    """Add a media player that looks like one from Alexa Media."""
    hass.states.async_set(entity_id, "idle", {"friendly_name": name})
    hass.data.setdefault(DATA_ENTITY_SOURCE, {})[entity_id] = {
        "domain": "alexa_media",
        "custom_component": True,
    }


def _alexa_event(hass: HomeAssistant, summary: str, name: str = ECHO_NAME) -> None:
    """Fire the event Alexa Media sends for a spoken sentence."""
    hass.bus.async_fire(
        "alexa_media_last_called_event", {"name": name, "summary": summary}
    )


def _capture_payload(text: str = "kellerlicht dimmen", **extra: Any) -> dict[str, Any]:
    """Return what the skill sends for a spoken idea."""
    return {
        "application_id": SKILL_ID,
        "device_id": DEVICE_ID,
        "text": text,
        "action": "capture",
    } | extra


async def test_echo_known_before_idea_is_stored(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test that the first request waits for the Echo and later ones do not."""
    entry = await _setup_skill(hass, setup_entry)
    _add_echo(hass)
    client = await hass_client_no_auth()
    url = f"/api/webhook/{entry.runtime_data.alexa_skill._webhook_id}"  # noqa: SLF001

    request = asyncio.create_task(client.post(url, json=_capture_payload()))
    await asyncio.sleep(0.05)
    assert not entry.runtime_data.ideas
    _alexa_event(hass, "sage brainstorm notiere kellerlicht dimmen")
    assert (await request).status == 200
    assert entry.runtime_data.ideas[0]["device"] == ECHO_NAME

    # Now known: answers at once, even though Alexa has not reported anything
    with patch.object(alexa_skill, "DEVICE_WAIT_SECONDS", 0):
        await client.post(url, json=_capture_payload("rosen schneiden"))
    await hass.async_block_till_done()
    rosen = [i for i in entry.runtime_data.ideas if "rosen" in i["text"].lower()]
    assert rosen[0]["device"] == ECHO_NAME


async def test_alexa_event_before_request_is_used(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test that the history entry may arrive before the skill's request."""
    entry = await _setup_skill(hass, setup_entry)
    _add_echo(hass)
    _alexa_event(hass, "sage brainstorm notiere kellerlicht dimmen")

    with patch.object(alexa_skill, "DEVICE_WAIT_SECONDS", 0):
        await _post(hass_client_no_auth, entry, _capture_payload())

    assert entry.runtime_data.ideas[0]["device"] == ECHO_NAME


async def test_late_echo_is_added_and_idea_never_lost(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test that a slow Alexa history saves the idea and fills in the Echo later."""
    entry = await _setup_skill(hass, setup_entry)
    _add_echo(hass)

    with patch.object(alexa_skill, "DEVICE_WAIT_SECONDS", 0):
        response = await _post(hass_client_no_auth, entry, _capture_payload())
    assert (await response.json())["speech"]
    assert not entry.runtime_data.ideas[0].get("device")

    _alexa_event(hass, "sage brainstorm notiere kellerlicht dimmen")
    await hass.async_block_till_done()
    assert entry.runtime_data.ideas[0]["device"] == ECHO_NAME
    assert entry.runtime_data.alexa_skill._devices[DEVICE_ID]["entity_id"] == ECHO_ENTITY  # noqa: SLF001


async def test_unrelated_sentence_is_not_learned(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test that another person's sentence cannot set the wrong Echo."""
    entry = await _setup_skill(hass, setup_entry)
    _add_echo(hass)

    with patch.object(alexa_skill, "DEVICE_WAIT_SECONDS", 0):
        await _post(hass_client_no_auth, entry, _capture_payload())
    _alexa_event(hass, "licht aus", name="Anderer Echo")
    _alexa_event(hass, "sage brainstorm notiere etwas anderes", name="Anderer Echo")
    await hass.async_block_till_done()

    assert not entry.runtime_data.ideas[0].get("device")
    assert not entry.runtime_data.alexa_skill._devices  # noqa: SLF001


async def test_echo_selection_applies_to_skill(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test that an Echo outside the selection is ignored silently."""
    assert await async_setup_component(hass, "http", {})
    entry = await setup_entry(
        options={"voice_mode": "skill", "allowed_echos": ["media_player.other"]}
    )
    _add_echo(hass)
    _alexa_event(hass, "sage brainstorm notiere kellerlicht dimmen")

    response = await _post(hass_client_no_auth, entry, _capture_payload())

    assert await response.json() == {"silent": True}
    assert not entry.runtime_data.ideas


async def test_read_ideas_and_menu(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test the spoken announcement and the main menu of the native flow."""
    entry = await _setup_skill(hass, setup_entry)
    await entry.runtime_data.async_add_idea("rosen schneiden", category="Alltag")
    await entry.runtime_data.async_add_idea("licht dimmen", category="Projekte")

    response = await _post(
        hass_client_no_auth,
        entry,
        {"application_id": SKILL_ID, "action": "read", "text": "alltag"},
    )
    speech = (await response.json())["speech"]
    assert "Alltag" in speech
    assert "Projekte" not in speech

    response = await _post(
        hass_client_no_auth, entry, {"application_id": SKILL_ID, "action": "read"}
    )
    overview = await response.json()
    assert overview["speech"].startswith("Du hast 2 Einträge")
    assert "rosen" not in overview["speech"].lower()
    assert overview["end_session"] is False

    response = await _post(
        hass_client_no_auth, entry, {"application_id": SKILL_ID, "action": "read_all"}
    )
    assert "Projekte" in (await response.json())["speech"]

    response = await _post(
        hass_client_no_auth, entry, {"application_id": SKILL_ID, "action": "launch"}
    )
    assert (await response.json())["end_session"] is False


async def test_unknown_action_is_rejected(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test that the webhook only does what the skill may ask for."""
    entry = await _setup_skill(hass, setup_entry)

    response = await _post(
        hass_client_no_auth,
        entry,
        {"application_id": SKILL_ID, "action": "delete", "text": "x"},
    )

    assert response.status == 400
    assert not entry.runtime_data.alexa_skill.is_linked


async def test_alexa_app_can_be_named(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test giving the Alexa app, which Alexa Media never reports, its own name."""
    hass.config.external_url = "https://home.example.org"
    entry = await _setup_skill(hass, setup_entry)

    with patch.object(alexa_skill, "DEVICE_WAIT_SECONDS", 0):
        await _post(hass_client_no_auth, entry, _capture_payload("erste idee"))
    assert entry.runtime_data.alexa_skill.last_unknown_device["device_id"] == DEVICE_ID

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "alexa_skill"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"voice_mode": "skill"}
    )
    assert "device_name" in {str(k) for k in result["data_schema"].schema}
    await hass.config_entries.options.async_configure(
        result["flow_id"], {"device_name": "Alexa App iPhone"}
    )
    await hass.async_block_till_done()

    store = entry.runtime_data
    assert store.ideas[0]["device"] == "Alexa App iPhone"
    assert store.alexa_skill.last_unknown_device is None

    # Known at once from now on, and a matching history entry cannot replace it
    await _post(hass_client_no_auth, entry, _capture_payload("zweite idee"))
    _alexa_event(hass, "sage brainstorm notiere zweite idee", name="Anderer Echo")
    await hass.async_block_till_done()
    assert all(i["device"] == "Alexa App iPhone" for i in store.ideas)
    assert store.alexa_skill.last_request["device"] == "Alexa App iPhone"


async def test_late_echo_clears_unknown_device(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test that an Echo reported late is not offered for naming."""
    entry = await _setup_skill(hass, setup_entry)
    _add_echo(hass)

    with patch.object(alexa_skill, "DEVICE_WAIT_SECONDS", 0):
        await _post(hass_client_no_auth, entry, _capture_payload())
    _alexa_event(hass, "sage brainstorm notiere kellerlicht dimmen")
    await hass.async_block_till_done()

    assert entry.runtime_data.alexa_skill.last_unknown_device is None


def test_voice_model_matches_skill_code() -> None:
    """Test that the skill handles every custom intent of the voice model."""
    model = GERMAN.skill_model["interactionModel"]["languageModel"]
    assert model["invocationName"] == "brainstorm"
    for intent in model["intents"]:
        if not intent["name"].startswith("AMAZON."):
            assert intent["name"] in alexa_skill.SKILL_CODE_TEMPLATE
            for sample in intent["samples"]:
                # Amazon requires words next to a free text slot
                assert sample.replace("{text}", "").replace("{category}", "").strip()


def test_skill_code_never_claims_success_on_failure() -> None:
    """Test the answers when Home Assistant is down or the mode is off."""
    down, _ = _run_skill_code(TimeoutError())
    assert "nichts gespeichert" in down["response"]["outputSpeech"]["text"]

    # Home Assistant answers an unknown webhook with an empty 200
    closed, _ = _run_skill_code(b"")
    assert "nichts gespeichert" in closed["response"]["outputSpeech"]["text"]

    # An Echo outside the selection stays silent, like in the native capture
    silent, _ = _run_skill_code(b'{"silent": true}')
    assert "outputSpeech" not in silent["response"]


async def test_skill_refuses_a_broken_request(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test a request whose body is no JSON at all."""
    entry = await _setup_skill(hass, setup_entry)
    client = await hass_client_no_auth()
    skill = entry.runtime_data.alexa_skill
    response = await client.post(
        f"/api/webhook/{skill._webhook_id}",  # noqa: SLF001
        data="kein json",
    )
    assert response.status == 400


async def test_skill_says_when_an_idea_cannot_be_stored(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test that a failed save is spoken, so that nobody relies on the idea."""
    hass.config.language = "en"
    entry = await _setup_skill(hass, setup_entry)
    with patch.object(
        type(entry.runtime_data),
        "async_add_idea",
        side_effect=HomeAssistantError("voll"),
    ):
        response = await _post(
            hass_client_no_auth,
            entry,
            {"application_id": SKILL_ID, "text": "wir brauchen neue blumenerde"},
        )
    assert (await response.json())["speech"] == "I could not save that."


async def test_skill_refuses_a_reminder_in_the_past(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test a spoken time that has already passed."""
    hass.config.language = "en"
    entry = await _setup_skill(hass, setup_entry)
    past = dt_util.now() - timedelta(hours=1)
    request = ReminderRequest(text="Regal bauen", due=past)
    with patch(
        "custom_components.brainstorm.alexa_skill.build_reminder_request",
        return_value=request,
    ):
        response = await _post(
            hass_client_no_auth,
            entry,
            {"application_id": SKILL_ID, "action": "remind", "text": "regal bauen"},
        )
    assert (await response.json())["speech"] == "That time is in the past."
    assert entry.runtime_data.ideas == []


APL = {"Alexa.Presentation.APL": {"runtime": {"maxVersion": "2024.3"}}}
SHOW_REQUEST = {
    "type": "IntentRequest",
    "intent": {"name": "ShowIdeasIntent", "slots": {"category": {"value": "alltag"}}},
}


def _pages(answer: dict[str, Any]) -> dict[str, Any]:
    """Return the data of the screen in a webhook answer."""
    assert answer["directives"][0]["type"] == "Alexa.Presentation.APL.RenderDocument"
    return answer["directives"][0]["datasources"][alexa_display.DATA_NAME]


async def test_lists_are_only_sent_to_a_screen(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test that older skill code and Echos without a screen get voice only."""
    entry = await _setup_skill(hass, setup_entry)
    await entry.runtime_data.async_add_idea("rosen schneiden", category="Alltag")

    for action in ("read", "read_all", "show", "launch"):
        response = await _post(
            hass_client_no_auth,
            entry,
            {"application_id": SKILL_ID, "action": action, "text": "alltag"},
        )
        answer = await response.json()
        assert "directives" not in answer
        assert answer["speech"]

        response = await _post(
            hass_client_no_auth,
            entry,
            {
                "application_id": SKILL_ID,
                "action": action,
                "text": "alltag",
                "display": True,
            },
        )
        assert _pages(await response.json())["pages"][0]["category"] == "Alltag"


async def test_lists_have_a_page_per_category_and_start_on_the_spoken_one(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test the pages, subtasks, and text that would break the screen's markup."""
    hass.config.language = "de"
    entry = await _setup_skill(hass, setup_entry)
    store = entry.runtime_data
    parent = await store.async_add_idea("garage <aufräumen> & mehr", category="Alltag")
    await store.async_add_idea("regal bauen", category="Alltag", parent_id=parent["id"])
    await store.async_add_idea("licht dimmen", category="Projekte")

    response = await _post(
        hass_client_no_auth,
        entry,
        {
            "application_id": SKILL_ID,
            "action": "show",
            "text": "projekte",
            "display": True,
        },
    )
    answer = await response.json()
    payload = _pages(answer)

    assert answer["speech"] == "Hier ist Projekte."
    names = [page["category"] for page in payload["pages"]]
    assert sorted(names) == ["Alltag", "Projekte"]
    assert payload["start"] == names.index("Projekte")
    rows = payload["pages"][names.index("Alltag")]["items"]
    assert [row["subtask"] for row in rows] == [False, True]
    assert rows[0]["text"] == "Garage &lt;aufräumen&gt; &amp; mehr"


async def test_touch_completes_an_idea_and_keeps_the_page(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test touching an idea, also twice, and an idea that is gone."""
    hass.config.language = "de"
    entry = await _setup_skill(hass, setup_entry)
    store = entry.runtime_data
    idea = await store.async_add_idea("rosen schneiden", category="Alltag")
    await store.async_add_idea("kompost", category="Alltag")
    await store.async_add_idea("licht dimmen", category="Projekte")

    payload = {
        "application_id": SKILL_ID,
        "action": "display_done",
        "text": idea["id"],
        "display": True,
    }
    for _ in range(2):
        answer = await (await _post(hass_client_no_auth, entry, payload)).json()
        assert answer["speech"].startswith("Erledigt")
        pages = _pages(answer)
        assert pages["pages"][pages["start"]]["category"] == "Alltag"
        assert "rosen" not in str(pages)
    assert store.get_idea(idea["id"])["status"] == "completed"

    payload["text"] = "gibtsnicht"
    answer = await (await _post(hass_client_no_auth, entry, payload)).json()
    assert "nicht gefunden" in answer["speech"]


async def test_screen_says_when_everything_is_done(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test the screen without any open ideas."""
    entry = await _setup_skill(hass, setup_entry)
    response = await _post(
        hass_client_no_auth,
        entry,
        {"application_id": SKILL_ID, "action": "show", "display": True},
    )
    payload = _pages(await response.json())
    assert payload["start"] == 0
    assert payload["pages"][0]["items"] == []
    assert payload["pages"][0]["hint"]


async def test_screen_and_touch_respect_private_ideas(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test that an Echo shows and completes only the ideas of its person."""
    hass.config.language = "de"
    assert await async_setup_component(hass, "http", {})
    entry = await setup_entry(
        options={
            "voice_mode": "skill",
            "privacy_enabled": True,
            "privacy_owner": "owner-id",
        }
    )
    store = entry.runtime_data
    mine = await store.async_add_idea("meine idee", owner="owner-id")
    foreign = await store.async_add_idea("fremde idee", owner="other-id")

    response = await _post(
        hass_client_no_auth,
        entry,
        {"application_id": SKILL_ID, "action": "show", "display": True},
    )
    shown = str(_pages(await response.json())).lower()
    assert "meine idee" in shown
    assert "fremde idee" not in shown

    response = await _post(
        hass_client_no_auth,
        entry,
        {
            "application_id": SKILL_ID,
            "action": "display_done",
            "text": foreign["id"],
            "display": True,
        },
    )
    assert "nicht gefunden" in (await response.json())["speech"]
    assert store.get_idea(foreign["id"])["status"] == "active"
    assert store.get_idea(mine["id"])["status"] == "active"


def test_document_receives_its_data() -> None:
    """Test what a real Echo Show showed empty: no page data and a wrong page count."""
    directive = alexa_display.build_directive(
        [
            {"id": "a", "text": "eins", "category": "Alltag"},
            {"id": "b", "text": "zwei", "category": "Projekte"},
        ],
        ["Alltag", "Projekte"],
        {},
        None,
        GERMAN,
    )
    parameters = directive["document"]["mainTemplate"]["parameters"]
    document = json.dumps(directive["document"])

    assert "payload" not in parameters
    assert set(parameters) == set(directive["datasources"])
    # These count the neighbours of a nested component, not the pages
    assert "${index" not in document
    assert "${length" not in document
    pages = directive["datasources"][alexa_display.DATA_NAME]["pages"]
    on, off = alexa_display.TEXT_COLOR, alexa_display.INACTIVE_DOT_COLOR
    assert [page["dots"] for page in pages] == [[on, off], [off, on]]
    # Two categories without a chosen color do not look the same
    assert pages[0]["color"] != pages[1]["color"]


def test_tile_labels_priority_due_date_and_parent() -> None:
    """Test the labels below an idea, and an overdue date in red."""
    now = dt_util.now()
    ideas = [
        {
            "id": "a",
            "text": "eltern",
            "category": "Alltag",
            "priority": "urgent",
            "due": (now - timedelta(hours=3)).isoformat(),
        },
        {
            "id": "b",
            "text": "kind",
            "category": "Alltag",
            "priority": "medium",
            "parent_id": "a",
            "due": (now + timedelta(days=1)).isoformat(),
        },
        {"id": "c", "text": "ohne", "category": "Alltag", "due": "kein datum"},
    ]
    directive = alexa_display.build_directive(ideas, ["Alltag"], {}, None, GERMAN)
    page = directive["datasources"][alexa_display.DATA_NAME]["pages"][0]
    parent, child, plain = page["items"]

    assert page["subtitle"] == "3 offen · 1 dringend"
    assert parent["chips"][0]["color"] == alexa_display.OVERDUE_COLOR
    assert parent["chips"][1]["text"] == "Dringend"
    assert parent["accent"] == alexa_display.PRIORITY_COLORS["urgent"]
    assert child["chips"][0]["text"].startswith("Morgen")
    assert child["chips"][-1]["text"] == "↳ eltern"
    assert plain["chips"] == []


def test_short_colors_can_be_tinted() -> None:
    """Test that every color from the settings still gives a valid tint."""
    ideas = [{"id": "a", "text": "b", "category": "Alltag"}]
    for color in ("#abc", "#aabbcc", "#aabbccdd"):
        directive = alexa_display.build_directive(
            ideas, ["Alltag"], {"Alltag": color}, None, GERMAN
        )
        page = directive["datasources"][alexa_display.DATA_NAME]["pages"][0]
        assert page["color"] == "#aabbcc"
        assert page["tint"] == "#aabbcc33"


def test_logo_address_points_to_a_file_of_this_repository() -> None:
    """Test that moving the logo cannot leave the screen without it."""
    prefix = "https://raw.githubusercontent.com/nukleuz80/ha_brainstorm/main/"
    assert alexa_display.LOGO_URL.startswith(prefix)
    path = alexa_display.LOGO_URL.removeprefix(prefix)
    assert (Path(__file__).parent.parent / path).is_file()
    assert alexa_display.LOGO_URL in json.dumps(alexa_display.DOCUMENT)


def test_screen_limits_keep_the_answer_small() -> None:
    """Test that many long ideas stay well below Alexa's limit of 120 KB."""
    ideas = [
        {"id": f"{index:08x}", "text": "x" * 500, "category": "Alltag"}
        for index in range(500)
    ]
    directive = alexa_display.build_directive(ideas, ["Alltag"], {}, None, GERMAN)

    page = directive["datasources"][alexa_display.DATA_NAME]["pages"][0]
    assert len(page["items"]) == alexa_display.MAX_DISPLAY_ITEMS
    assert page["hint"] == "+ 350 weitere"
    assert len(json.dumps(directive).encode()) < 60_000


def test_screen_ignores_a_broken_color() -> None:
    """Test that a color from the settings cannot break the document."""
    ideas = [{"id": "a", "text": "b", "category": "Alltag"}]
    for color, expected in (
        ("#123456", "#123456"),
        ("${viewport}", alexa_display.DEFAULT_COLOR),
    ):
        directive = alexa_display.build_directive(
            ideas, ["Alltag"], {"Alltag": color}, None, GERMAN
        )
        assert directive["datasources"][alexa_display.DATA_NAME]["pages"][0]["color"] == expected


def test_skill_code_passes_the_screen_on() -> None:
    """Test that the session stays open with a closed microphone below the lists."""
    directive = {"type": "Alexa.Presentation.APL.RenderDocument"}
    reply = json.dumps(
        {"speech": "Hier.", "end_session": True, "directives": [directive]}
    ).encode()

    answer, requests = _run_skill_code(reply, SHOW_REQUEST, APL)

    assert answer["response"]["directives"] == [directive]
    assert "shouldEndSession" not in answer["response"]
    sent = json.loads(requests[0].data)
    assert (sent["action"], sent["text"], sent["display"]) == ("show", "alltag", True)

    reply = json.dumps(
        {"speech": "Welche?", "end_session": False, "directives": [directive]}
    ).encode()
    answer, _ = _run_skill_code(reply, SHOW_REQUEST, APL)
    assert answer["response"]["shouldEndSession"] is False


def test_skill_code_reports_no_screen_without_the_interface() -> None:
    """Test Echos without a screen, and skills without APL switched on."""
    answer, requests = _run_skill_code(b'{"speech": "Hier."}', SHOW_REQUEST)

    assert json.loads(requests[0].data)["display"] is False
    assert answer["response"]["shouldEndSession"] is True


def test_skill_code_handles_touch_and_screen_errors() -> None:
    """Test touch events, and that a broken screen stays silent."""
    touch = {
        "type": "Alexa.Presentation.APL.UserEvent",
        "arguments": ["done", "abc12345"],
    }
    _, requests = _run_skill_code(b'{"speech": "Erledigt."}', touch, APL)
    sent = json.loads(requests[0].data)
    assert (sent["action"], sent["text"]) == ("display_done", "abc12345")

    for request_data in (
        {"type": "Alexa.Presentation.APL.UserEvent", "arguments": ["other"]},
        {"type": "Alexa.Presentation.APL.RuntimeError", "errors": [{"type": "x"}]},
    ):
        answer, requests = _run_skill_code(b"{}", request_data, APL)
        assert requests == []
        assert answer["response"] == {}


async def test_skill_says_a_date_it_found(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test that a date from the sentence is announced, since it leads to a reminder."""
    hass.config.language = "de"
    entry = await _setup_skill(hass, setup_entry)

    response = await _post(
        hass_client_no_auth,
        entry,
        {"application_id": SKILL_ID, "text": "morgen um 10 uhr den arzt anrufen"},
    )

    assert "Termin morgen um 10 Uhr" in (await response.json())["speech"]
    idea = entry.runtime_data.ideas[0]
    assert idea["text"] == "Arzt anrufen"
    assert idea["due"] is not None
