"""English rules and words of Brainstorm Hub."""
from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime, time, timedelta
import re

from ..const import PRIORITY_HIGH, PRIORITY_LOW, PRIORITY_MEDIUM, PRIORITY_URGENT
from .common import (
    CATEGORY_BRAINSTORM,
    CATEGORY_DAILY,
    CATEGORY_HOME_GARDEN,
    CATEGORY_PROJECTS,
    CATEGORY_SMARTHOME,
    ENGLISH_CATEGORIES,
    LanguagePack,
    ReminderWords,
    apply_glossary,
    capitalize_first,
    merge_glossary,
    validate_rewrite,
)

# Verbs of everyday tasks, needed to recognize their forms for certain
BASE_VERBS: frozenset[str] = frozenset(
    """
    add adjust answer apply arrange ask assemble bake bring book build buy calibrate
    call cancel change charge check clean clear close collect connect cook copy
    cover cut dig dim discuss disconnect dispose do download drain drill drive drop
    dry dust email empty exchange feed fertilize file fill find finish fix flash
    fold get give glue go grease hang heat help hide hire hook inspect install invite
    iron label lay lift load lock look mail make measure meet mend mop mount move
    mow oil open order organize paint pay pick plan plant plug polish pour prepare
    print prune pull pump push put rake read rebuild reboot recycle refill remove
    renew rent repaint repair replace reply reset restart return rinse run sand
    save schedule screw seal sell send service set sew sharpen shovel show shut
    sign solder sort spray store sweep switch take test throw tidy tighten trim
    turn unblock unclog unload unlock unpack update upgrade vacuum wash water wax
    weed wipe wire write
    """.split()
)

# Participles that do not follow the regular pattern
IRREGULAR_PARTICIPLES: dict[str, str] = {
    "bought": "buy",
    "brought": "bring",
    "built": "build",
    "cut": "cut",
    "done": "do",
    "driven": "drive",
    "dug": "dig",
    "fed": "feed",
    "found": "find",
    "given": "give",
    "gone": "go",
    "got": "get",
    "gotten": "get",
    "hung": "hang",
    "hidden": "hide",
    "laid": "lay",
    "made": "make",
    "met": "meet",
    "mown": "mow",
    "paid": "pay",
    "put": "put",
    "read": "read",
    "rebuilt": "rebuild",
    "reset": "reset",
    "run": "run",
    "sent": "send",
    "set": "set",
    "sewn": "sew",
    "shown": "show",
    "shut": "shut",
    "sold": "sell",
    "swept": "sweep",
    "taken": "take",
    "thrown": "throw",
    "written": "write",
}

_PARTICLES = frozenset(
    {"up", "out", "off", "down", "in", "on", "away", "back", "over", "through"}
)
_PREPOSITIONS = frozenset(
    {
        "about", "above", "across", "after", "against", "around", "at", "before",
        "behind", "below", "beside", "between", "by", "down", "for", "from", "in",
        "inside", "into", "near", "of", "off", "on", "onto", "out", "outside", "over",
        "through", "to", "toward", "under", "with", "without",
    }
)
# Short words a task may keep from a sentence without it staying a sentence
_ARTICLES = frozenset({"the", "a", "an"})
# Never capitalized by themselves, 'may', 'march' and 'august' are too often other words
_NAMES = {
    word: word.capitalize()
    for word in (
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
        "january", "february", "april", "june", "july", "september", "october",
        "november", "december",
    )
}

_CONVERSATIONAL_PREFIXES: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"^(?:in|on|to|for)\s+(?:the\s+)?brainstorm(?:\s+hub)?\s*(?::|,|\s+that\b|\s+please|\s+)\s*",
        r"^(?:um+|uh+m?|er+m?|hm+|mhm|so|okay|ok|well|right|and|oh|by\s+the\s+way)\b[,.]?\s+",
        r"^(?:i\s+(?:think|guess|just\s+thought\s+of\s+this)|it\s+(?:just\s+)?occurred\s+to\s+me(?:\s+that)?|i\s+just\s+remembered(?:\s+that)?|i\s+wanted\s+to\s+say(?:\s+that)?)(?:\s*,)?\s+",
        r"^(?:(?:can|could|would)\s+you\s+(?:please\s+)?(?:note(?:\s+down)?|write\s+down|remember|add)|please\s+(?:note(?:\s+down)?|write\s+down|remember)|note\s+down|note|write\s+down|jot\s+down)\s*(?::|,|\s+that\b|\s+)\s*",
        r"^(?:new\s+)?(?:idea|note)\s*(?::|,)?\s+(?!(?:from|for|about|of|with|in|on|at|to|by)\b)",
        r"^that\s+",
        r"^please\s+",
    )
)
# Openers after which the rest is the actual task
_RE_REMINDER_OPENER = re.compile(
    r"^(?:please\s+)?(?:(?:don'?t|do\s+not)\s+forget(?:\s+to|\s+that)?|"
    r"remember\s+to|remember\s+that|remember|remind\s+me(?:\s+to|\s+that|\s+about)?)"
    r"(?:\s*,)?\s+",
    re.IGNORECASE,
)
_RE_NOT_FORGET_SUFFIX = re.compile(
    r"\s*,?\s+(?:(?:don'?t|do\s+not)\s+forget|remember)[.!]?$", re.IGNORECASE
)

_WORD = r"[a-zA-Z'-]+"
_STATE = (
    r"(?:broken|empty|leaking|clogged|blocked|loose|wet|out|dead|flat|stuck|missing|"
    r"cracked|dirty|full)"
)

