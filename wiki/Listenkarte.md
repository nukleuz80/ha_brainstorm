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
