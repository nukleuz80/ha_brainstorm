"""Tests for the connection to the user's own Alexa skill."""
from __future__ import annotations

import io
import json
from typing import Any
from unittest.mock import patch

from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from custom_components.brainstorm.const import OVERVIEW_ENTITY_ID

from .conftest import SetupEntry

SKILL_ID = "amzn1.ask.skill.mine"


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
    assert result["type"] is FlowResultType.CREATE_ENTRY
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


def _run_skill_code(reply: bytes | Exception) -> tuple[dict[str, Any], list[Any]]:
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
        "context": {"System": {"application": {"applicationId": SKILL_ID}}},
        "request": {
            "type": "IntentRequest",
            "intent": {
                "name": "CaptureIdeaIntent",
                "slots": {"text": {"value": "kellerlicht dimmen"}},
            },
        },
    }
    with patch("urllib.request.urlopen", fake_urlopen):
        return namespace["lambda_handler"](event, None), requests


def test_skill_code_speaks_answer_from_home_assistant() -> None:
    """Test that the generated code forwards the text and speaks the reply."""
    result, requests = _run_skill_code(b'{"speech": "Gespeichert."}')

    assert result["response"]["outputSpeech"]["text"] == "Gespeichert."
    assert json.loads(requests[0].data) == {
        "application_id": SKILL_ID,
        "text": "kellerlicht dimmen",
    }


def test_skill_code_never_claims_success_on_failure() -> None:
    """Test the answers when Home Assistant is down or the mode is off."""
    down, _ = _run_skill_code(TimeoutError())
    assert "nicht gespeichert" in down["response"]["outputSpeech"]["text"]

    # Home Assistant answers an unknown webhook with an empty 200
    closed, _ = _run_skill_code(b"")
    assert "nicht gespeichert" in closed["response"]["outputSpeech"]["text"]
