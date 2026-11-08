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
    "Brainstorm Hub": "brˈɛːnstɔɾm hˈab",
    "Alexa-Apps": "alˈɛksa ˈɛps",
    "Alexa-App": "alˈɛksa ˈɛp",
    "Action-Taste": "ˈɛkʃən tˈastə",
    "To-do-Listen": "tuːdˈuː lˈɪstən",
    "Permissions": "pœːmˈɪʃəns",
    "Reminders": "rɪmˈaɪndɐs",
    "Brainstorm": "brˈɛːnstɔɾm",
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
    ("Hey Siri", "He Siri"),
    ("Das war's", "Das war es schon"),
]

SPOKEN: list[tuple[str, str]] = [*_TEXT, *((t, f"[[{p}]]") for t, p in _TERMS.items())]
