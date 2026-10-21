# 🧠 Brainstorm Hub for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/default)
[![Version](https://img.shields.io/badge/version-1.4.9-blue.svg)](https://github.com/nukleuz80/ha_brainstorm/releases)
[![GitHub Release](https://img.shields.io/github/v/release/nukleuz80/ha_brainstorm)](https://github.com/nukleuz80/ha_brainstorm/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/nukleuz80/ha_brainstorm)

**Brainstorm Hub** ist die smarte Ideen-, Gedanken- und Notizen-Sammelzentrale für dein Home Assistant Smarthome.  
Egal ob beim Kochen, im Garten oder unterwegs: Erfasse Geistesblitze sekundenschnell per Sprache (**Amazon Alexa** oder **Home Assistant Assist**), über das Lovelace-Dashboard oder Automationen. Brainstorm ordnet deine Ideen durch intelligente Heuristiken automatisch der passenden Kategorie zu und synchronisiert sie auf Wunsch als Markdown-Dateien für Obsidian, Logseq oder Nextcloud.

---

## 🌟 Highlights & Features

- 🧠 **Intelligente Text-Optimierung & NLP-Bereinigung (NEU in v1.4.0):**
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
   - **URL:** `/local/brainstorm-card.js?v=1.4.9` (Typ: `JavaScript-Modul`)
   - **URL:** `/local/brainstorm-mindmap-card.js?v=1.4.9` (Typ: `JavaScript-Modul`)
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

---

## 🗣️ Sprachsteuerung

### 1. Amazon Alexa

#### Variante A: Interaktiver Dialog-Modus (Empfohlen)
Triggere den Dialog per Sprachbefehl, Szene oder Alexa-Routine:
> 🗣️ *„Alexa, Neue Idee“* oder *„Alexa, Brainstorm“*  
> 🤖 **Alexa:** *„Was möchtest du notieren?“*  
> 🗣️ **Du:** *„Im Garten müssen die Rosen geschnitten werden.“*  
> 🤖 **Alexa:** *„Zu Brainstorm hinzugefügt unter Haus & Garten.“*

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
