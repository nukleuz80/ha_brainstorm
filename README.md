<div align="center">

# 🧠 Brainstorm Hub for Home Assistant

**[🇬🇧 English](README.md)** &nbsp;|&nbsp; **[🇩🇪 Deutsch](README_de.md)**

[![English Docs](https://img.shields.io/badge/Language-English%20%F0%9F%87%AC%F0%9F%87%A7-blue.svg)](README.md)
[![German Docs](https://img.shields.io/badge/Sprache-Deutsch%20%F0%9F%87%A9%F0%9F%87%AA-green.svg)](README_de.md)
[![Open in HACS](https://img.shields.io/badge/HACS-Add%20Repository-41BDF5?logo=home-assistant&logoColor=white)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nukleuz80&repository=ha_brainstorm&category=integration)
[![Start Config Flow](https://img.shields.io/badge/Home%20Assistant-Add%20Integration-41BDF5?logo=home-assistant&logoColor=white)](https://my.home-assistant.io/redirect/config_flow_start/?domain=brainstorm)
[![Version](https://img.shields.io/badge/version-1.4.36-blue.svg)](https://github.com/nukleuz80/ha_brainstorm/releases)
[![Vibe Coding](https://img.shields.io/badge/Vibe%20Coding-100%25%20with%20Devotion-ff69b4?logo=sparkles&logoColor=white)](https://github.com/nukleuz80/ha_brainstorm)
[![Quality Scale](https://img.shields.io/badge/Quality%20Scale-Silver-C0C0C0.svg)](https://developers.home-assistant.io/docs/integration_quality_scale_index/)
[![GitHub Release](https://img.shields.io/github/v/release/nukleuz80/ha_brainstorm)](https://github.com/nukleuz80/ha_brainstorm/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/nukleuz80/ha_brainstorm)

</div>

**Brainstorm Hub** is the ultimate smart capture center for all your thoughts, ideas, and tasks in your Home Assistant smart home.  
Whether you are cooking, working in the workshop, relaxing in the garden, or on the go: capture sudden flashes of inspiration within seconds hands-free via voice (**Amazon Alexa** or **Home Assistant Assist**), through interactive Lovelace dashboard cards, or via automated triggers. Brainstorm categorizes your thoughts using intelligent NLP heuristics and optionally synchronizes them as clean Markdown files for Obsidian, Logseq, or Nextcloud.

---

## 🌟 🗣️ Key Feature: Seamless Amazon Alexa Hands-Free Voice Capture

> 🗣️ *“Alexa, Brainstorm”* ➔ 🤖 *“Brainstorm ready. What's on your mind?”*  
> 🗣️ *“Urgent garden: Repair lawnmower”* ➔ 🤖 *“Saved under House & Garden [🔥 Urgent].”*

Brainstorm Hub turns every **Amazon Echo** device in your home into an instant, friction-free thought catcher — ideal when your hands are wet, dirty, or occupied.

### ⚡ Why Alexa Voice Capture is the Premier Feature:
- 🚫 **Zero Music & Shopping List Collisions:** Out of the box, Alexa frequently misinterprets open-ended notes by dumping them into chaotic Amazon shopping lists or launching songs by the rock band *“Brainstorm”* on Spotify. Brainstorm Hub eliminates this friction with optimized routine triggers and automatic background stop commands for a whisper-quiet, 100% reliable dialogue.
- 🗣️ **Interactive Two-Way Dialogue Mode:** Simply say *“Alexa, Brainstorm”* or *“Alexa, New Idea”*. Alexa listens, parses your input, and instantly responds with spoken confirmation of the assigned category and urgency level.
- ⚡ **One-Shot Direct Voice Commands:** When seconds count: *“Alexa, note in Smarthome dim basement light”* or *“Alexa, idea urgent Garden: Clean patio”*.
- 🧠 **Smart NLP Text Cleaning & Grammar Transformation:** Strips out conversational filler words (*“please write down that we need to…”* ➔ *“Clean patio”*), fixes speech typos, and transforms passive verb constructions into clear actionable tasks.
- 🏷️ **Contextual Priority & Category Extraction:** Detects priority triggers (*“urgent”*, *“important”*, *“priority 1”*, *“whenever possible”*) and category prefixes (*“in Smarthome”*, *“for the garden”*) regardless of word order in the sentence.
- 📍 **Echo Origin Tracking:** Automatically records which Echo device received the idea (e.g., `🗣️ Alexa (Echo Show Kitchen)` vs. `🗣️ Alexa (Workshop Echo Dot)`).

---

## 🌟 Highlights & Features

- 🎯 **Intelligent Priority Management & Visual Urgency Levels:**
  - **4 Priority Levels:** `low` (🟢 Low), `medium` (🟡 Medium / Default), `high` (🔴 High), and `urgent` (🔥 Urgent).
  - **Natural Language Urgency Detection:** Recognizes priority words in spoken or typed notes (e.g. *“Urgent Garden: Fix mower”*, *“Priority 1…”*, *“!urgent”*, *“!high”*), cleans the text, and sets the priority automatically.
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
  - Synchronizes all active categories as native Home Assistant To-do entities (`todo.brainstorm_*`).

---

## 🚀 Installation

### Option 1: HACS (Recommended - 1-Click)

Click the button below to add this repository directly to your HACS installation:

[![Open in HACS](https://img.shields.io/badge/HACS-Add%20Repository-41BDF5?logo=home-assistant&logoColor=white)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nukleuz80&repository=ha_brainstorm&category=integration)

Or manually:
1. Open **HACS** in your Home Assistant sidebar.
2. Click the three dots in the top right corner and select **Custom repositories**.
3. Enter `https://github.com/nukleuz80/ha_brainstorm`, choose **Integration** as category, and click **Add**.
4. Search for **Brainstorm Hub** and click **Download**.
5. Restart Home Assistant.

### Option 2: Add Integration (Config Flow)

[![Start Config Flow](https://img.shields.io/badge/Home%20Assistant-Add%20Integration-41BDF5?logo=home-assistant&logoColor=white)](https://my.home-assistant.io/redirect/config_flow_start/?domain=brainstorm)

1. Go to **Settings ➔ Devices & Services ➔ Add Integration**.
2. Search for **Brainstorm Hub** and follow the on-screen setup guide.

---

## 🎴 Lovelace Cards Configuration

Add the custom cards to your Lovelace dashboard resources:

```yaml
resources:
  - url: /local/brainstorm-card.js?v=1.4.32
    type: module
  - url: /local/brainstorm-mindmap-card.js?v=1.4.32
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

---

## ⚙️ Services

| Service | Description | Parameters |
| :--- | :--- | :--- |
| `brainstorm.add_idea` | Adds a new thought with auto or manual category | `text` (required), `category`, `source`, `priority`, `tags` |
| `brainstorm.update_idea` | Updates note text, category, priority, or status | `id` (required), `text`, `category`, `priority`, `status` |
| `brainstorm.delete_idea` | Permanently removes an idea | `id` (required) |
| `brainstorm.reorder_ideas` | Updates the persistent custom order of notes | `idea_ids` (required) |
| `brainstorm.add_category` | Creates a new category | `name` (required) |
| `brainstorm.remove_category` | Removes category (ideas move to Inbox) | `name` (required) |
| `brainstorm.export_markdown` | Triggers immediate markdown export | `path` (optional) |

---

## 📜 Version History & Changelog

| Version | Date | Status & Highlights |
| :--- | :--- | :--- |
| **`v1.4.36`** | 2026-10-29 | **Streamlined Compact Task Rows & Mobile Optimization:**<br>• **Reduced Task Row Height:** Optimized vertical task padding (from 12px down to 8px/6px) and list spacing (down to 5px/4px) across `brainstorm-card`. Displays significantly more tasks per screen without clutter.<br>• **Smartphone & iPhone Refinement:** Fine-tuned mobile breakpoints (`≤600px` and `380px`) with smaller check buttons (18px), compact badges, and narrower subtask indentation (10px instead of 24px/16px) to eliminate premature line wraps on iPhone screens.<br>• **New Compact Mode (`compact_mode`):** Card configuration toggle for maximum task density on busy dashboards.<br>• **Mindmap Mobile Cards:** Scaled note clouds in `brainstorm-mindmap-card` on mobile screens. |
| **`v1.4.35`** | 2026-10-29 | **Customizable Category Colors & Home Assistant MDI Icons:**<br>• **Category Design in Settings:** New *„Category Design (Color & Icon)“* section in Hub options flow using Home Assistant native `selector.IconSelector` (MDI icon browser & search) and visual `selector.ColorRGBSelector`.<br>• **1-Click Card Design Editor:** Quick 🎨 button on active category pills in `brainstorm-card` allows customizing colors and icons directly from dashboards with live preview.<br>• **Full Dashboard Rendering:** Category pills, note tags, and the central mindmap hub in `brainstorm-mindmap-card` seamlessly display custom icons and colors.<br>• **New Service:** `brainstorm.set_category_style` service added; `brainstorm.add_category` updated with optional `icon` and `color`. |
| **`v1.4.34`** | 2026-10-29 | **Category Options Cleanup (Deduplication of `hide_empty_categories`):**<br>• Removed redundant toggle *„Hide categories without notes (0)“* from Hub *General Settings*.<br>• The central dashboard default option is now cleanly and contextually located under *„Manage Categories“* as well as individually configurable per Lovelace card. |
| **`v1.4.33`** | 2026-10-29 | **Vibe Coding Manifesto & Badges:** Official badge and dedicated declaration celebrating passionate AI-assisted software development (*“Crafted with Pure Vibe Coding”*). |
| **`v1.4.32`** | 2026-10-29 | **Bilingual Documentation (EN/DE), Alexa Voice Capture Spotlight & 1-Click Badges:**<br>• **Full English Documentation:** Comprehensive English documentation (`README.md`) alongside German version (`README_de.md`) with country flag language switcher (`🇬🇧 English` ⇄ `🇩🇪 Deutsch`).<br>• **Alexa Voice Capture Spotlight:** Prominent hero section showcasing hands-free voice capturing, two-way dialogue, anti-music collision protection, NLP text cleaning, and Echo device origin tracking.<br>• **1-Click My Home Assistant Badges:** Direct integration via HACS repository link and Config Flow launch buttons.<br>• **Version Synchronization:** Unified release across manifest, sensor, todo platforms, and Lovelace cards. |
| **`v1.4.31`** | 2026-10-29 | **Background Rendering Fix & Synchronized Dot Grid:**<br>• **Eliminated Moiré Artifacts & Color Blocks:** Resolved visual banding in `brainstorm-mindmap-card` caused by steep radial-gradient stops and GPU compositor layers.<br>• **Subpixel Anti-Aliasing & Canvas Transparency:** Smooth dot grid transitions and clean canvas layer over `ha-card`.<br>• **Synchronized Pan & Zoom:** Background grid moves and scales naturally with the mindmap viewport.<br>• **Configurable Grid:** Added `show_grid` card toggle in the visual UI editor. |
| **`v1.4.30`** | 2026-10-29 | **Mindmap Synapses Bugfix on Category Switch:**<br>• **Eliminated Orphaned Ghost Lines:** Resolved an issue where switching categories left residual Bézier curves without node boxes. `_drawConnections` now strictly verifies active category filtering.<br>• **Clean Layout Reset:** Node positions and dragging states reset cleanly on category switch. |
| **`v1.4.29`** | 2026-10-29 | **Drag & Drop Reordering, Subtask Nesting & Apple Reminders Menu:**<br>• **Drag & Drop Sorting:** Reorder ideas in the list view smoothly via drag handles (`⠿`) with persistent storage.<br>• **Drag & Drop Subtask Nesting:** Dragging an item onto an existing task nests it directly as a subtask.<br>• **Apple Reminders Context Menu:** Long-press on mobile (~420ms) or right-click on desktop triggers haptic feedback and opens a quick menu for indenting, unindenting, moving, editing, or deleting. |
| **`v1.4.28`** | 2026-10-29 | **Hide Empty Categories Default:** Empty categories (0 notes) hidden by default in filter pills across both cards (`hide_empty_categories: true`). |
| **`v1.4.22`** | 2026-10-25 | **Priority Management:** 4 priority levels (`urgent`, `high`, `medium`, `low`), NLP urgency extraction, 1-click badge cycling, and animated flame pulse effects in mindmap. |
| **`v1.4.20`** | 2026-10-24 | **Assist LLM Function Calling:** 5 native Home Assistant LLM tools for conversational AI assistants. |
| **`v1.4.0`** | 2026-10-20 | **NLP Text Optimization:** Automatic conversational filler stripping, verb infinitizing, and spell correction. |
| **`v1.3.0`** | 2026-10-20 | **Mindmap Card Release:** Interactive radial synapse layout with category hub and idea clouds. |
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
