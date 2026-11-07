# Video-Werkzeuge

Erzeugen die Erklärvideos in [`docs/video`](../../docs/video/) ohne Schnittprogramm: Folien als HTML, per Chromium abfotografiert, deutsche Sprecherstimme mit [Piper](https://github.com/rhasspy/piper), zusammengesetzt mit ffmpeg samt Kapitelmarken.

| Datei | Zweck |
| :--- | :--- |
| `intro.py` | Wiederverwendbares Intro: Funken, Glühbirne schaltet sich wie eine Neonröhre ein, Schockwelle, Schriftzug im Farbverlauf, Jingle. `--title`, `--subtitle`, `--out` |
| `script.py` | Drehbuch: Kapitel, Szenen, Sprechertext und Ausspracheliste für englische Begriffe |
| `build.py` | Rendert das Drehbuch, setzt `intro.mp4` davor (`--no-intro` lässt es weg), `--frames` erzeugt nur die Folienbilder |

## Einrichtung

```bash
python3 -m venv vv
vv/bin/pip install imageio-ffmpeg piper-tts pillow numpy
curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx
curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx.json
cp ../../custom_components/brainstorm/brand/icon@2x.png icon.png
vv/bin/python intro.py --subtitle "Ideen sammeln mit Home Assistant"
vv/bin/python build.py
```

`build.py` ruft Chromium unter `/snap/bin/chromium` auf; passe den Pfad bei Bedarf an. Erzeugte Dateien (`out/`, `intro_frames/`, `*.mp4`, Stimme, `vv/`) gehören nicht ins Repository.