_RE_KEEP_SENTENCE = re.compile(
    r"\b(?:not|never|nothing|nobody|none|no|cannot|was|were|had|did|\w+n't|dont|wont|"
    r"cant|didnt|doesnt|isnt|wasnt)\b",
    re.IGNORECASE,
)
_RE_QUESTION_START = re.compile(
    r"^(?:if|when|whenever|because|since|why|how|what|where|who|which|whether|although|"
    r"is|are|do|does|can|could|would|will|shall|should)\b",
    re.IGNORECASE,
)
_RE_SUBJECT_MODAL_START = re.compile(
    r"^(?:i|we)(?:'ve|\s+have)?\s+(?:(?:really|still|also|probably|just|definitely)\s+)*"
    r"(?:need\s+to|have\s+to|got\s+to|gotta|must|should|ought\s+to|want\s+to|"
    r"wanna|would\s+like\s+to|'d\s+like\s+to|'ll\s+have\s+to)\s+"
    r"(?:(?:really|still|also|probably|just|definitely)\s+)*",
    re.IGNORECASE,
)
_RE_PASSIVE_MODAL = re.compile(
    rf"^(?P<object>.+?)\s+(?:(?:still|really|also)\s+)?"
    r"(?:needs?\s+to\s+be|has\s+to\s+be|have\s+to\s+be|must\s+be|should\s+be|"
    r"ought\s+to\s+be|got\s+to\s+be|gotta\s+be)\s+"
    rf"(?P<participle>{_WORD})(?:\s+(?P<rest>.+))?$",
    re.IGNORECASE,
)
_RE_NEEDS_GERUND = re.compile(
    r"^(?P<object>.+?)\s+needs?\s+(?:(?:a|some)\s+)?(?P<gerund>[a-zA-Z-]+ing)"
    r"(?:\s+(?P<rest>.+))?$",
    re.IGNORECASE,
)
_RE_STATE = re.compile(
    rf"^(?P<subject>.+?)\s+(?:is|are)\s+(?:(?:now|currently|still|again|already)\s+)*"
    rf"(?P<state>{_STATE})$",
    re.IGNORECASE,
)
_RE_CLAUSE_WORD = re.compile(
    r"\b(?:because|although|while|since|but|if|when|who|which|that|is|are|will)\b",
    re.IGNORECASE,
)
_RE_FILLERS = re.compile(
    r"\b(?:please|just|really|maybe|perhaps|probably|definitely|kind\s+of|sort\s+of|"
    r"actually|basically|at\s+some\s+point)\b",
    re.IGNORECASE,
)
_RE_SENTENCE_WORD = re.compile(
    r"\b(?:i|you|he|she|we|they|it|that|if|because|is|are|was|were|am|will|would|can|"
    r"could|should|must|need|needs|has|have|had|did|does|want|wants|not|never|no|"
    r"\w+n't)\b",
    re.IGNORECASE,
)

BUILTIN_GLOSSARY: dict[str, str] = {
    "ai": "AI",
    "alexa": "Alexa",
    "e-mail": "email",
    "echo show": "Echo Show",
    "grafana": "Grafana",
    "hdmi": "HDMI",
    "home assistant": "Home Assistant",
    "homeassistant": "Home Assistant",
    "ipad": "iPad",
    "iphone": "iPhone",
    "led": "LED",
    "nas": "NAS",
    "pdf": "PDF",
    "siri": "Siri",
    "tv": "TV",
    "usb": "USB",
    "wifi": "Wi-Fi",
    "wi-fi": "Wi-Fi",
}


def _regular_base(word: str, ending: str) -> str | None:
    """Return the known verb a regular form belongs to."""
    if not word.endswith(ending) or len(word) <= len(ending) + 1:
        return None
    stem = word[: -len(ending)]
    candidates = [stem, f"{stem}e"]
    if stem.endswith("i"):
        candidates.append(f"{stem[:-1]}y")
    if len(stem) > 2 and stem[-1] == stem[-2]:
        candidates.append(stem[:-1])
    return next((verb for verb in candidates if verb in BASE_VERBS), None)


def participle_to_base(word: str) -> str | None:
    """Return the base form of a participle, None unless it is known for certain."""
    lowered = word.lower()
    return IRREGULAR_PARTICIPLES.get(lowered) or _regular_base(lowered, "ed")


def gerund_to_base(word: str) -> str | None:
    """Return the base form of an '-ing' form, None unless it is known for certain."""
    return _regular_base(word.lower(), "ing")


def _build_task(verb: str, task_object: str, rest: str | None) -> str:
    """Put a task together, moving a particle next to its verb ('pick up')."""
    words = (rest or "").split()
    if words and words[0].lower() in _PARTICLES:
        verb = f"{verb} {words.pop(0).lower()}"
    return " ".join(part for part in (verb, task_object, " ".join(words)) if part)


def _rewrite_as_task(text: str) -> str:
    """Reduce a whole sentence to its task, or leave it exactly as it was."""
    if _RE_KEEP_SENTENCE.search(text) or _RE_QUESTION_START.match(text) or "?" in text:
        return text
    s = text.rstrip(" .!")

    if match := _RE_SUBJECT_MODAL_START.match(s):
        task = s[match.end() :]
        return text if not task or _RE_CLAUSE_WORD.search(task) else task

    if match := _RE_PASSIVE_MODAL.match(s):
        base = participle_to_base(match.group("participle"))
        rest = match.group("rest")
        if base is None or _RE_CLAUSE_WORD.search(rest or ""):
            return text
        return _build_task(base, match.group("object"), rest)

    if match := _RE_NEEDS_GERUND.match(s):
        base = gerund_to_base(match.group("gerund"))
        rest = match.group("rest")
        if base is None or _RE_CLAUSE_WORD.search(rest or ""):
            return text
        return _build_task(base, match.group("object"), rest)

    if match := _RE_STATE.match(s):
        return f"{match.group('subject')} {match.group('state')}"
    return s


