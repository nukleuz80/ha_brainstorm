# 🧠 Brainstorm Hub for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/default)
[![GitHub Release](https://img.shields.io/github/v/release/nukleuz80/ha_brainstorm)](https://github.com/nukleuz80/ha_brainstorm/releases)

**Brainstorm Hub** ist eine smarte Ideen- und Gedanken-Sammelzentrale für Home Assistant. Erfasse Geistesblitze per Sprache (Alexa Custom Skill / Cloud), Dashboard oder Automationen, lasse sie automatisch nach Kategorien einordnen und synchronisiere sie optional als Markdown-Notizen.

---

## ✨ Features

- 🗣️ **Spracherfassung (Alexa Dialog & Nabu Casa Cloud):** Schnelles Aufnehmen von Notizen über Alexa ("Alexa, starte Brainstorm...").
- 🏷️ **Intelligente Kategorisierung:** Automatische Einordnung in Kategorien wie *Haus & Garten*, *Smarthome*, *Projekte*, *Alltag* und *Inbox*.
- ⚙️ **Kategorienverwaltung:** Direkt im Home Assistant Backend (Optionen-Flow) oder komfortabel auf der Dashboard-Karte (Erstellen, Bearbeiten, Löschen).
- 📝 **Automatischer Markdown-Export:** Speichert Ideen und Notizen geordnet nach Kategorien in Markdown-Dateien für Obsidian, Logseq etc.
- 🎴 **Custom Lovelace Card:** Moderne Übersichtskarte mit Filtern, Schnell-Eingabe, Quell-Icons (🗣️ Alexa, 📝 Notiz, 🎛️ Dashboard) und Erledigt-Verwaltung.
- ✅ **Erledigt-Status:** Ideen abhaken, durchstreichen und bei Bedarf wiederherstellen oder löschen.

---

## 📦 Installation

### Über HACS (Custom Repository)
1. In Home Assistant **HACS** öffnen.
2. Oben rechts auf das Drei-Punkte-Menü ➔ **Benutzerdefinierte Repositories** klicken.
3. Repository-URL eintragen: `https://github.com/nukleuz80/ha_brainstorm`
4. Kategorie: **Integration**
5. Auf **Hinzufügen** klicken und anschließend die Integration installieren.
6. Home Assistant neu starten.

### Manuelle Installation
1. Den Ordner `custom_components/brainstorm` in dein `/config/custom_components/`-Verzeichnis kopieren.
2. Die Datei `www/brainstorm-card.js` in dein `/config/www/`-Verzeichnis kopieren.
3. Unter *Einstellungen ➔ Dashboards ➔ Ressourcen* `/local/brainstorm-card.js` als JavaScript-Modul hinzufügen.
4. Home Assistant neu starten.

---

## 🛠️ Konfiguration

1. Unter **Einstellungen ➔ Geräte & Dienste ➔ Integration hinzufügen** nach **Brainstorm Hub** suchen.
2. Den Schritten des Einrichtungsassistenten folgen.
3. Über **Konfigurieren** lassen sich Kategorien pflegen und der automatische Markdown-Export einstellen.

---

## 🎴 Lovelace Card

```yaml
type: custom:brainstorm-card
title: Brainstorm Hub
```

---

## 🗣️ Alexa Sprachsteuerung: Varianten & Beispiele

Ideen können auf verschiedene Arten per Sprache mit Alexa erfasst werden:

### 1. Interaktiver Dialog-Modus (Empfohlen)
Aktiviere den Dialog über die Szene oder eine Alexa-Routine:
- *"Alexa, aktiviere Neue Idee"*
- *"Alexa, starte Brainstorm"*
- *"Alexa, Neue Idee"*

**Alexa fragt:** *„Was möchtest du notieren?“*  
**Deine Antwort (Beispiele):**
1. **Haus & Garten:** *"Im Garten müssen die Rosen geschnitten werden"*
2. **Haus & Garten (mit Kategorie):** *"Garten: Neue Solarleuchten für die Terrasse kaufen"*
3. **Smarthome:** *"Neuen Zigbee Bewegungsmelder im Flur anlernen"*
4. **Smarthome:** *"Heizungsautomation für das Badezimmer überprüfen"*
5. **Projekte:** *"Projekt: Holzregal für die Werkstatt bauen"*
6. **Projekte:** *"Geburtstagsüberraschung für Anna planen"*
7. **Alltag:** *"Kühlschrank am Wochenende abtauen"*
8. **Alltag:** *"Mülltonnen heute Abend an die Straße stellen"*
9. **Alltag / Haushalt:** *"Akkus der Fernbedienung aufladen"*
10. **Inbox (Allgemein):** *"Telefonnummer vom Handwerker heraussuchen"*

---

### 2. Schnelle Direktbefehle (Ein-Satz-Erfassung)
Ohne vorherige Nachfrage direkt in einem Satz sprechen:
1. *"Alexa, **Idee** Rasensprenger reparieren"* ➔ `Haus & Garten`
2. *"Alexa, **Notiere** Licht im Keller automatisch ausschalten"* ➔ `Smarthome`
3. *"Alexa, **Merke dir für den Garten** Blumen giessen"* ➔ `Haus & Garten`
4. *"Alexa, **Notiz** Waschmaschine entkalken"* ➔ `Alltag`
5. *"Alexa, **Neue Idee für Projekte** Smart Mirror mit Raspberry Pi bauen"* ➔ `Projekte`
6. *"Alexa, **Brainstorm** Balkonkraftwerk Ertrag auswerten"* ➔ `Smarthome`
7. *"Alexa, **Schreibe** ESPHome Sensor kalibrieren"* ➔ `Smarthome`
8. *"Alexa, **Merke** Steuerunterlagen sortieren"* ➔ `Alltag`
9. *"Alexa, **Erinnere mich an** Poolfilter reinigen"* ➔ `Haus & Garten`
10. *"Alexa, **Idee** Notizbuch für Besprechung einpacken"* ➔ `Inbox`

---

### 3. Home Assistant Assist / Cloud Intent
Über Home Assistant Assist oder Cloud-Intents:
- *"Setze Rasenmähen auf Brainstorm"*
- *"Neue Idee im Bereich Smarthome Heizplan anpassen"*

---

## 📄 Lizenz

MIT License © 2026 nukleuz80

