# 📘 Brainstorm Hub – Anleitung mit Beispielen

🇬🇧 [English version](guide.md) · ⬅️ [Zurück zur README](../README_de.md)

Diese Anleitung zeigt an Beispielen, was du **sagen**, **schreiben**, **einstellen** und **automatisieren** kannst. Die Installation steht in der [README](../README_de.md#-installation).

## Inhalt

1. [Sagen – Sprachbefehle](#1-sagen--sprachbefehle)
   - [Alexa ohne Skill](#11-alexa-ohne-skill)
   - [Alexa mit eigenem Skill](#12-alexa-mit-eigenem-skill)
   - [Home Assistant Assist](#13-home-assistant-assist)
   - [iPhone und Siri](#14-iphone-und-siri)
   - [Mikrofon in der Karte](#15-mikrofon-in-der-karte)
   - [KI-Assistent (LLM)](#16-ki-assistent-llm)
2. [Was Brainstorm aus einem Satz liest](#2-was-brainstorm-aus-einem-satz-liest)
   - [Kategorie](#21-kategorie)
   - [Priorität](#22-priorität)
   - [Erinnerung und Termin](#23-erinnerung-und-termin)
3. [Schreiben – Karten bedienen](#3-schreiben--karten-bedienen)
   - [Formatierung und Links](#31-formatierung-und-links)
   - [Listenkarte](#32-listenkarte)
   - [Mindmap: Maus, Finger, Tastatur](#33-mindmap-maus-finger-tastatur)
4. [Einstellen](#4-einstellen)
   - [Integration](#41-integration)
   - [Listenkarte](#42-listenkarte-brainstorm-card)
   - [Mindmap-Karte](#43-mindmap-karte-brainstorm-mindmap-card)
5. [Automatisieren](#5-automatisieren)
   - [Dienste](#51-dienste)
   - [Ereignisse](#52-ereignisse)
   - [Sensor-Attribute](#53-sensor-attribute)
   - [Fertige Rezepte](#54-fertige-rezepte)

---

## 1. Sagen – Sprachbefehle

### 1.1 Alexa ohne Skill

Dafür brauchst du die Integration Alexa Media und eigene Automationen; Vorlagen (englisch, zum Anpassen) liegen in [`examples/`](../examples/). Die Einrichtung steht in der [README](../README_de.md#1-amazon-alexa).

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

### 1.2 Alexa mit eigenem Skill

Mit dem Skill antwortet Alexa nur einmal. Die Einrichtung steht in der [README](../README_de.md#variante-c-eigener-alexa-skill-optional-ein-satz-eine-antwort) und als 🎬 [Video mit einem Kapitel pro Einstellung](video-alexa-skill.md). Alle Sätze beginnen mit **„Alexa, sage Brainstorm …“**, nach *„Alexa, öffne Brainstorm“* auch ohne diesen Anfang.

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

### 1.3 Home Assistant Assist

Die Satzvorlagen liegen in [`examples/custom_sentences/de/brainstorm.yaml`](../examples/custom_sentences/de/brainstorm.yaml), das Skript in [`examples/intent_script.de.yaml`](../examples/intent_script.de.yaml).

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

### 1.4 iPhone und Siri

Ein Kurzbefehl mit **Text diktieren** und der Home-Assistant-Aktion `brainstorm.add_idea`:

```json
{"text": "<Diktierter Text>", "source": "siri", "device": "iPhone"}
```

> 🗣️ „Hey Siri, Brainstorm“ → „Fahrradschloss kaufen, ist dringend“ → Notiz mit Priorität **Dringend**.

Auslösen geht auch mit der Action-Taste oder per Doppeltippen auf die Rückseite. Die Schritte stehen in der [README](../README_de.md#3-iphone-kurzbefehl-mit-siri-action-taste-oder-rückseite).

### 1.5 Mikrofon in der Karte

Tippe auf 🎙️ neben dem Feld *Blitz-Idee* und sprich. Der Text steht danach zum Prüfen im Feld. Die Aufnahme endet bei einer Pause, durch erneutes Tippen oder nach 30 Sekunden. Das geht nur über HTTPS und mit einer Assist-Pipeline mit Spracherkennung.

### 1.6 KI-Assistent (LLM)

Ein Gesprächsagent wie OpenAI, Google Gemini oder Ollama kann Brainstorm bedienen, wenn du in seinen Optionen unter **Home Assistant steuern** zusätzlich **Brainstorm Hub** auswählst. Er bekommt diese Werkzeuge:

| Werkzeug | Beispiel |
|---|---|
| `brainstorm_add_idea` | „Schreib auf, dass wir Grillkohle brauchen, für Samstag.“ |
| `brainstorm_get_ideas` | „Was steht noch auf meiner Gartenliste?“ |
| `brainstorm_complete_idea` | „Die Grillkohle habe ich gekauft.“ |
| `brainstorm_delete_idea` | „Lösch die Notiz mit dem Fahrradschloss.“ |
| `brainstorm_list_categories` | „Welche Listen gibt es?“ |

Unter **Konfigurieren ➔ KI** kannst du außerdem einen KI-Dienst wählen, der gesprochene Texte aufräumt (Füllwörter, Satzzeichen).

---

## 2. Was Brainstorm aus einem Satz liest

Kategorie, Vorsätze und `!`-Tags gelten für jeden Text, ob gesprochen oder getippt. Prioritätswörter mitten im Satz und Termine werden nur aus gesprochenen Sätzen gelesen. Getippter Text wird sonst nur bei der Rechtschreibung korrigiert.

### 2.1 Kategorie

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

### 2.2 Priorität

| Priorität | Am Satzanfang (gesprochen und getippt) | Irgendwo im gesprochenen Satz | Tag (überall) |
|---|---|---|---|
| 🔥 Dringend | „Dringend: …“, „Sofort …“, „Eilig, …“, „Notfall …“, „Prio dringend …“ | „dringend“, „ganz dringend“, „eilig“, „sofort“ | `!dringend`, `!urgent`, `!sofort` |
| 🔴 Hoch | „Wichtig: …“, „Prio hoch …“, „Prio 1 …“, „Hohe Priorität …“ | „wichtig“, „sehr wichtig“, „unbedingt“ | `!wichtig`, `!hoch`, `!high` |
| 🟡 Mittel | – | – | `!mittel`, `!normal` |
| 🟢 Niedrig | „Irgendwann …“, „Wenn Zeit ist, …“, „Optional …“, „Prio niedrig …“ | „irgendwann (mal)“, „wenn Zeit ist“ | `!niedrig`, `!low` |

Ohne Angabe gilt **Mittel**. Verneinungen und Fragen zählen nicht: *„nicht so dringend“* oder *„ist das wichtig?“* ändern die Priorität nicht. Das erkannte Wort wird aus dem Text entfernt: *„Dringend: Wasserhahn reparieren“* wird zu *Wasserhahn reparieren* mit 🔥.

### 2.3 Erinnerung und Termin

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

Wie und wo erinnert wird, stellst du unter [Erinnerungen](#41-integration) ein.

---

## 3. Schreiben – Karten bedienen

### 3.1 Formatierung und Links

In jedem Notiztext funktioniert ein kleines Markdown:

| Du schreibst | Ergebnis |
|---|---|
| `**Milch**` | **Milch** |
| `*bald*` | *bald* |
| `~~erledigt~~` | ~~erledigt~~ |
| `` `sensor.bad` `` | `sensor.bad` |
| `[Anleitung](https://example.com)` | anklickbarer Link |
| `https://example.com` | wird automatisch ein Link |

Mit **Intelligente Formatierung** (Allgemeine Einstellungen) werden gesprochene Notizen außerdem aufgeräumt: Füllwörter fallen weg, der Anfang wird großgeschrieben. Im **Glossar** stehen eigene Begriffe, einer pro Zeile (`Lenia`), oder Korrekturen (`fehler = Richtig`). Namen von Personen und Kategorien kennt Brainstorm von selbst.

### 3.2 Listenkarte

| Aktion | So geht es |
|---|---|
| Neue Notiz | in *Blitz-Idee* tippen, z. B. `Garten: Baum schneiden`, und **Enter** |
| Kategorie und Priorität vorgeben | Auswahlfelder 🏷️ und Priorität unter dem Eingabefeld (*Auto* erkennt sie aus dem Text) |
| Bearbeiten | auf den Text oder den Stift tippen; im Dialog speichert **Strg+Enter** |
| Kontextmenü | lange auf eine Notiz drücken |
| Abhaken | Kreis links antippen, im Reiter Erledigt wieder aktivieren |
| Löschen | ✕ |
| Unteraufgabe | Unteridee anlegen, oder Notiz ziehen und auf eine andere fallen lassen |
| Ein- und ausrücken | Knöpfe *Unter vorherige Aufgabe einrücken* und *Ausrücken* |
| Unteraufgaben vorschlagen | ✨ lässt die KI Unteraufgaben vorschlagen (KI unter Konfigurieren) |
| Sortieren | halten und ziehen |
| Filtern | Kategorie-Pills oben |
| Farbmodus | 🌈 bunt / 🎨 Theme-Farben im Kopf |
| Zur Mindmap | 🧠 im Kopf öffnet sie als Ebene, **Esc** schließt |

### 3.3 Mindmap: Maus, Finger, Tastatur

**Maus und Finger**

| Aktion | So geht es |
|---|---|
| Verschieben | Notiz ziehen |
| Unterpunkt anlegen | Notiz auswählen und **Tab** |
| Text ändern | Doppelklick auf die Notiz |
| Mehrere auswählen | **Umschalt** oder **Strg** + Klick, mit gedrückter **Umschalt**-Taste einen Rahmen ziehen, oder ⬚ und dann Rahmen ziehen (am Handy) |
| Zoomen | Mausrad oder zwei Finger |
| Fläche bewegen | leere Fläche ziehen |
| Zweig ein-/ausklappen | Knopf am Ast, oder **→** auf einem eingeklappten Punkt |
| Als Bild speichern | 🖼️ |
| Vollbild | ⛶ |
| Suchen und filtern | 🔍, oder **/** bzw. **Strg+F** auf der Map |
| Nach einem Tag filtern | auf ein #Tag in einer Notiz tippen |
| Marker setzen | ✏️ Bearbeiten ➔ *Marker*, ein Tipp auf einen Marker an der Notiz filtert danach |
| Fortschritt weiterschalten | auf den Ring an einer Notiz ohne Unteraufgaben tippen: 0 ➔ 25 ➔ 50 ➔ 75 ➔ 100 % |
| Nur einen Zweig zeigen | 🎯 an der Notiz oder **F4**, zurück über die Brotkrumen, **Umschalt+F4** oder **Esc** |
| Ebenen ein- und ausklappen | ∞ unten rechts: 1 ➔ 2 ➔ 3 ➔ alle, oder die Tasten **1–9**, **0** = alle |
| Zwei Notizen verbinden | 🔗 an der Notiz oder **L**, dann die Ziel-Notiz antippen; zwei ausgewählte Notizen ➔ 🔗 *Verbinden* |
| Verbindung beschriften oder löschen | auf die gestrichelte Linie tippen |
| Rahmen um Notizen | Notizen auswählen ➔ ▢ *Rahmen*, oder ✏️ Bearbeiten ➔ *Rahmen*; ein Tipp auf den Rahmennamen benennt um |
| Callout | ✏️ Bearbeiten ➔ *Callout* |
| Unterpunkte nummerieren | ✏️ Bearbeiten ➔ *Unterpunkte nummerieren*: 1., 1.1 · a) · I. |
| Unterpunkte sortieren | ✏️ Bearbeiten ➔ *Unterpunkte sortieren*, oder **S** (ohne Auswahl: die Hauptnotizen) |

**Suchen und filtern:** 🔍 öffnet eine Leiste über der Map. Alle getippten Wörter müssen im Titel, in der Beschreibung, im Ergebnis oder bei der Person vorkommen; `#gar` findet Notizen mit einem Tag, das mit *gar* beginnt. Die Chips filtern nach Priorität (🔥 🔴 🟡 🟢), nach *Überfällig* oder *7 Tage*, nach *In Arbeit* und nach den Tags der Liste, mit ihrer Anzahl. Passende Notizen bleiben hell, ihre übergeordneten Punkte halb, der Rest tritt zurück. Ein eingeklappter Zweig mit Treffern zeigt seinen Knopf farbig. **Enter** springt zum nächsten Treffer und klappt seinen Zweig auf, **Umschalt+Enter** zum vorigen, **Esc** leert die Suche und schließt danach die Leiste, das hebt auch den Filter auf.

**Tags:** `#garten` oder `#3d-druck` irgendwo in Titel oder Beschreibung schreiben, oder Alexa bzw. Assist *„Hashtag Garten“* sagen. Ein Tag braucht einen Buchstaben, `#1` bleibt also eine Zahl und eine Farbe wie `#ff7800` eine Farbe. Tags aus `tags:` bei `brainstorm.add_idea` zählen auch.

**Marker:** Kleine Zeichen an einer Notiz, wie bei MindManager: ❓ Frage, 💡 Idee, ⚠️ Achtung, 💰 Geld, ⭐ Stern, 🚩 Flagge, ✅ Haken, ⛔ Blockiert, ⏳ Wartet, ❤️ Herz. Du setzt sie im Bearbeiten-Dialog beider Karten oder mit `markers` bei `brainstorm.update_idea`. Die Suchleiste bekommt für jeden Marker der Liste einen Chip.

**Fortschritt:** Eine Notiz mit Unteraufgaben zeigt einen Ring mit *erledigt/gesamt*, z. B. `3/5`. Der Ring füllt sich wie bei MindManager: Erledigte Unteraufgaben zählen 100 %, eine Unteraufgabe mit eigenen Unteraufgaben den Durchschnitt davon, jede andere ihren eigenen Fortschritt. Bei einer Notiz ohne Unteraufgaben stellst du den Fortschritt selbst ein, in Viertelschritten im Bearbeiten-Dialog, per Tipp auf den Ring oder mit `progress` bei `brainstorm.update_idea`. Bei 100 % wird der Ring grün.

**Fokus und Ebenen:** Bei großen Maps zeigt 🎯 (oder **F4**) nur den Zweig einer Notiz, die Notiz rückt in die Mitte. Über der Map steht der Weg dorthin, ein Tipp auf einen Eintrag springt zurück, ✕ zeigt wieder die ganze Map. Neue Notizen landen im Fokus unter der Fokus-Notiz. ∞ unten rechts klappt alle Zweige ab der gewählten Ebene ein, die Tasten **1** bis **9** tun das direkt, **0** klappt alles wieder auf.

**Querverbindungen:** Die Linien der Map zeigen, was wozu gehört. Eine Querverbindung verbindet zwei beliebige Notizen, auch aus verschiedenen Zweigen, mit einem gebogenen, gestrichelten Pfeil. 🔗 an der Notiz (oder **L**) startet, ein Tipp auf das Ziel beendet, **Esc** bricht ab. Ein Tipp auf die Linie öffnet einen Dialog für eine Beschriftung wie *braucht* oder *siehe auch*. Mit dem Haken *blockiert* wird die Verbindung rot: Die Ziel-Notiz wird grau und zeigt ⛔ *Wartet*, bis die erste Notiz erledigt ist. Das Abzeichen erscheint auch in der Listenkarte.

**Nummerierung und Sortieren:** Im Bearbeiten-Dialog einer Notiz mit Unteraufgaben nummeriert *Unterpunkte nummerieren* alles darunter, wie in MindManager: 1., 1.1, 1.2 … oder a), b) oder I., II. Eine Unteraufgabe kann eine eigene Art wählen, die dann für ihren Zweig gilt. Die Nummern stehen in beiden Karten vor dem Text und passen sich an, wenn Punkte dazukommen oder wandern. *Unterpunkte sortieren* ordnet sofort nach Titel (A → Z oder Z → A), Priorität, Fälligkeit oder Alter. Die übrigen Notizen bleiben an ihrem Platz, ↶ macht es rückgängig. Auf der Map öffnet **S** dieselbe Auswahl, ohne ausgewählte Notiz für die Hauptnotizen der Kategorie. Bei frei verschobenen Notizen ordnet 🪄 die Map danach passend neu.

**Rahmen und Callouts:** Ein Rahmen ist ein gestricheltes Rechteck mit Namen um mehrere Notizen, etwa *Phase 1* oder *Erdgeschoss*. Notizen mit demselben Rahmennamen teilen sich einen Rahmen. Ein Callout ist eine kurze Anmerkung in einer Sprechblase über der Notiz, für Dinge wie *Farbe noch offen*. Die Listenkarte zeigt den Rahmen als Chip und den Callout unter dem Text.

**Tastatur** (eine Notiz ist ausgewählt)

| Taste | Wirkung |
|---|---|
| **Tab** | neuer Unterpunkt |
| **Enter** | neuer Punkt daneben (ohne Auswahl: neue Notiz) |
| **F2** | Text bearbeiten |
| **Entf** / **Rücktaste** | löschen (mit Rückfrage, auch für mehrere) |
| **←** | zum übergeordneten Punkt |
| **→** | zum ersten Unterpunkt, eingeklappten Zweig öffnen |
| **↑** / **↓** | zum vorherigen / nächsten Geschwister |
| **F4** / **Umschalt+F4** | nur diesen Zweig zeigen / eine Ebene zurück |
| **1**–**9** / **0** | Ebenen bis 1–9 zeigen / alle Ebenen |
| **L** | Querverbindung zu einer anderen Notiz ziehen |
| **S** | Unterpunkte sortieren (ohne Auswahl: Hauptnotizen) |
| **Esc** | Auswahl aufheben, im Fokus eine Ebene zurück, beim Verbinden abbrechen |
| **Strg+Z** | rückgängig |

Im Textfeld: **Enter** speichert, **Umschalt+Enter** macht eine neue Zeile, **Esc** bricht ab.

---

## 4. Einstellen

### 4.1 Integration

**Einstellungen ➔ Geräte & Dienste ➔ Brainstorm Hub ➔ Konfigurieren** öffnet ein Menü. Alle Felder sind in der [README](../README_de.md#️-alle-einstellungen) einzeln beschrieben.

| Menü | Typische Einstellung |
|---|---|
| **Kategorien verwalten** | Kategorie „Urlaub“ anlegen, „Projekte“ umbenennen, leere ausblenden |
| **Kategorie-Design** | „Urlaub“ bekommt ☀️ `mdi:beach` und Orange |
| **Allgemeine Einstellungen & Export** | Standardkategorie, Intelligente Formatierung, Gesprochene Termine, Glossar, Markdown-Export nach `/config/brainstorm.md`, erlaubte Echos |
| **Alexa-Spracheingabe & Skill** | Modus *Routinen*, *Skill* oder *Beide*; Skill-Code und Sprachmodell zum Kopieren |
| **To-do-Listen koppeln** | Kategorie *Einkauf* mit Todoist oder Google Tasks abgleichen, in beide Richtungen |
| **Erinnerungen ➔ Ein/Aus & Kanäle** | Ansage auf Echo Küche, Push aufs Handy 5 Min. später, dringende Notizen sofort |
| **Erinnerungen ➔ Ruhezeit, Briefing & Wochenrückblick** | Ruhe 22–7 Uhr, Briefing 7:30 nur wenn jemand zu Hause ist, Rückblick sonntags 18 Uhr |
| **Erinnerungen ➔ Regeln pro Liste** | „Einkaufen“ nur im Laden (Zone) ansagen, „Alltag“ montags 8 Uhr |
| **Erinnerungen ➔ Orte & Heimkommen** | „Vergiss nicht, beim Baumarkt Schrauben“ meldet sich beim Betreten der Zone Baumarkt |
| **Erinnerungen ➔ Personen** | Jans Erinnerungen auf Jans Handy und den Echo im Büro |
| **Erinnerungen ➔ Kalender & Alexa-Erinnerungen** | Termine in `calendar.familie` eintragen, zusätzlich echte Alexa-Erinnerung stellen |
| **Erinnerungen ➔ Sperrzeiten pro Echo** | Kinderzimmer-Echo 19–7 Uhr stumm, optional mit Nicht stören |
| **Erinnerungen ➔ Kanäle jetzt testen** | Probeansage und Probe-Push |
| **KI** | Gesprochenes von einem KI-Dienst aufräumen lassen |
| **Privatsphäre & Benutzer** | Jeder sieht nur eigene Notizen, Listen gezielt teilen |
| **Echos & Apps Personen zuordnen** | Echo Schlafzimmer gehört zu Anna |
| **🛒 Bring!** | Bring-Listen als Hauptnotizen, Einträge als Unteraufgaben, in beide Richtungen (nur mit Bring-Integration) |
| **🔋 Batterien** | unter 20 % die Aufgabe *Batterie wechseln: Bewegungsmelder Flur (18 %)*, hakt sich nach dem Wechsel selbst ab |
| **🧹 Erledigte Einträge löschen** | Erledigte nach 30 Tagen automatisch entfernen |

### 4.2 Listenkarte (`brainstorm-card`)

Alle Optionen gibt es auch im grafischen Karteneditor.

```yaml
type: custom:brainstorm-card
title: Einkauf & Ideen
default_category: Einkaufen   # Filter beim Öffnen, "all" = alle
max_items: 20                  # 0 = alle
compact_mode: true
color_mode: multicolor         # oder theme
show_mic: true
hide_empty_categories: true
allow_delete: false            # z. B. für ein Wand-Tablet
```

| Option | Standard | Bedeutung |
|---|---|---|
| `title` | Brainstorm Hub | Kartentitel |
| `sensor` | `sensor.brainstorm_ideen_ubersicht` | Datenquelle |
| `color_mode` | `multicolor` | `multicolor` (Farbe je Kategorie) oder `theme` (Theme-Farben) |
| `default_category` | `all` | Filter beim Öffnen |
| `max_items` | `0` | höchstens so viele Notizen (0 = alle) |
| `compact_mode` | `false` | flachere Zeilen |
| `show_logo` | `true` | Logo im Kopf |
| `show_badge` | `true` | Zähler im Kopf |
| `show_quick_input` | `true` | Feld *Blitz-Idee* |
| `show_mic` | `true` | 🎙️ im Feld (nur HTTPS) |
| `show_categories` | `true` | Kategorie-Pills |
| `hide_empty_categories` | `true` | leere Kategorien ausblenden |
| `show_mindmap_button` | `true` | 🧠 im Kopf |
| `show_color_toggle` | `true` | 🎨/🌈 im Kopf |
| `show_source_icons` | `true` | Herkunft (Alexa, Assist, Handy …) |
| `show_timestamps` | `true` | „vor 5 Min.“ |
| `allow_edit` | `true` | Bearbeiten erlaubt |
| `allow_delete` | `true` | Löschen erlaubt |
| `show_last_alexa` | `false` | zuletzt aktiven Echo anzeigen |
| `last_alexa_entity` | `sensor.last_alexa` | Entität dafür |

### 4.3 Mindmap-Karte (`brainstorm-mindmap-card`)

```yaml
type: custom:brainstorm-mindmap-card
map_template: sketch    # standard, clean, sketch, neon
node_shape: thought     # überschreibt die Vorlage
line_style: curve
color_scheme: pastel
height: 75vh
default_category: Projekte
```

**Vorlagen** setzen Form, Linien und Farben auf einmal:

| `map_template` | Form | Linien | Farben |
|---|---|---|---|
| `standard` | Karte | geschwungen | Kategorie |
| `clean` | Rechteck | eckig | Kategorie |
| `sketch` | Pille | gestrichelt | Pastell |
| `neon` | Pille | geschwungen | Neon |

Jeder Teil lässt sich einzeln überschreiben, `template` heißt „wie die Vorlage“:

- `node_shape`: `card`, `cloud` (Wolke), `bubble` (Sprechblase), `thought` (Gedankenblase), `pill`, `rect`, `ellipse`, `hexagon` (Sechseck), `note` (Notizzettel), `underline` (unterstrichen)
- `line_style`: `curve`, `straight`, `angled`, `dashed`
- `color_scheme`: `category`, `pastel`, `mono`, `neon`

Pro Notiz kannst du die Form auch im Bearbeiten-Dialog wählen oder per Dienst setzen (`node_shape` bei `brainstorm.update_idea`).

| Option | Standard | Bedeutung |
|---|---|---|
| `title` | Brainstorm Mindmap | Titel |
| `height` | `calc(100vh - 32px)` | Höhe, z. B. `600px` oder `75vh` |
| `voice_bubbles` | `true` | Sprachnotizen als Sprechblase |
| `default_category` | `all` | Kategorie im Fokus |
| `show_toolbar` | `true` | Werkzeugleiste mit Filtern |
| `show_logo` | `true` | Logo |
| `show_bulb_watermark` | `true` | leuchtende Glühbirne in der Mitte |
| `show_grid` | `true` | Punktraster |
| `show_controls` | `true` | Zoom und Zentrieren |
| `show_add_btn` | `true` | „+ Idee“ |
| `show_export_btn` | `true` | 🖼️ Als Bild speichern |
| `show_filter` | `true` | 🔍 Suchen und filtern |
| `show_fullscreen_btn` | `true` | ⛶ Vollbild |
| `show_color_toggle` | `true` | 🎨/🌈 |
| `hide_empty_categories` | `true` | leere Kategorien ausblenden |
| `color_mode`, `sensor`, `show_last_alexa`, `last_alexa_entity` | | wie bei der Listenkarte |

---

## 5. Automatisieren

### 5.1 Dienste

Alle Parameter stehen in der [README](../README_de.md#️-dienste-services) und unter **Entwicklerwerkzeuge ➔ Aktionen**.

| Dienst | Kurzbeispiel |
|---|---|
| `brainstorm.add_idea` | `text: "Filter tauschen"`, `category: Smarthome`, `priority: high`, `due: "2026-12-01 18:00"` |
| `brainstorm.update_idea` | `id: …`, `status: completed`, `in_progress: true`, `markers: [question, money]`, `progress: 50`, `links: [{to: …, label: braucht, blocks: true}]`, `frame: Phase 1` oder `callout: Farbe offen` |
| `brainstorm.delete_idea` | `id: …` |
| `brainstorm.delete_done` | erledigte löschen, optional nur ältere (`older_than_days`) |
| `brainstorm.restore_idea` | gelöschte Notiz zurückholen |
| `brainstorm.get_ideas` | Liste als Antwort, z. B. `category: Einkaufen` |
| `brainstorm.get_announcement` | fertiger Vorlesetext (`speech`) |
| `brainstorm.add_category` / `remove_category` | Kategorie anlegen oder entfernen |
| `brainstorm.set_category_style` | Icon und Farbe |
| `brainstorm.export_markdown` / `export_json` / `import_json` | Sichern und Übertragen |
| `brainstorm.bring_message` | Nachricht an Bring! |
| `brainstorm.reorder_ideas` | Reihenfolge setzen |
| `brainstorm.sort_children` | Unterpunkte sortieren: `parent_id: …`, `by: text`, `priority`, `due` oder `created` |
| `brainstorm.share` | Liste mit Personen teilen |

Mit `parse_due: true` wertet `add_idea` einen Zeitpunkt im Text aus wie bei Sprache:

```yaml
action: brainstorm.add_idea
data:
  text: "Erinnere mich morgen um 8 an den Müll"
  parse_due: true
```

### 5.2 Ereignisse

| Ereignis | Wann |
|---|---|
| `brainstorm_idea_added` | neue Notiz |
| `brainstorm_idea_updated` | Notiz geändert |
| `brainstorm_idea_completed` | Notiz abgehakt |
| `brainstorm_idea_deleted` | Notiz gelöscht |
| `brainstorm_reminder_due` | Erinnerung ist fällig |

In den Ereignisdaten steckt die ganze Notiz (`id`, `text`, `category`, `priority`, `source`, …):

```yaml
triggers:
  - trigger: event
    event_type: brainstorm_idea_added
    event_data:
      priority: urgent
actions:
  - action: light.turn_on
    target:
      entity_id: light.flur
    data:
      color_name: red
```

### 5.3 Sensor-Attribute

`sensor.brainstorm_ideen_ubersicht` zählt offene Notizen. In den Attributen stehen u. a. alle Notizen, Kategorien, `allowed_echos` und `voice_mode`.

```yaml
{{ state_attr('sensor.brainstorm_ideen_ubersicht', 'ideas')
   | selectattr('category', 'eq', 'Einkaufen') | list | count }}
```

### 5.4 Fertige Rezepte

**Morgens vorlesen, was offen ist**

```yaml
triggers:
  - trigger: time
    at: "07:30:00"
actions:
  - action: brainstorm.get_announcement
    response_variable: ueberblick
  - action: notify.alexa_media
    data:
      target: media_player.echo_kuche
      data:
        type: announce
      message: "{{ ueberblick.speech }}"
```

**Notiz, wenn die Waschmaschine fertig ist**

```yaml
triggers:
  - trigger: state
    entity_id: binary_sensor.waschmaschine_lauft
    to: "off"
actions:
  - action: brainstorm.add_idea
    data:
      text: Wäsche aufhängen
      category: Alltag
      priority: high
```

**Erledigte jeden Sonntag aufräumen**

```yaml
triggers:
  - trigger: time
    at: "03:00:00"
conditions:
  - condition: time
    weekday: sun
actions:
  - action: brainstorm.delete_done
    data:
      older_than_days: 14
```

Weitere Vorlagen für Alexa und Assist liegen in [`examples/`](../examples/).
