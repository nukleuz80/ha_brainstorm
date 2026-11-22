"""Several items spoken in one sentence, like "Butter, Eier und Milch".

A shopping list wants one entry per item, so it can be ticked off and sent to
Bring! item by item. Only the words a language names split a sentence, and
pairs like "Salz und Pfeffer" stay one item.
"""

from __future__ import annotations

import re

from .languages.common import LanguagePack

# More is not a list of items any more, but a sentence that happens to have commas
MAX_ITEMS = 12
# A long part is a sentence, not an item
MAX_ITEM_WORDS = 5
# Stands in for the separator inside a pair while the sentence is split
_KEEP = "\u0000"


def split_items(text: str, pack: LanguagePack) -> list[str]:
    """Return the items of a sentence, or the sentence alone if it is one item."""
    text = " ".join((text or "").split())
    if not pack.item_separators or not text or "#" in text:
        return [text] if text else []
    work = text
    for pair in pack.item_pairs:
        # The spaces of a pair are protected, so its separator does not split
        work = re.sub(
            rf"(?<!\w){re.escape(pair)}(?!\w)",
            lambda match: match.group(0).replace(" ", _KEEP),
            work,
            flags=re.IGNORECASE,
        )
    words = "|".join(re.escape(word) for word in pack.item_separators)
    # A comma between digits is a decimal comma: "1,5 kg Mehl"
    parts = re.split(
        rf"\s*(?:(?<!\d),|,(?!\d))\s*(?:(?:{words})\s+)?|\s+(?:{words})\s+",
        work,
        flags=re.IGNORECASE,
    )
    items = [part.replace(_KEEP, " ").strip(" .") for part in parts]
    if (
        len(items) < 2
        or len(items) > MAX_ITEMS
        or any(not item for item in items)
        or any(len(item.split()) > MAX_ITEM_WORDS for item in items)
    ):
        return [text]
    return [item[:1].upper() + item[1:] for item in items]