def _drop_articles(text: str) -> str:
    """Drop articles, keeping those after a preposition ('from the garage')."""
    words = text.split()
    kept: list[str] = []
    for index, word in enumerate(words):
        core = word.lower().strip("\"'([<.,!?:;)]>")
        previous = words[index - 1].lower().strip("\"'([<.,!?:;)]>") if index else ""
        # After 'take out' the word 'out' belongs to the verb, it is no preposition
        if core in _ARTICLES and (
            previous not in _PREPOSITIONS or (index == 2 and previous in _PARTICLES)
        ):
            continue
        kept.append(word)
    return " ".join(kept) or text


def _format_words(text: str) -> str:
    """Apply English capitalization: first word, 'I', days and months."""
    words = text.split()
    for index, word in enumerate(words):
        core = word.strip("\"'([<>)]>.,!?:;")
        if core.lower() in _NAMES:
            words[index] = word.replace(core, _NAMES[core.lower()])
        elif core == "i" or core.startswith("i'"):
            words[index] = word.replace("i", "I", 1)
    if words:
        words[0] = capitalize_first(words[0])
    return " ".join(words)


def format_typed_text(raw_text: str) -> str:
    """Keep what the person wrote, only starting with a capital letter."""
    words = raw_text.strip().split()
    if words:
        words[0] = capitalize_first(words[0])
    return " ".join(words)


def clean_text(raw_text: str, glossary: dict[str, str] | None = None) -> str:
    """Reduce a spoken English sentence to a short task note.

    Turns 'the lawn has to be mowed' into 'Mow lawn'. A sentence that cannot be
    reduced completely keeps its articles and only gets its spelling corrected.
    """
    if not raw_text or not raw_text.strip():
        return ""

    s = raw_text.strip()
    changed = True
    while changed:
        changed = False
        if match := _RE_REMINDER_OPENER.match(s):
            s = s[match.end() :].strip()
            changed = True
        for pattern in _CONVERSATIONAL_PREFIXES:
            new_s = pattern.sub("", s).strip()
            if new_s != s and new_s:
                s = new_s
                changed = True
    s = _RE_NOT_FORGET_SUFFIX.sub("", s).strip()

    s = _rewrite_as_task(s)

    if not (_RE_SENTENCE_WORD.search(s) or _RE_QUESTION_START.match(s) or "?" in s):
        no_fillers = re.sub(r"\s+", " ", _RE_FILLERS.sub(" ", s)).strip(" ,")
        s = _drop_articles(no_fillers or s)

    result = apply_glossary(
        _format_words(s), BUILTIN_GLOSSARY if glossary is None else glossary
    )
    if not result.endswith("?"):
        result = re.sub(r"[\.,;:!\?]+$", "", result).strip()
    return result


_NUMBER_WORDS: dict[str, int] = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "fifteen": 15,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "forty-five": 45,
    "fifty": 50,
}
_NUMBER = r"\d{1,2}|" + "|".join(sorted(_NUMBER_WORDS, key=len, reverse=True))
_WEEKDAYS = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)
_MONTHS = (
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
)
_MONTH = "|".join(_MONTHS)
_ORDINAL = r"(\d{1,2})(?:st|nd|rd|th)?"
_DAY_PARTS: dict[str, tuple[int, bool]] = {
    "morning": (8, False),
    "noon": (12, False),
    "afternoon": (15, True),
    "evening": (19, True),
    "tonight": (19, True),
    "night": (22, True),
}
_DEFAULT_DUE_TIME = time(9, 0)
_DAY_PART = "|".join(sorted(_DAY_PARTS, key=len, reverse=True))

_RE_HALF_AN_HOUR = re.compile(r"\bin\s+(?:half\s+an\s+hour|thirty\s+minutes)\b", re.I)
_RE_RELATIVE = re.compile(
    rf"\bin\s+({_NUMBER}|an?)\s+(minutes?|hours?|days?|weeks?)\b", re.I
)
_RE_DAY = re.compile(
    r"\b(?:the\s+)?(day\s+after\s+tomorrow|tomorrow|today|tonight)\b(?!'s)", re.I
)
_RE_NEXT_WEEK = re.compile(r"\b(?:next|coming)\s+week\b", re.I)
_RE_WEEKDAY = re.compile(
    r"\b(?:(?:on|next|this|coming)\s+)?(" + "|".join(_WEEKDAYS) + r")\b(?!s\b|'s)", re.I
)
_RE_MONTH_DATE = re.compile(
    rf"\b(?:on\s+)?(?:the\s+)?{_ORDINAL}\s+(?:of\s+)?({_MONTH})\b"
    rf"|\b(?:on\s+)?({_MONTH})\s+(?:the\s+)?{_ORDINAL}\b(?!\s*(?:am|pm|o'clock)\b)",
    re.I,
)
_RE_PAST_HOUR = re.compile(rf"\b(?:at\s+)?half\s+past\s+({_NUMBER})(?:\s*(am|pm))?\b", re.I)
_RE_QUARTER = re.compile(
    rf"\b(?:at\s+)?quarter\s+(to|past)\s+({_NUMBER})(?:\s*(am|pm))?\b", re.I
)
_RE_CLOCK = re.compile(
    rf"\bat\s+({_NUMBER})(?:[:.](\d{{2}})|\s+({_NUMBER}))?(?:\s*(am|pm|a\.m\.|p\.m\.)|\s*o'clock)?(?=\s|$|[,.])"
    rf"|\b({_NUMBER})(?:[:.](\d{{2}}))?\s*(am|pm|a\.m\.|p\.m\.|o'clock)(?=\s|$|[,.])",
    re.I,
)
_RE_NOON = re.compile(r"\b(?:at\s+)?(noon|midnight)\b", re.I)
_RE_DAY_PART = re.compile(
    rf"\b(?:(?:in\s+the|this|at)\s+)?({_DAY_PART})\b(?!'s)", re.I
)
_RE_LEADING_WORDS = re.compile(
    r"^(?:to|that|about|at|on|by|me|please|due|of)\b\s*", re.I
)
_RE_TRAILING_WORDS = re.compile(r"\s*\b(?:please|by|on|at)$", re.I)


