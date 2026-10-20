# 🧠 Brainstorm Hub for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/default)
[![GitHub Release](https://img.shields.io/github/v/release/nukleuz80/ha_brainstorm)](https://github.com/nukleuz80/ha_brainstorm/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/nukleuz80/ha_brainstorm)

**Brainstorm Hub** ist die smarte Ideen-, Gedanken- und Notizen-Sammelzentrale für dein Home Assistant Smarthome.  
Egal ob beim Kochen, im Garten oder unterwegs: Erfasse Geistesblitze sekundenschnell per Sprache (**Amazon Alexa** oder **Home Assistant Assist**), über das Lovelace-Dashboard oder Automationen. Brainstorm ordnet deine Ideen durch intelligente Heuristiken automatisch der passenden Kategorie zu und synchronisiert sie auf Wunsch als Markdown-Dateien für Obsidian, Logseq oder Nextcloud.

---

## 🌟 Highlights & Features

- 🗣️ **Zwei-Wege-Spracherfassung:**
  - **Amazon Alexa:** Interaktiver Dialog-Modus (über Alexa Actionable Notifications Skill) und schnelle Direktbefehle ohne Musikunterbrechung oder ungewollte Einkaufslisten-Einträge.
  - **Home Assistant Assist:** Vollständige Unterstützung via lokaler Spracherkennung (Custom Sentences mit Wildcard-Support) und nativer Home Assistant Listen-Befehle.
- 🏷️ **Intelligente, automatische Kategorisierung:**
  - Mehrstufige semantische Heuristik: Erkennung von Präfixen (*„Garten: …“*), Präpositionen (*„im Garten …“*, *„für das Smarthome …“*) und Kontext-Schlagwörtern (Pool, Rasen, Heizung, ESPHome, Lampe etc.).
  - Standard-Kategorien: *Haus & Garten*, *Smarthome*, *Projekte*, *Alltag*, *Inbox*.
- 🎴 **Moderne Custom Lovelace Card (v1.2.1):**
  - **Zweistöckiges Design:** Obere Toolbar mit Kategorie-Dropdown (*Auto Erkennen* oder feste Kategorie) und schnellem `➕`-Button zum Anlegen neuer Kategorien.
  - **Breite Eingabezeile:** Volle Breite für das Textfeld und übersichtlicher Hinzufügen-Button.
  - **Pills mit Zeilenumbruch:** Keine abgeschnittenen Buttons mehr auf Smartphones.
  - **Erledigt-Verwaltung:** Ideen abhaken, durchstreichen und über den Filter `✓ Erledigt` jederzeit einsehen, wiederherstellen oder löschen.
  - **Quellen-Badges:** Zeigt auf einen Blick, woher die Idee stammt (`🗣️ Alexa`, `✨ Assist`, `💻 Dashboard`, `📝 Notiz`).
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
3. Kopiere die Datei `www/brainstorm-card.js` in `/config/www/`.
4. Trage die Ressource unter *Einstellungen ➔ Dashboards ➔ Ressourcen* ein:
   - **URL:** `/local/brainstorm-card.js?v=1.2.1`
   - **Typ:** `JavaScript-Modul`
5. Starte Home Assistant neu.

---

## 🛠️ Konfiguration

1. Gehe in Home Assistant auf **Einstellungen ➔ Geräte & Dienste ➔ Integration hinzufügen**.
2. Suche nach **Brainstorm Hub** und schließe die Ersteinrichtung ab.
3. Über den Button **Konfigurieren** stehen dir zwei Menübereiche zur Verfügung:
   - **📁 Kategorien verwalten:** Neue Kategorien hinzufügen, ungenutzte löschen oder per Kommaliste anpassen.
   - **⚙️ Allgemeine Einstellungen & Export:** Standard-Kategorie festlegen, automatischen Markdown-Export aktivieren und Zielpfad konfigurieren.

---

## 🎴 Dashboard Card einbinden

Füge deiner Lovelace-Oberfläche eine neue Karte hinzu (Code-Editor):

```yaml
type: custom:brainstorm-card
title: Brainstorm Hub
```

---

## 🗣️ Sprachsteuerung

### 1. Amazon Alexa

#### Variante A: Interaktiver Dialog-Modus (Empfohlen)
Triggere den Dialog per Sprachbefehl, Szene oder Alexa-Routine:
> 🗣️ *„Alexa, Neue Idee“*  
> 🤖 **Alexa:** *„Was möchtest du notieren?“*  
> 🗣️ **Du:** *„Im Garten müssen die Rosen geschnitten werden.“*  
> 🤖 **Alexa:** *„Zu Brainstorm hinzugefügt unter Haus & Garten.“*

#### Variante B: Schnelle Direktbefehle
Direkt in einem Satz sprechen (Automation stoppt eventuelle Musik-Wiedergabe automatisch):
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

## 📄 Lizenz

Dieses Projekt ist unter der **MIT-Lizenz** lizenziert – siehe [LICENSE](LICENSE) für Details.

Copyright © 2026 [nukleuz80](https://github.com/nukleuz80)
