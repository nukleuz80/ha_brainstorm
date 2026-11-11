"""Transcribe the voiced scenes of a build with Whisper to check pronunciation.

Usage: WM=small vv/bin/python wavcheck.py out_script_features_en [en]
Prints one line per scene: file name and what Whisper heard.
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


def main() -> None:
    folder = ROOT / sys.argv[1]
    lang = sys.argv[2] if len(sys.argv) > 2 else "en"
    model = WhisperModel(os.environ.get("WM", "small"), device="cpu", compute_type="int8",
                         cpu_threads=int(os.environ.get("THREADS", "4")))
    # Changed scenes keep their old takes in the cache, only check the newest one
    newest: dict[str, Path] = {}
    for wav in folder.glob("c*_*_*.wav"):
        scene = "_".join(wav.name.split("_")[:2])
        if scene not in newest or wav.stat().st_mtime > newest[scene].stat().st_mtime:
            newest[scene] = wav
    for wav in (newest[k] for k in sorted(newest)):
        with wave.open(str(wav)) as src:
            audio = np.frombuffer(src.readframes(src.getnframes()), np.int16).astype(np.float32) / 32768
            rate = src.getframerate()
        audio = np.interp(np.arange(0, len(audio), rate / 16000), np.arange(len(audio)), audio)
        segments, _ = model.transcribe(audio.astype(np.float32), language=lang, beam_size=5)
        print(f"{wav.name.split('_')[0]}_{wav.name.split('_')[1]}: {' '.join(s.text.strip() for s in segments)}",
              flush=True)


if __name__ == "__main__":
    main()
