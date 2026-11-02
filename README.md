<div align="center">

# 🧠 Brainstorm Hub for Home Assistant

**[🇬🇧 English](README.md)** &nbsp;|&nbsp; **[🇩🇪 Deutsch](README_de.md)**

[![English Docs](https://img.shields.io/badge/Language-English%20%F0%9F%87%AC%F0%9F%87%A7-blue.svg)](README.md)
[![German Docs](https://img.shields.io/badge/Sprache-Deutsch%20%F0%9F%87%A9%F0%9F%87%AA-green.svg)](README_de.md)
[![Open in HACS](https://img.shields.io/badge/HACS-Add%20Repository-41BDF5?logo=home-assistant&logoColor=white)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nukleuz80&repository=ha_brainstorm&category=integration)
[![Start Config Flow](https://img.shields.io/badge/Home%20Assistant-Add%20Integration-41BDF5?logo=home-assistant&logoColor=white)](https://my.home-assistant.io/redirect/config_flow_start/?domain=brainstorm)
[![Version](https://img.shields.io/badge/version-1.6.0-blue.svg)](https://github.com/nukleuz80/ha_brainstorm/releases)
[![Vibe Coding](https://img.shields.io/badge/Vibe%20Coding-100%25%20with%20Devotion-ff69b4?logo=sparkles&logoColor=white)](https://github.com/nukleuz80/ha_brainstorm)
[![Quality Scale](https://img.shields.io/badge/Quality%20Scale-Silver%20self--assessed-C0C0C0.svg)](https://contributors.home-assistant.io/core/quality-scale/)
[![GitHub Release](https://img.shields.io/github/v/release/nukleuz80/ha_brainstorm)](https://github.com/nukleuz80/ha_brainstorm/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/nukleuz80/ha_brainstorm)

</div>

**Brainstorm Hub** is the ultimate smart capture center for all your thoughts, ideas, and tasks in your Home Assistant smart home.  
Whether you are cooking, working in the workshop, relaxing in the garden, or on the go: capture sudden flashes of inspiration within seconds hands-free via voice (**Amazon Alexa** or **Home Assistant Assist**), through interactive Lovelace dashboard cards, or via automated triggers. Brainstorm categorizes your thoughts using intelligent NLP heuristics and optionally synchronizes them as clean Markdown files for Obsidian, Logseq, or Nextcloud.

---

## 🌍 Language Support

Brainstorm Hub works in German and English, and your existing categories and entries are never translated or renamed. The table shows the current state. To add a language, see [`CONTRIBUTING.md`](CONTRIBUTING.md).

| Area | German | English |
| :--- | :--- | :--- |
| Settings of the integration | ✅ | ✅ |
| Documentation | ✅ | ✅ |
| Spoken answers of the Alexa skill | ✅ | ✅ |
| Voice commands of the Alexa skill | ✅ | ✅ |
| Assist sentences | ✅ | ✅ (`examples/`) |
| Shortening sentences, due dates and priorities from speech | ✅ | ✅ |
| Dashboard cards | ✅ | ✅ |
| Reminder texts, logbook and error messages | ✅ | ✅ |

The English voice commands are listed under [Voice Commands](#-voice-commands), with the German ones next to them. Text in other languages stays as you say or type it, with a capital first letter. Home Assistant's language decides which rules apply, and `brainstorm.add_idea` also accepts a `language` field.

---

## 🌟 🗣️ Key Feature: Seamless Amazon Alexa Hands-Free Voice Capture

> 🗣️ *“Alexa, ask Brainstorm to note the lawn has to be mowed”* ➔ 🤖 *“Saved under House and Garden.”*  
> 🗣️ *“Alexa, ask Brainstorm to remind me tomorrow at 8 to take out the bins”* ➔ 🤖 *“Okay, I will remind you tomorrow at 8 am about Take out bins.”*

Brainstorm Hub turns every **Amazon Echo** device in your home into an instant, friction-free thought catcher — ideal when your hands are wet, dirty, or occupied.

### ⚡ Why Alexa Voice Capture is the Premier Feature:
- 🚫 **Zero Music & Shopping List Collisions:** Out of the box, Alexa frequently misinterprets open-ended notes by dumping them into chaotic Amazon shopping lists or launching songs by the rock band *“Brainstorm”* on Spotify. Brainstorm Hub eliminates this friction with optimized routine triggers and automatic background stop commands for a whisper-quiet, 100% reliable dialogue.
- 🗣️ **Interactive Two-Way Dialogue Mode:** Simply say *“Alexa, Brainstorm”*. Alexa listens, parses your input, and instantly responds with spoken confirmation of the assigned category and urgency level.
- ⚡ **One-Shot Direct Voice Commands:** When seconds count: *“Alexa, note for smart home dim the basement light”* or *“Alexa, idea urgent garden: clean the patio”*.
- 🧠 **Smart NLP Text Cleaning & Grammar Transformation:** Strips out conversational filler words (*“please write down that we need to clean the patio”* ➔ *“Clean patio”*), fixes speech typos, and transforms passive verb constructions into clear actionable tasks.
  - **Whole sentences instead of fragments (v1.5.8):** *"the lawn has to be mowed"* ➔ *"Mow lawn"*. Negations, questions and sentences that cannot be rebuilt completely keep their wording. Typed text only gets its typos fixed.
  - **Due date and priority from the sentence (v1.5.10):** *"I need to call the doctor tomorrow asap"* ➔ *"Call doctor"*, due tomorrow at 09:00, urgent. The due date leads to a reminder and can be switched off. The spoken sentence stays stored and can be restored in the card.
  - **Own terms (v1.5.10):** Names of people and categories are spelled right automatically, own terms and corrections are set under *General settings*.
  - **Optional AI step (v1.5.10):** An AI task entity improves the entry in the background. If it adds words or numbers or changes a negation, the version of the rules stays.
- 🏷️ **Contextual Priority & Category Extraction:** Detects priority triggers (*“urgent”*, *“important”*, *“priority 1”*, *“no rush”*) and category prefixes (*“for smart home”*, *“in the garden”*) regardless of word order in the sentence.
- 📍 **Echo Origin Tracking:** Automatically records which Echo device received the idea (e.g., `🗣️ Alexa (Echo Show Kitchen)` vs. `🗣️ Alexa (Workshop Echo Dot)`).

---

## 🌟 Highlights & Features

- 🎯 **Intelligent Priority Management & Visual Urgency Levels:**
  - **4 Priority Levels:** `low` (🟢 Low), `medium` (🟡 Medium / Default), `high` (🔴 High), and `urgent` (🔥 Urgent).
  - **Natural Language Urgency Detection:** Recognizes priority words in spoken or typed notes (e.g. *“Urgent garden: repair lawnmower”*, *“Priority 1…”*) and the tags *“!urgent”*, *“!high”* and *“!low”*, cleans the text, and sets the priority automatically.
  - **1-Click Priority Cycling:** Cycle priorities directly (`Medium` ➔ `High` ➔ `Urgent` ➔ `Low`) by clicking the priority badge in either the list or mindmap view.
  - **Visual Mindmap Pulse Effects:** Urgent idea nodes pulse with an animated flame effect (`cloud-urgent`), while high-priority notes glow with a warm highlight.
- 🤖 **Assist LLM Tools & Function-Calling API:**
  - **Natural Conversational AI:** Native integration with Home Assistant's LLM API (`homeassistant.helpers.llm`). Works with OpenAI, Google Gemini, Ollama, and local models.
  - **5 AI Tools Included:** `brainstorm_add_idea`, `brainstorm_get_ideas`, `brainstorm_complete_idea`, `brainstorm_delete_idea`, and `brainstorm_list_categories`.
- 📋 **Drag & Drop Sorting & Subtasks:**
  - **Intuitive Reordering:** Reorder items in the list view smoothly via drag handle (`⠿`). Order is preserved persistently via `brainstorm.reorder_ideas`.
  - **Drag & Drop Subtasks:** Drag a note onto another note to instantly nest it as a subtask.
  - **Apple Reminders Context Menu:** Long-press on mobile (~420ms) or right-click on desktop triggers haptic feedback and opens a quick menu for indenting, unindenting, moving, editing, or deleting.
- 🧠 **Dynamic Mindmap Card (`custom:brainstorm-mindmap-card`):**
  - Interactive radial synapse layout with glowing central category hub and floating idea clouds.
  - Smooth pan & zoom with synchronized background dot grid and canvas transparency.
  - Instant category filtering without ghost lines or orphaned connections.
- 🎴 **Quick Capture Card (`custom:brainstorm-card`):**
  - Two-tiered sleek design with quick-input bar, priority selector, category pills, and full edit/delete modal dialogs.
  - View switcher (`🧠 Mindmap` ⇄ `📋 List`) in card header.
  - Automatically hides empty categories (`hide_empty_categories: true`) to keep dashboards clutter-free.
- 📝 **Markdown Synchronization:**
  - Auto-export to structured markdown files with YAML frontmatter, timestamps, and priority tags.
  - Plug-and-play with **Obsidian**, **Logseq**, or **Nextcloud Notes**.
- 🛠️ **Home Assistant To-do Platform:**
  - Synchronizes all active categories as native Home Assistant To-do entities (`todo.brainstorm_hub_*`).

---

## 🚀 Installation

### Prerequisites

1. Home Assistant 2026.10 or newer.
2. [HACS](https://hacs.xyz), if you want to install through it.
3. Optional, for voice input with Alexa: the [Alexa Media Player](https://github.com/alandtse/alexa_media_player) integration.
4. Optional, for your own Alexa skill: an Amazon developer account and a public HTTPS address for your Home Assistant.

Brainstorm Hub connects to no external service by itself, so setup needs no account or password.

### Option 1: HACS (Recommended - 1-Click)

Click the button below to add this repository directly to your HACS installation:

[![Open in HACS](https://img.shields.io/badge/HACS-Add%20Repository-41BDF5?logo=home-assistant&logoColor=white)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nukleuz80&repository=ha_brainstorm&category=integration)

Or manually:
1. Open **HACS** in your Home Assistant sidebar.
2. Click the three dots in the top right corner and select **Custom repositories**.
3. Enter `https://github.com/nukleuz80/ha_brainstorm`, choose **Integration** as category, and click **Add**.
4. Search for **Brainstorm Hub** and click **Download**.
5. Restart Home Assistant.

HACS only installs the integration, so continue with [Install the cards](#install-the-cards), then add the integration as shown in the next option.

### Option 2: Add Integration (Config Flow)

[![Start Config Flow](https://img.shields.io/badge/Home%20Assistant-Add%20Integration-41BDF5?logo=home-assistant&logoColor=white)](https://my.home-assistant.io/redirect/config_flow_start/?domain=brainstorm)

1. Go to **Settings ➔ Devices & Services ➔ Add Integration**.
2. Search for **Brainstorm Hub** and follow the on-screen setup guide.

### Option 3: Manual Installation

1. Download the latest release.
2. Copy the folder `custom_components/brainstorm` to `/config/custom_components/`.
3. Continue with [Install the cards](#install-the-cards).
4. Restart Home Assistant and add the integration as shown in option 2.

### Install the Cards

1. Copy `www/brainstorm-card.js`, `www/brainstorm-mindmap-card.js` and `www/brainstorm-i18n.js` from the release to `/config/www/`. The third file holds the texts and needs no resource entry.
2. Add both under **Settings ➔ Dashboards ➔ Resources** as **JavaScript module**:
   - `/local/brainstorm-card.js?v=1.6.0`
   - `/local/brainstorm-mindmap-card.js?v=1.6.0`
3. Reload the page in your browser.

### Removing the Integration

1. Go to **Settings ➔ Devices & Services ➔ Brainstorm Hub**, open the three dots and choose **Delete**.
2. Installed through HACS: open Brainstorm Hub in HACS and choose **Remove**. Installed manually: delete `/config/custom_components/brainstorm` and the three card files in `/config/www/`.
3. Remove the two card resources under **Settings ➔ Dashboards ➔ Resources**, and any Brainstorm cards from your dashboards.
4. Restart Home Assistant.

Depending on what you used, also remove:
- **Your Alexa skill:** Delete it in the Alexa developer console and its code in AWS Lambda. Real Alexa reminders stay in the Alexa app until you delete them there.
- **Automations and sentences:** Your own automations, scripts, and custom sentences that call Brainstorm, as well as an iPhone shortcut.
- **Your data:** Home Assistant keeps your ideas in `/config/.storage/brainstorm.storage`, the skill link in `brainstorm.alexa_skill` and the reminder state in `brainstorm.reminders` in the same folder. Delete these files and the Markdown folder (default `/config/brainstorm`) if you do not plan to come back.

---

## 🗣️ Voice Commands

Which language applies depends on where you speak: the skill follows the language of your Echo, everything else the language of Home Assistant. The German commands are in the [German documentation](README_de.md).

### Alexa Skill (Recommended)

Your own skill is the most reliable way. The setup is in the chapter *Optional: Your Own Alexa Skill* below. Start each sentence with *"Alexa, ask Brainstorm to"*:

| You say | What happens |
| :--- | :--- |
| *"note dim the basement light"* | Saves a note. Also: *idea*, *remember*, *add*, *write down* |
| *"remind me tomorrow at 8 to take out the bins"* | Saves a note with a reminder |
| *"done take out the bins"* or *"done"* | Completes a note, or the last reminder |
| *"later"* | Moves the last reminder by one hour |
| *"read"* or *"read daily life"* | Gives the overview, or reads a category |
| *"read everything"* | Reads all notes |
| *"show my lists"* or *"show daily life"* | Shows the lists on an Echo with a screen |

### Alexa Dialog

Say *"Alexa, brainstorm"*, Alexa asks for your note and confirms the category. It needs the Alexa Actionable Notifications skill. Copy the script and automation from [`examples/alexa_dialog.en.yaml`](examples/alexa_dialog.en.yaml) and create a routine in the Alexa app with the script as its scene, because **Brainstorm** is also the name of a band and Alexa would otherwise try to play music. Routines take priority over music search.

### Alexa Direct Commands

Say everything in one sentence: *"Alexa, note dim the basement light"*, *"Alexa, idea repair the sprinkler"*, *"Alexa, remember to fertilize the tomatoes"*. An automation stops any skill or music that started and confirms the entry. Copy it from [`examples/alexa_direct_commands.en.yaml`](examples/alexa_direct_commands.en.yaml). Alexa does not know these commands, so it may answer with an error first.

### Home Assistant Assist

**Brainstorm sentences** need your own custom sentences. Copy [`examples/custom_sentences/en/brainstorm.yaml`](examples/custom_sentences/en/brainstorm.yaml) to `/config/custom_sentences/en/`, add [`examples/intent_script.en.yaml`](examples/intent_script.en.yaml) to your `intent_script`, and restart Home Assistant:

- 🗣️ *"Add mow the lawn to Brainstorm"*
- 🗣️ *"New idea water the flowers"*
- 🗣️ *"Note create a database backup"*
- 🗣️ *"Remember to change the tires"*
- 🗣️ *"What is in daily life in Brainstorm?"*

**To-do list sentences** use Home Assistant's built-in commands:

- 🗣️ *"Add milk to the Brainstorm Hub Inbox list"*
- 🗣️ *"Check off milk on the Brainstorm Hub Inbox list"*

---

## 🎙️ Using Only Selected Echos

By default, every Echo can capture ideas. To limit this, go to **Settings ➔ Devices & Services ➔ Brainstorm Hub ➔ Configure ➔ General Settings & Export** and select the Echos under **Echo devices for voice input**. An empty list means all Echos.

The Alexa voice flows run as automations and scripts in your own Home Assistant configuration, so each entry point needs this condition (`echo_device` holds the calling Echo):

```yaml
- condition: template
  value_template: >-
    {% set allowed = state_attr('sensor.brainstorm_ideen_ubersicht', 'allowed_echos') %}
    {{ not allowed or echo_device in allowed }}
```

---

## 🎙️ Optional: Your Own Alexa Skill (One Sentence, One Answer)

Without a skill, Alexa often reports an error first when you say *"Alexa, note ..."*, because it does not know that command. Your own skill gives a single answer: *"Alexa, ask Brainstorm to note dim the basement light."* ➔ *"Saved under Smart Home."*

The skill belongs to you and only talks to your own Home Assistant. **Requirements:** a free [Amazon developer account](https://developer.amazon.com/alexa/console/ask) on the same account as your Echos and a Home Assistant reachable over public HTTPS (for example through Home Assistant Cloud). Home Assistant offers the voice model in its own language. German and English exist, and other languages get the English one. The skill answers in the language of the request.

1. In Home Assistant, go to **Brainstorm Hub ➔ Configure ➔ Alexa Voice Input & Skill**, choose **Skill** or **Both** and continue. Keep this window open, it shows the two fields to copy.
2. In the [Alexa developer console](https://developer.amazon.com/alexa/console/ask), click **Create Skill** and choose: name `Brainstorm`, the language of your Echo, such as **English (US)**, type **Custom**, hosting **Alexa-hosted (Python)**, template **Start from Scratch**.
3. Open **Build ➔ Interaction Model ➔ JSON Editor**, replace the content with the **Voice model** field, click **Save**, then **Build**, and wait for the success message.
4. In the **Code** tab, replace `lambda_function.py` with the **Skill code** field and click **Deploy**.
5. In the **Test** tab, set the stage to **Development**.
6. Click **Submit** in Home Assistant and say *"Alexa, ask Brainstorm to note test idea."* The first request links your skill, other skills are rejected afterwards. **Configure** shows the link and the last request.

**Notes:** Keep the skill code private, it contains your secret address. If it leaks, create a new one there and copy the skill code again. The Echo selection and device display apply to the skill too. For this, Home Assistant learns each Echo from the Alexa history on its first sentence (this needs the Alexa Media integration), which can take up to 3.5 seconds longer. If the history entry arrives later, the idea is still saved and the Echo is added afterwards. In the menu you need a command word such as *"note ..."*, plain free text is not possible in a skill. For **Skill** mode to turn off the existing capture, your automation has to check the `voice_mode` attribute:

```yaml
- condition: template
  value_template: "{{ state_attr('sensor.brainstorm_ideen_ubersicht', 'voice_mode') != 'skill' }}"
```

**Troubleshooting:** *"I don't know how to help with that"* usually means the **Build** is missing, the **Test** tab is not set to **Development**, or the console and Echo use different Amazon accounts. Try the sentence in the **Test** tab first. If Alexa says the idea was not saved, check the mode and whether Home Assistant is reachable.

---

## 📱 iPhone: Shortcut with Siri, Action Button or Back Tap

The fastest way from an iPhone: trigger, speak, done, without opening an app. It needs the Home Assistant companion app.

1. In the **Shortcuts** app, create a shortcut named **Brainstorm**. The name is also your Siri phrase.
2. Add **Dictate Text**, choose your language, and stop listening **After Pause**.
3. Add the Home Assistant action **Perform Action** and choose `brainstorm.add_idea`.
4. Paste this JSON into the data field and put the **Dictated Text** variable between the quotes after `"text":`:
   ```json
   {"text": "", "source": "siri", "device": "iPhone"}
   ```
5. Choose a trigger: **Settings ➔ Action Button ➔ Shortcut**, **Settings ➔ Accessibility ➔ Touch ➔ Back Tap ➔ Double Tap**, or *"Hey Siri, Brainstorm"*.

The note appears as **Siri (iPhone)** with an Apple logo. You can choose any device name in the JSON. If the shortcut reports that the data could not be read, the field is not valid JSON, often because the iPhone typed curly quotes. Paste the text or temporarily turn off **Settings ➔ General ➔ Keyboard ➔ Smart Punctuation**.

## 🎙️ Microphone in the Quick Input

The list card has a **🎙️** next to the quick input. Tap, speak, and the text appears in the field for checking. Recording ends on a pause, on another tap or after 30 seconds. It uses your preferred Assist pipeline, which needs a speech-to-text engine. The microphone only appears over HTTPS, so in the companion app or through an HTTPS address such as Home Assistant Cloud. Turn it off in the card settings or with `show_mic: false`.

## 👥 Privacy & Sharing

By default, all users of your Home Assistant see all ideas. Change this under **Brainstorm Hub ➔ Configure ➔ Privacy & Users**, and choose a **main user** who owns all existing ideas.

- **When on:** Every idea belongs to its creator, and only they and people it is shared with can see it.
- **Single ideas:** Long-press an idea ➔ **Share**, for each person to view or edit, or for all users.
- **Categories:** Select a category ➔ **👥 Share …**. This covers your own ideas in it, including later ones.
- **Several ideas:** **☑️ Select**, then complete, move, share or delete them at once. This also works without privacy.
- **Rights:** Edit allows changing and completing. Deleting and passing on stay with the owner.
- **Echos and Alexa apps:** Under **Assign Echos & Apps to People**, each device belongs to one person. What is said there is theirs, and only their ideas are read out. Home Assistant cannot recognize voices, and everyone in the room can hear it.

Admins and anyone with file access can still read everything. Home Assistant's to-do lists only show what is shared with everyone, because all users can read them. Existing Markdown exports stay in place when you switch this on, and new ones are only created if you allow it.

## ⏰ Reminders & Notifications

Brainstorm reminds you of due ideas on its own, over the services you have already set up in Home Assistant. Everything is optional and runs locally.

**Setting a time**
- **By voice (skill):** *"Alexa, ask Brainstorm to remind me tomorrow at 8 to take out the bins"*. Phrases like *tonight*, *tomorrow morning*, *on Friday*, *next week*, *March 15th*, *in two hours* are understood. Numeric dates like 3/4 are not, because countries read them differently, and *at 5* without am or pm means the next time it comes up.
- **In the lists:** Set a due date in the Home Assistant to-do lists. A plain date means 09:00.
- **On the card:** Long-press an idea ➔ choose a reminder.
- **In automations:** `brainstorm.add_idea` and `brainstorm.update_idea` with the `due` field.

**Configure** under **Brainstorm Hub ➔ Configure ➔ Reminders & Notifications**. Every feature has its own switch:

- **On/Off & Channels:** a master switch, the Alexa announcement (origin, most recent or fixed Echos, needs Alexa Media), any `notify` services (the companion app gets **Done**, **1 hour later** and **Tomorrow** buttons) and sending important open ideas to further services after a waiting time.
- **Quiet Hours, Briefing & Weekly Review:** Urgent ideas still reach your notification services during quiet hours, but no Echo speaks. The briefing can wait until a sensor or person detects someone.
- **Rules per List:** normal channels, Alexa only, notifications only (private) or nothing, own services, sending a list on certain days or at a place.
- **Places & Coming Home:** *"remind me to take out the trash when I get home"*, *"remind me of the milk when I get to the market"*, using your zones.
- **People:** *"remind Alex tomorrow at 8 to call the dentist"*, with own channels per person.
- **Calendar, AI & Alexa Reminders:** adds reminders once to a calendar (later changes are not transferred), shortens the briefing and review with an `ai_task` entity (your ideas go to its provider), and optionally creates real Amazon reminders in the skill (switch on **Build ➔ Permissions ➔ Reminders** in the Alexa console and grant consent once in the Alexa app).

**Lists on an Echo Show:** With the skill, an Echo with a screen shows your open ideas next to the voice answer: one page per category with tiles, swipe left or right to change it and scroll within a page. Touch the circle in front of an idea to complete it; a completed idea can be restored on the card. *"show daily life"* or *"show my lists"* shows the lists with only a short answer, while *"read"* and *"read everything"* show them while reading aloud.

To set this up, open **Build ➔ Interfaces** in the Alexa developer console, switch on **Alexa Presentation Language** with the Echo Show profiles, and click **Save**. Then copy the **Voice model** and **Skill code** fields again, click **Build** and **Deploy**. Without these steps, the skill keeps answering by voice only. Amazon decides how long a screen stays visible, and it can return to the home screen earlier than the requested two minutes.

**More skill sentences:** *"done bins"* or just *"done"* for the last reminder, *"later"* moves it one hour, *"read daily life"* reads a category, *"read"* gives only the overview, *"read everything"* reads everything.

**Your own automations:** Every reminder fires the `brainstorm_reminder_due` event, also without any services.

---

## 🎴 Lovelace Cards Configuration

Add the custom cards to your Lovelace dashboard resources:

```yaml
resources:
  - url: /local/brainstorm-card.js?v=1.6.0
    type: module
  - url: /local/brainstorm-mindmap-card.js?v=1.6.0
    type: module
```

### 1. List View (`brainstorm-card`)
```yaml
type: custom:brainstorm-card
title: Brainstorm Hub
sensor: sensor.brainstorm_ideen_ubersicht
color_mode: multicolor
hide_empty_categories: true
show_quick_input: true
show_categories: true
```

### 2. Mindmap View (`brainstorm-mindmap-card`)
```yaml
type: custom:brainstorm-mindmap-card
title: Brainstorm Mindmap
sensor: sensor.brainstorm_ideen_ubersicht
color_mode: multicolor
height: 650px
show_grid: true
show_bulb_watermark: true
hide_empty_categories: true
```

Click `⛶` at the top right to enlarge the mindmap to the full screen.

### 3. Your Own Sidebar Dashboard

Brainstorm also works as its own entry in the Home Assistant sidebar, for example under the path `/brainstorm-hub`, with three views: the mindmap above the list, the mindmap as a full-screen panel, and the list alone for fast typing and touch input.

`sensor.brainstorm_ideen_ubersicht` is the fixed entity ID in every language, so cards and automations keep working.

---

## 🎛️ All Settings

### During Setup

These can be changed later under **Reconfigure**. None of them is required, the defaults work for everyone.

| Field | What it does |
| :--- | :--- |
| Hide categories without notes (0) | Hides categories that have no notes from the cards. |
| Auto-export ideas to Markdown files | Writes one Markdown file per category to the folder below whenever ideas change. |
| File path for Markdown files | Folder for the Markdown files, for example /config/brainstorm. |

Reconfigure also offers:

| Field | What it does |
| :--- | :--- |
| Smart Text Optimization | Corrects capitalization and grammar of new ideas and removes filler words. |

### After Setup

Find these under **Settings ➔ Devices & Services ➔ Brainstorm Hub ➔ Configure**.

#### Brainstorm › Categories

| Field | What it does |
| :--- | :--- |
| ➕ Add new category (optional) | Name of a category to add. Leave empty to add none. |
| 🗑️ Delete existing category (optional) | The ideas of a deleted category move to Inbox. |
| ✏️ Edit full list (comma-separated) | All categories, separated by commas. Change this list to rename, reorder or remove several at once. |
| Hide categories without notes (0) | Hides categories that have no notes from the cards. |

#### Brainstorm › Category Design

| Field | What it does |
| :--- | :--- |
| Select Category | The category whose icon and color you want to change. |

#### Brainstorm › Category Design

| Field | What it does |
| :--- | :--- |
| Category Icon (Home Assistant / MDI) | Shown for this category on the cards. |
| Category Color | Color of this category on the cards. |
| Reset to default icon and color | Removes the icon and color of this category and ignores the two fields above. |

#### Brainstorm › General

| Field | What it does |
| :--- | :--- |
| Default category for new ideas | Used when an idea cannot be assigned to a category. |
| Smart Text Optimization (grammar, capitalization, infinitive formatting) | Corrects capitalization and grammar of new ideas and removes filler words. |
| Take dates from spoken text as a due date | A spoken "tomorrow" or "on 25.11." moves out of the text and becomes a due date. A due date leads to a reminder at that time, without a time of day at 09:00. |
| Own terms for spoken text | One term per line, for example Lenia, or a correction, for example fehler = Richtig. Names of people and categories are known automatically. |
| Auto-export ideas to Markdown files | Writes one Markdown file per category to the folder below whenever ideas change. |
| File path for Markdown files | Folder for the Markdown files, for example /config/brainstorm. |
| Echo devices for voice input | Only these Echos can capture ideas and open Brainstorm by voice. Leave empty to use all Echos. |

#### Brainstorm › Alexa

| Field | What it does |
| :--- | :--- |
| Voice input | Native uses the Alexa Media sentence without a skill. Skill and Both use your own Alexa skill. |

#### Brainstorm › Alexa › Skill

| Field | What it does |
| :--- | :--- |
| Skill code (lambda_function.py) | Copy this into lambda_function.py of your skill. Keep it private, it contains your secret address. |
| Voice model (JSON editor) | Paste this into the JSON editor of the Alexa developer console. |
| Create a new secret address and remove the skill link | Use this if the address leaked or you built a new skill. Copy the new skill code afterwards. |
| Name for this unknown device | For example Alexa App iPhone. Home Assistant cannot detect the Alexa app by itself. The name applies to the last idea and all later ones from this device. |

#### Brainstorm › Reminders › On/Off & Channels

| Field | What it does |
| :--- | :--- |
| Use reminders | Off stops all reminders, the briefing, the review and everything else in this menu. |
| Alexa announcement | Which Echo speaks a reminder. Off means no announcement. |
| Echos for announcements | Used for fixed Echos, as a fallback and for the briefing and review. |
| Send notifications | Off stops notifications but keeps the chosen services. |
| Notification services | These services receive reminders, for example your phone. |
| Wait before sending notifications (minutes) | Only with Alexa: gives you time to react before your phone is notified. 0 sends both at once. |
| Send important open ideas again | Sends entries with high or urgent priority again while they stay open. |
| Services for important ideas | These services receive the repeated message. |
| Send again after (minutes) | Applies to ideas with high or urgent priority that are still open. |

#### Brainstorm › Reminders › Quiet Hours, Briefing & Review

| Field | What it does |
| :--- | :--- |
| Use quiet hours | Off ignores the times below but keeps them. |
| Quiet hours from | Reminders wait until the quiet hours end. Urgent ideas still reach your notification services, but no Echo speaks. |
| Quiet hours until | Reminders that had to wait are sent at this time. |
| Daily briefing | Sends an overview of the day once a day. |
| Time of the briefing | When the briefing is sent. |
| Only when someone is detected here | Optional: The briefing then waits up to 6 hours after its time until a sensor or person here reports someone. |
| Weekly review | Sends an overview of older open entries once a week. |
| Day of the review | The day of the week for the review. |
| Time of the review | When the review is sent. |
| Mention ideas open for more than (days) | Entries that have been open for longer than this appear in the review. |

#### Brainstorm › Reminders › Rules per List

| Field | What it does |
| :--- | :--- |
| Use rules per list | Off makes all lists use the normal settings and keeps the rules. |
| List to edit | Choose a list to edit its rule on the next page. |

#### Brainstorm › Reminders › Rules › …

| Field | What it does |
| :--- | :--- |
| Reminders of this list go to | Normal channels follow the general settings of the reminders. |
| Own notification services for this list | Replace the normal services for this list. Empty uses the normal ones. |
| Send the open ideas on certain days | Sends the open entries of this list on the days and at the time below. |
| Days | The days on which the list is sent. |
| Time | When the list is sent on these days. |
| Send the open ideas at a place | Sent once a day when someone arrives there. Needs the switch for places. |
| Place | The zone in which the open entries of this list are sent. |

#### Brainstorm › Reminders › Places & Coming Home

| Field | What it does |
| :--- | :--- |
| Remind when coming home | Lets you say that a reminder should come when you get home. |
| Remind at places (zones) | Lets you name a zone for a reminder, for example a supermarket. |
| Who is meant by "ich" | Without a person, anyone arriving there triggers the reminder. |

#### Brainstorm › Reminders › People

| Field | What it does |
| :--- | :--- |
| Use reminders for other people | Lets a reminder be meant for someone else, such as: remind Alex. |
| Person to edit | Choose a person to set their channels on the next page. |

#### Brainstorm › Reminders › People › …

| Field | What it does |
| :--- | :--- |
| Notification services | This person's notification services. |
| Echos | The Echos that speak this person's reminders. |

#### Brainstorm › Reminders › Calendar, AI & Alexa

| Field | What it does |
| :--- | :--- |
| Add reminders to a calendar | One way, once per reminder. Later changes are not transferred. |
| Calendar | The calendar that receives the reminders. |
| Shorten the briefing and review with AI | Your ideas are sent to the provider of the chosen AI. |
| Improve spoken entries with AI | Each spoken entry is stored first and improved a few seconds later. The result is dropped if it adds words or changes a negation. The text is sent to the provider of the chosen AI. |
| AI task entity | The AI task entity that shortens the texts. |
| Also create real Alexa reminders | In the Alexa console, also switch on Reminders under Build ➔ Permissions. Alexa then rings itself and Home Assistant does not speak as well. |

#### Brainstorm › Privacy & Users

| Field | What it does |
| :--- | :--- |
| Keep ideas private | Each person then sees only their own entries and what is shared with them. |
| Main user | Owns all existing ideas, and everything said to an Echo. Voice, briefing and review only mention this person's ideas. |
| Keep exporting to Markdown files | These files contain all ideas and can be read by anyone with access to the config folder. |
| Offer these users for sharing | Leave empty to offer everyone. Use this to hide technical accounts such as MQTT. |

#### Brainstorm › Assign Echos & Apps

| Field | What it does |
| :--- | :--- |
| Echo or Alexa app | The Echo or Alexa app you want to assign. You can also type a name. |
| Person | Leave empty to remove the assignment. |

---

## ⚙️ Services

Every action stays available while the integration is not loaded and then explains why it cannot run.

### `brainstorm.add_idea`

Adds a new idea and detects the category in the text, such as `Garden: plant flowers` or `#smarthome`.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `text` | Yes | The content of the idea. |
| `category` | No | Category. If empty, it is detected from the text or set to `Inbox`. |
| `priority` | No | Urgency (`low`, `medium`, `high`, `urgent`). Detected automatically if empty. |
| `source` | No | Where the idea comes from, such as `alexa` or `dashboard`. |
| `device` | No | The device that triggered it, such as `Echo Show Küche`. |
| `tags` | No | Additional keywords. |
| `parent_id` | No | ID of the parent idea, to create a subtask. |
| `due` | No | When Brainstorm should remind you of this idea. |
| `parse_due` | No | Detects phrases like `tomorrow at 8` in the text and uses them as the time. |
| `assignee` | No | The person to remind. |
| `zone` | No | Reminds when entering this zone. |
| `language` | No | Language of the text, such as `de` or `en`. Without it, the language of Home Assistant applies. |

### `brainstorm.update_idea`

Changes an existing idea.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `id` | Yes | Unique ID of the idea. |
| `text` | No | New text. |
| `category` | No | New category. |
| `priority` | No | New priority (`low`, `medium`, `high`, `urgent`). |
| `status` | No | New status (`active`, `completed`, `archived`). |
| `device` | No | New device. |
| `parent_id` | No | ID of the parent idea. Empty makes it a main task. |
| `order` | No | Custom sort index. |
| `due` | No | When Brainstorm should remind you of this idea. |
| `assignee` | No | The person to remind. |
| `zone` | No | Reminds when entering this zone. |

### `brainstorm.delete_idea`

Permanently removes an idea.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `id` | Yes | ID of the idea to delete. |

### `brainstorm.get_ideas`

Returns stored ideas as a response, for templates and automations.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `category` | No | Only this category. |
| `priority` | No | Only this priority (`low`, `medium`, `high`, `urgent`). |
| `status` | No | Status filter (`active`, `completed` or `all`). |

### `brainstorm.get_announcement`

Returns a spoken text about all categories or one of them as a response, for Alexa or Assist.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `category` | No | Only this category, such as `Smarthome`. Empty means all. |
| `device` | No | The device that asked. With privacy on, it decides whose entries are named. |

### `brainstorm.add_category`

Creates a new category and its to-do list.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `name` | Yes | Name of the new category. |
| `icon` | No | Optional Home Assistant / MDI icon. |
| `color` | No | Optional accent color as hexadecimal, such as `#ff7800`. |

### `brainstorm.set_category_style`

Sets a custom icon and accent color for a category.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `category` | Yes | Name of the category. |
| `icon` | No | Home Assistant / MDI icon. |
| `color` | No | Accent color as hexadecimal, such as `#06b6d4`. |
| `reset` | No | Removes the custom icon and color. |

### `brainstorm.remove_category`

Removes a category. Its ideas move to `Inbox`.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `name` | Yes | Name of the category. |

### `brainstorm.export_markdown`

Writes all categories and ideas as Markdown files.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `path` | No | Target folder. Default: `/config/brainstorm`. |

### `brainstorm.reorder_ideas`

Saves the custom order of the ideas.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `idea_ids` | Yes | Ordered list of idea IDs. |

### `brainstorm.share`

Shares several ideas or a whole category. Needs privacy to be switched on.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `ids` | No | IDs of the ideas to share. |
| `category` | No | Shares all your ideas in this category, including later ones. |
| `shares` | Yes | User ID (or `all`) and level, such as `{"all": "view"}`. Levels are `view` and `edit`; `null` removes a share. |

---

## 📜 Version History & Changelog

| Version | Date | Status & Highlights |
| :--- | :--- | :--- |
| **`v1.6.0`** | 2026-11-02 | **English is officially supported:**<br>• **Complete:** Settings, cards, spoken notes, due dates, priorities, reminders, the Alexa skill and Assist sentences work in English.<br>• **Your data stays:** Stored categories and entries are not translated, renamed or migrated, in any language. A test checks this for German, English and an unknown language.<br>• **More languages:** `CONTRIBUTING.md` explains how to add one in three steps. Until then, other languages keep your text as it is and answer in English. |
| **`v1.5.16`** | 2026-11-02 | **Speak English with your own skill:**<br>• **Voice model:** Home Assistant offers an English voice model when it runs in English: *"Alexa, ask Brainstorm to note dim the basement light"*, *"remind me tomorrow at 8 to …"*, *"done"*, *"later"*, *"read"*, *"show my lists"*.<br>• **Language of the request:** With the new skill code, the skill follows the language of the Echo. Existing skills keep working without any change and use the language of Home Assistant.<br>• **Without Home Assistant:** The skill code holds its messages in all languages for when Home Assistant cannot be reached.<br>• **Examples:** `examples/` has Assist sentences and intent scripts in both languages, and an English Alexa dialog and direct command automation. |
| **`v1.5.15`** | 2026-11-02 | **The cards in English:**<br>• **All texts:** Both cards and their editors show their texts in the language of your Home Assistant profile, with dates to match. Languages without their own texts show English.<br>• **New file to copy:** `www/brainstorm-i18n.js` holds the texts. Copy it next to the two card files when you update by hand. It needs no resource entry.<br>• **Card editor:** The category choice only offers categories that exist. |
| **`v1.5.14`** | 2026-11-02 | **English texts in the backend:**<br>• **Reminders:** Spoken reminders, notifications with their buttons, the briefing, the weekly review and the AI summary follow the language of Home Assistant.<br>• **Also in English:** Logbook, to-do descriptions, Markdown export, read-aloud texts, AI tool answers and the Echo Show lists.<br>• **Reminder phrases:** *"when I get home"*, *"when I get to the market"* and *"remind Alex tomorrow at 8"* work in English.<br>• **Error messages and actions:** They now use Home Assistant's translations, which also shows them in the language of each user.<br>• **German stays:** All German texts keep their wording. |
| **`v1.5.13`** | 2026-11-02 | **English notes:**<br>• **Short tasks:** *"the lawn has to be mowed"* ➔ *"Mow lawn"*, *"I need to call the doctor"* ➔ *"Call doctor"*. Negations, questions and sentences that cannot be rebuilt completely keep their wording.<br>• **Due dates and priorities from the sentence:** *tomorrow at 8*, *next Monday at 5 pm*, *in two hours*, *March 15th*, *asap*, *important*, *someday*.<br>• **English categories:** A new installation in English starts with English categories. Existing categories keep their names and also understand English words.<br>• **New field:** `brainstorm.add_idea` accepts `language`, for example for a shortcut in another language. |
| **`v1.5.12`** | 2026-11-02 | **Prepared for more languages, no change in German:**<br>• **Language packs:** All German rules now live in their own pack, ready for further languages.<br>• **Same results:** A reference test with over 1,100 sentences ensures that German entries are built exactly as before.<br>• **Other languages:** Home Assistant in another language no longer applies German grammar to your text. It stays as spoken, with a capital first letter. |
| **`v1.5.11`** | 2026-11-02 | **Honest English documentation:**<br>• **Language support table:** Both READMEs show what works in which language today. Voice input and the cards are German for now.<br>• **Correct examples:** English examples of commands that do not exist are replaced by the real German ones with a translation.<br>• **Missing chapters:** The English README now covers voice commands, manual installation, installing the cards and the sidebar dashboard, and its changelog is complete.<br>• **HACS note:** Both READMEs say that HACS does not install the cards. |
| **`v1.5.10`** | 2026-11-01 | **Glossary and optional AI for spoken entries:**<br>• **Right spellings:** Names of people and categories and fixed terms like *PDF* or *Home Assistant* are spelled right automatically. Own terms and corrections are set under *General settings*.<br>• **More nouns:** A word list and compounds like *Sportverein* improve capitalization.<br>• **Optional AI step:** Under *Calendar, AI & Alexa Reminders*, an AI task entity improves the entry in the background. If it adds words or numbers or changes a negation, the version of the rules stays. The text goes to the provider of the chosen AI, and the step is off by default. |
| **`v1.5.9`** | 2026-11-01 | **Date, priority and original text:**<br>• **Date from the sentence:** *"morgen Arzt anrufen"* becomes *"Arzt anrufen"* with a due date and therefore a reminder, without a time of day at 09:00. The skill announces it. A new switch under *General settings* turns this off, and without reminders the date stays in the text.<br>• **Priority from the sentence:** "ganz wichtig", "unbedingt", "dringend" and "irgendwann" are found anywhere in the sentence.<br>• **Original text:** The spoken sentence stays stored and can be restored in the edit dialog of the card.<br>• **Category as subject:** *"Garten muss gegossen werden"* becomes *"Garten gießen"* instead of *"Muss gegossen werden"*. |
| **`v1.5.8`** | 2026-11-01 | **Better shortening of spoken entries:**<br>• **Whole sentences are rebuilt:** *"der Rasen muss gemäht werden"* becomes *"Rasen mähen"* instead of *"Rasen muss mähen"*. This now also covers "sollte", "will", "möchte" and separable verbs like *"rausgestellt"*.<br>• **New openers and filler words:** "äh", "ich glaube", "mir ist eingefallen", "vergiss nicht", "mal", "halt" and similar are removed.<br>• **All or nothing:** Negations, questions and sentences that cannot be rebuilt completely keep their wording.<br>• **Typed text stays:** Entries from the dashboard and to-do lists only get their typos fixed. |
| **`v1.5.7`** | 2026-11-01 | **Logo on the Echo Show:** The header of each page shows the Brainstorm logo. The Echo loads it from this GitHub repository. No new skill code is needed. |
| **`v1.5.6`** | 2026-11-01 | **New look on the Echo Show:** Tiles in two columns instead of a plain list, a colored header per category with open and urgent counts, page dots, and labels for priority, due date and parent task. Overdue dates are red. No new skill code is needed. |
| **`v1.5.5`** | 2026-11-01 | **Echo Show lists appear:** The screen stayed empty on a real Echo Show because the document did not receive its data, and it showed a wrong page count. No new skill code is needed. |
| **`v1.5.4`** | 2026-11-01 | **Lists on the Echo Show:**<br>• **Screen next to the voice answer:** One swipeable page per category, with subtasks and priority colors.<br>• **Complete by touch:** Touching the circle completes an idea, respecting private ideas.<br>• **New sentence:** *"zeige Alltag"* shows the lists with a short answer.<br>• **Setup:** Needs Alexa Presentation Language in the developer console and the new voice model and skill code. Older skill code keeps working by voice. |
| **`v1.5.3`** | 2026-11-01 | **Cards stay current with private ideas:**<br>• **Indenting works again:** With privacy on, the sensor did not change when an idea was indented, edited or moved, so the cards kept showing the old list. That could also lead to a false cycle error when indenting. The sensor now has a `revision` attribute without any idea content, which tells the cards to reload. |
| **`v1.5.2`** | 2026-11-01 | **Home Assistant Quality Scale: Silver:**<br>• **Silver checked rule by rule:** Still a self-assessment.<br>• **Actions report failures:** Removing a category that does not exist, unknown ideas when sorting or sharing, an unknown parent, and failed Markdown exports now raise a clear error instead of returning `success: false` or being ignored. To-do lists do the same for items that are gone.<br>• **Tests:** Every module is covered above 95 percent, including cleaning up when the integration is unloaded.<br>• **Docs:** All setup fields and settings are described. |
| **`v1.5.1`** | 2026-11-01 | **Home Assistant Quality Scale: Bronze:**<br>• **Bronze checked rule by rule:** The README and manifest claimed Silver, which was not correct. The status is now a self-assessment of Bronze, as Home Assistant did not review this custom integration.<br>• **Shorter names:** Lists are now called *Alltag* instead of *Brainstorm: Alltag*, and the sensor *Ideas overview*. Existing entity IDs stay the same; new lists get `todo.brainstorm_hub_*`.<br>• **No more polling:** Entities only update when something changes.<br>• **Clear errors:** If stored data cannot be read, Home Assistant tries the setup again. Actions explain when the integration is not loaded.<br>• **Settings:** New setups keep their settings in the options, and every field now has an explanation.<br>• **Tests and docs:** The config flow is fully tested. All actions and fields, the prerequisites, and removal are documented.<br>• **Brand images:** Now real PNG files in the correct sizes. |
| **`v1.5.0`** | 2026-11-01 | **Big Update: Skill, Reminders, Privacy & Sharing** (summary of v1.4.46 to v1.4.64):<br>• **Voice in one sentence:** Your own optional Alexa skill with one clean answer, Echo origin, Echo selection, an iPhone shortcut and a microphone in the quick input.<br>• **Proactive reminders:** Due dates by voice, list, card or service, over Alexa and any `notify` service, with phone buttons, quiet hours, briefing, weekly review, rules per list, places, people, calendar and AI.<br>• **Privacy & sharing:** Private ideas per user, sharing of ideas and categories with view or edit rights, multi-select, Echos and apps per person.<br>• **Settings:** Back navigation, live status, channel test and a switch for every feature. |
| **`v1.4.64`** | 2026-11-01 | **Apple Logo for Siri:** Ideas from an iPhone shortcut show an Apple logo. |
| **`v1.4.63`** | 2026-11-01 | **Documentation:** Added the iPhone shortcut, the microphone, privacy and sharing, and the new services. |
| **`v1.4.62`** | 2026-11-01 | **Siri as a Source:** Ideas from an iPhone shortcut with the source `siri` now show Siri and their device on both cards. |
| **`v1.4.61`** | 2026-11-01 | **Assist Microphone in the Quick Input:** A microphone next to the quick input turns speech into text with your preferred Assist pipeline. You can check the text before adding it. It can be switched off in the card settings and needs HTTPS. |
| **`v1.4.60`** | 2026-11-01 | **Select Several Ideas, Echos per Person:**<br>• **Selection mode:** Select several ideas on the list card, then complete, move, share or delete them at once.<br>• **Echos and apps per person:** What is said at an assigned device belongs to that person, and only their ideas are read out. Assist on a satellite without a user sticks to the main user.<br>• **Native announcements:** Use the service `brainstorm.get_announcement`, so they keep working with privacy on. |
| **`v1.4.59`** | 2026-11-01 | **Sharing Ideas and Categories:** With privacy on, ideas and whole categories can be shared with chosen people or everyone, to view or to edit. The list card gets a share dialog, the filters *Alle*, *Meine* and *Mit mir geteilt* and badges. To-do lists show what is shared with everyone, and a person who gets a reminder also gets access. New service `brainstorm.share`. |
| **`v1.4.58`** | 2026-10-31 | **Private Ideas per User (Foundation):** New switch *Privacy & Users*, off by default. When on, ideas belong to their creator: the sensor holds no idea texts, the cards load only the user's own ideas, and services, Assist, logbook, voice, briefing and reminders respect this. Existing ideas go to the chosen main user. To-do lists stay empty while it is on. Sharing follows in the next stage. |
| **`v1.4.57`** | 2026-10-31 | **Selected Category Stays:** Both cards remember the selected category after a page reload, per browser. A deleted category falls back to all. |
| **`v1.4.56`** | 2026-10-31 | **Settings with Back Navigation, Live Status and Channel Test:**<br>• **Stay in the settings:** Saving applies at once and returns to the menu. Every form can go back without saving, and titles show where you are.<br>• **Live status:** The reminder menu shows what is switched on and the next reminder.<br>• **Channel test:** *Test channels now* sends a real message and reports each channel. |
| **`v1.4.55`** | 2026-10-31 | **Own Name for the Alexa App:** Home Assistant cannot detect the Alexa app by itself, so the skill settings now let you name the last unknown device, for example *Alexa App iPhone*. The name appears at its ideas from then on, without any waiting time. |
| **`v1.4.54`** | 2026-10-31 | **Reliable Reminder Targets:** With an unknown origin, such as a sentence from the Alexa app, only fixed Echos speak, never the most recently used one. A phone chosen by its notify entity now finds its own service even when renamed, so its buttons appear. |
| **`v1.4.53`** | 2026-10-31 | **Deleting:** A double tap on delete in the list card no longer shows a wrong error message. |
| **`v1.4.52`** | 2026-10-31 | **Reminders Reach the Right Echo:** Echos with the same name in another integration, such as Music Assistant, no longer take the announcement. Choosing a phone's notify entity now also shows the buttons. |
| **`v1.4.51`** | 2026-10-31 | **Reminder Rules, Places, People, Calendar and AI:**<br>• **Every feature has its own switch** in a new settings menu, including a master switch.<br>• **Rules per list:** private lists only on the phone, lists on certain days or at a place.<br>• **Places and people:** reminders when coming home or at zones, and for other people with their own channels.<br>• **Follow-ups and extras:** important open ideas to further services, a briefing that waits for someone, calendar entries, AI summaries and optional real Alexa reminders. |
| **`v1.4.50`** | 2026-10-31 | **Proactive Reminders, Briefing and Weekly Review:**<br>• **Due dates** by voice, in the to-do lists, on the card and through services.<br>• **Your channels:** Alexa announcement and any `notify` service, phone buttons, a waiting time and the `brainstorm_reminder_due` event.<br>• **Quiet hours, daily briefing and weekly review.**<br>• **Skill:** new *erinnere mich*, *erledigt* and *später* sentences, and *Ansage* now gives a short overview. The skill needs a new build and code. |
| **`v1.4.49`** | 2026-10-31 | **Alexa Skill with the Native Features:**<br>• **Echo origin:** Ideas from the skill show the Echo they came from. Home Assistant learns each Echo once from the Alexa history and knows it immediately afterwards.<br>• **Echo selection:** Echos outside the selection are ignored silently, also in the skill.<br>• **Same language:** The skill understands the native command words and cleans the text the same way.<br>• **Announcement and menu:** *„Alexa, sage Brainstorm Ansage“* reads your ideas, also per category, and *„Alexa, starte Brainstorm“* opens the menu. |
| **`v1.4.48`** | 2026-10-31 | **Alexa Skill with Home Assistant Cloud:** The skill setup no longer reports a missing public HTTPS address when Home Assistant is reachable through Home Assistant Cloud (Nabu Casa). Unencrypted addresses are never offered. |
| **`v1.4.47`** | 2026-10-31 | **Optional Alexa Skill for One-Sentence Voice Input:**<br>• **Voice modes:** New *Alexa Voice Input & Skill* options with **Native** (default, unchanged), **Skill** and **Both**.<br>• **Your own skill:** *„Alexa, sage Brainstorm notiere …“* now gives one clean answer. Home Assistant generates the skill code and voice model to copy, links the first skill automatically and rejects others.<br>• **Reliable answers:** Alexa only confirms what was really saved. |
| **`v1.4.46`** | 2026-10-31 | **Selected Echos for Voice Input:**<br>• **New option:** *General Settings & Export* now has a multi-select for Alexa Media Echos. Only the selected Echos can capture ideas and open Brainstorm by voice; with an empty list, all Echos keep working.<br>• **For automations:** The selection is available as the `allowed_echos` attribute of `sensor.brainstorm_ideen_ubersicht`. |
| **`v1.4.45`** | 2026-10-31 | **Reliable Categories, Auto-Export, LLM Tools, Text Optimization & Security:**<br>• **Options Flow:** Adding or deleting a category no longer gets reverted by the pre-filled list field; the list is only applied if it was actually edited.<br>• **Persistent Categories:** Deleted default categories stay deleted after a reload or restart, and the custom order is kept.<br>• **Auto-Export:** A failing Markdown export is logged and no longer aborts the action, so events and entity updates still fire. Export data is collected in the event loop instead of the executor.<br>• **LLM Tools:** `brainstorm_list_categories` no longer crashes, the category `all` and case-insensitive names work, and ambiguous delete or complete requests now return the candidates instead of acting on the first match.<br>• **Text Optimization:** A single remaining word keeps its category word (*Haus streichen*), spellings like *WLAN* or *iPhone* are preserved, and capitalization, infinitives and genitive articles are handled correctly.<br>• **Security:** Markdown exports are limited to config subfolders and `allowlist_external_dirs`, category names are escaped in both cards, and icons and colors are validated (colors must be hex values).<br>• **Recorder:** Large sensor attributes are no longer recorded, which avoids the 16 KB limit.<br>• **Reconfigure:** Changes now take effect even if options exist, without the deprecated reload helper.<br>• **Lifecycle:** Removed the runtime module reload and translation cache manipulation, services are now registered in `async_setup`, and the non-functional YAML import is gone. Python changes now need a restart.<br>• **To-do Lists:** Entities of deleted categories are removed, archived ideas are no longer shown as open, and editing a completed idea no longer fires `idea_completed` again.<br>• **Data Integrity:** Parent cycles are rejected, unknown IDs raise an error, and the `default_category` option now works.<br>• **Compatibility:** LLM tools use `ToolResult` and annotations, minimum version is Home Assistant 2026.10.<br>• **Tests:** Added a test suite running against real Home Assistant. |
| **`v1.4.44`** | 2026-10-30 | **Last Alexa Display with Entity Selection & Resilient Visual Card Editor:**<br>• **Last Alexa Display in Card Headers:** Added an active Alexa badge (`.last-alexa-badge`) with a crisp microphone micro-icon and live device name in the header of `brainstorm-card` and the toolbar of `brainstorm-mindmap-card`. Tapping/clicking the badge opens the native Home Assistant `more-info` dialog for the active Echo device.<br>• **Visual Entity Selector for Last Alexa:** Added `show_last_alexa` toggle and `last_alexa_entity` selector (defaulting to `sensor.last_alexa` or any `media_player` / `sensor` entity) directly inside both visual card editors.<br>• **Resilient Visual Card Editor Architecture:** Resolved lifecycle timing in `BrainstormCardEditor` and `BrainstormMindmapCardEditor`. Both editors now preload Lovelace helpers in `static async getConfigElement()`, implement `connectedCallback()`, and properly merge form updates without inadvertently resetting boolean card settings. |
| **`v1.4.43`** | 2026-10-30 | **Category Design Flow UX Optimization & Clear Step Progression:**<br>• **Clear Multi-Step Navigation („Next“ instead of „OK“):** Configured `last_step=False` on the category selection screen so the Home Assistant action button renders unambiguously as *“Next”* (*„Weiter“*) instead of a misleading *“OK”*, eliminating the impression of an incomplete dialog.<br>• **Explicit Step Progression Titles & Descriptions:** Step 1 clearly states *“Category Design (Step 1 of 2)”* and instructs users to proceed to icon and color selection; Step 2 explicitly announces *“Design for '{category}' (Step 2 of 2)”* with Home Assistant MDI icon picker, RGB color selector, and reset toggle.<br>• **Category State Preview:** The category dropdown displays the currently configured icon and color in parentheses (or *Standard*) for instant overview.<br>• **New „Done & Close“ Option:** Added a dedicated completion action (*„Fertig & Schließen“*) upon saving styles to cleanly exit the options flow. |
| **`v1.4.42`** | 2026-10-30 | **Direct Dictionary Mapping for Options Menu Labels (Fix Blank Row):**<br>• **Permanent Menu Label Resolution:** Passed explicit localized label dictionaries (`dict[str, str]`) in `async_show_menu` for `init` and `category_style_done` steps. This completely bypasses the frontend's cached translation lookups, ensuring that *“Kategorie-Design (Farbe & Icon)”* / *“Category Design (Color & Icon)”* is rendered reliably without blank rows regardless of browser or core translation cache status.<br>• **Full Bilingual Support:** Auto-detects active language (`de` vs. `en`) with complete fallback. |
| **`v1.4.41`** | 2026-10-30 | **Maximum Space-Filling Bulb Logo & Enhanced Visual Presence:**<br>• **Full-Bleed Bulb Geometry:** Redesigned the brain-lightbulb vector graphic with a fuller, wider dome (aspect ratio ~0.92:1) and compact metallic fitting, completely eliminating empty side margins inside square icon containers. The visible bulb area is more than doubled (+132%) in size.<br>• **Tight ViewBox & Minimal Padding:** Set precision-fitted `viewBox="136 58 240 261"` and reduced container padding to 1px (with 36px icon container), allowing the glowing bulb to fully exploit all available card header space edge-to-edge.<br>• **Universal High-Impact Assets:** Synchronized full-bleed graphic across `brainstorm-card`, `brainstorm-mindmap-card`, `brainstorm-logo.svg`, and `brainstorm-bulb.svg` (mindmap central watermark and card config editors). |
| **`v1.4.40`** | 2026-10-29 | **Adaptive Theme Logo (Light/Dark), Visual Refinements & Logo Toggle:**<br>• **Adaptive Theme Styling (Light & Dark):** Brand logo container across `brainstorm-card` and `brainstorm-mindmap-card` now utilizes dynamic CSS color mixing (`color-mix(in srgb, var(--primary-color) 12%, var(--card-background-color))`) rather than hardcoded dark squares (`#0d1117`), perfectly blending with light dashboards and dark themes alike.<br>• **Crisp Vector Brain-Bulb Graphic:** Re-engineered the central SVG graphic into an ultra-sharp, transparent-background vector icon with glowing synapses, golden filament spark, and metallic base, eliminating illegible micro-text and pixelation at compact card header sizes.<br>• **Show/Hide Logo Option (`show_logo`):** Added `show_logo: true` toggle in YAML configuration and both visual UI card editors (`BrainstormCardEditor` & `BrainstormMindmapCardEditor`) to let users easily display or hide the brand logo.<br>• **Options Flow Label Fix:** Guaranteed menu translation synchronization in `async_step_init` so all Hub options rows display localized titles cleanly without empty lines. |
| **`v1.4.39`** | 2026-10-29 | **100% Fully Responsive Layouts & Deep Mobile Optimizations:**<br>• **Container Queries & Dynamic Column Adaptation:** Implemented modern CSS Container Queries (`@container (max-width: ...)`) alongside viewport `@media` queries across both `brainstorm-card` and `brainstorm-mindmap-card`. Cards now adapt their density, layout, headers, and quick-capture bars perfectly to their exact container width—whether viewed on a small smartphone, tablet, or in narrow multi-column sections on desktop dashboards.<br>• **Adaptive Mindmap Geometry & Mobile Auto-Fit:** The mindmap radial layout engine now dynamically adapts elliptical radii (`rx0`, `ry0`) and node collision boundaries when card width is narrow (< 550px). Auto-scale limit relaxes down to 0.35 to guarantee the entire mindmap remains fully visible and centered on mobile devices.<br>• **Fullscreen Mobile Mindmap Modal:** Opening the mindmap layer popup on mobile devices (< 768px) now expands to a clean, edge-to-edge full-screen app view without borders or wasted margins.<br>• **Touch Usability & iOS Auto-Zoom Prevention:** Form inputs now enforce `font-size: max(0.92rem, 16px)` to eliminate unwanted iOS Safari page zoom upon tapping inputs. List actions (`✎`, `✕`, `↳`) maintain permanent accessibility on touchscreens (`@media (hover: none)`).<br>• **Responsive Modal Dialogs:** Priority and category grids in editing dialogs now automatically wrap to 2 columns on small screens instead of overflowing. |
| **`v1.4.38`** | 2026-10-29 | **Bugfix Options Flow Menu Labels & Live Cache Invalidation:**<br>• **Direct Label Mapping in Options Menu:** Fixed blank menu row in Brainstorm Hub Options (*„Brainstorm Hub Optionen“*) where the second item (*„Kategorie-Design (Farbe & Icon)“* / *„Category Design (Color & Icon)“*) appeared without text due to frontend string cache fallback. Options flow now passes localized menu mapping directly in `async_show_menu`.<br>• **Automatic Translation Cache Invalidation:** Added runtime invalidation for `_TranslationCache` in `async_setup_entry` ensuring new flow steps and labels are immediately available without requiring a full Home Assistant restart. |
| **`v1.4.37`** | 2026-10-29 | **Logbook & Activity Task Attribution (Home Assistant „What happened?“ Cause Linking):**<br>• **Task Attribution in Activity Details:** When inspecting the Activity (Logbook) history for `sensor.brainstorm_ideen_ubersicht` and opening the *„What happened?“* (*Was ist passiert?*) dialog, the specific task text and category are now clearly attributed as the cause/reason for the activity instead of showing generic state changes or *„No cause was recorded for this activity“*.<br>• **Native Context & Entity Linking:** Fired event payloads (`EVENT_IDEA_ADDED`, `EVENT_IDEA_COMPLETED`, `EVENT_IDEA_UPDATED`, `EVENT_IDEA_DELETED`) now include `entity_id` (`sensor.brainstorm_ideen_ubersicht`) and preserve the triggering `context` (`call.context`), allowing Home Assistant's native logbook chain resolver to stitch together user attributions, service calls, events, and state changes.<br>• **Sensor Attribute `last_action`:** `sensor.brainstorm_ideen_ubersicht` exposes `last_action` (action type, note text, category, priority, and timestamp) for easy access in automations, templates, and dashboard cards. |
| **`v1.4.36`** | 2026-10-29 | **Streamlined Compact Task Rows & Mobile Optimization:**<br>• **Reduced Task Row Height:** Optimized vertical task padding (from 12px down to 8px/6px) and list spacing (down to 5px/4px) across `brainstorm-card`. Displays significantly more tasks per screen without clutter.<br>• **Smartphone & iPhone Refinement:** Fine-tuned mobile breakpoints (`≤600px` and `380px`) with smaller check buttons (18px), compact badges, and narrower subtask indentation (10px instead of 24px/16px) to eliminate premature line wraps on iPhone screens.<br>• **New Compact Mode (`compact_mode`):** Card configuration toggle for maximum task density on busy dashboards.<br>• **Mindmap Mobile Cards:** Scaled note clouds in `brainstorm-mindmap-card` on mobile screens. |
| **`v1.4.35`** | 2026-10-29 | **Customizable Category Colors & Home Assistant MDI Icons:**<br>• **Category Design in Settings:** New *„Category Design (Color & Icon)“* section in Hub options flow using Home Assistant native `selector.IconSelector` (MDI icon browser & search) and visual `selector.ColorRGBSelector`.<br>• **1-Click Card Design Editor:** Quick 🎨 button on active category pills in `brainstorm-card` allows customizing colors and icons directly from dashboards with live preview.<br>• **Full Dashboard Rendering:** Category pills, note tags, and the central mindmap hub in `brainstorm-mindmap-card` seamlessly display custom icons and colors.<br>• **New Service:** `brainstorm.set_category_style` service added; `brainstorm.add_category` updated with optional `icon` and `color`. |
| **`v1.4.34`** | 2026-10-29 | **Category Options Cleanup (Deduplication of `hide_empty_categories`):**<br>• Removed redundant toggle *„Hide categories without notes (0)“* from Hub *General Settings*.<br>• The central dashboard default option is now cleanly and contextually located under *„Manage Categories“* as well as individually configurable per Lovelace card. |
| **`v1.4.33`** | 2026-10-29 | **Vibe Coding Manifesto & Badges:** Official badge and dedicated declaration celebrating passionate AI-assisted software development (*“Crafted with Pure Vibe Coding”*). |
| **`v1.4.32`** | 2026-10-29 | **Bilingual Documentation (EN/DE), Alexa Voice Capture Spotlight & 1-Click Badges:**<br>• **Full English Documentation:** Comprehensive English documentation (`README.md`) alongside German version (`README_de.md`) with country flag language switcher (`🇬🇧 English` ⇄ `🇩🇪 Deutsch`).<br>• **Alexa Voice Capture Spotlight:** Prominent hero section showcasing hands-free voice capturing, two-way dialogue, anti-music collision protection, NLP text cleaning, and Echo device origin tracking.<br>• **1-Click My Home Assistant Badges:** Direct integration via HACS repository link and Config Flow launch buttons.<br>• **Version Synchronization:** Unified release across manifest, sensor, todo platforms, and Lovelace cards. |
| **`v1.4.31`** | 2026-10-29 | **Background Rendering Fix & Synchronized Dot Grid:**<br>• **Eliminated Moiré Artifacts & Color Blocks:** Resolved visual banding in `brainstorm-mindmap-card` caused by steep radial-gradient stops and GPU compositor layers.<br>• **Subpixel Anti-Aliasing & Canvas Transparency:** Smooth dot grid transitions and clean canvas layer over `ha-card`.<br>• **Synchronized Pan & Zoom:** Background grid moves and scales naturally with the mindmap viewport.<br>• **Configurable Grid:** Added `show_grid` card toggle in the visual UI editor. |
| **`v1.4.30`** | 2026-10-29 | **Mindmap Synapses Bugfix on Category Switch:**<br>• **Eliminated Orphaned Ghost Lines:** Resolved an issue where switching categories left residual Bézier curves without node boxes. `_drawConnections` now strictly verifies active category filtering.<br>• **Clean Layout Reset:** Node positions and dragging states reset cleanly on category switch. |
| **`v1.4.29`** | 2026-10-29 | **Drag & Drop Reordering, Subtask Nesting & Apple Reminders Menu:**<br>• **Drag & Drop Sorting:** Reorder ideas in the list view smoothly via drag handles (`⠿`) with persistent storage.<br>• **Drag & Drop Subtask Nesting:** Dragging an item onto an existing task nests it directly as a subtask.<br>• **Apple Reminders Context Menu:** Long-press on mobile (~420ms) or right-click on desktop triggers haptic feedback and opens a quick menu for indenting, unindenting, moving, editing, or deleting. |
| **`v1.4.28`** | 2026-10-29 | **Hide Empty Categories Default:** Empty categories (0 notes) hidden by default in filter pills across both cards (`hide_empty_categories: true`). |
| **`v1.4.27`** | 2026-10-28 | **Subtasks and active category:** Indent and outdent notes with one tap or in the edit dialog. New notes from the quick input go to the active category tab. The mindmap toolbar hides *All* on phones. |
| **`v1.4.26`** | 2026-10-28 | **Hide empty categories:** New option `hide_empty_categories` for the integration and for each card. The selected category stays visible and the dropdowns keep all categories. |
| **`v1.4.25`** | 2026-10-25 | **Category dropdown in the card editors:** `default_category` lists all categories and still accepts free input. |
| **`v1.4.24`** | 2026-10-25 | **Fix:** A syntax error stopped the mindmap card from loading (*Custom element doesn't exist*). |
| **`v1.4.23`** | 2026-10-25 | **Responsive header and color mode fix:** Tidier header and quick capture with chips for category and priority, better phone layout. The color mode button now switches immediately in both cards. |
| **`v1.4.22`** | 2026-10-25 | **Priority Management:** 4 priority levels (`urgent`, `high`, `medium`, `low`), NLP urgency extraction, 1-click badge cycling, and animated flame pulse effects in mindmap. |
| **`v1.4.21`** | 2026-10-25 | **Dynamic category detection:** Aliases and keywords are built for all active categories at runtime, including your own. *Projekt …* prefixes are understood, and project notes in the Alexa main menu are no longer taken for a query. |
| **`v1.4.20`** | 2026-10-24 | **Assist LLM Function Calling:** 5 native Home Assistant LLM tools for conversational AI assistants. |
| **`v1.4.19`** | 2026-10-24 | **Silver quality scale as a self-assessment (corrected to Bronze in v1.5.1, reached with v1.5.2) and logbook:** Native logbook entries, a reconfigure flow, standard service errors and clean unloading. |
| **`v1.4.18`** | 2026-10-24 | **Bronze quality scale as a self-assessment (checked again in v1.5.1) and faster Alexa:** `runtime_data`, `PARALLEL_UPDATES` and `quality_scale.yaml`. Removing delays and repeated stops makes dialogs four times faster. |
| **`v1.4.17`** | 2026-10-23 | **Category colors:** Each category gets its own color, your own categories get one from a hash. Edges, lines and tags show it, and the category bar gets colored dots. |
| **`v1.4.16`** | 2026-10-23 | **Multi-ring mindmap:** Up to three rings, a relaxation pass against overlaps, a free center, colored connection lines and zoom to fit. Moved cards stay in place. |
| **`v1.4.15`** | 2026-10-23 | **Fix for the visual card editor:** Switches now take effect immediately in the preview and on dashboards. Better layout for the sidebar dashboard. |
| **`v1.4.14`** | 2026-10-23 | **Device origin for Alexa and Assist:** The cards, sensor attributes, to-do descriptions, Markdown export and services show the device that captured an idea. |
| **`v1.4.13`** | 2026-10-22 | **Reading ideas aloud:** New service `brainstorm.get_announcement`, attribute `speech_overview`, an Alexa dialog and Assist intents. |
| **`v1.4.12`** | 2026-10-22 | **Sensor fallback:** Cards fall back to the Brainstorm sensor if another entity is configured, and the editor only offers Brainstorm entities. |
| **`v1.4.11`** | 2026-10-22 | **Category filter:** Spaces around category names no longer hide ideas. |
| **`v1.4.10`** | 2026-10-21 | **Validation:** Both cards reject empty or duplicate input with a clear message, and the backend raises `ServiceValidationError`. |
| **`v1.4.9`** | 2026-10-21 | **Fix:** A `TypeError` stopped active ideas from showing in the list. |
| **`v1.4.8`** | 2026-10-21 | **Fix:** The input in the *New category* dialog uses the full width again. |
| **`v1.4.7`** | 2026-10-21 | **Fix:** A duplicate declaration stopped the card from loading, `customElements.define` got guards, and a YAML error in `services.yaml` is gone. |
| **`v1.4.6`** | 2026-10-20 | **Visual card editors:** All card settings can be changed with clicks, dropdowns and switches. |
| **`v1.4.5`** | 2026-10-20 | **Theme colors and color mode switch:** Theme or multicolor mode in both cards, stored in the browser and in the card option `color_mode`. |
| **`v1.4.4`** | 2026-10-20 | **Transparent bulb and full height:** A transparent bulb watermark and full use of the popup height. |
| **`v1.4.3`** | 2026-10-20 | **No more jitter, own dialogs:** Smoother clicks and dragging. Browser prompts are replaced by dialogs inside the card. |
| **`v1.4.2`** | 2026-10-20 | **Mushroom design and popup:** The mindmap follows the Mushroom and Minimalist style, and the preview became a centered popup. |
| **`v1.4.1`** | 2026-10-20 | **Mindmap display:** Theme colors for categories and the full-screen button, and almost full screen height by default. |
| **`v1.4.0`** | 2026-10-20 | **NLP Text Optimization:** Automatic conversational filler stripping, verb infinitizing, and spell correction. |
| **`v1.3.0`** | 2026-10-20 | **Mindmap Card Release:** Interactive radial synapse layout with category hub and idea clouds. |
| **`v1.2.1`** | 2026-10-20 | **Fixes:** No more `ResponseNone` entries or music collisions with Alexa, fixed the Assist wildcard parsing and a card error (`counts is not defined`). |
| **`v1.1.0`** | 2026-10-20 | **Frontend redesign and standards:** Two-tier card layout, HACS compatibility, `DeviceInfo` and Assist support. |
| **`v1.0.0`** | 2026-10-19 | **Initial Release:** Core integration, To-do platform, Markdown export, and Alexa dialogue. |

---

## ✨ 🚀 Crafted with Pure Vibe Coding

> *“Vibe coding is the art of turning pure ideas into reality through fluid conversation, human creativity, and AI superpowers.”*

This project was built and continues to grow with pure passion and full devotion to **Vibe Coding**. We don't hide the AI — we celebrate it openly and proudly:
- **Human Product & UX Vision:** Every feature, every mobile gesture, every mindmap detail, and every voice routine is born from real-life smart home needs and a genuine love for great UX.
- **High-Velocity AI Pair Programming:** Powered by advanced agentic AI coding assistants (Google Antigravity & Claude/Gemini), turning ambitious architecture, bug fixes, and polish into reality at lightning speed.
- **100% Open Source & Community First:** Transparent, hackable, and built for everyone in the Home Assistant ecosystem.

---

## 📄 License

This project is licensed under the **MIT License** – see [LICENSE](LICENSE) for details.

Copyright © 2026 [nukleuz80](https://github.com/nukleuz80)
