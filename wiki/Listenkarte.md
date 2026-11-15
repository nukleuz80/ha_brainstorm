🏠 [Start](Home) · 🇬🇧 [English version](List-Card)

## Brainstorm Card (Listenansicht mit integriertem Mindmap-Umschalter)
```yaml
type: custom:brainstorm-card
title: Brainstorm Hub
```

## Eigenständiges Seitenleisten-Dashboard (`Brainstorm Hub`)
Für maximale Übersicht lässt sich Brainstorm als vollwertiger Menüpunkt direkt in der linken Home Assistant Seitenleiste einbinden (z. B. unter Pfad `/brainstorm-hub`):
- **Ansicht 1: Übersicht (Kombiniert):** Die interaktive Gedankenlandkarte (`custom:brainstorm-mindmap-card`) thront oben im Großformat (z. B. Höhe 580px), während sich die Schnelleingabe und Notizenliste (`custom:brainstorm-card`) mit Filtern und Badges direkt darunter befindet.
- **Ansicht 2: Mindmap Vollbild:** 100% Panel-Ansicht für ausgedehntes visuelles Brainstorming.
- **Ansicht 3: Listenansicht:** Schnelle, fokussierte Notizenliste für Tastatur- und Touch-Eingaben.

## ✨ Funktionen im Überblick

- 🎯 **NEU (v1.4.22): Intelligentes Prioritäten-Management & Visuelle Dringlichkeitsstufen:**
  - **4 Prioritätsstufen:** `low` (🟢 Niedrig), `medium` (🟡 Mittel / Standard), `high` (🔴 Hoch) und `urgent` (🔥 Dringend).
  - **Automatische Spracherkennung (NLP & Heuristik):** Natürliche Erkennung von Dringlichkeits-Signalwörtern und Tags per Sprache oder Texteingabe (z. B. *„Dringend Garten: Rasenmäher reparieren“*, *„Garten: Wichtig Rasenmäher reparieren“*, *„Sofort Notiz…“*, *„Prio 1…“*, *„Wenn Zeit ist…“*, *„!urgent“*, *„!high“*, *„!low“*). Das System erkennt Prioritäten unabhängig von der Reihenfolge vor oder nach dem Kategoriepräfix, filtert die Signalwörter sauber aus dem Notiztext und setzt die Priorität automatisch.
  - **1-Klick Prioritätswechsel im Dashboard:** Direktes Weiterschalten der Priorität (`Mittel` ➔ `Hoch` ➔ `Dringend` ➔ `Niedrig`) per Klick auf das Prioritäts-Badge in der Notizenliste (`brainstorm-card`) oder der Mindmap (`brainstorm-mindmap-card`).
  - **Prioritätsauswahl in Toolbar & Dialogen:** Schnellauswahl in der Erfassungszeile sowie farbige Chip-Auswahl in Neu- und Bearbeiten-Dialogen.
  - **Visuelle Effekte in der Mindmap:** Dringende Gedankenwolken (`urgent`) pulsieren mit einem sanften Feuereffekt (`cloud-urgent`), während hohe Prioritäten (`high`) durch einen dezenten Warm-Glow hervorgehoben werden.
  - **Vollständige Plattform-Integration:** Prioritäten werden im Sensor (`priority_counts`), in To-do-Listen (`todo.brainstorm_hub_*`), im Logbook, in den LLM-Tools und beim Markdown-Export (`[🔥 Dringend]`, `[🔴 Hoch]`) lückenlos gepflegt.