def _number(value: str) -> int:
    """Convert a spoken or written number."""
    lowered = value.lower()
    if lowered in ("a", "an"):
        return 1
    return int(lowered) if lowered.isdigit() else _NUMBER_WORDS[lowered]


def _resolve_hour(hour: int, meridiem: str | None, has_day: bool) -> int | None:
    """Apply am or pm. Without them, an early hour on a known day means the afternoon."""
    marker = (meridiem or "").lower().replace(".", "")
    if hour > 24:
        return None
    if marker == "pm":
        return hour if hour >= 12 else hour + 12
    if marker == "am":
        return 0 if hour == 12 else hour
    if has_day and 1 <= hour <= 6:
        return hour + 12
    return hour


def _date_in_future(now: datetime, day: int, month: int) -> date | None:
    """Build a date, moving to next year if it has passed."""
    try:
        result = now.date().replace(month=month, day=day)
        if result < now.date():
            result = result.replace(year=result.year + 1)
    except ValueError:
        return None
    return result


def _next_time(now: datetime, hour: int, minute: int, meridiem: bool) -> datetime:
    """Return the next time of day. Without am or pm, it may be either half of the day."""
    day = now.date()
    candidates = [hour] if meridiem or hour > 12 or hour == 0 else [hour % 12, hour % 12 + 12]
    for candidate in candidates:
        result = datetime.combine(day, time(candidate % 24, minute), now.tzinfo)
        if result > now:
            return result
    return datetime.combine(
        day + timedelta(days=1), time(candidates[0] % 24, minute), now.tzinfo
    )


def _combine(
    now: datetime,
    day: date | None,
    take: Callable[[re.Pattern[str]], re.Match[str] | None],
    evening: bool = False,
) -> datetime | None:
    """Add the spoken time of day to a date, which may not be known yet."""
    hour: int | None = None
    minute = 0
    meridiem: str | None = None
    if match := take(_RE_PAST_HOUR):
        hour, minute, meridiem = _number(match.group(1)), 30, match.group(2)
    elif match := take(_RE_QUARTER):
        base = _number(match.group(2))
        meridiem = match.group(3)
        hour, minute = (base - 1, 45) if match.group(1).lower() == "to" else (base, 15)
    elif match := take(_RE_NOON):
        hour, meridiem = (12, "pm") if match.group(1).lower() == "noon" else (12, "am")
    elif match := take(_RE_CLOCK):
        hour = _number(match.group(1) or match.group(5))
        minute_text = match.group(2) or match.group(3) or match.group(6)
        if minute_text:
            minute = _number(minute_text)
        meridiem = match.group(4) or match.group(7)
        if meridiem and meridiem.lower() == "o'clock":
            meridiem = None
    if hour is not None and (hour > 24 or minute > 59):
        return None

    if evening:
        if hour is None:
            hour, meridiem = 19, "known"
        elif meridiem is None:
            meridiem = "pm"

    part = take(_RE_DAY_PART)
    part_name = part.group(1).lower() if part else None
    if part_name:
        default_hour, afternoon = _DAY_PARTS[part_name]
        if hour is None:
            hour = default_hour
            meridiem = "known"
        elif meridiem is None:
            meridiem = "pm" if afternoon else "am"

    if day is None and hour is None:
        return None
    if hour is None:
        return datetime.combine(day, _DEFAULT_DUE_TIME, now.tzinfo)
    if meridiem == "known":
        clock = time(hour, minute)
        if day is None:
            day = now.date()
            if datetime.combine(day, clock, now.tzinfo) <= now:
                day += timedelta(days=1)
        return datetime.combine(day, clock, now.tzinfo)
    if day is None and meridiem is None:
        return _next_time(now, hour, minute, False)
    resolved = _resolve_hour(hour, meridiem, day is not None)
    if resolved is None:
        return None
    clock = time(resolved % 24, minute)
    if day is None:
        day = now.date()
        if datetime.combine(day, clock, now.tzinfo) <= now:
            day += timedelta(days=1)
    return datetime.combine(day, clock, now.tzinfo)


def parse_due(text: str, now: datetime) -> tuple[datetime | None, str]:
    """Find a spoken English date and time, returning it and the remaining text.

    Numeric dates like 3/4 are not read, as countries read them differently. Without
    a date, a time means the next time it comes up. Without a time, a day means 09:00.
    """
    spans: list[tuple[int, int]] = []

    def take(pattern: re.Pattern[str]) -> re.Match[str] | None:
        """Search outside of what was already found and remember the match."""
        for match in pattern.finditer(text):
            if not any(s < match.end() and match.start() < e for s, e in spans):
                spans.append(match.span())
                return match
        return None

    due: datetime | None = None
    evening = False
    if take(_RE_HALF_AN_HOUR):
        due = now + timedelta(minutes=30)
    elif match := take(_RE_RELATIVE):
        amount = _number(match.group(1))
        unit = match.group(2).lower()
        if unit.startswith("minute"):
            due = now + timedelta(minutes=amount)
        elif unit.startswith("hour"):
            due = now + timedelta(hours=amount)
        else:
            days = amount * 7 if unit.startswith("week") else amount
            due = _combine(now, now.date() + timedelta(days=days), take)
    else:
        day: date | None = None
        if match := take(_RE_MONTH_DATE):
            number = match.group(1) or match.group(4)
            month = (match.group(2) or match.group(3)).lower()
            day = _date_in_future(now, int(number), _MONTHS.index(month) + 1)
        elif match := take(_RE_DAY):
            word = re.sub(r"\s+", " ", match.group(1).lower())
            evening = word == "tonight"
            offset = {"tomorrow": 1, "day after tomorrow": 2}.get(word, 0)
            day = now.date() + timedelta(days=offset)
        elif take(_RE_NEXT_WEEK):
            day = now.date() + timedelta(days=7 - now.weekday())
        elif match := take(_RE_WEEKDAY):
            ahead = (_WEEKDAYS.index(match.group(1).lower()) - now.weekday()) % 7
            day = now.date() + timedelta(days=ahead or 7)
        due = _combine(now, day, take, evening)

    if due is None:
        return None, text.strip()

    remaining = text
    for start, end in sorted(spans, reverse=True):
        remaining = f"{remaining[:start]} {remaining[end:]}"
    return due, strip_reminder_words(remaining)


