🏠 [Start](Home) · 🇬🇧 [English version](Quick-Start)

In fünf Schritten von der Installation zur ersten Idee auf der Mindmap. Alle Details stehen auf den verlinkten Seiten.

## 1. Installieren

Öffne Brainstorm Hub in HACS, klicke auf **Herunterladen** und starte Home Assistant neu:

[![Brainstorm Hub in HACS öffnen](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nukleuz80&repository=ha_brainstorm&category=integration)

Ohne HACS geht es auch von Hand, siehe [Installation & Einrichtung](Installation-und-Einrichtung).

## 2. Integration hinzufügen

[![Brainstorm Hub einrichten](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=brainstorm)

Die Einrichtung fragt nach Kategorien und schlägt *Haus & Garten*, *Smarthome*, *Projekte*, *Alltag* und *Inbox* vor. Alles lässt sich später unter **Konfigurieren** ändern, siehe [Einstellungen](Einstellungen).

## 3. Karten ins Dashboard

Dashboard bearbeiten ➔ **Karte hinzufügen** ➔ nach *Brainstorm* suchen, oder per YAML:

```yaml
type: custom:brainstorm-card
title: Brainstorm Hub
```

```yaml
type: custom:brainstorm-mindmap-card
height: 600px
```

Die Karten kommen mit der Integration, eine Ressource musst du nicht anlegen.

## 4. Erste Idee

Tippe in die Schnelleingabe der Listenkarte:

> `Dringend Garten: Rasenmäher reparieren`

Brainstorm legt *Rasenmäher reparieren* in **Haus & Garten** an, mit der Priorität 🔥 Dringend. Mit *„morgen um 8“* im Satz bekommt die Idee gleich eine Erinnerung. Über HTTPS (Companion-App oder Home Assistant Cloud) kannst du auch auf 🎙️ tippen und sprechen.

## 5. Per Sprache erfassen

| Weg | Beispiel | Einrichtung |
| :--- | :--- | :--- |
| Alexa | *„Alexa, sage Brainstorm notiere Kellerlicht dimmen“* | [Sprachsteuerung › Alexa](Sprachsteuerung#amazon-alexa) |
| Assist | *„Notiere Backup der Datenbank erstellen“* | [Sprachsteuerung › Assist](Sprachsteuerung#home-assistant-assist) |
| Siri | *„Hey Siri, Brainstorm“* | [Sprachsteuerung › iPhone](Sprachsteuerung#iphone-kurzbefehl-mit-siri-action-taste-oder-rückseite) |
| KI-Assistent | *„Was steht noch auf meiner Gartenliste?“* | [KI-Funktionen](KI-Funktionen) |

## Wie geht es weiter?

- 🧠 Ansichten, Tastenkürzel, Pinnwand und Zeichnen: [Mindmap & Pinnwand](Mindmap-und-Pinnwand)
- 👥 Mit der Familie teilen, abstimmen, kommentieren: [Zusammenarbeit](Zusammenarbeit)
- ⏰ Erinnerungen per Echo, Handy oder Kalender: [Erinnerungen](Erinnerungen)
- 🤖 Brainstorm in Automationen: [Automationen & Beispiele](Automationen-und-Beispiele)
