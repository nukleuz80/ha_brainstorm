"""Tests for the offline buffer of the Alexa skill code."""
from __future__ import annotations

import io
import json
import os
import sys
import urllib.error
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from custom_components.brainstorm.alexa_skill import SKILL_CODE_TEMPLATE
from custom_components.brainstorm.languages.de import PACK as GERMAN

from .conftest import SetupEntry
from .test_alexa_skill import DEVICE_ID, SKILL_ID, _post, _setup_skill

PREFIX = "brainstorm-queue/"


class FakeS3:
    """The few S3 calls the skill code uses, kept in memory."""

    def __init__(self, objects: dict[str, bytes] | None = None) -> None:
        self.objects = dict(objects or {})

    def put_object(self, Bucket: str, Key: str, Body: bytes) -> None:
        self.objects[Key] = Body

    def list_objects_v2(self, Bucket: str, Prefix: str, MaxKeys: int) -> dict:
        keys = sorted(k for k in self.objects if k.startswith(Prefix))[:MaxKeys]
        return {"Contents": [{"Key": key} for key in keys]}

    def get_object(self, Bucket: str, Key: str) -> dict:
        return {"Body": io.BytesIO(self.objects[Key])}

    def delete_object(self, Bucket: str, Key: str) -> None:
        self.objects.pop(Key, None)


def _event(intent: str = "CaptureIdeaIntent", text: str = "kellerlicht dimmen") -> dict:
    return {
        "context": {
            "System": {
                "application": {"applicationId": SKILL_ID},
                "device": {"deviceId": DEVICE_ID, "supportedInterfaces": {}},
            }
        },
        "request": {
            "locale": "de-DE",
            "requestId": "amzn1.echo-api.request.1",
            "type": "IntentRequest",
            "intent": {"name": intent, "slots": {"text": {"value": text}}},
        },
    }


def _run(
    replies: list[bytes | Exception],
    s3: FakeS3 | None,
    event: dict | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Run the skill code with a fake network and an optional S3 bucket."""
    namespace: dict[str, Any] = {}
    exec(SKILL_CODE_TEMPLATE.replace("__WEBHOOK_URL__", "https://x/y"), namespace)
    sent: list[dict[str, Any]] = []

    def fake_urlopen(request: Any, timeout: float) -> Any:
        sent.append(json.loads(request.data))
        reply = replies.pop(0) if replies else b'{"speech": "Gespeichert."}'
        if isinstance(reply, Exception):
            raise reply
        return io.BytesIO(reply)

    environment = {"S3_PERSISTENCE_BUCKET": "bucket"} if s3 is not None else {}
    boto3 = SimpleNamespace(client=lambda name: s3)
    with (
        patch("urllib.request.urlopen", fake_urlopen),
        patch.dict(os.environ, environment, clear=False),
        patch.dict(sys.modules, {"boto3": boto3}),
    ):
        if s3 is None:
            os.environ.pop("S3_PERSISTENCE_BUCKET", None)
        return namespace["lambda_handler"](event or _event(), None), sent


def test_unreachable_sentence_is_buffered() -> None:
    """Test that a sentence is kept in the skill's bucket while HA is down."""
    s3 = FakeS3()
    result, sent = _run([urllib.error.URLError("down")], s3)

    assert result["response"]["outputSpeech"]["text"] == GERMAN.messages["skill_buffered"]
    assert len(s3.objects) == 1
    stored = json.loads(next(iter(s3.objects.values())))
    assert stored["text"] == "kellerlicht dimmen"
    assert stored["request_id"] == sent[0]["request_id"] == "amzn1.echo-api.request.1"


def test_without_bucket_the_old_answer_stays() -> None:
    """Test that a skill without Alexa hosting still says HA is unreachable."""
    result, _ = _run([urllib.error.URLError("down")], None)

    assert result["response"]["outputSpeech"]["text"] == GERMAN.messages["skill_unreachable"]


def test_questions_are_not_buffered() -> None:
    """Test that only capturing and reminders are kept for later."""
    s3 = FakeS3()
    result, _ = _run([urllib.error.URLError("down")], s3, _event("ReadIdeasIntent"))

    assert result["response"]["outputSpeech"]["text"] == GERMAN.messages["skill_unreachable"]
    assert s3.objects == {}


def test_next_success_delivers_buffered_sentences() -> None:
    """Test that the next working request hands over what was kept."""
    old = {"application_id": SKILL_ID, "action": "capture", "text": "milch", "request_id": "r0"}
    s3 = FakeS3({f"{PREFIX}1.json": json.dumps(old).encode()})

    result, sent = _run([], s3)

    assert result["response"]["outputSpeech"]["text"] == "Gespeichert."
    assert [p["text"] for p in sent] == ["kellerlicht dimmen", "milch"]
    assert sent[1]["buffered"] is True
    assert s3.objects == {}


def test_buffered_sentence_stays_when_delivery_fails() -> None:
    """Test that a sentence is only removed once Home Assistant took it."""
    old = {"application_id": SKILL_ID, "action": "capture", "text": "milch", "request_id": "r0"}
    s3 = FakeS3({f"{PREFIX}1.json": json.dumps(old).encode()})

    _run([b'{"speech": "Gespeichert."}', urllib.error.URLError("gone again")], s3)

    assert list(s3.objects) == [f"{PREFIX}1.json"]


def test_rejected_buffered_sentence_is_dropped() -> None:
    """Test that a sentence Home Assistant refuses does not block the queue."""
    old = {"application_id": SKILL_ID, "action": "capture", "text": "milch", "request_id": "r0"}
    s3 = FakeS3({f"{PREFIX}1.json": json.dumps(old).encode()})
    refused = urllib.error.HTTPError("https://x/y", 400, "Bad Request", {}, None)  # type: ignore[arg-type]

    _run([b'{"speech": "Gespeichert."}', refused], s3)

    assert s3.objects == {}


async def test_repeated_request_is_stored_once(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test that a sentence sent again after a timeout is not stored twice."""
    entry = await _setup_skill(hass, setup_entry)
    payload = {"application_id": SKILL_ID, "text": "neue blumenerde", "request_id": "r1"}

    first = await _post(hass_client_no_auth, entry, payload)
    again = await _post(hass_client_no_auth, entry, payload | {"buffered": True})

    assert first.status == again.status == 200
    ideas = [i for i in entry.runtime_data.ideas if i["source"] == "alexa_skill"]
    assert len(ideas) == 1


async def test_buffered_request_does_not_wait_for_the_alexa_history(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
) -> None:
    """Test that a late sentence is placed without matching the Alexa history."""
    entry = await _setup_skill(hass, setup_entry)
    skill = entry.runtime_data.alexa_skill

    with patch.object(skill, "_async_resolve_echo", side_effect=AssertionError):
        response = await _post(
            hass_client_no_auth,
            entry,
            {
                "application_id": SKILL_ID,
                "device_id": DEVICE_ID,
                "text": "fahrrad aufpumpen",
                "request_id": "r2",
                "buffered": True,
            },
        )

    assert response.status == 200
    assert [i for i in entry.runtime_data.ideas if i["text"].lower() == "fahrrad aufpumpen"]
