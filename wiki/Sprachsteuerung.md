🏠 [Start](Home) · 🇬🇧 [English version](Voice-Control)

## ✨ Was Brainstorm versteht

- 🗣️ **Zwei-Wege-Spracherfassung:**
  - **Amazon Alexa:** Interaktiver Dialog-Modus (über Alexa Actionable Notifications Skill) und schnelle Direktbefehle ohne Musikunterbrechung oder ungewollte Einkaufslisten-Einträge.
  - **Home Assistant Assist:** Vollständige Unterstützung via lokaler Spracherkennung (Custom Sentences mit Wildcard-Support) und nativer Home Assistant Listen-Befehle.
- 🏷️ **Intelligente, automatische Kategorisierung:**
  - Mehrstufige semantische Heuristik: Erkennung von Präfixen (*„Garten: …“*), Präpositionen (*„im Garten …“*, *„für das Smarthome …“*) und Kontext-Schlagwörtern (Pool, Rasen, Heizung, ESPHome, Lampe etc.).
  - Standard-Kategorien: *Haus & Garten*, *Smarthome*, *Projekte*, *Alltag*, *Inbox*.

## Amazon Alexa

### Nur ausgewählte Echos nutzen
Standardmäßig kann jeder Echo Ideen erfassen. Zum Einschränken gehst du auf [**Einstellungen ➔ Geräte & Dienste ➔ Brainstorm Hub ➔ Konfigurieren ➔ Allgemeine Einstellungen & Export**](https://my.home-assistant.io/redirect/integration/?domain=brainstorm) und wählst die Echos unter **Echo-Geräte für die Spracheingabe** aus. Eine leere Liste bedeutet: alle Echos.

Die Alexa-Sprachabläufe laufen als Automationen und Skripte in deiner eigenen Home-Assistant-Konfiguration. Jeder Einstieg braucht deshalb diese Bedingung (`echo_device` enthält den aufrufenden Echo):

```yaml
- condition: template
  value_template: >-
    {% set allowed = state_attr('sensor.brainstorm_ideen_ubersicht', 'allowed_echos') %}
    {{ not allowed or echo_device in allowed }}
```

### Variante A: Interaktiver Dialog-Modus (Empfohlen)
Triggere den Dialog per Sprachbefehl, Szene oder Alexa-Routine:
> 🗣️ *„Alexa, Neue Idee“* oder *„Alexa, Brainstorm“*  
> 🤖 **Alexa:** *„Brainstorm bereit. Sprich deine Notiz oder sage Ansage.“*  
> 🗣️ **Du:** *„Im Garten müssen die Rosen geschnitten werden.“*  
> 🤖 **Alexa:** *„Gespeichert unter Haus & Garten.“*

#### 📱 Einrichtung der Alexa-Routinen (Wichtig gegen Musik-Konflikte)
Da **„Brainstorm“** auch der Name einer bekannten Rockband und diverser Songs ist, versucht Alexa bei Einzelwörtern ohne Routine standardmäßig, Musik über Amazon Music / Spotify abzuspielen. In Home Assistant fängt zwar ein unbedingter Stopp-Befehl anlaufende Streams ab – für ein absolut sauberes und lautloses Nutzererlebnis empfiehlt sich die Einrichtung von **zwei separaten Alexa-Routinen** in der Smartphone-App (da Amazon pro Routine immer nur genau **einen** Sprachauslöser erlaubt):

1. **Routine 1: Vollständiger Aufruf**
   * **Wenn Folgendes passiert:** Stimme ➔ `Alexa, öffne brainstorm`
   * **Aktion hinzufügen:** Smart Home ➔ Szenen ➔ **`Brainstorm Hauptmenü`** *(in Alexa werden Home Assistant Skripte als Szenen bereitgestellt)*
2. **Routine 2: Kurzer Direktaufruf**
   * **Wenn Folgendes passiert:** Stimme ➔ `Alexa, brainstorm`
   * **Aktion hinzufügen:** Smart Home ➔ Szenen ➔ **`Brainstorm Hauptmenü`**

> [!TIP]
> **Warum zwei getrennte Routinen?**  
> Alexa-Routinen haben bei Amazon immer oberste Priorität vor der allgemeinen Musik- und Websuche. Sobald beide Varianten als separate Routinen angelegt sind, unterdrückt Alexa die Musiksuche vollständig und startet unmittelbar und lautlos die Brainstorm-Sprachabfrage.

### Variante B: Schnelle Direktbefehle
Direkt in einem Satz sprechen (Automation sendet automatisch einen internen Stopp-Befehl für eventuell gestartete Skills/Musik und bestätigt direkt):
- 🗣️ *„Alexa, **Idee** Rasensprenger reparieren.“* ➔ `Haus & Garten`
- 🗣️ *„Alexa, **Notiere** Kellerlicht dimmen.“* ➔ `Smarthome`
- 🗣️ *„Alexa, **Merke dir für den Garten** Tomaten düngen.“* ➔ `Haus & Garten`
- 🗣️ *„Alexa, **Brainstorm** Balkonkraftwerk Ertrag auswerten.“* ➔ `Smarthome`
- 🗣️ *„Alexa, **Neue Idee für Projekte** Smart Mirror bauen.“* ➔ `Projekte`

### Variante C: Eigener Alexa-Skill (optional, ein Satz, eine Antwort)
Ohne Skill antwortet Alexa auf *„Alexa, notiere …“* oft zuerst mit einer Fehlermeldung, weil sie den Befehl nicht kennt. Mit deinem eigenen Skill gibt es nur eine einzige Antwort:

> 🗣️ *„Alexa, sage Brainstorm notiere Kellerlicht dimmen.“*  
> 🤖 **Alexa:** *„Gespeichert unter Smarthome.“*

Der Skill gehört dir allein und spricht nur mit deinem eigenen Home Assistant. **Voraussetzungen:** ein kostenloses [Amazon-Entwicklerkonto](https://developer.amazon.com/alexa/console/ask) mit demselben Konto wie deine Echos und ein aus dem Internet per HTTPS erreichbares Home Assistant (z. B. über Home Assistant Cloud). Home Assistant zeigt das Sprachmodell in seiner eigenen Sprache an. Es gibt Deutsch und Englisch, andere Sprachen bekommen das englische. Der Skill antwortet in der Sprache der Anfrage.

> 🎬 **Lieber zuschauen?** Das [Video zur Einrichtung](https://github.com/nukleuz80/ha_brainstorm/blob/main/docs/video-alexa-skill.md) zeigt jede Einstellung in einem eigenen Kapitel (6 Minuten).

1. Gehe in Home Assistant auf **Brainstorm Hub ➔ Konfigurieren ➔ Alexa-Spracheingabe & Skill**, wähle **Skill** oder **Beide** und klicke auf **Weiter**. Lass dieses Fenster offen, es zeigt die beiden Felder zum Kopieren.
2. Klicke in der [Alexa-Entwicklerkonsole](https://developer.amazon.com/alexa/console/ask) auf **Create Skill** und wähle: Name `Brainstorm`, Sprache **German (DE)**, Typ **Custom**, Hosting **Alexa-hosted (Python)**, Vorlage **Start from Scratch**.
3. Öffne **Build ➔ Interaction Model ➔ JSON Editor**, ersetze den Inhalt durch das Feld **Sprachmodell**, klicke auf **Save** und danach auf **Build** und warte auf die Erfolgsmeldung.
4. Ersetze im Tab **Code** den Inhalt von `lambda_function.py` durch das Feld **Skill-Code** und klicke auf **Deploy**.
5. Stelle im Tab **Test** oben **Development** ein.
6. Klicke in Home Assistant auf **Absenden** und sprich am Echo: *„Alexa, sage Brainstorm notiere Testidee.“* Die erste Anfrage koppelt deinen Skill, andere Skills werden danach abgewiesen. Unter **Konfigurieren** siehst du die Kopplung und die letzte Anfrage.

**Hinweise:** Halte den Skill-Code geheim, er enthält deine geheime Adresse. Wurde sie bekannt, erzeugst du dort eine neue und kopierst den Skill-Code erneut. Die Echo-Auswahl und die Geräteanzeige gelten auch im Skill. Dafür lernt Home Assistant jeden Echo beim ersten Satz aus dem Alexa-Verlauf (das braucht die Integration Alexa Media); dieser erste Satz kann bis zu 3,5 Sekunden länger dauern. Kommt der Eintrag im Verlauf später, wird die Idee trotzdem gespeichert und der Echo nachgetragen. Im Menü brauchst du ein Befehlswort wie *„notiere …“* oder einen Satzanfang wie *„wir brauchen …“*, *„wir müssen …“*, *„ich muss …“*. **Freie Sätze ohne Befehlswort** (*„Alexa, sage Brainstorm Duschgel ist alle“*) gibt Alexa dem Skill nicht weiter. Seit v1.6.20 holt Home Assistant solche Sätze aus dem Alexa-Verlauf des Echos (über Alexa Media) und speichert sie trotzdem. Alexa antwortet sofort mit *„Okay, notiert“*. Den Satz schreibt Alexa erst mit dieser Antwort in den Verlauf, deshalb erscheint der Eintrag wenige Sekunden später. Home Assistant erkennt den passenden Verlaufseintrag an genau dieser Antwort. Kommt innerhalb einer Minute keiner, meldet Home Assistant das als Benachrichtigung, statt den Satz still zu verlieren. Für die Alexa-App, die keinen Verlauf meldet, bleibt der Hinweis auf ein Befehlswort. Dafür musst du den Skill-Code einmal neu kopieren. Im Modus **Skill** solltest du die Alexa-Routinen für *„öffne Brainstorm“* aus Variante A löschen, sonst startet statt des Skills der alte Dialog. Der Modus **Skill** schaltet die bisherige Erfassung ab, wenn deine Automation das Attribut `voice_mode` von `sensor.brainstorm_ideen_ubersicht` prüft:

```yaml
- condition: template
  value_template: "{{ state_attr('sensor.brainstorm_ideen_ubersicht', 'voice_mode') != 'skill' }}"
```

**Falls es nicht klappt:** *„Ich weiß nicht, wie ich dabei helfen soll“* bedeutet meist, dass der **Build** fehlt, im Tab **Test** nicht **Development** eingestellt ist oder Konsole und Echo verschiedene Amazon-Konten nutzen. Teste den Satz zuerst im Tab **Test**. Sagt Alexa, die Idee wurde nicht gespeichert, prüfe den Modus und die Erreichbarkeit von Home Assistant.

---

## Home Assistant Assist

Assist versteht deine Notizen sowohl über dedizierte Sprachmuster als auch über Standard-Listenbefehle:

### Freie Brainstorm-Befehle:
* 🗣️ *„Setze Rasenmähen auf Brainstorm“*
* 🗣️ *„Neue Idee Blumen gießen“*
* 🗣️ *„Notiere Backup der Datenbank erstellen“*
* 🗣️ *„Merke dir Reifen wechseln“*
* 🗣️ *„Brainstorm Zigbee Bewegungsmelder testen“*

Die Vorlagen liegen unter [`examples/custom_sentences/de/brainstorm.yaml`](https://github.com/nukleuz80/ha_brainstorm/blob/main/examples/custom_sentences/de/brainstorm.yaml) und [`examples/intent_script.de.yaml`](https://github.com/nukleuz80/ha_brainstorm/blob/main/examples/intent_script.de.yaml). Kopiere die erste nach `/config/custom_sentences/de/`, ergänze die zweite in deinem `intent_script` und starte Home Assistant neu.

### Native Listenbefehle:
* 🗣️ *„Setze Rasenmähen auf die Liste Brainstorm Haus und Garten“*
* 🗣️ *„Füge Milch zu Brainstorm Inbox hinzu“*
* 🗣️ *„Hake Rasenmähen auf Brainstorm Haus und Garten ab“*

## iPhone: Kurzbefehl mit Siri, Action-Taste oder Rückseite
Der schnellste Weg vom iPhone: auslösen, sprechen, fertig, ganz ohne eine App zu öffnen. Voraussetzung ist die Home Assistant Companion-App.

1. Lege in der App **Kurzbefehle** einen neuen Kurzbefehl namens **Brainstorm** an. Der Name ist auch dein Siri-Satz.
2. Füge **Text diktieren** hinzu, Sprache **Deutsch**, Hören stoppen **Nach einer Pause**.
3. Füge von **Home Assistant** die Aktion **Aktion ausführen** hinzu und wähle **Idee hinzufügen** (`brainstorm.add_idea`).
4. Füge in das Datenfeld dieses JSON ein und setze zwischen die Anführungszeichen hinter `"text":` die Variable **Diktierter Text**:
   ```json
   {"text": "", "source": "siri", "device": "iPhone"}
   ```
5. Lege den Auslöser fest:
   - **Action-Taste:** **Einstellungen ➔ Action-Taste ➔ Kurzbefehl ➔ Brainstorm**
   - **Rückseite:** **Einstellungen ➔ Bedienungshilfen ➔ Tippen ➔ Auf Rückseite tippen ➔ Doppeltippen ➔ Brainstorm**
   - **Siri:** *„Hey Siri, Brainstorm“*

Die Notiz erscheint als **Siri (iPhone)** mit Apfel-Logo. Den Gerätenamen kannst du im JSON frei wählen.

> [!TIP]
> Meldet der Kurzbefehl *„Die Daten konnten nicht gelesen werden“*, ist das Datenfeld kein gültiges JSON. Oft hat das iPhone beim Tippen typografische Anführungszeichen eingesetzt. Füge den Text deshalb per Kopieren ein oder schalte vorübergehend **Einstellungen ➔ Allgemein ➔ Tastatur ➔ Intelligente Interpunktion** aus.

## Mikrofon in der Schnelleingabe
Neben dem Feld *Blitz-Idee* der Listenkarte gibt es ein **🎙️**. Tippen, sprechen, und der Text steht zum Prüfen im Feld. Die Aufnahme endet bei einer Sprechpause, durch erneutes Tippen oder nach 30 Sekunden. Genutzt wird deine bevorzugte Assist-Pipeline, die dafür eine Spracherkennung braucht. Das Mikrofon erscheint nur über HTTPS, also in der Companion-App oder über eine HTTPS-Adresse wie Home Assistant Cloud. Abschalten kannst du es in den Karteneinstellungen oder mit `show_mic: false`.

## 💬 Beispiele


### Alexa ohne Skill

Dafür brauchst du die Integration Alexa Media und eigene Automationen; Vorlagen (englisch, zum Anpassen) liegen in [`examples/`](https://github.com/nukleuz80/ha_brainstorm/tree/main/examples/). Die Einrichtung steht [oben](#amazon-alexa).

**Dialog (Variante A)**

> 🗣️ „Alexa, Brainstorm“
> 🤖 „Brainstorm bereit. Sprich deine Notiz oder sage Ansage.“
> 🗣️ „Im Garten müssen die Rosen geschnitten werden.“
> 🤖 „Gespeichert unter Haus & Garten.“

**Direkt in einem Satz (Variante B)**

| Du sagst | Ergebnis |
|---|---|
| „Alexa, **Idee** Rasensprenger reparieren“ | Haus & Garten |
| „Alexa, **Notiere** Kellerlicht dimmen“ | Smarthome |
| „Alexa, **Merke dir für den Garten** Tomaten düngen“ | Haus & Garten |
| „Alexa, **Neue Idee für Projekte** Smart Mirror bauen“ | Projekte |
| „Alexa, **Brainstorm** Balkonkraftwerk auswerten“ | Smarthome |

### Alexa mit eigenem Skill

Mit dem Skill antwortet Alexa nur einmal. Die Einrichtung steht [oben](#variante-c-eigener-alexa-skill-optional-ein-satz-eine-antwort) und als 🎬 [Video mit einem Kapitel pro Einstellung](https://github.com/nukleuz80/ha_brainstorm/blob/main/docs/video-alexa-skill.md). Alle Sätze beginnen mit **„Alexa, sage Brainstorm …“**, nach *„Alexa, öffne Brainstorm“* auch ohne diesen Anfang.

| Ziel | Beispiele |
|---|---|
| Notiz anlegen | „… **notiere** Kellerlicht dimmen“, „… **neue Idee** Hochbeet bauen“, „… **merke dir** Reifen wechseln“, „… **schreib auf** Druckerpatronen“, „… **setze** Milch auf Einkaufen“ |
| Satzanfang ohne Befehlswort | „… **wir brauchen** Batterien“, „… **wir müssen** den Keller aufräumen“, „… **ich sollte** den Arzt anrufen“ |
| Erinnerung | „… **erinnere mich** morgen um 8 an den Müll“, „… **termin** Zahnarzt am 25.11. um 14 Uhr“ |
| Abhaken | „… **erledigt** Müll rausbringen“, „… **hake** Milch **ab**“, „… **fertig** Rasen mähen“; nur „… **erledigt**“ hakt die letzte Erinnerung ab |
| Verschieben | „… **später**“ schiebt die letzte Erinnerung um eine Stunde |
| Liste zeigen (Echo Show) | „… **zeige meine Listen**“, „… **zeige** Einkaufen“ |
| Vorlesen | „… **Ansage**“, „… **lies** Haus und Garten“, „… **Kategorie** Projekte“, „… **alles vorlesen**“ |
| Freier Satz | „… Duschgel ist alle“ → Alexa sagt „Okay, notiert“, der Eintrag kommt wenige Sekunden später aus dem Alexa-Verlauf |

> [!TIP]
> Freie Sätze ohne Befehlswort klappen nur am Echo, nicht in der Alexa-App, weil die App keinen Verlauf meldet.

### Home Assistant Assist

Die Satzvorlagen liegen in [`examples/custom_sentences/de/brainstorm.yaml`](https://github.com/nukleuz80/ha_brainstorm/blob/main/examples/custom_sentences/de/brainstorm.yaml), das Skript in [`examples/intent_script.de.yaml`](https://github.com/nukleuz80/ha_brainstorm/blob/main/examples/intent_script.de.yaml).

| Du sagst | Wirkung |
|---|---|
| „Setze Rasenmähen auf Brainstorm“ | neue Notiz |
| „Neue Idee Blumen gießen“ | neue Notiz |
| „Notiere Backup der Datenbank erstellen“ | neue Notiz, Kategorie Smarthome |
| „Merke dir Reifen wechseln“ | neue Notiz |
| „Füge Milch zu Brainstorm Inbox hinzu“ | Notiz über die To-do-Liste |
| „Setze Rasenmähen auf die Liste Brainstorm Haus und Garten“ | Notiz direkt in der Kategorie |
| „Hake Rasenmähen auf Brainstorm Haus und Garten ab“ | erledigt |

Jede Kategorie ist auch eine To-do-Liste (`todo.brainstorm_…`). Darum funktionieren die normalen Listenbefehle von Assist ohne Vorlagen.

### iPhone und Siri

Ein Kurzbefehl mit **Text diktieren** und der Home-Assistant-Aktion `brainstorm.add_idea`:

```json
{"text": "<Diktierter Text>", "source": "siri", "device": "iPhone"}
```

> 🗣️ „Hey Siri, Brainstorm“ → „Fahrradschloss kaufen, ist dringend“ → Notiz mit Priorität **Dringend**.

Auslösen geht auch mit der Action-Taste oder per Doppeltippen auf die Rückseite. Die Schritte stehen [oben](#iphone-kurzbefehl-mit-siri-action-taste-oder-rückseite).

### Mikrofon in der Karte

Tippe auf 🎙️ neben dem Feld *Blitz-Idee* und sprich. Der Text steht danach zum Prüfen im Feld. Die Aufnahme endet bei einer Pause, durch erneutes Tippen oder nach 30 Sekunden. Das geht nur über HTTPS und mit einer Assist-Pipeline mit Spracherkennung.

## Was Brainstorm aus einem Satz liest

Kategorie, Vorsätze und `!`-Tags gelten für jeden Text, ob gesprochen oder getippt. Prioritätswörter mitten im Satz und Termine werden nur aus gesprochenen Sätzen gelesen. Getippter Text wird sonst nur bei der Rechtschreibung korrigiert.

### Kategorie

Brainstorm prüft der Reihe nach:

| Regel | Beispiel | Kategorie |
|---|---|---|
| Vorsatz mit Doppelpunkt | „Smarthome: Sensor im Bad tauschen“ | Smarthome |
| Eckige Klammern | „[Alltag] Oma anrufen“ | Alltag |
| „Projekt / Thema / Bereich …“ | „Projekt Werkstatt Regal bauen“ | Projekte |
| Satzanfang mit „für / im / beim / zum …“ | „Für den Garten Rindenmulch“, „Im Haushalt Entkalker kaufen“ | Haus & Garten, Alltag |
| Hashtag (bleibt als Tag erhalten) | „Rasen vertikutieren #garten“ | Haus & Garten |
| Schlüsselwörter im Satz | „Zigbee Bewegungsmelder testen“ | Smarthome |
| sonst | „Oma anrufen“ | Standardkategorie (anfangs *Inbox*) |

Mitgelieferte Stichwörter, je nach Kategorie:

- **Haus & Garten:** garten, haus, balkon, terrasse, rasen, …
- **Smarthome:** smart home, home assistant, iot, zigbee, sensor, …
- **Projekte:** projekt, basteln, werkstatt, diy, …
- **Alltag:** haushalt, einkauf, familie, privat, …
- **Brainstorm:** mindmap, …

Eigene Kategorien legst du unter **Konfigurieren ➔ Kategorien verwalten** an. Ihr Name zählt dann auch als Stichwort.

### Priorität

| Priorität | Am Satzanfang (gesprochen und getippt) | Irgendwo im gesprochenen Satz | Tag (überall) |
|---|---|---|---|
| 🔥 Dringend | „Dringend: …“, „Sofort …“, „Eilig, …“, „Notfall …“, „Prio dringend …“ | „dringend“, „ganz dringend“, „eilig“, „sofort“ | `!dringend`, `!urgent`, `!sofort` |
| 🔴 Hoch | „Wichtig: …“, „Prio hoch …“, „Prio 1 …“, „Hohe Priorität …“ | „wichtig“, „sehr wichtig“, „unbedingt“ | `!wichtig`, `!hoch`, `!high` |
| 🟡 Mittel | – | – | `!mittel`, `!normal` |
| 🟢 Niedrig | „Irgendwann …“, „Wenn Zeit ist, …“, „Optional …“, „Prio niedrig …“ | „irgendwann (mal)“, „wenn Zeit ist“ | `!niedrig`, `!low` |

Ohne Angabe gilt **Mittel**. Verneinungen und Fragen zählen nicht: *„nicht so dringend“* oder *„ist das wichtig?“* ändern die Priorität nicht. Das erkannte Wort wird aus dem Text entfernt: *„Dringend: Wasserhahn reparieren“* wird zu *Wasserhahn reparieren* mit 🔥.

### Erinnerung und Termin

**Überall derselbe Dialog:** Der Bearbeiten-Dialog von Liste und Mindmap hat dieselben Felder in derselben Reihenfolge. Callout, Rahmen, Form, Nummerierung und Sortierung gehen also auch aus der Liste, die übergeordnete Aufgabe auch aus der Mindmap.

**Wiederholen:** *Wiederholen* im Bearbeiten-Dialog lässt eine Notiz jeden Tag, Werktag, jede Woche, alle 2 Wochen, jeden Monat oder jedes Jahr wiederkommen. Beim Abhaken erscheint sofort die nächste Runde mit dem nächsten Termin und wieder offenen Unteraufgaben; die erledigte bleibt unter *Erledigt*. Spät abgehakt überspringt sie verpasste Termine. Wird die erledigte wieder aktiviert, verschwindet die neue Runde, solange sie noch offen ist. 🔁 kennzeichnet solche Notizen.

Ein gesprochener Satz mit einem Zeitpunkt bekommt eine Fälligkeit, z. B. nach **„erinnere mich (daran)“**, **„vergiss nicht“**, **„denk dran“** oder bei einem **„Termin“**. Abschalten kannst du das unter **Allgemeine Einstellungen ➔ Datum aus gesprochenem Text als Termin übernehmen**. Liegt der Zeitpunkt schon in der Vergangenheit, bleibt der Satz unverändert.

| Du sagst | Fällig am |
|---|---|
| „… heute Abend“ | heute 19:00 |
| „… morgen“ | morgen 09:00 |
| „… übermorgen früh“ | übermorgen 08:00 |
| „… am Freitag um halb neun“ | Freitag 08:30 |
| „… nächste Woche“ | Montag nächster Woche 09:00 |
| „… in 20 Minuten“, „in 2 Stunden“, „in 3 Tagen“ | jetzt + Zeitraum |
| „… am 25.11. um 14 Uhr“ | 25.11. 14:00 |
| „… am zweiten Dezember viertel nach drei“ | 02.12. 03:15 (mit „nachmittags“ 15:15) |

Tageszeiten ohne Uhrzeit: früh/morgens 8:00, vormittags 10:00, mittags 12:00, nachmittags 15:00, abends 19:00, nachts 22:00. Ohne jede Zeit gilt **9:00**.

Wie und wo erinnert wird, stellst du unter [Erinnerungen](Einstellungen#integration) ein.
