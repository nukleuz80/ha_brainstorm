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

## 📄 Lizenz

MIT License © 2026 nukleuz80

