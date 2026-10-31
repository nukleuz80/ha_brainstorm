<div align="center">

# 🧠 Brainstorm Hub für Home Assistant

**[🇩🇪 Deutsch](README_de.md)** &nbsp;|&nbsp; **[🇬🇧 English](README.md)**

[![German Docs](https://img.shields.io/badge/Sprache-Deutsch%20%F0%9F%87%A9%F0%9F%87%AA-green.svg)](README_de.md)
[![English Docs](https://img.shields.io/badge/Language-English%20%F0%9F%87%AC%F0%9F%87%A7-blue.svg)](README.md)
[![Open in HACS](https://img.shields.io/badge/HACS-Add%20Repository-41BDF5?logo=home-assistant&logoColor=white)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nukleuz80&repository=ha_brainstorm&category=integration)
[![Start Config Flow](https://img.shields.io/badge/Home%20Assistant-Integration%20hinzuf%C3%BCgen-41BDF5?logo=home-assistant&logoColor=white)](https://my.home-assistant.io/redirect/config_flow_start/?domain=brainstorm)
[![Version](https://img.shields.io/badge/version-1.4.53-blue.svg)](https://github.com/nukleuz80/ha_brainstorm/releases)
[![Vibe Coding](https://img.shields.io/badge/Vibe%20Coding-100%25%20mit%20Hingabe-ff69b4?logo=sparkles&logoColor=white)](https://github.com/nukleuz80/ha_brainstorm)
[![Quality Scale](https://img.shields.io/badge/Quality%20Scale-Silver-C0C0C0.svg)](https://developers.home-assistant.io/docs/integration_quality_scale_index/)
[![GitHub Release](https://img.shields.io/github/v/release/nukleuz80/ha_brainstorm)](https://github.com/nukleuz80/ha_brainstorm/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/nukleuz80/ha_brainstorm)

</div>

**Brainstorm Hub** ist die smarte Ideen-, Gedanken- und Notizen-Sammelzentrale für dein Home Assistant Smarthome.  
Egal ob beim Kochen, im Garten, unter der Dusche oder unterwegs: Erfasse Geistesblitze sekundenschnell per Sprache (**Amazon Alexa** oder **Home Assistant Assist**), über das Lovelace-Dashboard oder Automationen. Brainstorm ordnet deine Ideen durch intelligente Heuristiken automatisch der passenden Kategorie zu und synchronisiert sie auf Wunsch als Markdown-Dateien für Obsidian, Logseq oder Nextcloud.

---

## 🌟 🗣️ Key Feature: Nahtlose Amazon Alexa Hands-Free Spracherfassung

> 🗣️ *„Alexa, Brainstorm“* ➔ 🤖 *„Brainstorm bereit. Sprich deine Notiz oder sage Ansage.“*  
> 🗣️ *„Dringend Garten: Rasenmäher reparieren“* ➔ 🤖 *„Gespeichert unter Haus & Garten [🔥 Dringend].“*

Brainstorm Hub verwandelt alle deine **Amazon Echo**-Geräte im Haus in sekundenschnelle, reibungslose Ideensammler – perfekt beim Kochen, in der Werkstatt oder im Garten, wenn du keine Hand frei hast!

### ⚡ Warum die Alexa-Spracherfassung das absolute Herzstück ist:
- 🚫 **Keine Musik- & Einkaufslisten-Kollisionen mehr:** Standardmäßig leitet Alexa freie Notizen oft in unübersichtliche Amazon-Einkaufslisten um oder versucht die Rockband *„Brainstorm“* auf Spotify abzuspielen. Brainstorm Hub fängt dies durch vorkonfigurierte Routine-Empfehlungen und automatische Hintergrund-Stopp-Befehle vollständig ab – für ein 100 % lautloses, sauberes Dialogerlebnis!
- 🗣️ **Zwei-Wege-Dialog-Modus:** Sag einfach *„Alexa, Brainstorm“* oder *„Alexa, Neue Idee“*. Alexa hört aktiv zu, quittiert deine Notiz und bestätigt dir direkt per Sprache die zugeordnete Kategorie und Priorität.
- ⚡ **Schnelle Direktbefehle in einem Satz:** Wenn es schnell gehen muss: *„Alexa, notiere in Smarthome Kellerlicht dimmen“* oder *„Alexa, Idee dringend Garten: Terrasse reinigen“*.
- 🧠 **Automatische NLP-Textbereinigung & Grammatik-Transformation:** Filtert lästige Gesprächsfloskeln (*„schreib bitte auf dass wir...“* ➔ *„Terrasse reinigen“*), korrigiert Tipp-/Sprachfehler und wandelt passive Hilfsverb-Endungen in präzise Handlungsaufforderungen um.
- 🏷️ **Intelligente Prioritäts- & Kategorie-Extraktion:** Erkennt Signalwörter (*„dringend“*, *„wichtig“*, *„sofort“*, *„prio 1“*, *„wenn zeit ist“*) und Kontextbegriffe (*„für den Garten“*, *„im Smarthome“*) unabhängig von der Satzreihenfolge.
- 📍 **Geräte-Herkunftserfassung:** Erkennt genau, welches Echo-Gerät die Notiz aufgenommen hat (z. B. `🗣️ Alexa (Echo Show Küche)` vs. `🗣️ Alexa (Garten Echo Dot)`).

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

### Methode 1: Über HACS (Empfohlen – 1 Klick)

Klicke einfach auf diesen Button, um das Repository direkt in deiner Home Assistant Installation im HACS zu öffnen und hinzuzufügen:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nukleuz80&repository=ha_brainstorm&category=integration)

<details>
<summary><b>Alternativ: Manuell in HACS eintragen</b></summary>

1. Öffne **HACS** in deinem Home Assistant.
2. Klicke oben rechts auf das Drei-Punkte-Menü ➔ **Benutzerdefinierte Repositories**.
3. Trage folgende Repository-URL ein:
   ```text
   https://github.com/nukleuz80/ha_brainstorm
   ```
4. Wähle als Kategorie: **Integration**.
5. Klicke auf **Hinzufügen** und installiere die Integration.
6. Starte Home Assistant neu.
</details>

### Methode 2: Manuelle Installation

1. Lade das neueste Release herunter.
2. Kopiere den Ordner `custom_components/brainstorm` in dein Home Assistant Verzeichnis `/config/custom_components/`.
3. Kopiere die Dateien `www/brainstorm-card.js` und `www/brainstorm-mindmap-card.js` in `/config/www/`.
4. Trage die Ressourcen unter *Einstellungen ➔ Dashboards ➔ Ressourcen* ein:
   - **URL:** `/local/brainstorm-card.js?v=1.4.53` (Typ: `JavaScript-Modul`)
   - **URL:** `/local/brainstorm-mindmap-card.js?v=1.4.53` (Typ: `JavaScript-Modul`)
5. Starte Home Assistant neu.

---

## ⏰ Erinnerungen & Benachrichtigungen

Brainstorm erinnert dich von selbst an fällige Einträge, und zwar über die Dienste, die du in Home Assistant ohnehin eingerichtet hast. Alles ist optional und läuft lokal.

**Termin festlegen**
- **Per Sprache (Skill):** *„Alexa, sage Brainstorm erinnere mich morgen um 8 an die Mülltonnen“*. Verstanden werden z. B. *heute Abend*, *morgen früh*, *übermorgen*, *am Freitag*, *nächste Woche*, *am 25.11.*, *in zwei Stunden*, *um halb neun*.
- **Per Sprache (nativ):** *„Alexa, erinnere mich morgen um 8 an …“*. Amazon legt dabei eventuell zusätzlich eine eigene Erinnerung an.
- **In den Listen:** Fälligkeitsdatum in den To-do-Listen von Home Assistant setzen. Ein reines Datum bedeutet 9:00 Uhr.
- **Auf der Karte:** Eintrag lange drücken ➔ *Erinnern: heute Abend / morgen früh / nächste Woche / Zeitpunkt wählen*.
- **In Automationen:** `brainstorm.add_idea` und `brainstorm.update_idea` mit dem Feld `due`.

**Einstellen** unter **Brainstorm Hub ➔ Konfigurieren ➔ Erinnerungen & Benachrichtigungen**. Jede Funktion hat ihren eigenen Schalter:

| Bereich | Schalter | Was es tut |
| :--- | :--- | :--- |
| **Ein/Aus & Kanäle** | Erinnerungen nutzen | Hauptschalter für alles in diesem Menü |
| | Alexa-Ansage | Aus, Echo des Eintrags, zuletzt genutzter Echo oder feste Echos (benötigt Alexa Media) |
| | Benachrichtigungen senden | Beliebige `notify`-Dienste; die Companion-App bekommt die Knöpfe **Erledigt**, **1 Stunde später** und **Morgen** |
| | Wichtige offene Einträge erneut senden | Hohe oder dringende Einträge gehen nach einer Wartezeit an weitere Dienste, z. B. Pushover |
| **Ruhezeit, Briefing & Rückblick** | Ruhezeit nutzen | Erinnerungen warten; Dringendes erreicht das Handy, aber kein Echo spricht |
| | Tägliches Briefing | Zu einer Uhrzeit, optional erst wenn ein Sensor oder eine Person jemanden meldet |
| | Wochenrückblick | Nennt lange offene Einträge |
| **Regeln pro Liste** | Regeln pro Liste nutzen | Pro Liste: normale Kanäle, nur Alexa, nur Benachrichtigungen (privat) oder nichts; eigene Dienste; an bestimmten Tagen senden; an einem Ort senden |
| **Orte & Heimkommen** | Beim Heimkommen erinnern | *„erinnere mich wenn ich heimkomme an den Müll“* |
| | An Orten erinnern | *„erinnere mich wenn ich bei Edeka bin an die Milch“* (nutzt deine Zonen) |
| **Personen** | Erinnerungen für andere nutzen | *„erinnere Lenja morgen um 8 an den Termin“* mit eigenen Kanälen pro Person |
| **Kalender, KI & Alexa** | Kalender | Trägt Erinnerungen einmalig in einen Kalender ein; spätere Änderungen werden nicht übertragen |
| | KI | Kürzt Briefing und Rückblick mit einer `ai_task`-Entität; dabei gehen deine Einträge an deren Anbieter |
| | Echte Alexa-Erinnerungen | Legt im Skill zusätzlich eine Amazon-Erinnerung an, dafür muss in der Alexa-Konsole **Build ➔ Permissions ➔ Reminders** eingeschaltet sein und einmal die Zustimmung in der Alexa-App erteilt werden |

**Weitere Sätze im Skill**
- *„Alexa, sage Brainstorm erledigt Mülltonnen“* oder nur *„… erledigt“* für die letzte Erinnerung
- *„Alexa, sage Brainstorm später“* verschiebt die letzte Erinnerung um eine Stunde
- *„Alexa, sage Brainstorm Ansage Alltag“* liest eine Kategorie vor, *„… Ansage“* nennt nur den Überblick, *„… alles vorlesen“* liest alles vor

**Eigene Automationen:** Jede Erinnerung löst das Ereignis `brainstorm_reminder_due` aus, auch ohne eingerichtete Dienste.

---

## 🛠️ Konfiguration

Klicke auf diesen Button, um die Ersteinrichtung von **Brainstorm Hub** direkt in Home Assistant zu starten:

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=brainstorm)

<details>
<summary><b>Alternativ: Manuell über die UI einrichten</b></summary>

1. Gehe in Home Assistant auf **Einstellungen ➔ Geräte & Dienste ➔ Integration hinzufügen**.
2. Suche nach **Brainstorm Hub** und schließe die Ersteinrichtung ab.
3. Über den Button **Konfigurieren** stehen dir zwei Menübereiche zur Verfügung:
   - **📁 Kategorien verwalten:** Neue Kategorien hinzufügen, ungenutzte löschen oder per Kommaliste anpassen.
   - **⚙️ Allgemeine Einstellungen & Export:** Standard-Kategorie festlegen, automatischen Markdown-Export aktivieren, Zielpfad konfigurieren und die Echos für die Spracheingabe auswählen.
</details>

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

#### Nur ausgewählte Echos nutzen
Standardmäßig kann jeder Echo Ideen erfassen. Zum Einschränken gehst du auf **Einstellungen ➔ Geräte & Dienste ➔ Brainstorm Hub ➔ Konfigurieren ➔ Allgemeine Einstellungen & Export** und wählst die Echos unter **Echo-Geräte für die Spracheingabe** aus. Eine leere Liste bedeutet: alle Echos.

Die Alexa-Sprachabläufe laufen als Automationen und Skripte in deiner eigenen Home-Assistant-Konfiguration. Jeder Einstieg braucht deshalb diese Bedingung (`echo_device` enthält den aufrufenden Echo):

```yaml
- condition: template
  value_template: >-
    {% set allowed = state_attr('sensor.brainstorm_ideen_ubersicht', 'allowed_echos') %}
    {{ not allowed or echo_device in allowed }}
```

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

#### Variante C: Eigener Alexa-Skill (optional, ein Satz, eine Antwort)
Ohne Skill antwortet Alexa auf *„Alexa, notiere …“* oft zuerst mit einer Fehlermeldung, weil sie den Befehl nicht kennt. Mit deinem eigenen Skill gibt es nur eine einzige Antwort:

> 🗣️ *„Alexa, sage Brainstorm notiere Kellerlicht dimmen.“*  
> 🤖 **Alexa:** *„Gespeichert unter Smarthome.“*

Der Skill gehört dir allein und spricht nur mit deinem eigenen Home Assistant. **Voraussetzungen:** ein kostenloses [Amazon-Entwicklerkonto](https://developer.amazon.com/alexa/console/ask) mit demselben Konto wie deine Echos und ein aus dem Internet per HTTPS erreichbares Home Assistant (z. B. über Home Assistant Cloud). Das Sprachmodell ist derzeit nur auf Deutsch verfügbar.

1. Gehe in Home Assistant auf **Brainstorm Hub ➔ Konfigurieren ➔ Alexa-Spracheingabe & Skill**, wähle **Skill** oder **Beide** und klicke auf **Weiter**. Lass dieses Fenster offen, es zeigt die beiden Felder zum Kopieren.
2. Klicke in der [Alexa-Entwicklerkonsole](https://developer.amazon.com/alexa/console/ask) auf **Create Skill** und wähle: Name `Brainstorm`, Sprache **German (DE)**, Typ **Custom**, Hosting **Alexa-hosted (Python)**, Vorlage **Start from Scratch**.
3. Öffne **Build ➔ Interaction Model ➔ JSON Editor**, ersetze den Inhalt durch das Feld **Sprachmodell**, klicke auf **Save** und danach auf **Build** und warte auf die Erfolgsmeldung.
4. Ersetze im Tab **Code** den Inhalt von `lambda_function.py` durch das Feld **Skill-Code** und klicke auf **Deploy**.
5. Stelle im Tab **Test** oben **Development** ein.
6. Klicke in Home Assistant auf **Absenden** und sprich am Echo: *„Alexa, sage Brainstorm notiere Testidee.“* Die erste Anfrage koppelt deinen Skill, andere Skills werden danach abgewiesen. Unter **Konfigurieren** siehst du die Kopplung und die letzte Anfrage.

**Hinweise:** Halte den Skill-Code geheim, er enthält deine geheime Adresse. Wurde sie bekannt, erzeugst du dort eine neue und kopierst den Skill-Code erneut. Die Echo-Auswahl und die Geräteanzeige gelten auch im Skill. Dafür lernt Home Assistant jeden Echo beim ersten Satz aus dem Alexa-Verlauf (das braucht die Integration Alexa Media); dieser erste Satz kann bis zu 3,5 Sekunden länger dauern. Kommt der Eintrag im Verlauf später, wird die Idee trotzdem gespeichert und der Echo nachgetragen. Im Menü brauchst du ein Befehlswort wie *„notiere …“*, reiner Freitext geht im Skill nicht. Der Modus **Skill** schaltet die bisherige Erfassung ab, wenn deine Automation das Attribut `voice_mode` von `sensor.brainstorm_ideen_ubersicht` prüft:

```yaml
- condition: template
  value_template: "{{ state_attr('sensor.brainstorm_ideen_ubersicht', 'voice_mode') != 'skill' }}"
```

**Falls es nicht klappt:** *„Ich weiß nicht, wie ich dabei helfen soll“* bedeutet meist, dass der **Build** fehlt, im Tab **Test** nicht **Development** eingestellt ist oder Konsole und Echo verschiedene Amazon-Konten nutzen. Teste den Satz zuerst im Tab **Test**. Sagt Alexa, die Idee wurde nicht gespeichert, prüfe den Modus und die Erreichbarkeit von Home Assistant.

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
| `brainstorm.reorder_ideas` | Aktualisiert die benutzerdefinierte Sortierreihenfolge der Notizen | `idea_ids` (erforderlich) |
| `brainstorm.export_markdown` | Triggert sofortigen Markdown-Export | `path` (optional) |

---

## 📜 Versionshistorie & Changelog

| Version | Datum | Status & Highlights |
| :--- | :--- | :--- |
| **`v1.4.53`** | 31.10.2026 | **Löschen:** Ein Doppeltipp auf Löschen in der Listenkarte zeigt keine falsche Fehlermeldung mehr. |
| **`v1.4.52`** | 31.10.2026 | **Erinnerungen erreichen den richtigen Echo:** Gleichnamige Echos aus anderen Integrationen wie Music Assistant bekommen die Ansage nicht mehr. Auch beim Auswählen der Notify-Entität eines Handys erscheinen jetzt die Knöpfe. |
| **`v1.4.51`** | 31.10.2026 | **Erinnerungsregeln, Orte, Personen, Kalender und KI:**<br>• **Jede Funktion hat einen eigenen Schalter** in einem neuen Einstellungsmenü, dazu ein Hauptschalter.<br>• **Regeln pro Liste:** private Listen nur aufs Handy, Listen an bestimmten Tagen oder an einem Ort.<br>• **Orte und Personen:** Erinnerungen beim Heimkommen oder an Zonen und für andere Personen mit eigenen Kanälen.<br>• **Nachfassen und Extras:** wichtige offene Einträge an weitere Dienste, ein Briefing, das auf jemanden wartet, Kalendereinträge, KI-Zusammenfassungen und optional echte Alexa-Erinnerungen. |
| **`v1.4.50`** | 31.10.2026 | **Proaktive Erinnerungen, Briefing und Wochenrückblick:**<br>• **Termine** per Sprache, in den To-do-Listen, auf der Karte und über Dienste.<br>• **Deine Kanäle:** Alexa-Ansage und beliebige `notify`-Dienste, Handy-Knöpfe, Wartezeit und das Ereignis `brainstorm_reminder_due`.<br>• **Ruhezeiten, tägliches Briefing und Wochenrückblick.**<br>• **Skill:** neue Sätze *erinnere mich*, *erledigt* und *später*; *Ansage* gibt jetzt einen kurzen Überblick. Der Skill braucht einen neuen Build und neuen Code. |
| **`v1.4.49`** | 31.10.2026 | **Alexa-Skill mit den nativen Funktionen:**<br>• **Echo-Herkunft:** Ideen aus dem Skill zeigen den Echo, von dem sie stammen. Home Assistant lernt jeden Echo einmal aus dem Alexa-Verlauf und kennt ihn danach sofort.<br>• **Echo-Auswahl:** Echos außerhalb der Auswahl werden auch im Skill still ignoriert.<br>• **Gleiche Sprache:** Der Skill versteht die nativen Befehlswörter und bereinigt den Text genauso.<br>• **Ansage und Menü:** *„Alexa, sage Brainstorm Ansage“* liest deine Ideen vor, auch pro Kategorie, und *„Alexa, starte Brainstorm“* öffnet das Menü. |
| **`v1.4.48`** | 31.10.2026 | **Alexa-Skill mit Home Assistant Cloud:** Die Skill-Einrichtung meldet keine fehlende öffentliche HTTPS-Adresse mehr, wenn Home Assistant über Home Assistant Cloud (Nabu Casa) erreichbar ist. Unverschlüsselte Adressen werden nie angeboten. |
| **`v1.4.47`** | 31.10.2026 | **Optionaler Alexa-Skill für die Spracheingabe in einem Satz:**<br>• **Sprachmodi:** Neue Optionen unter *Alexa-Spracheingabe & Skill* mit **Nativ** (Standard, unverändert), **Skill** und **Beide**.<br>• **Eigener Skill:** *„Alexa, sage Brainstorm notiere …“* gibt jetzt eine einzige saubere Antwort. Home Assistant erzeugt Skill-Code und Sprachmodell zum Kopieren, koppelt den ersten Skill automatisch und weist andere ab.<br>• **Verlässliche Antworten:** Alexa bestätigt nur, was wirklich gespeichert wurde. |
| **`v1.4.46`** | 31.10.2026 | **Ausgewählte Echos für die Spracheingabe:**<br>• **Neue Option:** Unter *Allgemeine Einstellungen & Export* gibt es jetzt eine Mehrfachauswahl für Alexa-Media-Echos. Nur die ausgewählten Echos können Ideen per Sprache erfassen und Brainstorm öffnen; bei leerer Liste funktionieren weiterhin alle Echos.<br>• **Für Automationen:** Die Auswahl steht als Attribut `allowed_echos` von `sensor.brainstorm_ideen_ubersicht` bereit. |
| **`v1.4.45`** | 31.10.2026 | **Zuverlässige Kategorien, Auto-Export, LLM-Tools, Text-Optimierung & Sicherheit:**<br>• **Options-Flow:** Hinzufügen und Löschen von Kategorien wird nicht mehr durch das vorausgefüllte Listenfeld rückgängig gemacht; die Liste wird nur noch übernommen, wenn sie tatsächlich bearbeitet wurde.<br>• **Dauerhafte Kategorien:** Gelöschte Standardkategorien bleiben nach Reload oder Neustart gelöscht, die eigene Reihenfolge bleibt erhalten.<br>• **Auto-Export:** Ein fehlgeschlagener Markdown-Export wird protokolliert und bricht die Aktion nicht mehr ab, Events und Entity-Updates laufen weiter. Die Exportdaten werden im Event-Loop statt im Executor zusammengestellt.<br>• **LLM-Tools:** `brainstorm_list_categories` stürzt nicht mehr ab, die Kategorie `all` und Namen in beliebiger Schreibweise funktionieren, und mehrdeutige Lösch- oder Erledigt-Anfragen liefern jetzt die Kandidaten, statt den ersten Treffer zu ändern.<br>• **Text-Optimierung:** Bleibt nur ein Wort übrig, bleibt das Kategoriewort erhalten (*Haus streichen*), Schreibweisen wie *WLAN* oder *iPhone* bleiben bestehen, und Großschreibung, Infinitive und Genitiv-Artikel werden korrekt behandelt.<br>• **Sicherheit:** Markdown-Exporte sind auf Unterordner des Config-Verzeichnisses und `allowlist_external_dirs` beschränkt, Kategorienamen werden in beiden Karten maskiert, Icons und Farben werden geprüft (Farben müssen Hex-Werte sein).<br>• **Recorder:** Große Sensor-Attribute werden nicht mehr aufgezeichnet, das vermeidet das 16-KB-Limit.<br>• **Reconfigure:** Änderungen greifen jetzt auch bei vorhandenen Optionen, ohne den veralteten Reload-Helper.<br>• **Lifecycle:** Modul-Reload zur Laufzeit und Eingriffe in den Übersetzungs-Cache entfernt, Services werden jetzt in `async_setup` registriert, der nicht funktionsfähige YAML-Import ist entfernt. Python-Änderungen brauchen jetzt einen Neustart.<br>• **To-do-Listen:** Entitäten gelöschter Kategorien werden entfernt, archivierte Ideen erscheinen nicht mehr als offen, und das Bearbeiten erledigter Ideen löst `idea_completed` nicht erneut aus.<br>• **Datenintegrität:** Eltern-Zyklen werden abgelehnt, unbekannte IDs lösen einen Fehler aus, und die Option `default_category` funktioniert jetzt.<br>• **Kompatibilität:** LLM-Tools nutzen `ToolResult` und Annotations, Mindestversion ist Home Assistant 2026.10.<br>• **Tests:** Testsuite ergänzt, die gegen echtes Home Assistant läuft. |
| **`v1.4.44`** | 30.10.2026 | **Anzeige der zuletzt aktiven Alexa (Last Alexa) mit Entitätsauswahl & Robuster visueller Karteneditor:**<br>• **Last-Alexa-Badge in Karten-Kopfzeilen:** Anzeige eines dezenten, interaktiven Badges (`.last-alexa-badge`) mit Mikrofon-Icon und Klarnamen des aktiven Echo-Geräts im Header der `brainstorm-card` und der Toolbar der `brainstorm-mindmap-card`. Ein Klick auf das Badge öffnet direkt den nativen Home Assistant *More-Info*-Dialog des aktiven Geräts.<br>• **Visuelle Entitätsauswahl in den Karteneinstellungen:** Schalter *„Zuletzt aktive Alexa (Last Alexa) anzeigen“* (`show_last_alexa`) sowie Entitäts-Picker für *„Last Alexa Entität“* (`last_alexa_entity`, z. B. `sensor.last_alexa` oder beliebiges `media_player`-Gerät) in beiden visuellen Lovelace-Karteneditoren.<br>• **Robuster visueller Karteneditor:** Grundlegende Absicherung der Editor-Komponenten (`BrainstormCardEditor` & `BrainstormMindmapCardEditor`) mit Vorab-Initialisierung der Lovelace-Form-Helper (`static async getConfigElement()`), `connectedCallback()`-Lifecycle und bereinigtem Event-Merging, wodurch versehentliches Zurücksetzen von Boolean-Einstellungen ausgeschlossen ist. |
| **`v1.4.43`** | 30.10.2026 | **Optimierte Benutzerführung im Kategorie-Design (Klare Schritt-Abfolge & Aktionen):**<br>• **Eindeutiger „Weiter“-Button statt verwirrendem „OK“:** In Schritt 1 der Kategorie-Auswahl wurde `last_step=False` hinterlegt. Der Home-Assistant-Aktionsbutton heißt nun eindeutig *„Weiter“* anstelle des missverständlichen *„OK“*, wodurch sofort ersichtlich ist, dass es sich um einen 2-Schritt-Assistenten handelt.<br>• **Aussagekräftige Schritt-Titel & Beschreibungen:** Schritt 1 ist jetzt klar als *„Kategorie-Design (Schritt 1 von 2)“* ausgewiesen mit dem Hinweis, dass Icon und Farbe im nächsten Schritt folgen. Schritt 2 leitet mit *„Design für ‚{category}‘ (Schritt 2 von 2)“* direkt in die MDI-Icon-Suche und Farbwahl.<br>• **Zustands-Vorschau in der Auswahlliste:** Das Kategorie-Dropdown zeigt nun für jede Kategorie die aktuell vergebenen Icons und Farben in Klammern an (z. B. `Smarthome (Icon: mdi:home, Farbe: #03a9f4)` oder `Inbox (Standard)`).<br>• **Aktion „Fertig & Schließen“:** Nach dem Speichern des Stylings steht nun neben *„Weitere Kategorie anpassen“* und *„Zurück zum Hauptmenü“* die direkte Option *„Fertig & Schließen“* zur Verfügung. |
| **`v1.4.42`** | 30.10.2026 | **Direkte Menü-Label-Übergabe in den Hub-Optionen (Dauerhafte Behebung der leeren Menüzeile):**<br>• **Garantierte Menübeschriftung:** Übergabe expliziter lokalisierter Wörterbücher (`dict[str, str]`) in `async_show_menu` für die Schritte `init` und `category_style_done`. Dadurch wird die fehleranfällige Frontend-Übersetzungs-Cache-Auflösung vollständig umgangen. Der Menüpunkt *„Kategorie-Design (Farbe & Icon)“* wird unabhängig vom Zustand des lokalen Browser-Caches oder Home-Assistant-Neustarts immer zuverlässig und sauber dargestellt.<br>• **Zweisprachige Unterstützung:** Automatische Erkennung der Spracheinstellung (`de` vs. `en`) mit sicherem Fallback. |
| **`v1.4.41`** | 30.10.2026 | **Maximale Raumnutzung der Glühbirne & Prägnantes Logodesign:**<br>• **Flächendeckende Birnen-Geometrie:** Das Vektordesign der Brainstorm-Glühbirne wurde mit einer breiteren, runderen Kuppel (Seitenverhältnis ~0.92:1) und einem kompakten Metallsockel grundlegend optimiert. Leere Seitenränder im quadratischen Logo-Container gehören der Vergangenheit an – die sichtbare Fläche der leuchtenden Birne hat sich mehr als verdoppelt (+132 %).<br>• **Präzise ViewBox & Minimiertes Padding:** Durch die maßgeschneiderte `viewBox="136 58 240 261"` und 1px Innenabstand im 36px-Container nutzt die Glühbirne den verfügbaren Platz in der Kopfzeile beider Karten nun vollständig von Rand zu Rand aus.<br>• **Universelle Asset-Aktualisierung:** Synchroner Einsatz des optimierten Vektors in `brainstorm-card`, `brainstorm-mindmap-card`, `brainstorm-logo.svg` und `brainstorm-bulb.svg` (inkl. zentralem Mindmap-Wasserzeichen und Konfigurations-Editoren). |
| **`v1.4.40`** | 29.10.2026 | **Adaptives Logo-Design (Hell & Dunkel), Vektor-Optimierung & Ein-/Ausblenden:**<br>• **Design-Adaptiver Logo-Hintergrund:** Der Logo-Container in `brainstorm-card` und `brainstorm-mindmap-card` passt sich über dynamisches CSS-Color-Mixing (`color-mix(in srgb, var(--primary-color) 12%, var(--card-background-color))`) nun nahtlos dem aktiven Home Assistant Theme an. Kein unschöner schwarzer Kasten mehr bei hellen Themes!<br>• **Gestochen scharfe Vektorgrafik:** Überarbeitete Vektor-Glühbirne mit transparentem Hintergrund, leuchtenden Synapsen, goldenem Ideen-Blitz und metallischem Sockel ohne unleserlichen Mikro-Text oder Artefakte bei kompakten Icon-Größen.<br>• **Logo ein- und ausblenden (`show_logo`):** Neuer Schalter `show_logo: true/false` sowohl per YAML als auch in den visuellen UI-Karteneditoren (`BrainstormCardEditor` & `BrainstormMindmapCardEditor`), um das Logo in der Kopfzeile nach Wunsch ein- oder auszublenden.<br>• **Synchronisation des Optionsmenüs:** Bereinigung der Menü-Labels in den Hub-Optionen (`async_step_init`), sodass stets alle Menüpunkte vollständig beschriftet sind. |
| **`v1.4.39`** | 29.10.2026 | **100 % Responsive Kartendesigns & Umfassende Mobile-Optimierung:**<br>• **Container Queries & Dynamische Spaltenanpassung:** Einführung moderner CSS Container Queries (`@container (max-width: ...)`) parallel zu Viewport-`@media`-Queries in `brainstorm-card` und `brainstorm-mindmap-card`. Die Karten passen ihre Dichte, Typografie, Header und Schnellerfassungsleisten nun dynamisch an die exakte Breite ihres Einbettungscontainers an – egal ob auf Smartphones, Tablets oder in schmalen Mehrspalten-Sektionen auf Desktop-Dashboards.<br>• **Adaptive Mindmap-Geometrie & Mobiles Auto-Fit:** Das radiale Mindmap-Layout passt seine elliptischen Radien (`rx0`, `ry0`) und Kollisionsabstände bei geringer Kartenbreite (< 550px) dynamisch an. Die automatische Skalierungsuntergrenze wurde auf 0.35 abgesenkt, sodass selbst umfangreiche Mindmaps auf Handydisplays immer vollständig zentriert sichtbar bleiben ohne abzuschneiden.<br>• **Mobiles Vollbild-Mindmap-Modal:** Das Öffnen des Mindmap-Popup-Layers auf Mobilgeräten (< 768px) füllt nun nahtlos 100 % des Bildschirms im App-Stil aus (ohne störende Ränder oder Randverschnitt).<br>• **Touch-Bedienbarkeit & Schutz vor iOS-Auto-Zoom:** Text- und Eingabefelder erzwingen eine Mindestschriftgröße von 16px (`max(0.92rem, 16px)`), wodurch das lästige automatische Hineinzoomen von iOS Safari beim Fokussieren von Eingabefeldern wirksam unterbunden wird. Aufgaben-Aktionen (`✎`, `✕`, `↳`) bleiben auf Touchscreens (`@media (hover: none)`) dauerhaft sichtbar und bequem bedienbar.<br>• **Responsive Modaldialoge:** Prioritäts- und Kategorie-Raster in Bearbeitungsdialogen wechseln auf kleinen Displays automatisch in ein sauberes 2-Spalten-Layout ohne Textüberlauf. |
| **`v1.4.38`** | 29.10.2026 | **Bugfix Menü-Labels in den Optionen & Dynamische Cache-Invalidierung:**<br>• **Direkte Label-Übergabe im Optionsmenü:** Behebung der leeren Menüzeile in den Hub-Einstellungen (*„Brainstorm Hub Optionen“*), bei der der zweite Menüpunkt (*„Kategorie-Design (Farbe & Icon)“*) aufgrund eines verzögerten Frontend-Übersetzungscaches ohne Text dargestellt wurde. `async_show_menu` übergibt die Menüeinträge nun direkt als lokalisiertes Wörterbuch.<br>• **Automatische Übersetzungscache-Bereinigung:** `async_setup_entry` invalidiert nun zur Laufzeit den internen Home Assistant `_TranslationCache` (`async_invalidate`), sodass neue Schritte und Optionsmenüs sofort nach dem Neuladen der Integration aktiv sind, ohne dass ein kompletter Home-Assistant-Neustart erforderlich ist. |
| **`v1.4.37`** | 29.10.2026 | **Logbuch- & Aktivitäts-Zuordnung (Home Assistant „Was ist passiert?“ Ursachen-Kette):**<br>• **Aufgabe als Grund im Aktivitäts-Dialog:** Beim Öffnen des Reiters *„Aktivität“* (Logbuch) auf `sensor.brainstorm_ideen_ubersicht` und Klick auf einen Eintrag wird unter *„Was ist passiert?“* nun die konkrete Aufgabe mit Kategorie und Aktion (`Idee erfasst`, `Idee erledigt`, `Idee geändert`, `Idee gelöscht`) direkt als Grund ausgewiesen, anstelle von leeren Zustandswechseln oder *„Für diese Aktivität wurde kein Grund erfasst“*.<br>• **Native Kontext- & Entitäts-Verknüpfung:** Eintreffende Ereignisse (`EVENT_IDEA_ADDED`, `EVENT_IDEA_COMPLETED`, `EVENT_IDEA_UPDATED`, `EVENT_IDEA_DELETED`) übergeben nun die `entity_id` (`sensor.brainstorm_ideen_ubersicht`) und bewahren den ursprünglichen Aktionskontext (`call.context`). Über `async_set_context(context)` verknüpft der native Chain-Resolver von Home Assistant den auslösenden Benutzer, den Dienstaufruf und das Brainstorm-Ereignis nahtlos miteinander.<br>• **Sensor-Attribut `last_action`:** `sensor.brainstorm_ideen_ubersicht` stellt die letzte Aktion mit Notiztext, Kategorie, Priorität, Zeitstempel und Zusammenfassung als Attribut für Templates, Scripts und Automationen bereit. |
| **`v1.4.36`** | 29.10.2026 | **Schlankes, kompaktes Zeilendesign & Smartphone-Optimierung:**<br>• **Reduzierte Aufgaben-Zeilenhöhe:** Grundlegende Straffung der Aufgabenhöhe in `brainstorm-card` (Padding von 12px auf 8px/6px reduziert, vertikaler Listenabstand von 8px auf 5px/4px, optimierte Zeilenhöhe). Deutlich mehr Notizen auf einen Blick ohne langes Scrollen.<br>• **Smartphone- & iPhone-Feinschliff:** Spezifische Mobile-Breakpoints (`@media (max-width: 600px)` und `380px`) mit schlankeren Checkboxen (18px), kompakten Badges und optimierter Unteraufgaben-Einrückung (10px statt 24px/16px). Verhindert horizontales Zusammendrücken und vorzeitiges Umbrechen auf schmalen iPhone-Displays.<br>• **Neue Option „Kompakte Zeilenhöhe“ (`compact_mode`):** Im visuellen UI-Karteneditor zuschaltbar für maximale Informationsdichte auf Tablets und Dashboards.<br>• **Kompakte Mindmap-Wolken:** Proportionierte Notizwolken in `brainstorm-mindmap-card` auf mobilen Bildschirmen. |
| **`v1.4.35`** | 29.10.2026 | **Frei wählbare Farben & Home Assistant MDI-Icons für Kategorien:**<br>• **Kategorie-Design in den Einstellungen:** Neuer Menüpunkt *„Kategorie-Design (Farbe & Icon)“* im Hub-Optionsmenü (`OptionsFlow`). Kategorien können nun direkt mit dem nativen Home Assistant Icon-Picker (`selector.IconSelector` mit MDI-Volltextsuche) und visuellem Farb-Picker (`selector.ColorRGBSelector`) gestaltet werden.<br>• **1-Klick Farb- & Icon-Editor auf der Karte:** Über das neue 🎨-Icon auf dem aktiven Kategorie-Tab in `brainstorm-card` lässt sich das Design direkt aus dem Dashboard im Dialog mit Live-Vorschau anpassen oder auf Standard zurücksetzen.<br>• **Nahtlose Visualisierung:** Sämtliche Kategorie-Pills, Notiz-Tags und der zentrale Mindmap-Hub (`brainstorm-mindmap-card`) rendern die Icons und Akzentfarben harmonisch im gesamten Dashboard.<br>• **Neuer Service:** `brainstorm.set_category_style` zur Steuerung über Scripts und Automationen; `brainstorm.add_category` um optionale Attribute `icon` und `color` erweitert. |
| **`v1.4.34`** | 29.10.2026 | **Bereinigung der Kategorie-Optionen (Deduplizierung `hide_empty_categories`):**<br>• Die redundante Konfigurationsoption *„Kategorien ohne Notizen (0) ausblenden“* wurde aus den *„Allgemeinen Einstellungen“* des Hubs entfernt.<br>• Die globale Standardeinstellung für Dashboards verbleibt nun logisch und fokussiert direkt unter *„Kategorien verwalten“* sowie individuell konfigurierbar je Lovelace-Karte. |
| **`v1.4.33`** | 29.10.2026 | **Vibe Coding Manifest & Badges:** Offizieller Hinweis und Badges zur leidenschaftlichen KI-gestützten Entwicklung (*„Vibe Coding mit voller Hingabe“*) in Dokumentation und Repositories aufgenommen. |
| **`v1.4.32`** | 29.10.2026 | **Zweisprachige Dokumentation (EN/DE), Alexa Key-Feature Spotlight & 1-Klick Installation:**<br>• **Vollständige englische Dokumentation:** Umfassendes englisches Handbuch (`README.md`) parallel zur deutschen Version (`README_de.md`) mit intuitivem Länderflaggen-Umschalter (`🇩🇪 Deutsch` ⇄ `🇬🇧 English`).<br>• **Key-Feature Spotlight Amazon Alexa:** Ausführliche Dokumentation der nahtlosen Alexa-Spracherfassung als zentrales Highlight (Hands-Free Notizenerfassung, Zwei-Wege-Dialog, Schutz vor Musik- und Einkaufslisten-Kollisionen, automatische NLP-Grammatikbereinigung und Echo-Geräteherkunft).<br>• **1-Klick My Home Assistant Badges:** Schnelle Installation via HACS-Redirect und nativer Config-Flow-Start mit einem Klick.<br>• **Versions- & Komponenten-Synchronisation:** Einheitlicher Release-Stand für Karten, Sensoren und Plattform. |
| **`v1.4.31`** | 29.10.2026 | **Hintergrund-Rendering Fix & Synchrones Punktraster:**<br>• **Beseitigung von Farb- und Blockartefakten im Hintergrund:** Behebung eines Darstellungsfehlers in `brainstorm-mindmap-card`, bei dem harte Gradientenstopps (`radial-gradient`) und GPU-Layer-Promotion (`will-change: transform`) auf dem Canvas zu Moiré-Interferenzen, Kachelsäumen und sichtbaren Farbblöcken führten, die sich beim Zoomen oder Scrollen störend verschoben haben.<br>• **Subpixel-Anti-Aliasing & Canvas-Transparenz:** Weiche Anti-Aliasing-Übergänge für das Punktraster sowie vollständige Bereinigung überlagernder Hintergrundfarben (`canvas-area` transparent über `ha-card`).<br>• **Synchrones Pan & Zoom:** Das Hintergrundraster bewegt und skaliert sich nun natürlich mit dem Mindmap-Viewport (`background-position` & `background-size`).<br>• **Konfigurierbares Raster:** Neue Option `show_grid` (im UI-Editor als *„Punktraster im Hintergrund anzeigen“* schaltbar). |
| **`v1.4.30`** | 29.10.2026 | **Bugfix Mindmap-Synapsen beim Umschalten von Kategorien:**<br>• **Keine Geisterlinien / leere Verbindungslinien mehr:** Behebung eines Fehlers in `brainstorm-mindmap-card`, bei dem beim Wechsel der Kategorie (z. B. von *„Alle“* auf *„Smarthome“*) die synaptischen Bézier-Linien zuvor angezeigter Notizen ohne Ideenkärtchen im Raum stehenblieben. Die Rendering-Logik (`_drawConnections`) validiert nun strikt, dass Verbindungslinien ausschließlich für Notizen der aktuell aktiven Kategorie gezeichnet werden, die auch tatsächlich als DOM-Element existieren.<br>• **Zuverlässige Layout- & Positions-Bereinigung:** Beim Umschalten auf eine andere Kategorie (via Toolbar-Pill oder Klick auf den Zentrums-Node) werden vorherige Knotenpositionen (`_nodePositions`) und Drag-Zustände sofort zurückgesetzt, sodass die verbleibenden Notizen harmonisch und frei von Artefakten neu arrangiert werden. |
| **`v1.4.29`** | 29.10.2026 | **Drag & Drop Sortierung, Unteraufgaben-Zuweisung & Apple Reminders Kontextmenü:**<br>• **Drag & Drop Sortierung in der Liste:** Notizen lassen sich nun per Drag & Drop über den Anfasser (`⠿`) intuitiv und flüssig in der Notizenliste nach oben oder unten verschieben. Die Reihenfolge wird über den Service `brainstorm.reorder_ideas` persistent im Store gespeichert (`order`-Attribut).<br>• **Drag & Drop Unteraufgaben-Zuweisung:** Ziehen einer Notiz nach rechts auf eine bestehende Hauptaufgabe blendet ein visuelles Feedback (`↳ Als Unteraufgabe`) ein und weist die Notiz beim Loslassen direkt als Unteraufgabe zu.<br>• **Apple Reminders Touch-Interaktion (Smartphone):** Langes Drücken (~420ms) auf eine Notiz am Smartphone (bzw. Rechtsklick am Desktop) öffnet ein elegantes Apple Reminders Style Kontextmenü mit dezentem Haptik-Feedback (`vibrate`). Ermöglicht 1-Tap Einrücken unter die vorherige Hauptaufgabe (*„Unteraufgabe einrücken (unter: ‚...‘)“*), Ausrücken (*„Wieder zur Hauptaufgabe machen“*), Verschieben nach oben/unten sowie direktes Bearbeiten und Löschen. |
| **`v1.4.28`** | 29.10.2026 | **Ausblenden leerer Kategorien (0) als Standard aktiviert (`hide_empty_categories: true`):**<br>• **Standardmäßig saubere Filterleisten:** Kategorien ohne aktive Notizen (z. B. *„Inbox 0“*, *„Projekte 0“*, *„Familie 0“*, *„Einkauf 0“*) werden nun in `brainstorm-card` und `brainstorm-mindmap-card` standardmäßig ausgeblendet, ohne dass eine manuelle Konfiguration in jedem Dashboard nötig ist.<br>• **Konfigurationsauflösung korrigiert:** Behebung eines Problems in beiden Karten, bei dem ungesetzte Card-Properties fälschlicherweise das globale Ausblenden überschrieben haben. Die Priorität greift nun zuverlässig: Individuelle Karteneinstellung ➔ Globale Integrationsoption ➔ Standard aktiv (`true`).<br>• **Fokus-Sichtbarkeit:** Neu erstellte oder aktiv angeklickte leere Kategorien bleiben zur Orientierung und schnellen Befüllung sichtbar, solange sie im Fokus stehen. |
| **`v1.4.27`** | 28.10.2026 | **Hierarchische Unteraufgaben, Aktives Kategorie-Routing & Mobile Mindmap-Pills:**<br>• **Unteraufgaben in der Liste einrücken:** Notizen lassen sich nun mit 1 Tap (`↳` unter vorherige Hauptaufgabe einrücken / `↰` zur Hauptaufgabe ausrücken) sowie über ein neues Dropdown im Bearbeiten-Dialog (`✏️`) als Unteraufgabe zuweisen. Mobile-optimierte Touch-Targets (mind. 28×28px, dauerhafte Sichtbarkeit auf Smartphones) für einfache Handhabung unterwegs. Visuelle Darstellung mit Einrückung, farbiger Führungslinie, `↳`-Indikator und Badge.<br>• **Schnellerfassung in aktiver Kategorie:** Wenn ein Kategorie-Tab (z. B. *„Smarthome“*, *„Haus & Garten“*, *„Brainstorm“*) aktiv ist, werden neue Notizen aus dem Schnellerfassungsfeld automatisch exakt dieser Kategorie zugeordnet, ohne bei fehlenden Schlagwörtern in die *„Inbox“* zu rutschen. Kategorie-Dropdown und Platzhaltertext passen sich synchron an den aktiven Tab an.<br>• **Mindmap-Toolbar auf Smartphones:** Die Kategorie *„Alle“* wird auf Mobilgeräten (`≤ 600px`) in der Mindmap-Toolbar automatisch ausgeblendet, um den horizontalen Platz optimal für konkrete Themenkategorien zu nutzen; das Antippen des Zentrum-Nodes überspringt *„Alle“* auf Smartphones automatisch. |
| **`v1.4.26`** | 28.10.2026 | **Konfigurierbares Ausblenden leerer Kategorien (0):** Neue Option *„Kategorien ohne Notizen (0) ausblenden“* (`hide_empty_categories`), um die Filterleisten (Pills) von `brainstorm-card` und `brainstorm-mindmap-card` von ungenutzten Kategorien freizuhalten. Die Funktion ist flexibel an zwei Stellen konfigurierbar: direkt in den Integrations-Optionen (unter *„Kategorien verwalten“* und *„Allgemeine Einstellungen“* als globale Standardeinstellung für alle Dashboards) sowie individuell je Lovelace-Karte im visuellen Karteneditor (`ha-form` & Fallback). Bei aktiver Option werden nur Kategorien mit mindestens einem aktiven Eintrag angezeigt; die gerade ausgewählte Kategorie bleibt zur Orientierung sichtbar und Schnellerfassungs-Dropdowns behalten stets den vollen Zugriff auf alle Kategorien. |
| **`v1.4.25`** | 25.10.2026 | **Dynamisches Kategorie-Dropdown in visuellen Karteneditoren:** Ersatz des statischen Textfelds für *„Standard-Kategorie im Fokus“* (`default_category`) in den Lovelace-UI-Editoren (`ha-form`) beider Karten (`brainstorm-card` und `brainstorm-mindmap-card`) durch ein dynamisches Dropdown-Menü. Das Dropdown listet automatisch alle verfügbaren Standard- und benutzerdefinierten Kategorien mit passenden Icons (z. B. `🌟 Alle Kategorien`, `📥 Inbox`, `🔷 Smarthome`, `🟢 Haus & Garten`, `🟣 Projekte`, `🟡 Alltag`, `🔮 Brainstorm`) auf und erlaubt dank `custom_value: true` bei Bedarf weiterhin die freie Eingabe. |
| **`v1.4.24`** | 25.10.2026 | **Bugfix JavaScript-Syntaxfehler in Brainstorm Mindmap Card:** Behebung eines Syntaxfehlers (`orphaned code block / unexpected token`) in `brainstorm-mindmap-card.js` innerhalb des `_showAddDialog`-Event-Listeners, durch den das Skript im Browser nicht evaluiert werden konnte und Home Assistant den Fehler *„Konfigurationsfehler: Custom element doesn't exist: brainstorm-mindmap-card“* anzeigte. Vollständige Bereinigung des Codes und Aktualisierung der Cache-Buster. |
| **`v1.4.23`** | 25.10.2026 | **Responsiver Header & Farbmodus-Fix:** Vollständige Neustrukturierung und Entrümpelung des Card-Headers und der Schnellerfassung in `brainstorm-card`. Integration von Titel und Status-Badge (`header-titles`), kompakte Anordnung der Aktionen (`header-actions`) und Ablösung der überladenen, doppelten Toolbar durch eine ultra-schlanke, einteilige **Quick Capture Card** (`.quick-capture-card`). Wegfall redundanter Buttons und statischer Textlabels; elegante Chip-Dropdowns für Kategorie (`🏷️`) und Priorität nebeneinander. Optimierte Mobile-Breakpoints (`@media (max-width: 520px)` und `380px`) für perfekte Touch-Bedienung und zentriertes Layout auf Smartphones. **Bugfix Farbmodus-Umschalter:** Korrektur von `_getCategoryColor` in beiden Karten (`brainstorm-card` und `brainstorm-mindmap-card`), sodass der runde Farbmodus-Button (`🎨` / `🌈`) nun sofort und reaktiv zwischen dem aktiven Home Assistant Theme-Farbton (`var(--primary-color)`) und lebendigen Multicolor-Kategoriefarben umschaltet und die Auswahl browserweit synchronisiert. |
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

## ✨ 🚀 Vibe Coding mit voller Hingabe

> *„Vibe Coding ist die Kunst, reine Ideen durch fließenden Dialog, menschliche Kreativität und KI-Superkräfte in funktionierende Realität zu verwandeln.“*

Dieses Projekt wurde und wird mit voller Hingabe durch **Vibe Coding** erschaffen. Wir verstecken uns nicht hinter KI, sondern stehen mit Stolz und voller Transparenz dazu:
- **Menschliche Produkt- & UX-Vision:** Jedes Feature, jede Smartphone-Geste, jedes Detail der interaktiven Mindmap und jede Alexa-Routine entstammt echter Alltagserfahrung und der Leidenschaft für ein smarteres Zuhause.
- **High-Velocity AI Pair-Programming:** Durch den Einsatz moderner agentischer KI-Entwicklung (Google Antigravity & Claude/Gemini) entstehen anspruchsvolle Architekturen, Bugfixes und Feinschliff in Höchstgeschwindigkeit.
- **100 % Open Source & Community First:** Transparent, erweiterbar und für jeden in der Home Assistant Community frei nutzbar.

---

## 📄 Lizenz

Dieses Projekt ist unter der **MIT-Lizenz** lizenziert – siehe [LICENSE](LICENSE) für Details.

Copyright © 2026 [nukleuz80](https://github.com/nukleuz80)