def strip_reminder_words(text: str) -> str:
    """Remove the words that only connect a reminder to its content."""
    remaining = re.sub(r"\s+", " ", text).strip(" ,.")
    previous = None
    while previous != remaining:
        previous = remaining
        remaining = _RE_LEADING_WORDS.sub("", remaining)
        remaining = _RE_TRAILING_WORDS.sub("", remaining).strip(" ,.")
    return remaining


# A spoken date only counts when it clearly means a day; a past or recurring day is
# not a due date, and neither is 'in the morning' by itself
_RE_SPOKEN_DATE = re.compile(
    r"\b(?:day\s+after\s+tomorrow|tomorrow|today|tonight)\b(?!'s)"
    rf"|{_RE_RELATIVE.pattern}"
    rf"|{_RE_HALF_AN_HOUR.pattern}"
    rf"|{_RE_NEXT_WEEK.pattern}"
    rf"|\b(?:{'|'.join(_WEEKDAYS)})\b(?!s\b|'s)"
    rf"|{_RE_MONTH_DATE.pattern}",
    re.IGNORECASE,
)
_RE_NO_DUE_DATE = re.compile(
    r"\b(?:since|last|previous|every|each|yesterday|ago|was|were|did|had)\b|\?",
    re.IGNORECASE,
)
_RE_DATE_CONNECTOR = re.compile(
    r"\b(?:by|until|till|no\s+later\s+than|at\s+the\s+latest\s+by|for|from|due)\s+"
    rf"(?=(?:the\s+day|tomorrow|today|tonight|next|coming|this|the\s+\d|\d|{'|'.join(_WEEKDAYS)}|{_MONTH})\b)",
    re.IGNORECASE,
)

_SPOKEN_PRIORITIES: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(
            r"\b(?:(?:very|really)\s+)?urgent(?:ly)?\b|\basap\b|\bas\s+soon\s+as\s+possible\b|"
            r"\bright\s+away\b|\bimmediately\b",
            re.IGNORECASE,
        ),
        PRIORITY_URGENT,
    ),
    (
        re.compile(
            r"\b(?:(?:very|really|super|extremely)\s+)?important\b|\bhigh\s+priority\b|"
            r"\bdefinitely\b",
            re.IGNORECASE,
        ),
        PRIORITY_HIGH,
    ),
    (
        re.compile(
            r"\bsome\s?day\b|\beventually\b|\bwhen(?:ever)?\s+(?:there'?s|there\s+is|i\s+have|"
            r"we\s+have)\s+time\b|\bno\s+rush\b|\blow\s+priority\b",
            re.IGNORECASE,
        ),
        PRIORITY_LOW,
    ),
)
_RE_NO_SPOKEN_PRIORITY = re.compile(
    r"\b(?:not|isn'?t|aren'?t|wasn'?t|no|never)\s+(?:so\s+|that\s+|very\s+|really\s+)?"
    r"(?:urgent|important)\b"
    r"|\b(?:is|are|was|were)\s+(?:\w+\s+)?(?:urgent|important)\b|\?",
    re.IGNORECASE,
)
_RE_VERB_AFTER_SUBJECT = re.compile(
    r"^(?:needs?|must|should|has|have|had|is|are|was|were|will|would|can|could|shall|"
    r"works?|broke|runs?|keeps?|goes|went|looks?|seems?)\b",
    re.IGNORECASE,
)


def starts_with_verb(text: str) -> bool:
    """Return whether a text begins with a verb, so what stood before it was the subject."""
    return bool(_RE_VERB_AFTER_SUBJECT.match(text))


def extract_spoken_due(text: str, now: datetime) -> tuple[datetime | None, str]:
    """Find a date in a spoken note, returning it and the text without it.

    The text stays as it is if nothing is left of it or the time has passed, which
    keeps 'today' in the text in the evening instead of reminding at once.
    """
    if _RE_NO_DUE_DATE.search(text) or not _RE_SPOKEN_DATE.search(text):
        return None, text
    due, remaining = parse_due(_RE_DATE_CONNECTOR.sub("", text), now)
    if due is None or due <= now or not remaining:
        return None, text
    return due, remaining


def extract_spoken_priority(text: str) -> tuple[str, str | None]:
    """Find a priority anywhere in a spoken note, returning the text without it."""
    if _RE_NO_SPOKEN_PRIORITY.search(text):
        return text, None
    for pattern, priority in _SPOKEN_PRIORITIES:
        remaining = re.sub(r"\s+", " ", pattern.sub(" ", text, count=1)).strip(" ,.")
        if remaining != text.strip(" ,.") and remaining:
            return remaining, priority
    return text, None


def build_glossary(custom_terms: str | None, names: list[str]) -> dict[str, str]:
    """Build the spellings to enforce from names and the person's own list."""
    return merge_glossary(BUILTIN_GLOSSARY, custom_terms, names, _RE_SENTENCE_WORD)


_RE_NEGATION = re.compile(
    r"\b(?:not|never|no|none|nothing|nobody|cannot|\w+n't)\b", re.IGNORECASE
)
_AI_ALLOWED_WORDS: frozenset[str] = frozenset(
    {
        "the", "and", "for", "from", "with", "into", "onto", "off", "out", "away",
        "back", "down", "over",
    }
)


