🏠 [Start](Home) · 🇬🇧 [English version](Import-Export-and-Storage)

## 💾 Funktionen

- 📝 **Automatischer Markdown-Export:**
  - Exportiert Ideen strukturiert nach Kategorien in Markdown-Dateien (z. B. `/config/brainstorm/`).
  - Ideal für Personal Knowledge Management (Obsidian, Logseq, Foam, SilverBullet).
- 📋 **Native Home Assistant To-do Plattform:**
  - Jede Brainstorm-Kategorie wird als echte Home Assistant To-do-Liste bereitgestellt (`todo.brainstorm_hub_haus_garten`, `todo.brainstorm_hub_inbox`, usw.).
- 🔁 **Gekoppelte To-do-Listen (v1.6.31):**
  - Koppelt eine Kategorie mit einer To-do-Liste einer anderen Integration, etwa **Bring!**, **Google Tasks**, **Todoist** oder einer lokalen To-do-Liste. Neue Einträge, Umbenennen und Abhaken gehen in beide Richtungen, so bleiben *Einkauf* in Brainstorm und deine Einkaufs-App gleich. Siehe *Konfigurieren ➔ To-do-Listen koppeln*.
- 🛒 **Native Bring!-Unterstützung (v1.7.0):**
  - Bring! unter *Konfigurieren ➔ 🛒 Bring!* einschalten, Kategorie wählen oder anlegen, fertig. Jede Bring-Liste wird eine Hauptnotiz, ihre Einträge werden Unteraufgaben. Notizen ohne Liste landen in der Standardliste, das Verschieben einer Unteraufgabe verschiebt den Eintrag, und die Bring-Spezifikation erscheint als Notiz. Umbenennen, Abhaken und neue Einträge gehen in beide Richtungen.
- 💾 **JSON-Export und -Import (v1.6.31):**
  - `brainstorm.export_json` gibt deine Ideen samt Kategorien, Icons und Farben als JSON zurück, auf Wunsch als Datei. `brainstorm.import_json` holt sie zurück, auf demselben oder einem anderen Home Assistant, und überspringt Vorhandenes.

## 📥 Aus Trello, Todoist und Miro übernehmen (v1.13.21)

In der Mindmap unter 🖼️ ➔ *Gliederung einfügen* ➔ *📂 Datei wählen*. Die Notizen landen in der gewählten Kategorie, im Fokus unter der Fokus-Notiz; ↶ nimmt alles wieder heraus. Höchstens 300 Notizen auf einmal.

| Quelle | So exportieren | Was daraus wird |
| :--- | :--- | :--- |
| **Trello** | Board-Menü ➔ *Drucken, Exportieren und Teilen* ➔ *Als JSON exportieren* | Listen werden Hauptnotizen, Karten Notizen darunter, Checklisten-Punkte Unteraufgaben. Beschreibung, Fälligkeit und Erledigt (Haken am Fälligkeitsdatum bzw. am Checklisten-Punkt) kommen mit; Archiviertes bleibt draußen. Große Exporte schrumpft die Karte vorher auf das Nötige. |
| **Todoist** | Projekt ➔ ⋯ ➔ *Als Vorlage exportieren* ➔ *Als Datei exportieren* (CSV) | Abschnitte werden Hauptnotizen, Aufgaben samt Einrückung Notizen darunter. Priorität p1 ➔ dringend, p2 ➔ hoch, p3 ➔ mittel; ein festes Datum wird zur Fälligkeit (ohne Uhrzeit 09:00), wiederkehrende Angaben wie „jeden Tag“ fallen weg; Kommentare hängen an der Beschreibung. |
| **Miro, Excel und andere Tabellen** | als CSV speichern | Mit Spalten wie *Titel/Name/Text*, *Beschreibung*, *Liste/Spalte/Abschnitt*, *Fällig/Datum*, *Priorität*, *Erledigt* und *Ebene* wird jede Zeile eine Notiz, gruppiert nach Liste. Ohne solche Spalten (z. B. ein Miro-Board als CSV) wird jede Spalte ein Zweig mit ihren Zellen. Komma, Semikolon und Tabulator gehen. |

Für Automationen: `brainstorm.import_outline` mit `format: trello` oder `format: csv`, siehe [Dienste und Ereignisse](Dienste-und-Ereignisse).

## 🗄️ Wo die Daten liegen

| Was | Wo |
| :--- | :--- |
| Ideen, Kategorien, Zeichnungen, Pinnwand | `/config/.storage/brainstorm.storage` |
| Kopplung des Alexa-Skills | `/config/.storage/brainstorm.alexa_skill` |
| Stand der Erinnerungen | `/config/.storage/brainstorm.reminders` |
| Anhänge | `/config/brainstorm_attachments/` |
| Markdown-Export | Standard `/config/brainstorm/`, einstellbar |

Alles liegt lokal in deinem Home Assistant und ist Teil jedes normalen Backups. Bearbeite die Dateien in `.storage` nicht von Hand, solange Home Assistant läuft; nutze dafür die Karten oder die [Dienste](Dienste-und-Ereignisse). Wie die Daten aktualisiert werden, steht unter [Entitäten & Attribute](Entitäten-und-Attribute#-wie-die-daten-aktualisiert-werden).

## 🔁 Sichern und umziehen

- **Als JSON:** [`brainstorm.export_json`](Dienste-und-Ereignisse#brainstormexport_json) gibt alles samt Kategorien, Icons, Farben, Pinnwand-Plätzen und Zeichnungen zurück, auf Wunsch als Datei. [`brainstorm.import_json`](Dienste-und-Ereignisse#brainstormimport_json) holt es zurück, auf demselben oder einem anderen Home Assistant, und überspringt Vorhandenes. Kommentare, Reaktionen und Stimmen bleiben draußen.
- **Als Markdown:** [`brainstorm.export_markdown`](Dienste-und-Ereignisse#brainstormexport_markdown) oder der automatische Export unter *Konfigurieren ➔ Allgemeine Einstellungen & Export*.
- **Aus der Mindmap:** 🖼️ speichert SVG, PNG, PDF, eine Markdown-Gliederung, OPML oder FreeMind (`.mm`); *Gliederung einfügen* liest `.md`, `.txt`, `.opml` und `.mm` wieder ein, seit v1.13.21 auch Trello-Boards (`.json`) und CSV aus Todoist, Miro oder Excel (siehe unten). Siehe [Mindmap & Pinnwand](Mindmap-und-Pinnwand).
- **Gelöscht?** Gelöschte Notizen liegen 30 Tage im **🗑️ Papierkorb** (v1.11.12), auch über einen Neustart: in der Listenkarte über *🗑️ Papierkorb* über der Liste, in der Mindmap über 🗑️ unten rechts. Dort holst du einzelne zurück (↩️, samt ihren Unterpunkten), löschst sie endgültig (✕) oder leerst den Papierkorb. Danach sind sie mit ihren Anhängen weg. Mit Privatsphäre sieht jede Person nur, was sie selbst gelöscht hat oder bearbeiten darf. Erledigte, die *🧹 Erledigte Einträge löschen* entfernt, kommen nicht in den Papierkorb. Für Automationen gibt es [`brainstorm.restore_idea`](Dienste-und-Ereignisse#brainstormrestore_idea).
