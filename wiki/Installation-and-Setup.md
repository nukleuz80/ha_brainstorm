🏠 [Home](Home) · 🇩🇪 [Deutsche Version](Installation-und-Einrichtung)

> 🎬 **Prefer to watch?** The [installation video](https://github.com/nukleuz80/ha_brainstorm/blob/main/docs/videos_en.md#installation-2-minutes) goes from HACS to your first idea in two minutes.

## 🔗 Quick Links

These buttons open the right page in your own Home Assistant:

[![Open Brainstorm Hub in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nukleuz80&repository=ha_brainstorm&category=integration) [![Set up Brainstorm Hub](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=brainstorm) [![Open Brainstorm Hub (configure, diagnostics, delete)](https://my.home-assistant.io/badges/integration.svg)](https://my.home-assistant.io/redirect/integration/?domain=brainstorm) [![Try the Brainstorm actions](https://my.home-assistant.io/badges/tools_actions.svg)](https://my.home-assistant.io/redirect/tools_actions/) [![Voice assistants (Assist, LLM API)](https://my.home-assistant.io/badges/voice_assistants.svg)](https://my.home-assistant.io/redirect/voice_assistants/) [![Repairs](https://my.home-assistant.io/badges/repairs.svg)](https://my.home-assistant.io/redirect/repairs/) [![Logs of Brainstorm Hub](https://my.home-assistant.io/badges/logs.svg)](https://my.home-assistant.io/redirect/logs/?integration=brainstorm)

The links go through [My Home Assistant](https://my.home-assistant.io/). On the first click it asks for the address of your Home Assistant and remembers it. Throughout this wiki, menu paths such as **Settings ➔ Devices & Services** are links of this kind too, and every action under [Services](Services-and-Events) has a link that opens it in the developer tools.

## Prerequisites

1. Home Assistant 2026.10 or newer.
2. [HACS](https://hacs.xyz), if you want to install through it.
3. Optional, for voice input with Alexa: the [Alexa Media Player](https://github.com/alandtse/alexa_media_player) integration.
4. Optional, for your own Alexa skill: an Amazon developer account and a public HTTPS address for your Home Assistant.

Brainstorm Hub connects to no external service by itself, so setup needs no account or password.

## Option 1: HACS (Recommended - 1-Click)

Brainstorm Hub is part of the HACS default list since 9 November 2026. Click the button below to open it in your HACS:

[![Open in HACS](https://img.shields.io/badge/HACS-Open%20Repository-41BDF5?logo=home-assistant&logoColor=white)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nukleuz80&repository=ha_brainstorm&category=integration)

Or step by step:
1. Open **HACS** in your Home Assistant sidebar.
2. Search for **Brainstorm Hub** and click **Download**.
3. Restart Home Assistant.

The cards come with the integration: after the restart Home Assistant loads them by itself. Then add the integration as shown in the next option.

## Option 2: Add Integration (Config Flow)

[![Start Config Flow](https://img.shields.io/badge/Home%20Assistant-Add%20Integration-41BDF5?logo=home-assistant&logoColor=white)](https://my.home-assistant.io/redirect/config_flow_start/?domain=brainstorm)

1. Go to [**Settings ➔ Devices & Services ➔ Add Integration**](https://my.home-assistant.io/redirect/config_flow_start/?domain=brainstorm).
2. Search for **Brainstorm Hub** and follow the on-screen setup guide.

## Option 3: Manual Installation

1. Download the latest release.
2. Copy the folder `custom_components/brainstorm` to `/config/custom_components/`.
3. Restart Home Assistant and add the integration as shown in option 2.

## The Cards

The cards live in the folder of the integration (`cards/`), and Home Assistant loads them on every dashboard by itself, in storage and YAML mode alike. There is nothing to copy and no resource to add.

> **Updating from a version before 1.7.15:** Remove the old resources `/local/brainstorm-card.js` and `/local/brainstorm-mindmap-card.js` under [**Settings ➔ Dashboards ➔ Resources**](https://my.home-assistant.io/redirect/lovelace_resources/) (or from `resources:` in YAML mode) and delete the card files in `/config/www/`. Otherwise the browser may still load the old cards.

## Removing the Integration

1. Go to [**Settings ➔ Devices & Services ➔ Brainstorm Hub**](https://my.home-assistant.io/redirect/integration/?domain=brainstorm), open the three dots and choose **Delete**.
2. Installed through HACS: open Brainstorm Hub in HACS and choose **Remove**. Installed manually: delete `/config/custom_components/brainstorm`.
3. Remove any Brainstorm cards from your dashboards.
4. Restart Home Assistant.

Depending on what you used, also remove:
- **Your Alexa skill:** Delete it in the Alexa developer console and its code in AWS Lambda. Real Alexa reminders stay in the Alexa app until you delete them there.
- **Automations and sentences:** Your own automations, scripts, and custom sentences that call Brainstorm, as well as an iPhone shortcut.
- **Your data:** Home Assistant keeps your ideas in `/config/.storage/brainstorm.storage`, the skill link in `brainstorm.alexa_skill` and the reminder state in `brainstorm.reminders` in the same folder. Delete these files and the Markdown folder (default `/config/brainstorm`) if you do not plan to come back.