def validate_ai_rewrite(spoken: str, rule_text: str, candidate: str) -> str | None:
    """Return the AI's text if it only shortens what was said, otherwise None."""
    return validate_rewrite(
        spoken, rule_text, candidate, _RE_NEGATION, _AI_ALLOWED_WORDS, r"[a-z]+"
    )


def ai_cleanup_prompt(spoken_text: str, rule_text: str) -> str:
    """Return the instructions for an AI to improve a spoken note."""
    return (
        "Turn this spoken note into a short English bullet point for a task list, "
        "with correct spelling and capitalization. Reply with the bullet point only. "
        "Do not invent content, names or numbers and never change a negation. Leave "
        "out filler words and words like 'important' or 'urgent'. A task starts with "
        "the verb in its base form.\n"
        f"Spoken: {spoken_text}\n"
        f"Current bullet point: {rule_text}"
    )


CATEGORY_ALIASES: dict[str, list[str]] = {
    CATEGORY_HOME_GARDEN: [
        "house & garden", "house and garden", "home & garden", "home and garden",
        "garden", "yard", "backyard", "house", "gardening",
    ],
    CATEGORY_SMARTHOME: [
        "smart home", "smarthome", "home automation", "home assistant",
        "homeassistant", "iot",
    ],
    CATEGORY_PROJECTS: ["projects", "project", "diy", "workshop", "crafts"],
    CATEGORY_DAILY: [
        "daily life", "daily", "household", "errands", "chores", "everyday",
    ],
    CATEGORY_BRAINSTORM: ["brainstorm", "brainstorming", "brainstorm hub"],
}

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    CATEGORY_BRAINSTORM: [
        "brainstorm", "brainstorming", "mindmap", "synapse", "idea hub", "alexa skill",
    ],
    CATEGORY_HOME_GARDEN: [
        "garden", "lawn", "lawnmower", "mower", "mow", "hedge", "hedges", "tree",
        "trees", "shrub", "flowers", "roses", "tomatoes", "plants", "soil", "compost",
        "fertilizer", "fertilize", "water", "sprinkler", "irrigation", "patio",
        "terrace", "fence", "shed", "greenhouse", "pool", "gutter", "roof", "window",
        "windows", "door", "basement", "attic", "garage", "paint", "wall", "plumber",
        "leak", "faucet", "radiator", "boiler", "furnace", "weeds", "leaves",
    ],
    CATEGORY_SMARTHOME: [
        "esphome", "esp32", "esp8266", "zigbee", "z-wave", "zwave", "matter", "thread",
        "mqtt", "automation", "automations", "sensor", "sensors", "motion sensor",
        "thermostat", "smart plug", "smart lock", "dashboard", "lovelace", "node-red",
        "tasmota", "shelly", "hue", "light", "lights", "lamp", "bulb", "dimmer",
        "router", "wifi", "server", "backup", "firmware", "update", "script", "nas",
    ],
    CATEGORY_PROJECTS: [
        "project", "projects", "prototype", "3d print", "3d printer", "solder",
        "arduino", "raspberry", "workshop", "build", "woodworking", "drill", "saw",
        "shelf", "workbench", "diy", "crafts",
    ],
    CATEGORY_DAILY: [
        "buy", "shopping", "groceries", "milk", "bread", "eggs", "supermarket",
        "pharmacy", "doctor", "dentist", "appointment", "call", "laundry", "ironing",
        "vacuum", "dishes", "dishwasher", "trash", "garbage", "recycling", "bin",
        "bins", "bill", "bills", "invoice", "bank", "tax", "taxes", "insurance",
        "school", "kids", "birthday", "gift", "cook", "dinner", "lunch", "clean",
    ],
}

# Words Alexa may leave in front of a note, tried in this order
VOICE_PREFIXES: tuple[str, ...] = (
    "add to my shopping list ",
    "add to my to do list ",
    "add to my list ",
    "add to the list ",
    "put on my list ",
    "put on the list ",
    "add ",
    "put ",
    "write down ",
    "write ",
    "jot down ",
    "note down ",
    "remind me to ",
    "remind me about ",
    "remind me of ",
    "remind me that ",
    "remind me ",
    "remind ",
    "new idea for the ",
    "new idea for ",
    "new idea ",
    "idea for the ",
    "idea for ",
    "idea ",
    "new note for the ",
    "new note for ",
    "new note ",
    "note for the ",
    "note for ",
    "note ",
    "remember that ",
    "remember to ",
    "remember ",
    "brainstorm ",
    # Alexa has already removed the command word from the skill's text
    "for the ",
    "for ",
)
VOICE_SUFFIXES: tuple[str, ...] = (
    " on my shopping list",
    " on the shopping list",
    " to my shopping list",
    " on my to do list",
    " on the to do list",
    " to my to do list",
    " on my list",
    " on the list",
    " to my list",
    " to the list",
)

