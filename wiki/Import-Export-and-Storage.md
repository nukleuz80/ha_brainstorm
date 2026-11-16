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

## 📥 Bring in from Trello, Todoist and Miro (v1.13.21)

In the mind map under 🖼️ ➔ *Insert an outline* ➔ *📂 Choose file*. The notes go into the chosen category, in focus below the focused note; ↶ takes them all out again. At most 300 notes at once.

| Source | How to export | What it becomes |
| :--- | :--- | :--- |
| **Trello** | Board menu ➔ *Print, export and share* ➔ *Export as JSON* | Lists become main notes, cards notes below them, checklist items subtasks. Description, due date and done (the tick on the due date or the checklist item) come along; archived items stay out. The card shrinks big exports to what is needed first. |
| **Todoist** | Project ➔ ⋯ ➔ *Export as template* ➔ *Export as file* (CSV) | Sections become main notes, tasks with their indents notes below. Priority p1 ➔ urgent, p2 ➔ high, p3 ➔ medium; a fixed date becomes the due date (09:00 without a time), recurring ones such as "every day" are dropped; comments go into the description. |
| **Miro, Excel and other tables** | save as CSV | With columns such as *Title/Name/Text*, *Description*, *List/Column/Section*, *Due/Date*, *Priority*, *Done* and *Level*, each row becomes a note, grouped by list. Without such columns (a Miro board as CSV, say) each column becomes a branch with its cells. Comma, semicolon and tab all work. |

For automations: `brainstorm.import_outline` with `format: trello` or `format: csv`, see [Services and Events](Services-and-Events).

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
- **From the mind map:** 🖼️ saves SVG, PNG, PDF, a Markdown outline, OPML or FreeMind (`.mm`); *Insert an outline* reads `.md`, `.txt`, `.opml` and `.mm` back in, since v1.13.21 also Trello boards (`.json`) and CSV from Todoist, Miro or Excel (see below). See [Mind Map & Pinboard](Mind-Map-and-Pinboard).
- **Deleted?** Deleted notes stay in the **🗑️ trash** for 30 days (v1.11.12), also across a restart: in the list card through *🗑️ Trash* above the list, in the mind map through 🗑️ at the bottom right. There you bring single notes back (↩️, with their subitems), delete them for good (✕) or empty the trash. After that they are gone with their attachments. With privacy, everyone only sees what they deleted themselves or may edit. Done notes removed by *🧹 Delete done entries* do not go to the trash. For automations there is [`brainstorm.restore_idea`](Services-and-Events#brainstormrestore_idea).
