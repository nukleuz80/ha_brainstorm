🏠 [Home](Home) · 🇩🇪 [Deutsche Version](Import-Export-und-Speicherung)

## 💾 Features

- 📝 **Markdown Synchronization:**
  - Auto-export to structured markdown files with YAML frontmatter, timestamps, and priority tags.
  - Plug-and-play with **Obsidian**, **Logseq**, or **Nextcloud Notes**.
- 🛠️ **Home Assistant To-do Platform:**
  - Synchronizes all active categories as native Home Assistant To-do entities (`todo.brainstorm_hub_*`).
- 🔁 **Linked to-do lists (v1.6.31):**
  - Link a category to a to-do list of another integration, such as **Bring!**, **Google Tasks**, **Todoist** or a local to-do list. New entries, renames and ticks travel both ways, so *Einkauf* in Brainstorm and your shopping app stay the same. See *Configure ➔ Link To-do Lists*.
- 🛒 **Native Bring! support (v1.7.0):**
  - Switch on Bring! under *Configure ➔ 🛒 Bring!*, pick or create a category, done. Every Bring list becomes a main note, its items become subtasks. Notes without a list go to your default list, moving a subtask moves the item, and the Bring specification shows as a note. Renames, ticks and new items travel both ways.
- 💾 **JSON export and import (v1.6.31):**
  - `brainstorm.export_json` returns your ideas with categories, icons and colors as JSON, optionally into a file. `brainstorm.import_json` brings them back, on the same or another Home Assistant, and skips what exists already.

## 🗄️ Where the data lives

| What | Where |
| :--- | :--- |
| Ideas, categories, drawings, pinboard | `/config/.storage/brainstorm.storage` |
| Alexa skill link | `/config/.storage/brainstorm.alexa_skill` |
| Reminder state | `/config/.storage/brainstorm.reminders` |
| Attachments | `/config/brainstorm_attachments/` |
| Markdown export | Default `/config/brainstorm/`, configurable |

Everything stays local in your Home Assistant and is part of every normal backup. Do not edit the files in `.storage` by hand while Home Assistant runs; use the cards or the [services](Services-and-Events) instead. How the data updates is described under [Entities & Attributes](Entities-and-Attributes#-how-the-data-updates).

## 🔁 Back up and move

- **As JSON:** [`brainstorm.export_json`](Services-and-Events#brainstormexport_json) returns everything with categories, icons, colors, pinboard places and drawings, optionally into a file. [`brainstorm.import_json`](Services-and-Events#brainstormimport_json) brings it back, on the same or another Home Assistant, and skips what is already there. Comments, reactions and votes stay out.
- **As Markdown:** [`brainstorm.export_markdown`](Services-and-Events#brainstormexport_markdown) or the automatic export under *Configure ➔ General Settings & Export*.
- **From the mind map:** 🖼️ saves SVG, PNG, PDF, a Markdown outline, OPML or FreeMind (`.mm`); *Insert an outline* reads `.md`, `.txt`, `.opml` and `.mm` back in. See [Mind Map & Pinboard](Mind-Map-and-Pinboard).
- **Deleted?** Home Assistant keeps deleted notes until the next restart: ↶ in the card or [`brainstorm.restore_idea`](Services-and-Events#brainstormrestore_idea).
