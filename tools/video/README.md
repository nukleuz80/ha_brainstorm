# Video-Werkzeuge

Erzeugen die Erklärvideos in [`docs/video`](../../docs/video/) ohne Schnittprogramm: Folien als HTML, per Chromium abfotografiert, deutsche oder englische Sprecherstimme mit [Piper](https://github.com/rhasspy/piper), zusammengesetzt mit ffmpeg samt Kapitelmarken.

| Datei | Zweck |
| :--- | :--- |
| `intro.py` | Wiederverwendbares Intro: Funken, Glühbirne schaltet sich wie eine Neonröhre ein, Schockwelle, Schriftzug im Farbverlauf, Jingle. `--title`, `--subtitle`, `--out` |
| `script.py` | Drehbuch *Eigener Alexa-Skill* |
| `script_features.py` | Drehbuch *Die wichtigsten Funktionen* |
| `script_install.py` | Drehbuch *Installation* |
| `script_reminders.py` | Drehbuch *Erinnerungen & Benachrichtigungen* |
| `script_iphone.py` | Drehbuch *iPhone-Kurzbefehl* |
| `script_privacy.py` | Drehbuch *Privatsphäre, Freigaben & KI-Backlog* |
| `script_*_en.py` | Die sechs Drehbücher auf Englisch (`script_skill_en.py` ist der Alexa-Skill), mit `LANG = "en"` |
| `pron.py` | Aussprache englischer Begriffe als Lautschrift, gemeinsam für alle neuen Drehbücher |
| `ph.py` | Zeigt, welche Laute eSpeak für einen Text erzeugt: `ph.py de "iPhone"` |
| `saytest.py` | Spricht jede Zeile einer Textdatei und schreibt sie per Whisper wieder auf, zum Prüfen der Aussprache (`VOICE=` wählt die Stimme) |
| `wavcheck.py` | Schreibt die fertig gesprochenen Szenen eines Builds per Whisper auf: `wavcheck.py out_script_features_en en` |
| `build.py` | `build.py <drehbuch>` rendert ein Drehbuch, setzt `intro.mp4` davor (`--no-intro` lässt es weg), `--frames` erzeugt nur die Folienbilder |
| `cards/` | Echte Karten mit Beispieldaten für Screenshots, siehe [`cards/README.md`](cards/README.md) |

Jede Szene hat `v` (Folie) und `say` (Untertitel und Sprechertext). Weicht die Aussprache ab, steht der gesprochene Text in `speak`, und `SPOKEN` ersetzt englische Begriffe durch eine Lautschrift. 

**Englische Begriffe:** Die deutsche Stimme liest englische Wörter nach deutschen Regeln, aus *iPhone* wird „ih-fohne“, aus *JSON* „jotzohn“. Piper versteht Text in `[[ ]]` als Lautschrift, deshalb steht jeder englische Begriff in `pron.py` mit seinen Lauten, nur aus dem deutschen Lautinventar (kein ɹ, æ oder θ, die die Stimme nie gelernt hat). Neue Begriffe prüfst du so:

```bash
vv/bin/python ph.py de "Pushover"              # was eSpeak daraus macht
echo 'Wichtiges geht an [[pˈʊʃoʊvɐ]].' > t.txt
WM=small vv/bin/python saytest.py t.txt        # was Whisper hört (vv/bin/pip install faster-whisper)
```

**Englische Videos:** Ein Drehbuch mit `LANG = "en"` nutzt die Stimme `en_US-ryan-high`, die Screenshots aus `cards/en/`, `intro_en.mp4` und englische Beschriftungen (Kapitel, Konsole, Alexa-App). `SPOKEN` enthält dort nur wenige Ersetzungen wie *HACS* ➔ „hacks“, Lautschrift ist nicht nötig. Die MP4-Dateien heißen wie die deutschen mit `-en` am Ende.

Die Stimme wird nach dem Text zwischengespeichert, nach einer Änderung wird nur die geänderte Szene neu gesprochen. `COVERS` nennt die README-Abschnitte, die ein Video zeigt.

## Bei einem Release

Betrifft eine Änderung einen Abschnitt aus `COVERS`, passe die Szenen an, baue das Video neu und hänge es an das Release (`gh release upload vX.Y.Z <datei>.mp4`). Danach den Link in [`docs/videos.md`](../../docs/videos.md) bzw. [`docs/videos_en.md`](../../docs/videos_en.md) auf das neue Release setzen. Videos kommen nie ins Repository.

## Einrichtung

```bash
python3 -m venv vv
vv/bin/pip install imageio-ffmpeg piper-tts pillow numpy
curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx
curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx.json
cp ../../custom_components/brainstorm/brand/icon@2x.png icon.png
vv/bin/python intro.py --subtitle "Ideen sammeln mit Home Assistant"
vv/bin/python build.py script_features
# Englisch
curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/ryan/high/en_US-ryan-high.onnx
curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/ryan/high/en_US-ryan-high.onnx.json
vv/bin/python intro.py --subtitle "Collect ideas with Home Assistant" --out intro_en.mp4
vv/bin/python cards/shots.py en
vv/bin/python build.py script_features_en
```

`build.py` ruft Chromium unter `/snap/bin/chromium` auf; passe den Pfad bei Bedarf an. Erzeugte Dateien (`out*/`, `intro_frames/`, `*.mp4`, Stimme, `vv/`) gehören nicht ins Repository.
