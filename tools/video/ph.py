"""Print the phonemes eSpeak makes of a text, e.g. ``vv/bin/python ph.py de "iPhone"``."""
from __future__ import annotations

import sys
from pathlib import Path

import piper
from piper.phonemize_espeak import EspeakPhonemizer


def main() -> None:
    phonemizer = EspeakPhonemizer(str(Path(piper.__file__).parent / "espeak-ng-data"))
    for text in sys.argv[2:]:
        sentences = phonemizer.phonemize(sys.argv[1], text)
        print(text, "=>", " | ".join("".join(s) for s in sentences))


if __name__ == "__main__":
    main()
