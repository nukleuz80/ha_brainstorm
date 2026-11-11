🏠 [Home](Home) · 🇩🇪 [Deutsche Version](Listenkarte)

## List View (`brainstorm-card`)
```yaml
type: custom:brainstorm-card
title: Brainstorm Hub
sensor: sensor.brainstorm_ideen_ubersicht
color_mode: multicolor
hide_empty_categories: true
show_quick_input: true
show_categories: true
```

## Your Own Sidebar Dashboard

Brainstorm also works as its own entry in the Home Assistant sidebar, for example under the path `/brainstorm-hub`, with three views: the mindmap above the list, the mindmap as a full-screen panel, and the list alone for fast typing and touch input.

`sensor.brainstorm_ideen_ubersicht` is the fixed entity ID in every language, so cards and automations keep working.

## ✨ Features at a glance

- 🎯 **Intelligent Priority Management & Visual Urgency Levels:**
  - **4 Priority Levels:** `low` (🟢 Low), `medium` (🟡 Medium / Default), `high` (🔴 High), and `urgent` (🔥 Urgent).
  - **Natural Language Urgency Detection:** Recognizes priority words in spoken or typed notes (e.g. *“Urgent garden: repair lawnmower”*, *“Priority 1…”*) and the tags *“!urgent”*, *“!high”* and *“!low”*, cleans the text, and sets the priority automatically.
  - **1-Click Priority Cycling:** Cycle priorities directly (`Medium` ➔ `High` ➔ `Urgent` ➔ `Low`) by clicking the priority badge in either the list or mindmap view.
  - **Visual Mindmap Pulse Effects:** Urgent idea nodes pulse with an animated flame effect (`cloud-urgent`), while high-priority notes glow with a warm highlight.
- **Intuitive Reordering:** Reorder items in the list view smoothly via drag handle (`⠿`). Order is preserved persistently via `brainstorm.reorder_ideas`.
- **Drag & Drop Subtasks:** Drag a note onto another note to instantly nest it as a subtask.
- **New subtask with 🌿:** 🌿 on a main task, or in its long-press menu, adds a subtask right under it, in the same category (v1.6.29).
- **Attachments (v1.7.9):** 📎 in the edit dialog of both cards attaches screenshots, photos, PDFs, logs and other files to a note, up to 10 MB each and 20 per note. On a computer, paste a screenshot with Ctrl+V or drop files onto the dialog; on a phone the button offers the camera and the gallery. The list shows 📎 and the number; a tap shows the files, images as thumbnails, and opens them. Attachments of a note that is done (or archived) are deleted after 30 days, and reopening it keeps them. The files live in `/config/brainstorm_attachments/` and are only served to people who may see the note. Allowed: images, PDF, TXT/LOG/MD, CSV, JSON, YAML, ZIP.
- **Delete done entries (v1.7.13):** Settings › 🧹 Delete done entries deletes done (ticked off or archived) entries after a number of days by themselves, checked every six hours, and has a switch to delete all of them right away. Their attachments go with them. Off (0 days) by default. Action: `brainstorm.delete_done`.
- **Title and description (v1.7.8):** ✎ edits the title and, below it, an optional description for details, links or notes. The list shows up to three lines of it under the title; tapping it shows the rest. The mind map's edit dialog has it too, and the to-do lists of Home Assistant show and edit it as the item's description. Actions: `description` in `brainstorm.add_idea` and `brainstorm.update_idea` (empty removes it).
- **Search in the list (v1.8.11):** the 🔍 field above the list filters while you type, in the title, description, result and person, ignoring case and accents. `#tag` finds tags. A found subtask keeps its parent visible in grey, a found main task shows its subtasks. ✕ or Esc clears it; `show_search: false` hides the field.
- **Fold subtasks (v1.7.4):** A main task with subtasks shows ▾ and their number. Tap it to fold them away; ▸ unfolds them again. Handy for long Bring lists. Each browser remembers what is folded, per card.
- **Apple Reminders Context Menu:** Long-press on mobile (~420ms) or right-click on desktop triggers haptic feedback and opens a quick menu for indenting, unindenting, moving, editing, or deleting.
- 🎴 **Quick Capture Card (`custom:brainstorm-card`):**
  - Two-tiered sleek design with quick-input bar, priority selector, category pills, and full edit/delete modal dialogs.
  - View switcher (`🧠 Mindmap` ⇄ `📋 List`) in card header.
  - Automatically hides empty categories (`hide_empty_categories: true`) to keep dashboards clutter-free.
