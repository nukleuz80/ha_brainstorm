# Video-Werkzeuge

Erzeugen die Erklärvideos in [`docs/video`](../../docs/video/) ohne Schnittprogramm: Folien als HTML, per Chromium abfotografiert, deutsche Sprecherstimme mit [Piper](https://github.com/rhasspy/piper), zusammengesetzt mit ffmpeg samt Kapitelmarken.

| Datei | Zweck |
| :--- | :--- |
| `intro.py` | Wiederverwendbares Intro: Funken, Glühbirne schaltet sich wie eine Neonröhre ein, Schockwelle, Schriftzug im Farbverlauf, Jingle. `--title`, `--subtitle`, `--out` |
| `script.py` | Drehbuch *Eigener Alexa-Skill* |
| `script_features.py` | Drehbuch *Die wichtigsten Funktionen* |
| `script_install.py` | Drehbuch *Installation* |
| `build.py` | `build.py <drehbuch>` rendert ein Drehbuch, setzt `intro.mp4` davor (`--no-intro` lässt es weg), `--frames` erzeugt nur die Folienbilder |
| `cards/` | Echte Karten mit Beispieldaten für Screenshots, siehe [`cards/README.md`](cards/README.md) |

Jede Szene hat `v` (Folie) und `say` (Untertitel und Sprechertext). Weicht die Aussprache ab, steht der gesprochene Text in `speak`, und `SPOKEN` ersetzt englische Begriffe durch eine Lautschrift. Die Stimme wird nach dem Text zwischengespeichert, nach einer Änderung wird nur die geänderte Szene neu gesprochen. `COVERS` nennt die README-Abschnitte, die ein Video zeigt.

## Bei einem Release

Betrifft eine Änderung einen Abschnitt aus `COVERS`, passe die Szenen an, baue das Video neu und hänge es an das Release (`gh release upload vX.Y.Z <datei>.mp4`). Danach den Link in [`docs/videos.md`](../../docs/videos.md) auf das neue Release setzen. Videos kommen nie ins Repository.

## Einrichtung

```bash
python3 -m venv vv
vv/bin/pip install imageio-ffmpeg piper-tts pillow numpy
curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx
curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx.json
cp ../../custom_components/brainstorm/brand/icon@2x.png icon.png
vv/bin/python intro.py --subtitle "Ideen sammeln mit Home Assistant"
vv/bin/python build.py script_features
```

`build.py` ruft Chromium unter `/snap/bin/chromium` auf; passe den Pfad bei Bedarf an. Erzeugte Dateien (`out*/`, `intro_frames/`, `*.mp4`, Stimme, `vv/`) gehören nicht ins Repository.