- Zweistöckiges Design mit Schnellerfassungs-Toolbar, Auto-Kategorisierung und Pill-Filtern.
- Integrierter Ansichts-Umschalter (`🧠 Mindmap` ⇄ `📋 Liste`) direkt in der Kopfzeile.
- Erledigt-Verwaltung mit Durchstreich-Animation, Bearbeitungsfunktion und Quellen-Badges.
- **Unteraufgaben direkt anlegen (v1.6.29):** 🌿 an einer Hauptaufgabe oder in ihrem Menü bei langem Drücken legt eine Unteraufgabe direkt darunter an, in derselben Kategorie. Mit einer KI-Aufgaben-Entität schlägt ✨ daneben Unteraufgaben vor (v1.6.28).
- **Anhänge (v1.7.9):** 📎 im Bearbeiten-Dialog beider Karten hängt Screenshots, Fotos, PDFs, Logs und andere Dateien an eine Notiz, bis 10 MB pro Datei und 20 pro Notiz. Am Rechner fügst du einen Screenshot mit Strg+V ein oder ziehst Dateien auf den Dialog, am Handy bietet der Knopf Kamera und Galerie an. Die Liste zeigt 📎 mit der Anzahl, Antippen zeigt die Dateien, Bilder als Vorschau, und öffnet sie. Ist eine Notiz erledigt (oder archiviert), werden ihre Anhänge nach 30 Tagen gelöscht, wird sie wieder geöffnet, bleiben sie. Die Dateien liegen in `/config/brainstorm_attachments/` und gehen nur an Personen, die die Notiz sehen dürfen. Erlaubt: Bilder, PDF, TXT/LOG/MD, CSV, JSON, YAML, ZIP.
- **Erledigte Einträge löschen (v1.7.13):** Einstellungen › 🧹 Erledigte Einträge löschen löscht erledigte (abgehakte oder archivierte) Einträge nach einer Anzahl Tage von selbst, geprüft alle sechs Stunden, und hat einen Schalter, der alle sofort löscht. Ihre Anhänge gehen mit. Standardmäßig aus (0 Tage). Aktion: `brainstorm.delete_done`.
- **Titel und Beschreibung (v1.7.8):** ✎ bearbeitet den Titel und darunter eine optionale Beschreibung für Details, Links oder Notizen. Die Liste zeigt bis zu drei Zeilen davon unter dem Titel, Antippen zeigt den Rest. Der Bearbeiten-Dialog der Mindmap hat sie auch, und die To-do-Listen von Home Assistant zeigen und bearbeiten sie als Beschreibung des Eintrags. Aktionen: `description` in `brainstorm.add_idea` und `brainstorm.update_idea` (leer entfernt sie).
- **☀️ Mein Tag (v1.12.2):** Notizen bewusst für heute vornehmen: *Mein Tag* im Bearbeiten-Dialog beider Karten (🌅 morgens, ☀️ tagsüber, 🌙 abends) oder *Für heute vornehmen* im Menü bei langem Drücken. Die Auswahl gilt nur heute und läuft um Mitternacht von selbst ab. Der Knopf *☀️ Mein Tag* über der Liste zeigt nur diese Notizen, morgens zuerst, abends zuletzt, Oberpunkte grau zur Orientierung; in der Mindmap gibt es dafür den Filter *☀️ Mein Tag*. Das tägliche Briefing nennt den Plan zuerst, nach Tageszeit, danach was fällig ist. Aktion: `my_day` in `brainstorm.update_idea`.
- **📊 Statistik (v1.13.20):** Der Knopf *📊 Statistik* über der Liste öffnet erledigte und neue Notizen pro Woche als Balken (4 bis 52 Wochen), dazu offen und überfällig, die Durchlaufzeit (Median und Schnitt von *angelegt* bis *erledigt*), wer was abgehakt hat und die Kategorien mit erledigt/offen. In einer Kategorie lässt sich auf *Nur diese Kategorie* umschalten. Wer abhakt, merkt sich Brainstorm seit v1.13.20 pro Notiz (Home-Assistant-Benutzer; bei ChoreOps die Person, die die Aufgabe erledigt hat). Älteres, per Sprache oder Automation Abgehaktes steht unter *ohne Angabe*. Mit Privatsphäre zählt nur, was du sehen darfst. WebSocket: `brainstorm/statistics` (`weeks`, `category`).
- **🛒 An Bring! senden (v1.13.4):** Ist Bring eingeschaltet, bietet das ⋯-Menü einer offenen Notiz außerhalb der Bring-Kategorie *🛒 An Bring! senden*: Liste wählen und die Notiz selbst oder eine Auswahl ihrer offenen Unteraufgaben als Artikel senden. Was dort schon offen ist, kommt nicht doppelt dazu; die Notiz zeigt *🛒 1/3*, bis alles gekauft ist.
- **🏅 ChoreOps (v1.13.1):** Ist die Integration [ChoreOps](https://github.com/ccpk1/choreops) installiert, bietet das ⋯-Menü einer offenen Notiz *🏅 An ChoreOps übergeben*: Person (vorbelegt mit der zuständigen Person der Notiz) und Punkte (5, 10, 20, 50 oder frei) wählen, fertig. Brainstorm legt dafür eine einmalige ChoreOps-Aufgabe mit dem Label `brainstorm` an. Die Notiz zeigt 🏅 und die Punkte, ✋ sobald das Kind in ChoreOps „erledigt“ gemeldet hat, und wird abgehakt (🏅 +Punkte), sobald ein Elternteil in ChoreOps freigibt. Lehnt ein Elternteil ab, ist sie wieder offen. Wer Aufgaben anlegen darf, prüft ChoreOps selbst; Punkte und Freigabe bleiben bei den Eltern.
- **🏅 ChoreOps II (v1.13.10):** *🏅 Projekt an ChoreOps übergeben* im ⋯-Menü einer Notiz mit Unteraufgaben schickt jede offene Unteraufgabe (die unterste Ebene jedes Asts) als eigene Aufgabe, mit Person und Punkten pro Zeile. *🎁 Als ChoreOps-Belohnung anlegen* macht aus einer Notiz eine Belohnung in ChoreOps, die Punkte kostet, zum Beispiel den Gewinner einer Abstimmung auf einer Wunsch-Map: Name, Preis und wer sie einlösen darf; die Notiz zeigt danach 🎁 mit dem Preis. *✨ Vorschlagen* in allen drei Dialogen schlägt Punkte nach Aufwand oder einen Preis nach Größe und Stimmen vor; mit einer KI-Aufgaben-Entität macht das die KI (Dienst `brainstorm.send_reward_to_choreops`).
- **🔥 Gewohnheiten (v1.12.3):** Mit dem Schalter *Gewohnheit* im Bearbeiten-Dialog wird die Notiz einmal am Tag abgehakt statt erledigt. Das Häkchen zählt den heutigen Tag und die Notiz bleibt stehen; nochmal tippen nimmt den Tag zurück. Das 🔥-Badge zeigt die Serie (sie zählt ab gestern weiter, bis heute erledigt ist) und wird grün, sobald heute abgehakt ist. Antippen öffnet den Kalender: Serie, beste Serie, alle erledigten Tage und die letzten 18 Wochen als Heatmap; ein Tag lässt sich per Antippen nachtragen oder entfernen. Um Mitternacht beginnt die Liste den neuen Tag.
- **🗣️ Frei reden (v1.12.4):** *🗣️ Frei reden* unter der Schnelleingabe öffnet einen Dialog für mehrere Aufgaben auf einmal, mit dem, was schon im Eingabefeld steht. Erst mit 🎙️ sprechen oder tippen, z. B. „Morgen um zehn den Klempner anrufen, Anna kauft am Freitag Milch und dann noch den Keller aufräumen“. ✨ *Zerlegen* lässt die KI einzelne Notizen mit Datum, Uhrzeit und Person machen; ändere, was nicht passt, wähle ab, was nicht soll, dann *anlegen*. Die Notizen landen in der gewählten oder angezeigten Kategorie. Ohne KI-Aufgaben-Entität wird Satz für Satz zerlegt, und Angaben wie „morgen um 10“ werden trotzdem erkannt.
- **Suche in der Liste (v1.8.11):** Das Feld 🔍 über der Liste filtert beim Tippen, in Titel, Beschreibung, Ergebnis und Person, ohne auf Groß-/Kleinschreibung und Akzente zu achten. `#tag` findet Tags. Ein gefundener Unterpunkt zeigt seinen Oberpunkt grau mit, eine gefundene Hauptaufgabe ihre Unterpunkte. ✕ oder Esc leert sie; `show_search: false` blendet das Feld aus.
- **Unteraufgaben einklappen (v1.7.4):** Eine Hauptaufgabe mit Unteraufgaben zeigt ▾ und deren Anzahl. Antippen klappt sie zu, ▸ klappt sie wieder auf. Praktisch bei langen Bring-Listen. Jeder Browser merkt sich pro Karte, was eingeklappt ist.
- **Links und etwas Markdown in Notizen (beide Karten, v1.6.21):**
  - Webadressen werden anklickbar, ebenso `[Text](https://…)`. `**fett**`, `*kursiv*`, `~~durchgestrichen~~` und `` `Code` `` erscheinen formatiert, in der Notiz und in ihrer Ergebnisnotiz.
  - Sicher gebaut: Alles andere bleibt reiner Text, HTML in einer Notiz wird nie ausgeführt, und Links führen nur zu `http`-, `https`- und `mailto`-Adressen. Sie öffnen sich in einem neuen Tab, und ein Klick auf einen Link öffnet nicht den Editor.

## Formatierung und Links

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

## Listenkarte

| Aktion | So geht es |
|---|---|
| Neue Notiz | in *Blitz-Idee* tippen, z. B. `Garten: Baum schneiden`, und **Enter** |
| Kategorie und Priorität vorgeben | Auswahlfelder 🏷️ und Priorität unter dem Eingabefeld (*Auto* erkennt sie aus dem Text) |
| Bearbeiten | auf den Text oder den Stift tippen; im Dialog speichert **Strg+Enter** |
| Kontextmenü | lange auf eine Notiz drücken oder ⋯ rechts in der Zeile antippen |
| Reagieren | 👍 ❤️ 😂 ❗ oben im Kontextmenü, oder auf eine vorhandene Reaktion an der Notiz tippen |
| Kommentieren | Kontextmenü ➔ 💬 *Kommentare*, oder auf 💬 an der Notiz tippen; **Strg+Enter** sendet, `@Name` benachrichtigt die Person |
| Abstimmen | in einer laufenden Abstimmung − / + an der Notiz |
| Knöpfe einer Zeile | am Handy und auf schmalen Karten unter ⋯ (Einrücken, Unteridee, KI, Bearbeiten, Löschen), mit der Maus erscheinen sie beim Darüberfahren; `row_actions` ändert das |
| Unterpunkte auf- und zuklappen | Abzeichen ▾ 0/2 neben der Priorität antippen |
| Abhaken | Kreis links antippen, im Reiter Erledigt wieder aktivieren |
| Löschen | ✕ |
| Unteraufgabe | Unteridee anlegen, oder Notiz ziehen und auf eine andere fallen lassen |
| Ein- und ausrücken | Knöpfe *Unter vorherige Aufgabe einrücken* und *Ausrücken* |
| Unteraufgaben vorschlagen | ✨ lässt die KI Unteraufgaben vorschlagen (KI unter Konfigurieren) |
| Sortieren | halten und ziehen |
| Suchen | Feld 🔍 über der Liste: Wörter suchen in Titel, Beschreibung, Ergebnis und Person, `#tag` nach einem Tag; ✕ oder **Esc** leert es |
| Filtern | Kategorie-Pills oben |
| Farbmodus | 🌈 bunt / 🎨 Theme-Farben im Kopf |
| Zur Mindmap | 🧠 im Kopf öffnet sie als Ebene, **Esc** schließt |

## ⚙️ Kartenoptionen (`brainstorm-card`)

Alle Optionen gibt es auch im grafischen Karteneditor.

```yaml
type: custom:brainstorm-card
title: Einkauf & Ideen
default_category: Einkaufen   # Filter beim Öffnen, "all" = alle
max_items: 20                  # 0 = alle
compact_mode: true
color_mode: multicolor         # oder theme
show_mic: true
show_search: true
hide_empty_categories: true
allow_delete: false            # z. B. für ein Wand-Tablet
```

| Option | Standard | Bedeutung |
|---|---|---|
| `title` | Brainstorm Hub | Kartentitel |
| `sensor` | `sensor.brainstorm_ideen_ubersicht` | Datenquelle |
| `level` | wie in den Einstellungen | Bedienstufe nur dieser Karte: `beginner`, `normal` oder `pro`, siehe [4.0](Einstellungen#bedienstufe) |
| `color_mode` | `multicolor` | `multicolor` (Farbe je Kategorie) oder `theme` (Theme-Farben) |
| `default_category` | `all` | Filter beim Öffnen |
| `max_items` | `0` | höchstens so viele Notizen (0 = alle) |
| `compact_mode` | `false` | flachere Zeilen |
| `row_actions` | `auto` | Knöpfe in den Zeilen: `auto` (Handy ⋯, Maus beim Darüberfahren), `inline` (immer alle) oder `menu` (immer nur ⋯) |
| `show_logo` | `true` | Logo im Kopf |
| `show_badge` | `true` | Zähler im Kopf |
| `show_quick_input` | `true` | Feld *Blitz-Idee* |
| `show_mic` | `true` | 🎙️ im Feld (nur HTTPS) |
| `show_search` | `true` | Suchfeld 🔍 über der Liste |
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
