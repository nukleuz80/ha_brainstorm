# Karten mit Beispieldaten

Rendert die echten Karten ohne Home Assistant, für Screenshots in den Videos. `demo.js` enthält erfundene Beispieldaten und ein minimales `hass`-Objekt, `index.html` ersetzt `ha-card` und `ha-icon`.

```bash
cp ../../../custom_components/brainstorm/cards/*.js .
python3 -m http.server 8799
chromium --headless --force-device-scale-factor=2 --window-size=640,1000 --virtual-time-budget=8000 \
  --screenshot=list.png "http://localhost:8799/index.html?card=list&w=560"
```

Parameter: `card=list|mindmap`, `w` (Breite in px), `cfg` (Kartenkonfiguration als JSON), `click` (Texte, die nacheinander angeklickt werden, getrennt mit `|`, z. B. `click=Projekte`). `vv/bin/python cards/shots.py` erzeugt alle Screenshots für die Videos als `crop_*.png`, `build.py` übernimmt sie in die Folien.

**Englisch:** `lang=en` schaltet Karten und Beispieldaten auf Englisch um. `vv/bin/python cards/shots.py en` legt die englischen Screenshots in `cards/en/` ab, mit denselben Dateinamen; Drehbücher mit `LANG = "en"` holen sie von dort.
