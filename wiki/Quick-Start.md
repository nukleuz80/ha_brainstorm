🏠 [Home](Home) · 🇩🇪 [Deutsche Version](Schnellstart)

Five steps from installing to your first idea on the mind map. The linked pages have every detail.

## 1. Install

Open Brainstorm Hub in HACS, click **Download** and restart Home Assistant:

[![Open Brainstorm Hub in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nukleuz80&repository=ha_brainstorm&category=integration)

A manual install works too, see [Installation & Setup](Installation-and-Setup).

## 2. Add the integration

[![Set up Brainstorm Hub](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=brainstorm)

Setup asks for your categories and suggests a set to start with. You can change everything later under **Configure**, see [Settings](Settings).

## 3. Add the cards to a dashboard

Edit dashboard ➔ **Add card** ➔ search for *Brainstorm*, or use YAML:

```yaml
type: custom:brainstorm-card
title: Brainstorm Hub
```

```yaml
type: custom:brainstorm-mindmap-card
height: 600px
```

The cards ship with the integration, so you need no resource entry.

## 4. Your first idea

Type into the quick input of the list card:

> `Urgent garden: repair the lawn mower`

Brainstorm saves *Repair the lawn mower* with the priority 🔥 Urgent and picks the category from words like *garden*. Add *"tomorrow at 8"* and the idea gets a reminder right away. Over HTTPS (Companion app or Home Assistant Cloud) you can also tap 🎙️ and speak.

## 5. Capture by voice

| Way | Example | Setup |
| :--- | :--- | :--- |
| Alexa | *"Alexa, ask Brainstorm to note dim the basement light"* | [Voice Control › Alexa](Voice-Control#alexa-skill-recommended) |
| Assist | *"Note create a database backup"* | [Voice Control › Assist](Voice-Control#home-assistant-assist) |
| Siri | *"Hey Siri, Brainstorm"* | [Voice Control › iPhone](Voice-Control#-iphone-shortcut-with-siri-action-button-or-back-tap) |
| AI assistant | *"What is still on my garden list?"* | [AI Features](AI-Features) |

## What next?

- 🧠 Views, keyboard shortcuts, pinboard and drawing: [Mind Map & Pinboard](Mind-Map-and-Pinboard)
- 👥 Share with your family, vote, comment: [Collaboration](Collaboration)
- ⏰ Reminders by Echo, phone or calendar: [Reminders](Reminders)
- 🤖 Brainstorm in automations: [Automations & Examples](Automations-and-Examples)
