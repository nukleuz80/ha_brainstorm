"""Tests for the text normalization."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from custom_components.brainstorm.nlp import (
    clean_and_format_idea_text,
    extract_spoken_due,
    extract_spoken_priority,
    format_typed_text,
    participle_to_infinitive,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (
            "im brainstorm dass heute die kinder vom flughafen abgeholt werden müssen",
            "Heute Kinder vom Flughafen abholen",
        ),
        ("schreib bitte auf dass wir terrasse reinigen", "Terrasse reinigen"),
        ("notiere dass ich noch milch kaufen muss", "Milch kaufen"),
        ("WLAN Passwort ändern", "WLAN Passwort ändern"),
        ("ESP32 flashen", "ESP32 flashen"),
        ("iPhone laden", "iPhone laden"),
        ("Router zu reparieren", "Router zu reparieren"),
        ("Termin für morgen", "Termin für morgen"),
        ("Termin am morgen", "Termin am Morgen"),
        ("Heizung geliefert werden", "Heizung liefern"),
        ("Tür geöffnet werden", "Tür öffnen"),
        ("die Tür der Garage streichen", "Tür der Garage streichen"),
        ("kuchen für die oma backen", "Kuchen für die Oma backen"),
        ("auto in die werkstatt bringen", "Auto in die Werkstatt bringen"),
        ("Blumen pflanzen", "Blumen pflanzen"),
        ("", ""),
    ],
)
def test_clean_and_format(raw: str, expected: str) -> None:
    """Test that text is cleaned without losing meaning or spelling."""
    assert clean_and_format_idea_text(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        # A modal verb in the middle of the sentence
        ("der rasen muss gemäht werden", "Rasen mähen"),
        ("die hecke sollte geschnitten werden", "Hecke schneiden"),
        ("die terrasse muss abgehangen werden", "Terrasse abhängen"),
        ("die mülltonne muss rausgestellt werden", "Mülltonne rausstellen"),
        ("die garage muss mal aufgeräumt werden", "Garage aufräumen"),
        ("die waschmaschine muss repariert werden", "Waschmaschine reparieren"),
        ("der fernseher muss an die wand gehängt werden", "Fernseher an die Wand hängen"),
        ("das licht im keller muss ausgetauscht werden", "Licht im Keller austauschen"),
        ("die tür der garage muss gestrichen werden", "Tür der Garage streichen"),
        ("die kinder müssen heute vom flughafen abgeholt werden", "Kinder heute vom Flughafen abholen"),
        ("das auto muss in die werkstatt", "Auto in die Werkstatt"),
        ("der hund muss zum tierarzt", "Hund zum Tierarzt"),
        ("das paket abgeholt werden muss", "Paket abholen"),
        ("kürbisse müssen wir heute schnitzen", "Kürbisse heute schnitzen"),
        # Subject and modal verb at the start
        ("ich sollte mal die heizung entlüften", "Heizung entlüften"),
        ("wir sollten die garage aufräumen", "Garage aufräumen"),
        ("ich will die reifen wechseln", "Reifen wechseln"),
        ("ich müsste mal wieder oma anrufen", "Oma anrufen"),
        ("ich möchte den keller aufräumen", "Keller aufräumen"),
        ("wir brauchen neue batterien", "Neue batterien"),
        # Openers
        ("äh ich wollte noch sagen dass die lampe in der küche kaputt ist", "Lampe in der Küche kaputt"),
        ("also ich glaube wir müssen mal die fenster putzen", "Fenster putzen"),
        ("könntest du dir merken dass ich die rechnung bezahlen muss", "Rechnung bezahlen"),
        ("mir ist eingefallen dass wir das dach prüfen sollten", "Dach prüfen"),
        ("idee eine app für die kinder bauen", "Eine app für die Kinder bauen"),
        ("vergiss nicht die milch zu kaufen", "Milch kaufen"),
        ("nicht vergessen den müll rauszubringen", "Müll rausbringen"),
        ("rechnung bezahlen nicht vergessen", "Rechnung bezahlen"),
        ("die heizung ist kaputt", "Heizung kaputt"),
        # Fillers stay away only from a real short task
        ("die hecke muss noch geschnitten werden", "Hecke schneiden"),
        ("rasen noch mal mähen", "Rasen nochmal mähen"),
        ("rasenmäher muss noch einmal laufen", "Rasenmäher noch einmal laufen"),
    ],
)
def test_spoken_sentences_become_tasks(raw: str, expected: str) -> None:
    """Test that a whole spoken sentence is reduced to its task."""
    assert clean_and_format_idea_text(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        # Negations and facts must not turn into a task
        ("die rechnung wurde noch nicht bezahlt", "Die Rechnung wurde noch nicht bezahlt"),
        ("die kinder dürfen nicht vergessen werden", "Die Kinder dürfen nicht vergessen werden"),
        ("ich muss nicht zum arzt", "Ich muss nicht zum Arzt"),
        ("wir brauchen keine neue heizung", "Wir brauchen keine neue Heizung"),
        # Questions and subordinate clauses stay as they are
        ("ob schlaue antworten auch einen skill braucht", "Ob schlaue antworten auch einen skill braucht"),
        ("was macht die heizung?", "Was macht die Heizung?"),
        # Sentences that cannot be reduced completely keep their articles
        ("die spülmaschine muss repariert werden und die pumpe auch", "Die spülmaschine muss repariert werden und die Pumpe auch"),
        ("das muss weg", "Das muss weg"),
        ("sie muss zum arzt", "Sie muss zum Arzt"),
        ("der hund braucht futter", "Der Hund braucht futter"),
        ("muss auf jeden fall überarbeitet werden", "Muss auf jeden Fall überarbeitet werden"),
        ("das wetter sollte besser werden", "Das wetter sollte besser werden"),
        ("die lieferung muss gefxzbarn werden", "Die Lieferung muss gefxzbarn werden"),
    ],
)
def test_sentences_stay_whole_when_they_cannot_be_reduced(raw: str, expected: str) -> None:
    """Test that a sentence is reduced completely or not at all."""
    assert clean_and_format_idea_text(raw) == expected


@pytest.mark.parametrize(
    ("participle", "infinitive"),
    [
        ("gemäht", "mähen"),
        ("rausgestellt", "rausstellen"),
        ("weggeworfen", "wegwerfen"),
        ("angeschlossen", "anschließen"),
        ("zurückgeschnitten", "zurückschneiden"),
        ("ausprobiert", "ausprobieren"),
        ("überarbeitet", "überarbeiten"),
        ("besorgt", "besorgen"),
        ("entlüftet", "entlüften"),
        ("gefeiert", "feiern"),
        ("geleert", "leeren"),
        ("gespielt", "spielen"),
        ("gebügelt", "bügeln"),
        ("geöffnet", "öffnen"),
        ("besser", None),
        ("groß", None),
        ("vergessen", None),
    ],
)
def test_participle_to_infinitive(participle: str, infinitive: str | None) -> None:
    """Test deriving an infinitive, and refusing to guess one."""
    assert participle_to_infinitive(participle) == infinitive


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Die Hecke muss geschnitten werden", "Die Hecke muss geschnitten werden"),
        ("die Tür der Garage", "Die Tür der Garage"),
        ("Was macht Sinn?", "Was macht Sinn?"),
        ("seperat prüfen.", "Separat prüfen."),
        ("packet holen", "Paket holen"),
        ("iPhone laden", "iPhone laden"),
    ],
)
def test_typed_text_is_kept(raw: str, expected: str) -> None:
    """Test that a typed text only loses its typos."""
    assert format_typed_text(raw) == expected


# A Sunday evening
NOW = datetime(2026, 11, 1, 20, 0, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    ("raw", "expected_due", "expected_text"),
    [
        ("morgen arzt anrufen", (2026, 11, 2, 9, 0), "arzt anrufen"),
        ("ich muss morgen früh den arzt anrufen", (2026, 11, 2, 8, 0), "ich muss den arzt anrufen"),
        ("am 25.11. elternsprechtag", (2026, 11, 25, 9, 0), "elternsprechtag"),
        ("wäsche bis freitag waschen", (2026, 11, 6, 9, 0), "wäsche waschen"),
        ("termin für übermorgen um 14 uhr machen", (2026, 11, 3, 14, 0), "termin machen"),
        ("hecke schneiden in zwei wochen", (2026, 11, 15, 9, 0), "hecke schneiden"),
        ("heute abend um 22 uhr müll raus", (2026, 11, 1, 22, 0), "müll raus"),
    ],
)
def test_spoken_due_is_found(
    raw: str, expected_due: tuple[int, ...], expected_text: str
) -> None:
    """Test that a spoken date moves out of the text."""
    due, text = extract_spoken_due(raw, NOW)
    assert due == datetime(*expected_due, tzinfo=timezone.utc)
    assert text == expected_text


@pytest.mark.parametrize(
    "raw",
    [
        # Already over, it would remind at once
        "heute arzt anrufen",
        # Describe the task and not the day
        "am morgen brötchen holen",
        "früh aufstehen",
        "um 5 kisten bestellen",
        "abends licht aus",
        # In the past, recurring or a question
        "seit montag kaputt",
        "letzten freitag war der arzt da",
        "jeden montag müll raus",
        "kommt der arzt morgen?",
        # A version number is not a date
        "brainstorm 1.5.8 testen",
        # Nothing would be left of the note
        "morgen",
    ],
)
def test_spoken_due_stays_in_the_text(raw: str) -> None:
    """Test that the text is kept when no clear date in the future is meant."""
    assert extract_spoken_due(raw, NOW) == (None, raw)


@pytest.mark.parametrize(
    ("raw", "priority", "text"),
    [
        ("elternsprechtag ganz wichtig frei nehmen", "high", "elternsprechtag frei nehmen"),
        ("arzt unbedingt anrufen", "high", "arzt anrufen"),
        ("rechnung dringend bezahlen", "urgent", "rechnung bezahlen"),
        ("irgendwann mal garage streichen", "low", "garage streichen"),
        ("wichtige unterlagen holen", None, "wichtige unterlagen holen"),
        ("nicht so wichtig garage streichen", None, "nicht so wichtig garage streichen"),
        ("das ist wichtig", None, "das ist wichtig"),
        ("ist das dringend?", None, "ist das dringend?"),
        ("wichtig", None, "wichtig"),
    ],
)
def test_spoken_priority(raw: str, priority: str | None, text: str) -> None:
    """Test that a priority is found anywhere, but not in a different meaning."""
    assert extract_spoken_priority(raw) == (text, priority)
