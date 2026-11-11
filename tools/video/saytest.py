"""Speak each line of a text file and transcribe it with Whisper to check pronunciation.

Usage: WM=small PROMPT="JSON, Pushover" vv/bin/python saytest.py lines.txt
Needs ``vv/bin/pip install faster-whisper``. Lines may contain [[phonemes]].
"""
from __future__ import annotations

import os
import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parent
os.environ.setdefault("HF_HOME", str(ROOT / "tmp/hf"))

from faster_whisper import WhisperModel  # noqa: E402
from piper import PiperVoice  # noqa: E402


def main() -> None:
    voice = PiperVoice.load(str(ROOT / os.environ.get("VOICE", "de_DE-thorsten-high.onnx")))
    model = WhisperModel(os.environ.get("WM", "base"), device="cpu", compute_type="int8")
    wav_path = ROOT / "tmp/saytest.wav"
    wav_path.parent.mkdir(exist_ok=True)
    for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        with wave.open(str(wav_path), "wb") as out:
            voice.synthesize_wav(line, out)
        with wave.open(str(wav_path)) as src:
            audio = np.frombuffer(src.readframes(src.getnframes()), np.int16).astype(np.float32) / 32768
            rate = src.getframerate()
        # Whisper expects 16 kHz
        audio = np.interp(np.arange(0, len(audio), rate / 16000), np.arange(len(audio)), audio)
        segments, _ = model.transcribe(audio.astype(np.float32), language=os.environ.get("LANG_ASR", "de"),
                                       beam_size=5, initial_prompt=os.environ.get("PROMPT"))
        print(f"{line[:70]:70} -> {' '.join(s.text.strip() for s in segments)}", flush=True)


if __name__ == "__main__":
    main()