- 🔗 **Links and a little Markdown in notes (both cards):**
  - Web addresses become clickable, and so does `[text](https://…)`. `**bold**`, `*italic*`, `~~struck out~~` and `` `code` `` are shown formatted, in the note and in its result note.
  - Safe by design: everything else is shown as plain text, HTML in a note is never run, and links only go to `http`, `https` and `mailto` addresses. They open in a new tab, and a click on a link does not open the editor.

## Formatting and links

Every note supports a little Markdown:

| You write | Result |
|---|---|
| `**milk**` | **milk** |
| `*soon*` | *soon* |
| `~~done~~` | ~~done~~ |
| `` `sensor.bath` `` | `sensor.bath` |
| `[Manual](https://example.com)` | clickable link |
| `https://example.com` | becomes a link by itself |

With **Smart Text Optimization** (General Settings) spoken notes are tidied up as well: filler words go, the start is capitalized. The **glossary** holds your own terms, one per line (`Lenia`), or corrections (`wrong = Right`). Names of people and categories are known automatically.

## List card

| Action | How |
|---|---|
| New note | type in the quick input, e.g. `Garden: cut the tree`, and press **Enter** |
| Preset category and priority | the 🏷️ and priority selectors below the input (*Auto* detects them from the text) |
| Edit | tap the text or the pencil; in the dialog **Ctrl+Enter** saves |
| Context menu | long press a note or tap ⋯ on the right of the row |
| React | 👍 ❤️ 😂 ❗ at the top of the context menu, or tap a reaction already on the note |
| Comment | context menu ➔ 💬 *Comments*, or tap 💬 on the note; **Ctrl+Enter** sends, `@Name` tells that person |
| Vote | in a running vote, − / + on the note |
| Buttons of a row | on phones and narrow cards under ⋯ (indent, subidea, AI, edit, delete), with a mouse they appear on hover; `row_actions` changes this |
| Fold subtasks | tap the ▾ 0/2 badge next to the priority |
| Complete | tap the circle on the left, reactivate it in the Done tab |
| Delete | ✕ |
| Subtask | *Add a subidea*, or drag a note onto another |
| Indent and outdent | *Indent under the previous task* and *Outdent* buttons |
| Suggest subtasks | ✨ lets the AI suggest subtasks (AI under Configure) |
| Sort | hold and drag |
| Search | 🔍 field above the list: words search title, description, result and person, `#tag` a tag; ✕ or **Esc** clears it |
| Filter | category pills at the top |
| Color mode | 🌈 colorful / 🎨 theme colors in the header |
| Mind map | 🧠 in the header opens it as a layer, **Esc** closes it |

## ⚙️ Card options (`brainstorm-card`)

Every option is also in the visual card editor.

```yaml
type: custom:brainstorm-card
title: Shopping & Ideas
default_category: Shopping   # filter when opening, "all" = all
max_items: 20                 # 0 = all
compact_mode: true
color_mode: multicolor        # or theme
show_mic: true
show_search: true
hide_empty_categories: true
allow_delete: false           # e.g. for a wall tablet
```

| Option | Default | Meaning |
|---|---|---|
| `title` | Brainstorm Hub | card title |
| `sensor` | `sensor.brainstorm_ideen_ubersicht` | data source |
| `level` | as in the settings | operating level of this card only: `beginner`, `normal` or `pro`, see [4.0](Settings#operating-level) |
| `color_mode` | `multicolor` | `multicolor` (color per category) or `theme` (theme colors) |
| `default_category` | `all` | filter when opening |
| `max_items` | `0` | at most this many notes (0 = all) |
| `compact_mode` | `false` | lower rows |
| `row_actions` | `auto` | buttons in the rows: `auto` (⋯ on phones, on hover with a mouse), `inline` (always all) or `menu` (always only ⋯) |
| `show_logo` | `true` | logo in the header |
| `show_badge` | `true` | counter in the header |
| `show_quick_input` | `true` | quick input |
| `show_mic` | `true` | 🎙️ in the input (HTTPS only) |
| `show_search` | `true` | 🔍 search field above the list |
| `show_categories` | `true` | category pills |
| `hide_empty_categories` | `true` | hide empty categories |
| `show_mindmap_button` | `true` | 🧠 in the header |
| `show_color_toggle` | `true` | 🎨/🌈 in the header |
| `show_source_icons` | `true` | source (Alexa, Assist, phone …) |
| `show_timestamps` | `true` | "5 min ago" |
| `allow_edit` | `true` | editing allowed |
| `allow_delete` | `true` | deleting allowed |
| `show_last_alexa` | `false` | show the last active Echo |
| `last_alexa_entity` | `sensor.last_alexa` | entity for it |
