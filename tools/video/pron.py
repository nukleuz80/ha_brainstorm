"""English terms with their pronunciation for the German Piper voice.

Piper reads text in ``[[ ]]`` as raw phonemes. The German voice otherwise reads
English words by German rules, e.g. "iPhone" as "ih-fohne" or "JSON" as
"jotzohn". The phonemes stay in the German inventory (no ɹ, æ, θ) so the voice
renders them cleanly, and each entry was checked by transcribing the result
with Whisper (``saytest.py``). "Brainstorm" uses the German loanword sound
"Brähnstorm", which German listeners recognise best.

build.py moves punctuation after a block into it, Piper would drop it otherwise.

Check what eSpeak would say:  vv/bin/python ph.py de "Wort"
"""
from __future__ import annotations

# Longer phrases first, build.py replaces them in this order
_TERMS: dict[str, str] = {
    "Home Assistant Companion-App": "hˈoʊm asˈɪstənt kɔmpˈɛnjən ˈɛp",
    "brainstorm reminder due": "brˈɛːnstɔɾm rɪmˈaɪndɐ djˈuː",
    "Companion-App": "kɔmpˈɛnjən ˈɛp",
    "Home Assistant": "hˈoʊm asˈɪstənt",
    "Claude Code": "klˈɔːd kˈoʊd",
    "Skill Invocation Name": "skˈɪl ɪnvoʊkˈeːʃən nˈeːm",
    "Presentation Language": "prɛzəntˈeːʃən lˈɛŋɡwɪtʃ",
    "custom brainstorm card": "kˈastəm brˈɛːnstɔɾm kˈaːɐt",
    "ha underscore brainstorm": "hˈaː ˈaː ˈandɐskɔːɐ brˈɛːnstɔɾm",
    "Media Player": "mˈiːdiːa plˈeːɐ",
    "github punkt com": "ɡˈɪt hˈab pˈʊŋkt kˈɔm",
    "Start from Scratch": "stˈaːɐt frɔm skrˈɛtʃ",
    "Interaction Model": "ɪntɐrˈɛkʃən mˈɔdəl",
    "lambda function": "lˈambda fˈaŋkʃən",
    "Brainstorm Card": "brˈɛːnstɔɾm kˈaːɐt",
    "Brainstorm Hub": "brˈɛːnstɔɾm hˈab",
    "Google Tasks": "ɡˈuːɡəl tˈɛsks",
    "Open in HACS": "ˈoʊpən ɪn hˈaks",
    "Create Skill": "kriːˈeɪt skˈɪl",
    "Build Skill": "bˈɪlt skˈɪl",
    "JSON Editor": "dʒˈeɪsɔn ˈɛdɪtɔɐ",
    "Invocations": "ɪnvoʊkˈeːʃəns",
    "Repositories": "rɪpˈɔzɪtɔːɾiːs",
    "Development": "dɪvˈɛləpmənt",
    "Hub-Profile": "hˈab proːfˈiːlə",
    "Panel-Ansicht": "pˈɛnəl ˈanzɪçt",
    "voice mode": "vˈɔɪs mˈoʊt",
    "Node J S": "nˈoʊt dʒˈeɪ ˈɛs",
    "Interfaces": "ˈɪntɐfeːsɪs",
    "Dashboard": "dˈɛʃbɔːɐt",
    "Markdown": "mˈaːkdaʊn",
    "FreeMind": "frˈiːmaɪnt",
    "Callouts": "kˈɔːlaʊts",
    "Timer": "tˈaɪmɐ",
    "Tags": "tˈɛɡs",
    "nukleuz80": "nˈuːkleʊs ˈaxtsɪç",
    "Mindmap": "mˈaɪntmɛp",
    "Minimap": "mˈɪnimɛp",
    "Todoist": "tuːdˈuːɪst",
    "English": "ˈɪŋlɪʃ",
    "Release": "rɪlˈiːs",
    "German": "dʒˈœːmən",
    "Amazon": "ˈamazɔn",
    "Python": "pˈaɪtən",
    "Custom": "kˈastəm",
    "Deploy": "dɪplˈɔɪ",
    "README": "rˈiːdmiː",
    "Other": "ˈadɐ",
    "Build": "bˈɪlt",
    "YAML": "jˈɛməl",
    "Save": "sˈeɪf",
    "Action-Taste": "ˈɛkʃən tˈastə",
    "To-do-Listen": "tuːdˈuː lˈɪstən",
    "Permissions": "pœːmˈɪʃəns",
    "Reminders": "rɪmˈaɪndɐs",
    "Brainstorm": "brˈɛːnstɔɾm",
    "brainstorm": "brˈɛːnstɔɾm",
    "Pushover": "pˈʊʃoʊvɐ",
    "examples": "ɪkzˈɛmpəls",
    "Backlog": "bˈɛklɔk",
    "iPhones": "ˈaɪfoʊns",
    "iPhone": "ˈaɪfoʊn",
    "GitHub": "ɡˈɪt hˈab",
    "Coding": "kˈoʊdɪŋ",
    "Token": "tˈoʊkən",
    "JSON": "dʒˈeɪsɔn",
}

# Words that only need a spelling hint, not phonemes. Siri keeps its German
# sound, the English one was heard as "HSE".
_TEXT: list[tuple[str, str]] = [
    ("MCP-Server", "M C P Server"),
    ("KIs", "Ka-Is"),
    ("eine App", "eine [[ˈɛp]]"),
    ("die App ", "die [[ˈɛp]] "),
    ("Alexa-hosted", "Alexa [[hˈoʊstɪt]]"),
    ("Alexa-Apps", "Alexa-[[ˈɛps]]"),
    ("Alexa-App", "Alexa-[[ˈɛp]]"),
    ("Hey Siri", "He Siri"),
    ("PDF", "P D F"),
    ("OPML", "O P M L"),
    ("2026 Punkt 10", "zweitausendsechsundzwanzig Punkt zehn"),
    ("Das war's", "Das war es schon"),
]

SPOKEN: list[tuple[str, str]] = [*_TEXT, *((t, f"[[{p}]]") for t, p in _TERMS.items())]
