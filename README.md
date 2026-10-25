# 🧠 Brainstorm Hub for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/default)
[![Version](https://img.shields.io/badge/version-1.4.22-blue.svg)](https://github.com/nukleuz80/ha_brainstorm/releases)
[![Quality Scale](https://img.shields.io/badge/Quality%20Scale-Silver-C0C0C0.svg)](https://developers.home-assistant.io/docs/integration_quality_scale_index/)
[![GitHub Release](https://img.shields.io/github/v/release/nukleuz80/ha_brainstorm)](https://github.com/nukleuz80/ha_brainstorm/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/nukleuz80/ha_brainstorm)

**Brainstorm Hub** ist die smarte Ideen-, Gedanken- und Notizen-Sammelzentrale für dein Home Assistant Smarthome.  
Egal ob beim Kochen, im Garten oder unterwegs: Erfasse Geistesblitze sekundenschnell per Sprache (**Amazon Alexa** oder **Home Assistant Assist**), über das Lovelace-Dashboard oder Automationen. Brainstorm ordnet deine Ideen durch intelligente Heuristiken automatisch der passenden Kategorie zu und synchronisiert sie auf Wunsch als Markdown-Dateien für Obsidian, Logseq oder Nextcloud.

---

## 🌟 Highlights & Features

- 🎯 **NEU (v1.4.22): Intelligentes Prioritäten-Management & Visuelle Dringlichkeitsstufen:**
  - **4 Prioritätsstufen:** `low` (🟢 Niedrig), `medium` (🟡 Mittel / Standard), `high` (🔴 Hoch) und `urgent` (🔥 Dringend).
  - **Automatische Spracherkennung (NLP & Heuristik):** Natürliche Erkennung von Dringlichkeits-Signalwörtern und Tags per Sprache oder Texteingabe (z. B. *„Dringend Garten: Rasenmäher reparieren“*, *„Garten: Wichtig Rasenmäher reparieren“*, *„Sofort Notiz…“*, *„Prio 1…“*, *„Wenn Zeit ist…“*, *„!urgent“*, *„!high“*, *„!low“*). Das System erkennt Prioritäten unabhängig von der Reihenfolge vor oder nach dem Kategoriepräfix, filtert die Signalwörter sauber aus dem Notiztext und setzt die Priorität automatisch.
  - **1-Klick Prioritätswechsel im Dashboard:** Direktes Weiterschalten der Priorität (`Mittel` ➔ `Hoch` ➔ `Dringend` ➔ `Niedrig`) per Klick auf das Prioritäts-Badge in der Notizenliste (`brainstorm-card`) oder der Mindmap (`brainstorm-mindmap-card`).
  - **Prioritätsauswahl in Toolbar & Dialogen:** Schnellauswahl in der Erfassungszeile sowie farbige Chip-Auswahl in Neu- und Bearbeiten-Dialogen.
  - **Visuelle Effekte in der Mindmap:** Dringende Gedankenwolken (`urgent`) pulsieren mit einem sanften Feuereffekt (`cloud-urgent`), während hohe Prioritäten (`high`) durch einen dezenten Warm-Glow hervorgehoben werden.
  - **Vollständige Plattform-Integration:** Prioritäten werden im Sensor (`priority_counts`), in To-do-Listen (`todo.brainstorm_*`), im Logbook, in den LLM-Tools und beim Markdown-Export (`[🔥 Dringend]`, `[🔴 Hoch]`) lückenlos gepflegt.
- 🤖 **Assist LLM Tools & Function-Calling API (v1.4.20):**
  - **Freie natürliche Sprache statt starren Befehlen:** Vollständige Integration in das native Home Assistant LLM API (`homeassistant.helpers.llm`). Sprachmodelle (wie OpenAI, Google Gemini, Ollama oder lokale LLMs) erhalten direkten Zugriff auf Brainstorm als Werkzeugsatz.
  - **5 mächtige KI-Werkzeuge:**
    - `brainstorm_add_idea`: Erfasst Gedanken und ordnet sie kontextbezogen der passenden Kategorie zu.
    - `brainstorm_get_ideas`: Beantwortet Fragen zu bestehenden Notizen mit flexiblen Filtern nach Kategorie, Status und Freitext-Suche.
    - `brainstorm_complete_idea`: Hakt Aufgaben per natürlicher Sprache ab (per ID oder Volltextsuche, z. B. *„Die Hecke ist geschnitten“*).
    - `brainstorm_delete_idea`: Löscht Notizen unwiderruflich per Sprachbefehl.
    - `brainstorm_list_categories`: Gibt der KI Überblick über alle Kategorien und Aufgabenstatistiken.
  - **Universell einsetzbar:** Direkt in den Einstellungen jedes Sprachassistenten unter *LLM API: „Brainstorm Hub“* aktivierbar.
- 🧠 **Intelligente Text-Optimierung & NLP-Bereinigung (v1.4.0):**
  - **Prägnante Notizen statt Gesprächsfloskeln:** Verwandelt gesprochene Sätze wie *„im brainstorm dass heute die kinder vom flughafen abgeholt werden müssen“* vollautomatisch in *„Heute Kinder vom Flughafen abholen“*.
  - **Filterung von Füllwörtern:** Entfernt Einleitungen (*„notiere bitte dass…“*, *„merke dir…“*, *„kannst du aufschreiben…“*, *„ich muss…“*, *„dass wir…“*).
  - **Grammatik-Transformation (Infinitiv):** Wandelt passive Hilfsverb-Endungen (*„…geschnitten werden müssen“* ➔ *„…schneiden“*, *„…repariert werden soll“* ➔ *„…reparieren“*, *„…bezahlt werden muss“* ➔ *„…bezahlen“*) in präzise Handlungsaufforderungen um.
  - **Rechtschreibung & Groß-/Kleinschreibung:** Automatische Korrektur von typischen Sprach- und Tippfehlern (`terasse` ➔ `Terrasse`, `packet` ➔ `Paket`) und lückenlose Großschreibung deutscher Substantive.
  - **Schalter im Options-Flow:** Kann unter *Konfigurieren ➔ Allgemeine Einstellungen* jederzeit ein- oder ausgeschaltet werden.
- 🗣️ **Zwei-Wege-Spracherfassung:**
  - **Amazon Alexa:** Interaktiver Dialog-Modus (über Alexa Actionable Notifications Skill) und schnelle Direktbefehle ohne Musikunterbrechung oder ungewollte Einkaufslisten-Einträge.
  - **Home Assistant Assist:** Vollständige Unterstützung via lokaler Spracherkennung (Custom Sentences mit Wildcard-Support) und nativer Home Assistant Listen-Befehle.
- 🏷️ **Intelligente, automatische Kategorisierung:**
  - Mehrstufige semantische Heuristik: Erkennung von Präfixen (*„Garten: …“*), Präpositionen (*„im Garten …“*, *„für das Smarthome …“*) und Kontext-Schlagwörtern (Pool, Rasen, Heizung, ESPHome, Lampe etc.).
  - Standard-Kategorien: *Haus & Garten*, *Smarthome*, *Projekte*, *Alltag*, *Inbox*.
- 🎴 **Moderne Custom Lovelace Cards (v1.4.0):**
  - **Brainstorm Card (`custom:brainstorm-card`):**
    - Zweistöckiges Design mit Schnellerfassungs-Toolbar, Auto-Kategorisierung und Pill-Filtern.
    - Integrierter Ansichts-Umschalter (`🧠 Mindmap` ⇄ `📋 Liste`) direkt in der Kopfzeile.
    - Erledigt-Verwaltung mit Durchstreich-Animation, Bearbeitungsfunktion und Quellen-Badges.
  - **NEU: Brainstorm Mindmap Card (`custom:brainstorm-mindmap-card`):**
    - Interaktives Radial-Synapsen-Layout für eine visuelle Gedankenlandkarte.
    - Zentraler Knotenpunkt (Inbox / Fokus-Kategorie) mit edlem, transparentem Brainstorm-Logo im Hintergrund.
    - Notizen dargestellt als charmante Gedankenwolken mit gestrichelten Konturen und Kategorie-Farbcodes.
    - Organische Bézier-Verbindungslinien, die beim Überfahren aufleuchten.
    - Frei verschiebbare Notizen per Drag & Drop (auf Desktop und Touchscreens).
    - Stufenloser Zoom & Pan per Mausrad, Pinch-Geste oder Steuerungsbuttons.
    - **Vollbild-Modus (`⛶`):** Per Knopfdruck oder Dashboard-Einbindung als beeindruckendes Vollbild-Erlebnis (ESC zum Schließen).
    - Direkte Aktionen an jeder Gedankenwolke (Erledigen, Text editieren, Kategorie wechseln, Löschen).
- ⚙️ **Konfigurations- & Options-Flow im HA-Backend:**
  - Unter *Einstellungen ➔ Geräte & Dienste ➔ Brainstorm Hub ➔ Konfigurieren* Kategorien komfortabel pflegen (hinzufügen, löschen, anpassen) und Optionen steuern.
  - Sichere Migration: Beim Löschen einer Kategorie werden verbliebene Ideen automatisch in die `Inbox` verschoben.
- 📝 **Automatischer Markdown-Export:**
  - Exportiert Ideen strukturiert nach Kategorien in Markdown-Dateien (z. B. `/config/brainstorm/`).
  - Ideal für Personal Knowledge Management (Obsidian, Logseq, Foam, SilverBullet).
- 📋 **Native Home Assistant To-do Plattform:**
  - Jede Brainstorm-Kategorie wird als echte Home Assistant To-do-Liste bereitgestellt (`todo.brainstorm_haus_garten`, `todo.brainstorm_inbox`, usw.).
- 🏛️ **100% Home Assistant Standard-konform:**
  - Entwickelt nach den offiziellen Richtlinien von [contributors.home-assistant.io](https://contributors.home-assistant.io/) (strikte Typisierung, non-blocking Event-Loop, `DeviceInfo`, saubere Translation-Keys).

---

## 📦 Installation

### Methode 1: Über HACS (Empfohlen)

1. Öffne **HACS** in deinem Home Assistant.
2. Klicke oben rechts auf das Drei-Punkte-Menü ➔ **Benutzerdefinierte Repositories**.
3. Trage folgende Repository-URL ein:
   ```text
   https://github.com/nukleuz80/ha_brainstorm
   ```
4. Wähle als Kategorie: **Integration**.
5. Klicke auf **Hinzufügen** und installiere die Integration.
6. Starte Home Assistant neu.

### Methode 2: Manuelle Installation

1. Lade das neueste Release herunter.
2. Kopiere den Ordner `custom_components/brainstorm` in dein Home Assistant Verzeichnis `/config/custom_components/`.
3. Kopiere die Dateien `www/brainstorm-card.js` und `www/brainstorm-mindmap-card.js` in `/config/www/`.
4. Trage die Ressourcen unter *Einstellungen ➔ Dashboards ➔ Ressourcen* ein:
   - **URL:** `/local/brainstorm-card.js?v=1.4.18` (Typ: `JavaScript-Modul`)
   - **URL:** `/local/brainstorm-mindmap-card.js?v=1.4.18` (Typ: `JavaScript-Modul`)
5. Starte Home Assistant neu.

---

## 🛠️ Konfiguration

1. Gehe in Home Assistant auf **Einstellungen ➔ Geräte & Dienste ➔ Integration hinzufügen**.
2. Suche nach **Brainstorm Hub** und schließe die Ersteinrichtung ab.
3. Über den Button **Konfigurieren** stehen dir zwei Menübereiche zur Verfügung:
   - **📁 Kategorien verwalten:** Neue Kategorien hinzufügen, ungenutzte löschen oder per Kommaliste anpassen.
   - **⚙️ Allgemeine Einstellungen & Export:** Standard-Kategorie festlegen, automatischen Markdown-Export aktivieren und Zielpfad konfigurieren.

---

## 🎴 Dashboard Cards einbinden

### 1. Brainstorm Card (Listenansicht mit integriertem Mindmap-Umschalter)
```yaml
type: custom:brainstorm-card
title: Brainstorm Hub
```

### 2. Brainstorm Mindmap Card (Dedizierte interaktive Gedankenlandkarte)
Ideal für reguläre Dashboard-Karten oder als **Panel-Ansicht (Vollbild)** auf Tablets und Monitoren:
```yaml
type: custom:brainstorm-mindmap-card
title: Brainstorm Mindmap
height: 600px               # Optionale Höhe (z.B. 550px, 600px, 100%)
default_category: Inbox     # Standard-Kategorie beim Laden (oder 'all')
```
*Tipp:* Klicke oben rechts auf das Vollbild-Symbol `⛶`, um die Mindmap jederzeit auf den gesamten Bildschirm zu vergrößern!

### 3. Eigenständiges Seitenleisten-Dashboard (`Brainstorm Hub`)
Für maximale Übersicht lässt sich Brainstorm als vollwertiger Menüpunkt direkt in der linken Home Assistant Seitenleiste einbinden (z. B. unter Pfad `/brainstorm-hub`):
- **Ansicht 1: Übersicht (Kombiniert):** Die interaktive Gedankenlandkarte (`custom:brainstorm-mindmap-card`) thront oben im Großformat (z. B. Höhe 580px), während sich die Schnelleingabe und Notizenliste (`custom:brainstorm-card`) mit Filtern und Badges direkt darunter befindet.
- **Ansicht 2: Mindmap Vollbild:** 100% Panel-Ansicht für ausgedehntes visuelles Brainstorming.
- **Ansicht 3: Listenansicht:** Schnelle, fokussierte Notizenliste für Tastatur- und Touch-Eingaben.

---

## 🗣️ Sprachsteuerung

### 1. Amazon Alexa

#### Variante A: Interaktiver Dialog-Modus (Empfohlen)
Triggere den Dialog per Sprachbefehl, Szene oder Alexa-Routine:
> 🗣️ *„Alexa, Neue Idee“* oder *„Alexa, Brainstorm“*  
> 🤖 **Alexa:** *„Brainstorm bereit. Sprich deine Notiz oder sage Ansage.“*  
> 🗣️ **Du:** *„Im Garten müssen die Rosen geschnitten werden.“*  
> 🤖 **Alexa:** *„Gespeichert unter Haus & Garten.“*

##### 📱 Einrichtung der Alexa-Routinen (Wichtig gegen Musik-Konflikte)
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

#### Variante B: Schnelle Direktbefehle
Direkt in einem Satz sprechen (Automation sendet automatisch einen internen Stopp-Befehl für eventuell gestartete Skills/Musik und bestätigt direkt):
- 🗣️ *„Alexa, **Idee** Rasensprenger reparieren.“* ➔ `Haus & Garten`
- 🗣️ *„Alexa, **Notiere** Kellerlicht dimmen.“* ➔ `Smarthome`
- 🗣️ *„Alexa, **Merke dir für den Garten** Tomaten düngen.“* ➔ `Haus & Garten`
- 🗣️ *„Alexa, **Brainstorm** Balkonkraftwerk Ertrag auswerten.“* ➔ `Smarthome`
- 🗣️ *„Alexa, **Neue Idee für Projekte** Smart Mirror bauen.“* ➔ `Projekte`

---

### 2. Home Assistant Assist

Assist versteht deine Notizen sowohl über dedizierte Sprachmuster als auch über Standard-Listenbefehle:

#### Freie Brainstorm-Befehle:
* 🗣️ *„Setze Rasenmähen auf Brainstorm“*
* 🗣️ *„Neue Idee Blumen gießen“*
* 🗣️ *„Notiere Backup der Datenbank erstellen“*
* 🗣️ *„Merke dir Reifen wechseln“*
* 🗣️ *„Brainstorm Zigbee Bewegungsmelder testen“*

#### Native Listenbefehle:
* 🗣️ *„Setze Rasenmähen auf die Liste Brainstorm Haus und Garten“*
* 🗣️ *„Füge Milch zu Brainstorm Inbox hinzu“*
* 🗣️ *„Hake Rasenmähen auf Brainstorm Haus und Garten ab“*

---

## 🛠️ Dienste (Services)

Die Integration stellt folgende Services bereit:

| Service | Beschreibung | Parameter |
| :--- | :--- | :--- |
| `brainstorm.add_idea` | Erstellt eine neue Idee mit automatischer oder manueller Kategorie | `text` (erforderlich), `category` (optional), `source` (optional), `tags` (optional) |
| `brainstorm.update_idea` | Aktualisiert Text, Kategorie oder Status (`active` / `completed`) | `id` (erforderlich), `text`, `category`, `status` |
| `brainstorm.delete_idea` | Löscht eine Idee unwiderruflich | `id` (erforderlich) |
| `brainstorm.add_category` | Erstellt eine neue Kategorie | `name` (erforderlich) |
| `brainstorm.remove_category` | Entfernt eine Kategorie (Ideen wandern in `Inbox`) | `name` (erforderlich) |
| `brainstorm.export_markdown` | Triggert sofortigen Markdown-Export | `path` (optional) |

---

## 📜 Versionshistorie & Changelog

| Version | Datum | Status & Highlights |
| :--- | :--- | :--- |
| **`v1.4.22`** | 25.10.2026 | **Prioritäten-Management & Visuelle Dringlichkeit:** Einführung von vier Prioritätsstufen (`low` 🟢, `medium` 🟡, `high` 🔴, `urgent` 🔥) mit automatischer Signalwort- und Tag-Erkennung (`dringend`, `wichtig`, `sofort`, `eilig`, `prio 1`, `wenn zeit`, `!urgent`, `!high` etc.) bei Spracheingaben via Alexa und Assist. 2-Pass-Parsing filtert Signalwörter unabhängig von der Reihenfolge der Kategoriepräfixe sauber heraus. 1-Klick-Prioritätswechsel direkt auf den Badges beider Lovelace-Cards (`brainstorm-card` und `brainstorm-mindmap-card`). Feuer- und Puls-Effekte für dringende Gedankenwolken in der Mindmap. Vollständige Integration in Sensoren (`priority_counts`), To-do-Listen, Logbook, Markdown-Export und Assist LLM Function-Calling API. |
| **`v1.4.21`** | 25.10.2026 | **Dynamische Kategorie-Erkennung & Semantisches Routing:** Vollständige dynamische Synthese von Aliassen und Schlagwörtern für alle aktiven Kategorien (inkl. *„Brainstorm“* und frei erstellten Kategorien) zur Laufzeit. Direkte Erkennung zusammengesetzter Projekt- und Themenpräfixe (*„Projekt Brainstorm erweitern“* ➔ ordnet *„Brainstorm erweitern“* zielsicher der Kategorie *„Projekte“* bzw. *„Brainstorm“* zu, statt in der Inbox zu landen). Behebung einer Fehlleitung im Alexa-Hauptmenü-Workflow (`brainstorm_alexa_main_menu_response`), bei der gesprochene Notizen mit Projektbezug versehentlich als Abfragebefehl abgefangen wurden. |
| **`v1.4.20`** | 24.10.2026 | **Assist LLM Tools & Function-Calling Integration:** Vollständige Bereitstellung des offiziellen Home Assistant LLM API (`homeassistant.helpers.llm`) für Sprachmodelle (OpenAI, Google Gemini, Ollama, Groq, lokale LLMs). Implementierung von 5 nativen Werkzeugen (`brainstorm_add_idea`, `brainstorm_get_ideas`, `brainstorm_complete_idea`, `brainstorm_delete_idea`, `brainstorm_list_categories`). Ermöglicht völlig freie, kontextsensitive Konversationen (z. B. *„Was steht im Smarthome noch an?“*, *„Markiere Hecke schneiden als erledigt“* oder *„Wir brauchen neue Blumentöpfe, merk dir das mal“* mit automatischer Kategorisierung). Sauberes Unload-Lifecycle-Management via `async_on_unload`. |
| **`v1.4.19`** | 24.10.2026 | **Erreichen des offiziellen Silver Quality Scale Status & Home Assistant Logbook / Aktivität Integration:** Vollständige Umsetzung und Erfüllung sämtlicher Kriterien der Home Assistant Integration Quality Scale für den **Silber-Status** (u. a. native `logbook.py`-Plattform mit `async_describe_events` zur lückenlosen Formatierung aller Brainstorm-Ereignisse – Idee erfasst, aktualisiert, erledigt, gelöscht – inklusive Icon und direkter Verknüpfung mit dem Geräte-Logbuch/Aktivitäts-Panel von Home Assistant; nativer Reconfigure-Flow (`async_step_reconfigure`) zur Live-Anpassung der Konfiguration direkt aus der HA-Oberfläche ohne Neuinstallation; standardkonforme Dienst-Fehlerbehandlung mittels `ServiceValidationError` und `HomeAssistantError` (`action-exceptions`); saubere Deregistrierung aller Dienste und Entitäten beim Entladen (`config-entry-unregistered`); offizielle Silver-Klassifizierung in `quality_scale.yaml` und `manifest.json`). |
| **`v1.4.18`** | 24.10.2026 | **Erreichen des offiziellen Bronze Quality Scale Status & Alexa-Speedup:** Vollständige Zertifizierung und Erfüllung aller Kriterien der Home Assistant Integration Quality Scale für den **Bronze-Status** (u. a. `runtime-data` nach modernstem HA 2024.4+ Standard mit `entry.runtime_data = store`, Parallelitäts-Steuerung `PARALLEL_UPDATES = 0` auf den Plattformen `sensor` und `todo`, Ergänzung von `"quality_scale": "bronze"` in `manifest.json` sowie Bereitstellung der offiziellen `quality_scale.yaml`). Zudem umfassende Performance-Optimierung der Alexa-Sprachsteuerung: Wegfall von künstlichen Delays und redundanten Cloud-Stopps sowie Einführung der direkten Ein-Schritt-Spracherfassung (*„Brainstorm bereit. Sprich deine Notiz oder sage Ansage.“*) für 4x schnellere Dialoge. |
| **`v1.4.17`** | 23.10.2026 | **Individuelle Kategoriefarben & Pill-Dots:** Vollständige Neuausrichtung des Farbsystems. Jede Kategorie erhält nun eine unverwechselbare, harmonische und kontraststarke Einzelfarbe (z. B. Inbox = Royal Blue `#2563eb`, Smarthome = Aqua/Cyan `#06b6d4`, Haus & Garten = Emerald Green `#10b981`, Projekte = Indigo `#6366f1`, Alltag = Warm Amber `#f59e0b`, Brainstorm = Electric Purple `#a855f7`, Ideen = Pink `#ec4899`, Einkauf = Orange `#ea580c`, Finanzen = Teal `#14b8a6`, Familie = Rose `#f43f5e`, Gesundheit = Lime `#84cc16`). Automatische, deterministische Zuweisung einzigartiger Farbtöne für alle benutzerdefinierten Kategorien via Hash-Algorithmus. Kartenkanten, synaptische Verbindungslinien und Kategorie-Tags in Mindmap und Notizenliste spiegeln die Kategoriefarbe unmittelbar wider. Ergänzung von farbigen Indikatorpunkten (`pill-dot`) in der oberen Kategorie-Leiste zur sofortigen optischen Orientierung. |
| **`v1.4.16`** | 23.10.2026 | **Organische Multi-Ring Mindmap & Antikollisions-Layout:** Vollständige Neukonzeption der visuellen Mindmap-Knotenanordnung. Statt aller Notizen auf einem engen Kreisradius nutzt Brainstorm Mindmap nun ein intelligentes, mehrstufiges konzentrisches Ellipsen-Layout (1 Ring bei bis zu 6 Notizen, 2 Ringe bei 7–12 Notizen, 3 gestaffelte Ringe bei 13–20+ Notizen) unter optimaler Ausnutzung der Bildschirmbreite. Ein nativer Physik-Entspannungsdurchlauf (25 Iterationen) verhindert jegliche Überlappungen zwischen Ideenkarten und stellt sicher, dass das zentrale Glühbirnen-Symbol stets vollständig frei und sichtbar bleibt. Farbkodierte synaptische Bézier-Verbindungslinien passend zur jeweiligen Notizkategorie mit interaktivem Hover-Leuchten. Automatisches Zoom-to-Fit bei vielen Notizen und Beibehaltung manuell verschobener Karten. |
| **`v1.4.15`** | 23.10.2026 | **Bugfix Visueller Karteneditor & Seitenleisten-Dashboard:** Behebung eines Problems, bei dem Schalter im visuellen Lovelace-Karteneditor (`ha-form`) beim Ein- oder Ausschalten keine Wirkung zeigten und stets alle Elemente angezeigt blieben. Implementierung robuster Standardwerte (`default: true` in Schema & Initialisierung), vollständige Synchronisation deaktivierter Schalter (`show_quick_input`, `show_categories`, `show_badge`, `show_mindmap_button`, `show_color_toggle`, `show_source_icons`, `show_timestamps`, `allow_edit`, `allow_delete` bzw. `show_bulb_watermark`, `show_toolbar`, `show_fullscreen_btn`, `show_controls`, `show_add_btn`) und Beseitigung von Event-Bubbling-Kollisionen. Sofortige Live-Reaktivität in der Kartenvorschau und auf Dashboards. Optimierung der Dashboard-Einbindung für die Seitenleiste (Mindmap oben im Großformat, Notizenliste darunter). |
| **`v1.4.14`** | 23.10.2026 | **Geräte-Herkunftserfassung für Alexa & Assist:** Erfassung und optische Anzeige des konkreten Auslösegeräts bei Spracheingaben sowohl in `brainstorm-card` als auch in `brainstorm-mindmap-card` (z. B. `🗣️ Alexa (Echo Show Küche)`, `🗣️ Alexa (Wohnzimmer Echo Dot)`, `✨ Assist (Jan)` oder `✨ Assist (Küche Satellit)`). Vollständige Unterstützung in Sensor-Attributen (`device`), To-Do-Listen-Beschreibungen, Markdown-Export und `add_idea`/`update_idea`-Services. |
| **`v1.4.13`** | 22.10.2026 | **Sprachausgabe & Abfrage via Alexa & Assist:** Neuer Service `brainstorm.get_announcement` und Attribut `speech_overview` zur schnellen, flüssigen und gut verständlichen Sprachausgabe aktiver Notizen aller oder einzelner Kategorien (z. B. *„Smarthome hat drei Einträge: a, b und c“*). Interaktiver Alexa-Sprachdialog (*„Alexa, öffne Brainstorm“* ➔ *„Eintrag oder Ansage?“*) und native Assist-Intents (*„Was steht in Brainstorm?“*, *„Was habe ich in Smarthome notiert?“*). |
| **`v1.4.12`** | 22.10.2026 | **Resilienter Sensor-Fallback & Integration-Scoped Picker:** Automatischer Fallback auf `sensor.brainstorm_ideen_ubersicht`, falls in der Kartenkonfiguration eine fremde Entität (z. B. Feuchte-/Temperatursensor) ohne `ideas`-Attribut hinterlegt ist. Schutz im visuellen Editor durch Einschränkung des Entitäten-Selectors auf `integration: brainstorm`. |
| **`v1.4.11`** | 22.10.2026 | **Whitespace-Trimming & Robuster Kategorie-Filter:** Automatisches `.trim()` auf Kategorienamen bei Initialisierung (`default_category`), Pill-Klicks und Filterlogik in `brainstorm-card` und `brainstorm-mindmap-card`. Verhindert das versehentliche Nicht-Anzeigen von Ideen bei versehentlich eingegebenen Leerzeichen am Ende von Kategorienamen (z. B. `"Brainstorm "`). |
| **`v1.4.10`** | 21.10.2026 | **Kategorie- & Notiz-Validierung:** Robuste Validierung beim Erstellen und Ändern von Kategorien sowie beim Bearbeiten von Notizen in beiden Lovelace-Karten. Verhindert das Absenden leerer Eingaben oder von Duplikaten (Groß-/Kleinschreibung-unabhängig) mit klarer Fehlermeldung (`⚠️ Bitte gib einen Kategorienamen ein.`), roter Umrandung und sanfter Schüttel-Animation (`dialog-shake`). Automatisches Zurücksetzen der Fehleranzeige beim Weitertippen. Ergänzung von `ServiceValidationError` im Backend (`__init__.py` und `store.py`) für saubere Fehlermeldungen bei Service-Aufrufen. |
| **`v1.4.9`** | 21.10.2026 | **Notizen-Rendering Fix:** Behebung eines Laufzeitfehlers (`TypeError: this._escapeHtml is not a function`), durch den aktive Ideen in der Hauptkarten-Listenansicht nicht gerendert wurden. Implementierung von `_escapeHtml()` und `_getSensorEntity()` in `BrainstormCard`. |
| **`v1.4.8`** | 21.10.2026 | **Kategorie-Eingabefeld Layout-Fix:** Behebung des CSS-Kollabierens des Eingabefelds im Modal-Dialog *„Neue Kategorie“* (`width: 100%`, `box-sizing: border-box`, `min-height: 42px` und flexibler Wrapper), sodass das Feld über die volle Dialogbreite dargestellt wird und nicht mehr horizontal zusammengestaucht ist. |
| **`v1.4.7`** | 21.10.2026 | **Bugfix SyntaxError & Stabilität der Lovelace-Cards:** Behebung eines doppelten Deklarationsfehlers (`Identifier 'pillsContainer' has already been declared`), der das Laden der Karte im Browser verhinderte. `customElements.define`-Guards für beide Karten und Editoren ergänzt. Behebung des YAML-Parsingfehlers für unquoted Doppelpunkte in `services.yaml`. |
| **`v1.4.6`** | 20.10.2026 | **Visuelle Kartenkonfiguratoren (Lovelace Visual Editor):** Vollständige Unterstützung des nativen Home Assistant UI-Karteneditors (`getConfigElement()` & `getStubConfig()`) für beide Karten (`brainstorm-card` und `brainstorm-mindmap-card`). Alle Einstellungen lassen sich nun komfortabel per Klick, Dropdown und Schalter ohne YAML-Code anpassen: Kartentitel, Sensor-Auswahl mit Entitätenfilter, Farbmodus (`theme` vs. `multicolor`), Standard-Kategorie, Maximalanzahl an Notizen (`max_items`), Ein-/Ausblenden der Schnelleingabezeile, Kategorie-Filterleiste, Zähler-Badge, Mindmap-Button, Theme-Farbumschalter, Quellen-Icons, Zeitstempel sowie Bearbeitungs- und Löschrechte. In der Mindmap zusätzlich Steuerung von Höhe (`height`), Glühbirnen-Wasserzeichen, Toolbar, Vollbild-Button und Zoom-/Zentrier-Controls. |
| **`v1.4.5`** | 20.10.2026 | **Dynamische Home Assistant Theme-Farben & Farbmodus-Umschalter:** Neuer Farbmodus-Umschalter (`🎨` Theme-Modus ⇄ `🌈` Bunt-Modus) sowohl in der Lovelace-Hauptkarte als auch in der Mindmap. Im Theme-Modus passen sich alle Knoten, Kategorie-Pills, Verbindungslinien und Tags dynamisch an das aktive Home Assistant Theme an (`var(--primary-color)` und semantische Farbvariablen via `color-mix`), sodass sich das Design nahtlos in Dark/Light-Themes sowie Mushroom/Minimalist-Themes einfügt. Präferenz wird browserweit in `localStorage` (`brainstorm_color_mode`) und via Card-Option (`color_mode`) synchronisiert. |
| **`v1.4.4`** | 20.10.2026 | **Transparente Glühbirne & Vollständige Raumnutzung:** Ersatz des überlagerten Wasserzeichens durch ein transparentes SVG der leuchtenden Brainstorm-Birne (`brainstorm-bulb.svg` ohne störenden grauen Kasten, 100% freigestellt). Vollständige Ausnutzung der gesamten Bildschirm-/Popup-Höhe im 3/4-Modal (`height: 100%`, dynamische Radius-Skalierung und `ResizeObserver` zur Beseitigung ungenutzter Freiflächen). |
| **`v1.4.3`** | 20.10.2026 | **Zitterfreie Interaktion & Native Mushroom-Dialoge:** Beseitigung jeglichen Ruckelns/Zitterns beim Anklicken und Bearbeiten von Notizen (Hysterese-Drag-Schwelle von 5px, Entfernung sprung-auslösender Hover-Translationen und Drosselung unnötiger State-Re-Renders). Vollständiger Ersatz aller nativen Browser-Prompts (`prompt()` / `confirm()`) durch hochwertige, animierte In-Card Mushroom-Dialoge für Notiz-Bearbeitung, Kategorie-Auswahl-Chips und Neuanlage. |
| **`v1.4.2`** | 20.10.2026 | **Mushroom & Minimalist Design & 3/4-Modal-Layer:** Vollständige Designanpassung der Mindmap an Mushroom / UI Minimalist Design (helle/neutrale runde Buttons, dezente Pastell-/Kategoriefarben, feine Rahmen statt harter Kontraste). Die Mini-Vorschau in der Karte wurde durch ein zentriertes 3/4-Bildschirm-Modal-Popup (`75vw` × `75vh`) mit Blur-Backdrop und Schließen-Button ersetzt. |
| **`v1.4.1`** | 20.10.2026 | **Mindmap-Darstellung:** Theme-konforme Farben für Kategorien und Vollbild-Schaltfläche sowie nahezu bildschirmhohe Standarddarstellung. |
| **`v1.4.0`** | 20.10.2026 | **Intelligente Text-Optimierung & NLP:** Automatische Bereinigung gesprochener Notizen (Filterung von Gesprächsfloskeln, Partizip-zu-Infinitiv-Transformation, Rechtschreibprüfung und automatische Substantiv-Großschreibung). Schalter im Options-Flow hinzugefügt. |
| **`v1.3.0`** | 20.10.2026 | **Brainstorm Mindmap Card:** Neue interaktive Lovelace-Karte (`custom:brainstorm-mindmap-card`) mit Radial-Synapsen-Layout, transparentem Logo-Wasserzeichen im Zentrum, Gedankenwolken und Vollbild-Modus (`⛶`). Integrierter Umschalter (`🧠 Mindmap` ⇄ `📋 Liste`) in der Hauptkarte. |
| **`v1.2.1`** | 20.10.2026 | **Fehlerbehebungen & Stabilität:** Beseitigung von `ResponseNone`-Einträgen, Vermeidung von Musik-Kollisionen bei Alexa-Befehlen, Korrektur des Assist-Wildcard-Parsing-Fehlers, Behebung des Dashboard-Kartenfehlers (`counts is not defined`). |
| **`v1.1.0`** | 20.10.2026 | **Frontend Redesign & Standards:** 2-stufiges Layout für die Lovelace Card, HACS-Kompatibilität, vollständige `DeviceInfo`-Anbindung und Assist-Sprachunterstützung. |
| **`v1.0.0`** | 19.10.2026 | **Initiales Release:** Kern-Integration Brainstorm Hub, To-do-Plattform, Markdown-Export und Alexa-Sprachdialog. |

---

## 📄 Lizenz

Dieses Projekt ist unter der **MIT-Lizenz** lizenziert – siehe [LICENSE](LICENSE) für Details.

Copyright © 2026 [nukleuz80](https://github.com/nukleuz80)