INTERACTION_MODEL: dict = {
    "interactionModel": {
        "languageModel": {
            "invocationName": "brainstorm",
            "intents": [
                {
                    "name": "CaptureIdeaIntent",
                    "slots": [{"name": "text", "type": "AMAZON.SearchQuery"}],
                    "samples": [
                        "note {text}",
                        "note down {text}",
                        "new note {text}",
                        "idea {text}",
                        "new idea {text}",
                        "entry {text}",
                        "new entry {text}",
                        "remember {text}",
                        "remember that {text}",
                        "add {text}",
                        "put {text}",
                        "write {text}",
                        "write down {text}",
                        "jot down {text}",
                    ],
                },
                {
                    "name": "ReminderIntent",
                    "slots": [{"name": "text", "type": "AMAZON.SearchQuery"}],
                    "samples": [
                        "remind me to {text}",
                        "remind me about {text}",
                        "remind me {text}",
                        "remind {text}",
                        "reminder {text}",
                    ],
                },
                {
                    "name": "DoneIntent",
                    "slots": [{"name": "text", "type": "AMAZON.SearchQuery"}],
                    "samples": [
                        "done",
                        "it is done",
                        "finished",
                        "done with {text}",
                        "check off {text}",
                        "finished with {text}",
                    ],
                },
                {
                    "name": "SnoozeIntent",
                    "samples": ["later", "remind me later", "snooze"],
                },
                {
                    "name": "ShowIdeasIntent",
                    "slots": [{"name": "category", "type": "AMAZON.SearchQuery"}],
                    "samples": [
                        "show",
                        "show list",
                        "show lists",
                        "show my lists",
                        "show {category}",
                        "display {category}",
                    ],
                },
                {
                    "name": "ReadAllIdeasIntent",
                    "samples": [
                        "all entries",
                        "all notes",
                        "read everything",
                        "read all notes",
                    ],
                },
                {
                    "name": "ReadIdeasIntent",
                    "slots": [{"name": "category", "type": "AMAZON.SearchQuery"}],
                    "samples": [
                        "announcement",
                        "read",
                        "read aloud",
                        "what is on my list",
                        "announcement for {category}",
                        "read {category}",
                        "read out {category}",
                        "category {category}",
                    ],
                },
                {"name": "AMAZON.CancelIntent", "samples": []},
                {"name": "AMAZON.HelpIntent", "samples": []},
                {"name": "AMAZON.StopIntent", "samples": []},
                {"name": "AMAZON.NavigateHomeIntent", "samples": []},
                {"name": "AMAZON.FallbackIntent", "samples": []},
            ],
            "types": [],
        }
    }
}

MESSAGES: dict[str, str] = {
    "and": "and",
    "reminder_spoken": "Reminder: {text}.",
    "battery_task": "Replace the battery: {name}",
    "battery_task_level": "Replace the battery: {name} ({level} %)",
    "reminder_title": "Brainstorm: Reminder",
    "action_done": "Done",
    "action_snooze": "1 hour later",
    "action_tomorrow": "Tomorrow",
    "digest_title": "Brainstorm: Today",
    "review_title": "Brainstorm: Weekly review",
    "digest_one": "Due today: {item}.",
    "digest_many": "{count} things are due today: {items}.",
    "review": (
        "Weekly review: {count} entries have been open for more than {days} days. "
        "The oldest are: {items}. Can any of them go?"
    ),
    "subtasks_prompt": (
        "Break this task from a to-do list down into three to six short, concrete "
        "subtasks in a sensible order. Answer only with the subtasks, one per "
        "line, without numbers and without an introduction. Write them as brief "
        "English to-do items that start with a verb. Do not repeat an existing "
        "subtask and do not make up names, numbers or dates.\n"
        "Task: {text}\n"
        "Category: {category}\n"
        "Existing subtasks: {existing}"
    ),
    "summarize_prompt": (
        "Summarize this reminder as a short, natural English sentence to read aloud. "
        "Do not add anything and do not leave out any entry: {message}"
    ),
    "list_line": "{category}: {items}.",
    "overview_empty": "You have no open notes in Brainstorm right now.",
    "overview": "You have {total} entries: {parts}. Which category?",
    "overview_part": "{count} in {category}",
    "category_empty": "There are no open entries in the category {category} right now.",
    "category_items": "{category} has {count}: {items}.",
    "prio_urgent": "🔥 Urgent",
    "prio_high": "🔴 High",
    "prio_low": "🟢 Low",
    "todo_priority": "Priority: {label}",
    "todo_source": "Source: {value}",
    "todo_device": "Device: {value}",
    "log_private": "Private entry",
    "log_unknown": "Unknown note",
    "log_added": "Idea captured",
    "log_completed": "Idea completed",
    "log_updated": "Idea changed",
    "log_deleted": "Idea deleted",
    "log_restored": "Idea restored",
    "log_imported": "{count} ideas imported from JSON",
    "export_active": "## Active ideas",
    "export_none": "_No active ideas_",
    "export_done": "## Completed / Archived",
    "llm_added": "Idea captured in '{category}' (priority: {priority}).",
    "llm_completed": "'{text}' was marked as done.",
    "llm_deleted": "Idea '{text}' was deleted.",
    "llm_delete_failed": "Deleting failed.",
    "skill_unreachable": "Home Assistant cannot be reached. Nothing was saved.",
    "skill_inactive": "Skill mode is not active in Brainstorm. Nothing was saved.",
    "skill_no_text": "I did not understand any text.",
    "skill_help": (
        "For example, say: note dim the basement light, remind me tomorrow at 8 to take "
        "out the bins, or read daily life."
    ),
    "skill_fallback": (
        "I did not get that. Start with note, for example: note buy shower gel. Or say: "
        "remind me tomorrow at 8 to take out the bins."
    ),
    "skill_fallback_later": "Okay, noted.",
    "skill_fallback_lost": (
        "Alexa did not report a sentence for Brainstorm in its history, so it was not "
        "saved. Please say it again, best with note in front."
    ),
    "skill_launch": "Brainstorm is ready. Say note and your idea, or say read.",
    "skill_save_failed": "I could not save that.",
    "skill_saved_no_time": "Saved, but without a reminder. I did not understand a time.",
    "skill_saved": "Saved{when}.",
    "skill_saved_in": "Saved under {category}{when}.",
    "skill_due": ", due {when}",
    "skill_you": "you",
    "skill_remind": "Okay, I will remind {who} {when} about {text}.",
    "skill_at_home": "when arriving home",
    "skill_at": "at {name}",
    "skill_here": "at this place",
    "skill_reminders_off": "Saved, but reminders are switched off.",
    "skill_in_past": "That time is in the past.",
    "skill_not_found": "I could not find that idea.",
    "skill_done": "Done: {text}.",
    "skill_here_is": "Here is {category}.",
    "skill_here_are": "Here are your lists.",
    "skill_no_reminder": "There is no reminder to move.",
    "skill_snoozed": "Okay, again {when}.",
    "display_mark_done": "Mark as done",
    "display_no_open": "No open ideas.",
    "display_open": "open",
    "display_urgent": "urgent",
    "display_today": "Today",
    "display_tomorrow": "Tomorrow",
    "display_more": "+ {count} more",
    "display_prio_urgent": "Urgent",
    "display_prio_high": "High",
    "display_prio_low": "Low",
}


