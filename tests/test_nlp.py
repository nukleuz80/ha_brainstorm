"""Tests for the text normalization."""
from __future__ import annotations

import pytest

from custom_components.brainstorm.nlp import (
    clean_and_format_idea_text,
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
