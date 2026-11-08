# 📘 Brainstorm Hub – Guide with Examples

🇩🇪 [Deutsche Version](anleitung.md) · ⬅️ [Back to the README](../README.md)

This guide shows with examples what you can **say**, **write**, **set** and **automate**. Installation is covered in the [README](../README.md#-installation). The examples are in English. The German phrases are in the [German guide](anleitung.md).

## Contents

1. [Say – voice commands](#1-say--voice-commands)
   - [Alexa without a skill](#11-alexa-without-a-skill)
   - [Alexa with your own skill](#12-alexa-with-your-own-skill)
   - [Home Assistant Assist](#13-home-assistant-assist)
   - [iPhone and Siri](#14-iphone-and-siri)
   - [Microphone in the card](#15-microphone-in-the-card)
   - [AI assistant (LLM)](#16-ai-assistant-llm)
2. [What Brainstorm reads from a sentence](#2-what-brainstorm-reads-from-a-sentence)
   - [Category](#21-category)
   - [Priority](#22-priority)
   - [Reminders and due dates](#23-reminders-and-due-dates)
3. [Write – using the cards](#3-write--using-the-cards)
   - [Formatting and links](#31-formatting-and-links)
   - [List card](#32-list-card)
   - [Mind map: mouse, touch, keyboard](#33-mind-map-mouse-touch-keyboard)
4. [Set](#4-set)
   - [Integration](#41-integration)
   - [List card](#42-list-card-brainstorm-card)
   - [Mind map card](#43-mind-map-card-brainstorm-mindmap-card)
5. [Automate](#5-automate)
   - [Services](#51-services)
   - [Events](#52-events)
   - [Sensor attributes](#53-sensor-attributes)
   - [Ready-made recipes](#54-ready-made-recipes)

---

## 1. Say – voice commands

The skill follows the language of your Echo, everything else the language of Home Assistant.

### 1.1 Alexa without a skill

This needs the Alexa Media integration and the automations in [`examples/`](../examples/). The setup is in the [README](../README.md#️-voice-commands).

**Dialog** ([`alexa_dialog.en.yaml`](../examples/alexa_dialog.en.yaml))

> 🗣️ "Alexa, brainstorm"
> 🤖 "Brainstorm is ready. Speak your note."
> 🗣️ "The roses in the garden need cutting."
> 🤖 "Saved under House & Garden."

**Direct, in one sentence** ([`alexa_direct_commands.en.yaml`](../examples/alexa_direct_commands.en.yaml))

| You say | Result |
|---|---|
| "Alexa, **idea** repair the sprinkler" | House & Garden |
| "Alexa, **note** dim the basement light" | Smart Home |
| "Alexa, **remember to** fertilize the tomatoes" | House & Garden |

Alexa does not know these commands, so it may answer with an error first. The skill avoids that.

### 1.2 Alexa with your own skill

With the skill Alexa answers only once. The setup is in the [README](../README.md#️-optional-your-own-alexa-skill-one-sentence-one-answer). A 🎬 [video walkthrough](video-alexa-skill.md) with one chapter per setting is available in German, the console labels on screen are in English. Start each sentence with **"Alexa, ask Brainstorm to …"**.

| Goal | Examples |
|---|---|
| Add a note | "… **note** dim the basement light", "… **idea** build a raised bed", "… **remember** to change the tires", "… **add** milk", "… **write down** printer ink" |
| Reminder | "… **remind me** tomorrow at 8 to take out the bins" |
| Complete | "… **done** take out the bins"; just "… **done**" completes the last reminder |
| Postpone | "… **later**" moves the last reminder by one hour |
| Read out | "… **read**" (overview), "… **read** daily life", "… **read everything**" |
| Show (Echo Show) | "… **show my lists**", "… **show** daily life" |
| Free sentence | "… we are out of shower gel" → Alexa says "Okay, noted", the note follows a few seconds later from the Alexa history |

> [!TIP]
> Free sentences without a command word only work on an Echo, not in the Alexa app, because the app reports no history. They need the Alexa Media integration.

### 1.3 Home Assistant Assist

The custom sentences are in [`examples/custom_sentences/en/brainstorm.yaml`](../examples/custom_sentences/en/brainstorm.yaml), the script in [`examples/intent_script.en.yaml`](../examples/intent_script.en.yaml).

| You say | Effect |
|---|---|
| "Add mow the lawn to Brainstorm" | new note |
| "New idea water the flowers" | new note |
| "Note create a database backup" | new note, category Smart Home |
| "Remember to change the tires" | new note |
| "What is in daily life in Brainstorm?" | reads the category |
| "Add milk to the Brainstorm Hub Inbox list" | note through the to-do list |
| "Check off milk on the Brainstorm Hub Inbox list" | completed |

Every category is also a to-do list (`todo.brainstorm_…`), so Assist's built-in list commands work without custom sentences.

### 1.4 iPhone and Siri

A shortcut with **Dictate Text** and the Home Assistant action `brainstorm.add_idea`:

```json
{"text": "<Dictated Text>", "source": "siri", "device": "iPhone"}
```

> 🗣️ "Hey Siri, Brainstorm" → "buy a bike lock, very urgent" → note with priority **Urgent**.

The Action button or a back tap can start it too. The steps are in the [README](../README.md#-iphone-shortcut-with-siri-action-button-or-back-tap).

### 1.5 Microphone in the card

Tap 🎙️ next to the quick input and speak. The text then appears in the field for checking. Recording ends on a pause, on another tap or after 30 seconds. It only works over HTTPS and with an Assist pipeline that has speech-to-text.

### 1.6 AI assistant (LLM)

A conversation agent such as OpenAI, Google Gemini or Ollama can use Brainstorm when you also select **Brainstorm Hub** under **Control Home Assistant** in its options. It gets these tools:

| Tool | Example |
|---|---|
| `brainstorm_add_idea` | "Write down that we need charcoal for Saturday." |
| `brainstorm_get_ideas` | "What is still on my garden list?" |
| `brainstorm_complete_idea` | "I bought the charcoal." |
| `brainstorm_delete_idea` | "Delete the note about the bike lock." |
| `brainstorm_list_categories` | "Which lists are there?" |

Under **Configure ➔ AI** you can also pick an AI service that cleans up spoken text.

---

## 2. What Brainstorm reads from a sentence

Category, leading words and `!` tags work for any text, spoken or typed. Priority words in the middle of a sentence and due dates are only read from spoken sentences. Typed text is otherwise only corrected for spelling.

### 2.1 Category

Brainstorm checks in this order:

| Rule | Example | Category |
|---|---|---|
| Prefix with a colon | "Smart Home: replace the bathroom sensor" | Smart Home |
| Square brackets | "[Daily Life] call grandma" | Daily Life |
| "Project / Topic / Area …" | "Project workshop build a shelf" | Projects |
| Starts with "for / in the …" | "for the garden buy mulch", "for daily life buy descaler" | House & Garden, Daily Life |
| Hashtag (kept as a tag) | "Scarify the lawn #garden" | House & Garden |
| Keywords in the sentence | "test the zigbee motion sensor" | Smart Home |
| otherwise | "call grandma" | default category |

Built-in keywords per category, for example:

- **House & Garden:** garden, yard, house, lawn, patio, …
- **Smart Home:** smart home, home assistant, iot, zigbee, sensor, …
- **Projects:** project, diy, workshop, crafts, …
- **Daily Life:** household, errands, chores, …
- **Brainstorm:** mindmap, …

Add your own categories under **Configure ➔ Manage Categories**. Their name then counts as a keyword too.

### 2.2 Priority

| Priority | At the start (spoken and typed) | Anywhere in a spoken sentence | Tag (anywhere) |
|---|---|---|---|
| 🔥 Urgent | "Urgent: …", "ASAP …", "Immediately …", "Top priority …" | "urgent", "very urgent", "asap", "right away", "immediately" | `!urgent` |
| 🔴 High | "Important: …", "High priority …", "Priority 1 …" | "important", "very important", "definitely" | `!high` |
| 🟡 Medium | "Normal priority …" | – | `!medium`, `!normal` |
| 🟢 Low | "Someday …", "Eventually …", "No rush, …", "Low priority …" | "someday", "eventually", "whenever there's time", "no rush" | `!low` |

Without any of these, **Medium** applies. Negations and questions do not count: *"not that urgent"* or *"is it important?"* leave the priority alone. The word found is removed from the text: *"Urgent: fix the tap"* becomes *Fix tap* with 🔥.

### 2.3 Reminders and due dates

A spoken sentence with a point in time gets a due date, for example after **"remind me (to)"**, **"don't forget (to)"** or **"remember to"**. Turn this off under **General Settings ➔ Take dates from spoken text as a due date**. A time that has already passed leaves the sentence unchanged.

| You say | Due |
|---|---|
| "… tonight" | today 19:00 |
| "… tomorrow" | tomorrow 09:00 |
| "… the day after tomorrow in the morning" | in two days 08:00 |
| "… on Friday at half past eight" | Friday 08:30 |
| "… next week" | Monday next week 09:00 |
| "… in 20 minutes", "in 2 hours", "in 3 days" | now + that time |
| "… on November 25 at 2 pm" | 25 Nov 14:00 |
| "… tomorrow afternoon" | tomorrow 15:00 |

Without any time, **9:00** applies. How and where you are reminded is set under [Reminders](#41-integration).

---

## 3. Write – using the cards

### 3.1 Formatting and links

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

### 3.2 List card

| Action | How |
|---|---|
| New note | type in the quick input, e.g. `Garden: cut the tree`, and press **Enter** |
| Preset category and priority | the 🏷️ and priority selectors below the input (*Auto* detects them from the text) |
| Edit | tap the text or the pencil; in the dialog **Ctrl+Enter** saves |
| Context menu | long press a note |
| Complete | tap the circle on the left, reactivate it in the Done tab |
| Delete | ✕ |
| Subtask | *Add a subidea*, or drag a note onto another |
| Indent and outdent | *Indent under the previous task* and *Outdent* buttons |
| Suggest subtasks | ✨ lets the AI suggest subtasks (AI under Configure) |
| Sort | hold and drag |
| Filter | category pills at the top |
| Color mode | 🌈 colorful / 🎨 theme colors in the header |
| Mind map | 🧠 in the header opens it as a layer, **Esc** closes it |

### 3.3 Mind map: mouse, touch, keyboard

**Mouse and touch**

| Action | How |
|---|---|
| Move | drag a note |
| Add a child | select a note and press **Tab** |
| Edit text | double-click a note |
| Select several | **Shift** or **Ctrl** + click, drag a frame while holding **Shift**, or tap ⬚ and drag a frame (on a phone) |
| Zoom | mouse wheel or two fingers |
| Pan | drag the empty area |
| Fold/unfold a branch | button on the branch, or **→** on a folded note |
| Save as image or outline, insert an outline | 🖼️ |
| Full screen | ⛶ |
| Search and filter | 🔍, or **/** or **Ctrl+F** on the map |
| Filter by a tag | tap a #tag in a note |
| Set markers | ✏️ Edit ➔ *Markers*; tapping a marker on a note filters by it |
| Move the progress on | tap the ring of a note without subtasks: 0 ➔ 25 ➔ 50 ➔ 75 ➔ 100 % |
| Show one branch only | 🎯 on the note or **F4**, back via the breadcrumb, **Shift+F4** or **Esc** |
| Fold and unfold levels | ∞ at the bottom right: 1 ➔ 2 ➔ 3 ➔ all, or the keys **1–9**, **0** = all |
| Link two notes | 🔗 on the note or **L**, then tap the target note; two picked notes ➔ 🔗 *Link* |
| Label or delete a link | tap the dashed line |
| Frame around notes | pick notes ➔ ▢ *Frame*, or ✏️ Edit ➔ *Frame*; tapping the frame name renames it |
| Callout | ✏️ Edit ➔ *Callout* |
| Number the subtasks | ✏️ Edit ➔ *Number the subtasks*: 1., 1.1 · a) · I. |
| Sort the subtasks | ✏️ Edit ➔ *Sort the subtasks*, or **S** (no selection: the main notes) |

**Search and filter:** 🔍 opens a bar above the map. Words you type must all appear in the title, description, result or person; `#gar` finds notes with a tag starting with *gar*. The chips filter by priority (🔥 🔴 🟡 🟢), by *Overdue* or *7 days*, by *In progress* and by the tags of the list, with their number. Notes that fit stay bright, their parents half, the rest fades. A folded branch with hits shows its button in color. **Enter** jumps to the next hit and unfolds its branch, **Shift+Enter** to the previous one, **Esc** clears the search and then closes the bar, which also clears the filter.

**Tags:** write `#garten` or `#3d-druck` anywhere in the title or description, or say *"hashtag garden"* to Alexa or Assist. A tag needs a letter, so `#1` stays a number and a color like `#ff7800` stays a color. Tags given with `tags:` in `brainstorm.add_idea` count too.

**Markers:** small signs on a note, as in MindManager: ❓ question, 💡 idea, ⚠️ warning, 💰 money, ⭐ star, 🚩 flag, ✅ check, ⛔ blocked, ⏳ waiting, ❤️ heart. Set them in the edit dialog of either card or with `markers` in `brainstorm.update_idea`. The search bar gets a chip for every marker in the list.

**Progress:** a note with subtasks shows a ring with *done/total*, such as `3/5`. The ring fills like in MindManager: subtasks that are done count 100 %, a subtask with subtasks of its own the mean of those, any other its own progress. For a note without subtasks you set the progress yourself, in quarters, in the edit dialog, by tapping the ring or with `progress` in `brainstorm.update_idea`. At 100 % the ring turns green.

**Focus and levels:** on a big map, 🎯 (or **F4**) shows only the branch of one note, and the note moves to the middle. The way there shows above the map; tap an entry to go back, ✕ shows the whole map again. New notes land under the focused note. ∞ at the bottom right folds every branch below the chosen level, the keys **1** to **9** do that directly, **0** unfolds everything again.

**Links:** the lines of the map show what belongs where. A link joins any two notes, also from different branches, with a curved, dashed arrow. 🔗 on the note (or **L**) starts it, a tap on the target ends it, **Esc** cancels. A tap on the line opens a dialog for a label such as *needs* or *see also*. Tick *blocks* and the link turns red: the target note turns grey and shows ⛔ *Waiting* until the first note is done. The badge shows in the list card too.

**Numbering and sorting:** in the edit dialog of a note with subtasks, *Number the subtasks* numbers everything below it, as in MindManager: 1., 1.1, 1.2 … or a), b) or I., II. A subtask can pick a style of its own, which then applies to its branch. The numbers show in front of the text in both cards and follow along when notes are added or moved. *Sort the subtasks* orders them right away by title (A → Z or Z → A), priority, due date or age. All other notes keep their place, and ↶ undoes it. On the map, **S** opens the same choice, without a selected note for the main notes of the category. If notes were moved by hand, 🪄 arranges the map to match afterwards.

**Export and import:** 🖼️ saves the map as a picture (SVG, PNG) or as an outline: **Markdown** (a nested list, descriptions as a `>` line), **OPML** (for outliners such as Workflowy, OmniOutliner or Logseq) and **FreeMind** (`.mm`, opens in Freeplane, XMind and MindManager). The outline holds all notes of the map, folded ones too; in focus only the branch. Under *Insert an outline* you type or paste a list, one line per note, subtasks indented or with `-`, `*`, `1.` and `#` headings. Or you choose a file (`.md`, `.txt`, `.opml`, `.mm`). `- [x]` adds the item as done. The notes go in as main notes of the category, in focus below the focused note. At most 300 notes at once, and ↶ takes them all out again. Automations can use the service `brainstorm.import_outline`.

**Frames and callouts:** a frame is a dashed, named rectangle around several notes, such as *Phase 1* or *Ground floor*. Notes with the same frame name share one frame. A callout is a short remark in a speech bubble above the note, for things like *colour still open*. The list card shows the frame as a chip and the callout below the text.

**Keyboard** (with a note selected)

| Key | Effect |
|---|---|
| **Tab** | new child |
| **Enter** | new sibling (no selection: new note) |
| **F2** | edit text |
| **Delete** / **Backspace** | delete (asks first, also for several) |
| **←** | to the parent |
| **→** | to the first child, unfolds a folded branch |
| **↑** / **↓** | to the previous / next sibling |
| **F4** / **Shift+F4** | show only this branch / go up one level |
| **1**–**9** / **0** | show levels up to 1–9 / all levels |
| **L** | draw a link to another note |
| **S** | sort the subtasks (no selection: main notes) |
| **Esc** | clear the selection, go up one level in focus, cancel linking |
| **Ctrl+Z** | undo |

In a text field: **Enter** saves, **Shift+Enter** starts a new line, **Esc** cancels.

---

## 4. Set

### 4.1 Integration

**Settings ➔ Devices & Services ➔ Brainstorm Hub ➔ Configure** opens a menu. Every field is described in the [README](../README.md#️-all-settings).

| Menu | Typical setting |
|---|---|
| **Manage Categories** | add "Holiday", rename "Projects", hide empty ones |
| **Category Design (Color & Icon)** | "Holiday" gets `mdi:beach` and orange |
| **General Settings & Export** | default category, Smart Text Optimization, dates from speech, glossary, Markdown export to `/config/brainstorm.md`, allowed Echos |
| **Alexa Voice Input & Skill** | mode *routines*, *skill* or *both*; skill code and interaction model to copy |
| **Link To-do Lists** | keep *Shopping* in sync with Todoist or Google Tasks, both ways |
| **Reminders ➔ On/Off & Channels** | announcement on the kitchen Echo, push to the phone 5 minutes later, urgent notes at once |
| **Reminders ➔ Quiet Hours, Briefing & Weekly Review** | quiet 22–7, briefing at 7:30 only when someone is home, review on Sundays at 18:00 |
| **Reminders ➔ Rules per List** | announce "Shopping" only at the store (zone), "Daily Life" on Mondays at 8 |
| **Reminders ➔ Places & Coming Home** | "don't forget screws at the hardware store" fires when you enter that zone |
| **Reminders ➔ People** | Alex's reminders go to Alex's phone and the office Echo |
| **Reminders ➔ Calendar & Alexa Reminders** | put due dates into `calendar.family`, also set a real Alexa reminder |
| **Reminders ➔ Lock times per Echo** | kids' room Echo silent 19–7, optionally with Do Not Disturb |
| **Reminders ➔ 🧪 Test channels now** | test announcement and test push |
| **AI** | let an AI service clean up spoken text |
| **Privacy & Users** | everyone sees only their own notes, share lists on purpose |
| **Assign Echos & Apps to People** | the bedroom Echo belongs to Anna |
| **🛒 Bring!** | Bring lists as main notes, items as subtasks, both ways (only with the Bring integration) |
| **🔋 Batteries** | below 20 % the task *Change battery: hallway motion sensor (18 %)*, completes itself after the change |
| **🧹 Delete done entries** | remove done notes after 30 days automatically |

### 4.2 List card (`brainstorm-card`)

Every option is also in the visual card editor.

```yaml
type: custom:brainstorm-card
title: Shopping & Ideas
default_category: Shopping   # filter when opening, "all" = all
max_items: 20                 # 0 = all
compact_mode: true
color_mode: multicolor        # or theme
show_mic: true
hide_empty_categories: true
allow_delete: false           # e.g. for a wall tablet
```

| Option | Default | Meaning |
|---|---|---|
| `title` | Brainstorm Hub | card title |
| `sensor` | `sensor.brainstorm_ideen_ubersicht` | data source |
| `color_mode` | `multicolor` | `multicolor` (color per category) or `theme` (theme colors) |
| `default_category` | `all` | filter when opening |
| `max_items` | `0` | at most this many notes (0 = all) |
| `compact_mode` | `false` | lower rows |
| `show_logo` | `true` | logo in the header |
| `show_badge` | `true` | counter in the header |
| `show_quick_input` | `true` | quick input |
| `show_mic` | `true` | 🎙️ in the input (HTTPS only) |
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

### 4.3 Mind map card (`brainstorm-mindmap-card`)

```yaml
type: custom:brainstorm-mindmap-card
map_template: sketch    # standard, clean, sketch, neon
node_shape: thought     # overrides the template
line_style: curve
color_scheme: pastel
height: 75vh
default_category: Projects
```

**Templates** set shape, lines and colors at once:

| `map_template` | Shape | Lines | Colors |
|---|---|---|---|
| `standard` | card | curved | category |
| `clean` | rectangle | angled | category |
| `sketch` | pill | dashed | pastel |
| `neon` | pill | curved | neon |

Each part can be overridden, `template` means "as the template":

- `node_shape`: `card`, `cloud`, `bubble` (speech bubble), `thought` (thought bubble), `pill`, `rect`, `ellipse`, `hexagon`, `note` (sticky note), `underline`
- `line_style`: `curve`, `straight`, `angled`, `dashed`
- `color_scheme`: `category`, `pastel`, `mono`, `neon`

A single note can get its own shape in the edit dialog or through a service (`node_shape` in `brainstorm.update_idea`).

| Option | Default | Meaning |
|---|---|---|
| `title` | Brainstorm Mindmap | title |
| `height` | `calc(100vh - 32px)` | height, e.g. `600px` or `75vh` |
| `voice_bubbles` | `true` | voice notes as speech bubbles |
| `default_category` | `all` | category in focus |
| `show_toolbar` | `true` | toolbar with filters |
| `show_logo` | `true` | logo |
| `show_bulb_watermark` | `true` | glowing bulb in the center |
| `show_grid` | `true` | dot grid |
| `show_controls` | `true` | zoom and center |
| `show_add_btn` | `true` | "+ Idea" |
| `show_export_btn` | `true` | 🖼️ save as image or outline, insert an outline |
| `show_filter` | `true` | 🔍 search and filter |
| `show_fullscreen_btn` | `true` | ⛶ full screen |
| `show_color_toggle` | `true` | 🎨/🌈 |
| `hide_empty_categories` | `true` | hide empty categories |
| `color_mode`, `sensor`, `show_last_alexa`, `last_alexa_entity` | | as in the list card |

---

## 5. Automate

### 5.1 Services

All parameters are in the [README](../README.md#️-services) and under **Developer tools ➔ Actions**.

| Service | Short example |
|---|---|
| `brainstorm.add_idea` | `text: "Replace filter"`, `category: Smart Home`, `priority: high`, `due: "2026-12-01 18:00"` |
| `brainstorm.update_idea` | `id: …`, `status: completed`, `in_progress: true`, `markers: [question, money]`, `progress: 50`, `links: [{to: …, label: needs, blocks: true}]`, `frame: Phase 1` or `callout: colour open` |
| `brainstorm.delete_idea` | `id: …` |
| `brainstorm.delete_done` | delete done notes, optionally only older ones (`older_than_days`) |
| `brainstorm.restore_idea` | bring a deleted note back |
| `brainstorm.get_ideas` | list as a response, e.g. `category: Shopping` |
| `brainstorm.get_announcement` | ready-to-read text (`speech`) |
| `brainstorm.add_category` / `remove_category` | add or remove a category |
| `brainstorm.set_category_style` | icon and color |
| `brainstorm.export_markdown` / `export_json` / `import_json` | back up and transfer |
| `brainstorm.bring_message` | message to Bring! |
| `brainstorm.reorder_ideas` | set the order |
| `brainstorm.import_outline` | add an outline: `text: …`, `category: …` or `parent_id: …`, `format: auto` |
| `brainstorm.sort_children` | sort subtasks: `parent_id: …`, `by: text`, `priority`, `due` or `created` |
| `brainstorm.share` | share a list with people |

With `parse_due: true`, `add_idea` reads a point in time from the text like speech does:

```yaml
action: brainstorm.add_idea
data:
  text: "Remind me tomorrow at 8 to take out the bins"
  parse_due: true
```

### 5.2 Events

| Event | When |
|---|---|
| `brainstorm_idea_added` | new note |
| `brainstorm_idea_updated` | note changed |
| `brainstorm_idea_completed` | note completed |
| `brainstorm_idea_deleted` | note deleted |
| `brainstorm_reminder_due` | a reminder is due |

The event data holds the whole note (`id`, `text`, `category`, `priority`, `source`, …):

```yaml
triggers:
  - trigger: event
    event_type: brainstorm_idea_added
    event_data:
      priority: urgent
actions:
  - action: light.turn_on
    target:
      entity_id: light.hallway
    data:
      color_name: red
```

### 5.3 Sensor attributes

`sensor.brainstorm_ideen_ubersicht` counts open notes. Its attributes include all notes, the categories, `allowed_echos` and `voice_mode`.

```yaml
{{ state_attr('sensor.brainstorm_ideen_ubersicht', 'ideas')
   | selectattr('category', 'eq', 'Shopping') | list | count }}
```

### 5.4 Ready-made recipes

**Read out open notes in the morning**

```yaml
triggers:
  - trigger: time
    at: "07:30:00"
actions:
  - action: brainstorm.get_announcement
    response_variable: overview
  - action: notify.alexa_media
    data:
      target: media_player.echo_kitchen
      data:
        type: announce
      message: "{{ overview.speech }}"
```

**A note when the washing machine is done**

```yaml
triggers:
  - trigger: state
    entity_id: binary_sensor.washing_machine_running
    to: "off"
actions:
  - action: brainstorm.add_idea
    data:
      text: Hang up the laundry
      category: Daily Life
      priority: high
```

**Clean up done notes every Sunday**

```yaml
triggers:
  - trigger: time
    at: "03:00:00"
conditions:
  - condition: time
    weekday: sun
actions:
  - action: brainstorm.delete_done
    data:
      older_than_days: 14
```

More templates for Alexa and Assist are in [`examples/`](../examples/).