def format_due(due: datetime, today: date) -> str:
    """Return a local due time the way a person says it."""
    hour = due.hour % 12 or 12
    suffix = "am" if due.hour < 12 else "pm"
    clock = f"{hour} {suffix}" if due.minute == 0 else f"{hour}:{due.minute:02d} {suffix}"
    day = due.date()
    if day == today:
        return f"today at {clock}"
    if day == today + timedelta(days=1):
        return f"tomorrow at {clock}"
    if day == today + timedelta(days=2):
        return f"the day after tomorrow at {clock}"
    weekday = _WEEKDAYS[day.weekday()].capitalize()
    month = _MONTHS[day.month - 1].capitalize()
    return f"on {weekday}, {month} {day.day}, at {clock}"


def count_entries(count: int) -> str:
    """Return a number of entries the way a person says it."""
    if count == 1:
        return "one entry"
    words = {value: word for word, value in _NUMBER_WORDS.items() if value <= 10}
    return f"{words.get(count, str(count))} entries"


PACK = LanguagePack(
    code="en",
    default_categories=ENGLISH_CATEGORIES,
    category_names={
        CATEGORY_HOME_GARDEN: "House & Garden",
        CATEGORY_SMARTHOME: "Smart Home",
        CATEGORY_PROJECTS: "Projects",
        CATEGORY_DAILY: "Daily Life",
        CATEGORY_BRAINSTORM: "Brainstorm",
    },
    category_aliases=CATEGORY_ALIASES,
    category_keywords=CATEGORY_KEYWORDS,
    and_word="and",
    category_stop_words=frozenset({"and", "the", "for", "of"}),
    alias_lead=(
        r"^(?:(?:for|in|on|at|to|under)\s+(?:the\s+|my\s+|our\s+)?)?"
    ),
    alias_tail=r"(:|\s+that\s+|\s+i\s+|\s+we\s+|\s*,\s*|\s+)(.+)$",
    topic_pattern=re.compile(
        r"^(?:in\s+|for\s+|on\s+|under\s+)?(?:project|topic|area)\s+"
        r"([a-zA-Z0-9\-_&]{2,30})(?::|\s+that\s+|\s+i\s+|\s+we\s+|\s*,\s*|\s+)(.+)$",
        re.IGNORECASE,
    ),
    priority_prefixes=(
        (
            re.compile(
                r"^(?:this\s+is\s+urgent|urgent|asap|immediately|right\s+away|emergency|"
                r"highest\s+priority|top\s+priority|priority\s+urgent)(?::|\s+|,)\s*(.+)$",
                re.IGNORECASE,
            ),
            PRIORITY_URGENT,
        ),
        (
            re.compile(
                r"^(?:this\s+is\s+important|important|high\s+priority|priority\s+high|"
                r"priority\s+1|priority\s+one)(?::|\s+|,)\s*(.+)$",
                re.IGNORECASE,
            ),
            PRIORITY_HIGH,
        ),
        (
            re.compile(
                r"^(?:low\s+priority|priority\s+low|priority\s+3|priority\s+three|"
                r"when\s+there'?s\s+time|someday|some\s+day|eventually|optional|no\s+rush)"
                r"(?::|\s+|,)\s*(.+)$",
                re.IGNORECASE,
            ),
            PRIORITY_LOW,
        ),
        (
            re.compile(
                r"^(?:normal\s+priority|medium\s+priority|priority\s+normal|priority\s+medium|"
                r"priority\s+2|priority\s+two)(?::|\s+|,)\s*(.+)$",
                re.IGNORECASE,
            ),
            PRIORITY_MEDIUM,
        ),
    ),
    clean_text=clean_text,
    format_typed=format_typed_text,
    extract_due=extract_spoken_due,
    parse_due=parse_due,
    strip_reminder_words=strip_reminder_words,
    extract_priority=extract_spoken_priority,
    starts_with_verb=starts_with_verb,
    build_glossary=build_glossary,
    validate_ai_rewrite=validate_ai_rewrite,
    messages=MESSAGES,
    format_due=format_due,
    count_entries=count_entries,
    reminder_words=ReminderWords(
        me=("i",),
        others=("she", "he", "they"),
        when=r"(?:when|once|as\s+soon\s+as)",
        home=(
            r"(?:(?:get|gets|come|comes|arrive|arrives)\s+(?:back\s+)?home"
            r"|(?:am|is|are|'m)\s+(?:back\s+)?home)"
        ),
        place=(
            r"(?:(?:get|gets|arrive|arrives)\s+(?:to|at|in)(?:\s+the)?"
            r"|(?:am|is|are)\s+(?:at|in)(?:\s+the)?|reach|reaches)"
        ),
        place_lead=r"(?:at|in)(?:\s+the)?",
        place_end=r"",
    ),
    skill_model=INTERACTION_MODEL,
    voice_prefixes=VOICE_PREFIXES,
    voice_suffixes=VOICE_SUFFIXES,
    garden_words=("garden", "house"),
    garden_match="garden",
    ai_cleanup_prompt=ai_cleanup_prompt,
)
