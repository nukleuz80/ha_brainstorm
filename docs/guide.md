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
   - [Operating level](#40-operating-level)
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

**Same dialog everywhere:** the edit dialog of the list and of the mind map has the same fields in the same order, so callout, frame, shape, numbering and sorting can be set from the list as well, and the parent task from the mind map.

**Repeating:** *Repeat* in the edit dialog lets a note come back every day, weekday, week, 2 weeks, month or year. When you tick it off, the next round appears at once with the next due date and its subtasks open again; the done one stays under *Done*. Ticked off late, it skips the dates that passed. Reopening the done one removes the new round while it is still open. 🔁 marks such notes.

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
| Context menu | long press a note or tap ⋯ on the right of the row |
| React | 👍 ❤️ 😂 ❗ at the top of the context menu, or tap a reaction already on the note |
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
| Vote | 🗳️ at the bottom right or **V**: pick the category, votes per person and *hidden*, then − / + on the notes; *End* in the bar at the top shows the ranking |
| React | ⋯ on the note ➔ 👍 ❤️ 😂 ❗; tapping a reaction toggles yours |
| Overview (minimap) | 🗺️ at the bottom right or **M**; tap or drag in the overview at the bottom left to jump there |
| Link two notes | 🔗 on the note or **L**, then tap the target note; two picked notes ➔ 🔗 *Link* |
| Label or delete a link | tap the dashed line |
| Frame around notes | pick notes ➔ ▢ *Frame*, or ✏️ Edit ➔ *Frame*; tapping the frame name renames it |
| Callout | ✏️ Edit ➔ *Callout* |
| Brainstorm: collect many ideas fast | ⚡ at the bottom right or **B** |
| Tree, org chart, outline, Kanban, timeline or Eisenhower matrix | view button above ⚡ |
| Number the subtasks | ✏️ Edit ➔ *Number the subtasks*: 1., 1.1 · a) · I. |
| Sort the subtasks | ✏️ Edit ➔ *Sort the subtasks*, or **S** (no selection: the main notes) |

**Pictures:** the first picture among the attachments of a note shows inside the note. A tap opens it in full size. Add one with 📎 in the edit dialog, or paste or drop it there.

**Rules:** set a filter in the search bar, then 🎨 (or **R**) ➔ *Current filter as a rule*. Give it a name, one of nine colors and a sign. Every note that fits gets the color and the sign, in the map and in the list card; when several rules fit, the upper one wins. In the rule list, the box switches a rule on or off, ↑ moves it up, ✎ edits it and 🗑️ deletes it (↶ brings it back). Rules belong to your Home Assistant user and follow you to every device.

**Search and filter:** 🔍 opens a bar above the map. Words you type must all appear in the title, description, result or person; `#gar` finds notes with a tag starting with *gar*. The chips filter by priority (🔥 🔴 🟡 🟢), by *Overdue* or *7 days*, by *In progress* and by the tags of the list, with their number. Notes that fit stay bright, their parents half, the rest fades. A folded branch with hits shows its button in color. **Enter** jumps to the next hit and unfolds its branch, **Shift+Enter** to the previous one, **Esc** clears the search and then closes the bar, which also clears the filter.

**Tags:** write `#garten` or `#3d-druck` anywhere in the title or description, or say *"hashtag garden"* to Alexa or Assist. A tag needs a letter, so `#1` stays a number and a color like `#ff7800` stays a color. Tags given with `tags:` in `brainstorm.add_idea` count too.

**Markers:** small signs on a note, as in MindManager: ❓ question, 💡 idea, ⚠️ warning, 💰 money, ⭐ star, 🚩 flag, ✅ check, ⛔ blocked, ⏳ waiting, ❤️ heart. Set them in the edit dialog of either card or with `markers` in `brainstorm.update_idea`. The search bar gets a chip for every marker in the list.

**Progress:** a note with subtasks shows a ring with *done/total*, such as `3/5`. The ring fills like in MindManager: subtasks that are done count 100 %, a subtask with subtasks of its own the mean of those, any other its own progress. For a note without subtasks you set the progress yourself, in quarters, in the edit dialog, by tapping the ring or with `progress` in `brainstorm.update_idea`. At 100 % the ring turns green.

**Focus and levels:** on a big map, 🎯 (or **F4**) shows only the branch of one note, and the note moves to the middle. The way there shows above the map; tap an entry to go back, ✕ shows the whole map again. New notes land under the focused note. ∞ at the bottom right folds every branch below the chosen level, the keys **1** to **9** do that directly, **0** unfolds everything again.

**Links:** the lines of the map show what belongs where. A link joins any two notes, also from different branches, with a curved, dashed arrow. 🔗 on the note (or **L**) starts it, a tap on the target ends it, **Esc** cancels. A tap on the line opens a dialog for a label such as *needs* or *see also*. Tick *blocks* and the link turns red: the target note turns grey and shows ⛔ *Waiting* until the first note is done. The badge shows in the list card too.

**Numbering and sorting:** in the edit dialog of a note with subtasks, *Number the subtasks* numbers everything below it, as in MindManager: 1., 1.1, 1.2 … or a), b) or I., II. A subtask can pick a style of its own, which then applies to its branch. The numbers show in front of the text in both cards and follow along when notes are added or moved. *Sort the subtasks* orders them right away by title (A → Z or Z → A), priority, due date or age. All other notes keep their place, and ↶ undoes it. On the map, **S** opens the same choice, without a selected note for the main notes of the category. If notes were moved by hand, 🪄 arranges the map to match afterwards.

**Brainstorm mode:** ⚡ at the bottom right (or **B**) opens a big input with a timer: 3, 5, 10 or 15 minutes or no time limit. The clock starts with the first idea. **Enter** saves each idea as a note right away, the field is free again, and the idea shows as a coloured slip below. ✕ on a slip deletes it again. Ideas go into the chosen category, in focus below the focused note, under *All* into the matching category. After *Done*, ↶ takes all collected ideas out at once and 🪄 arranges the map. Then drag them into branches.

**Layouts:** the button above ⚡ opens the choice of views: ◎ around the center, ⇶ a tree to the right (main notes in one column, subtasks to their right), ⊤ an org chart downwards and ☰ an outline (one note per row, subtasks indented below their parent). In the tree and the org chart a parent sits in the middle of its subtasks and the lines run at right angles. The choice stays in this browser; the card option `layout` sets the default. Dragged notes stay where you put them until you switch the layout again.

**Boards:** three more views show the notes in columns instead of a map. **▥ Kanban** sorts by state: *Open*, *In progress*, *Waiting* (a blocking link) and *Done*. Drag a note to *In progress* to mark it, back to *Open* to unmark it, onto *Done* to tick it off. **📅 Timeline** sorts by due date: *Overdue*, *Today*, *Tomorrow*, *This week*, *Later*, *No date*. Dragging sets the date and keeps the time (09:00 for a note without one); *No date* removes it. **⊞ Eisenhower matrix** sorts by importance (priority 🔥 or 🔴) and urgency (🔥 or due within three days): *Do now*, *Schedule*, *Delegate*, *Later or never*. Dragging sets the priority; *Delegate* gives a note without a near date one for tomorrow. Columns that follow from something else (*Waiting*, *Overdue*, a near date) cannot be reached by dragging; a short note says why. ↶ takes every move back.

**Presentation:** **P** (or ▶ *Present* in the view choice) turns the map into a slide show. It opens full screen without buttons, first with the whole map, then note by note in branch order. The view zooms to the note, its parent and subtasks stay half visible, and a bar at the bottom shows the path, the title and the description. **→**, **space** or **Enter** go on, **←** back, **Home** to the overview, **Esc** ends. Folded branches open on the way and fold again at the end. It works in every view, also in focus.

**AI help:** with an AI task entity (Brainstorm Hub ➔ Configure ➔ AI), ✨ on a note suggests subtasks. On a note with subtasks, ✨ asks first: *Suggest subtasks* or *Summarize the branch*. The summary covers the note and everything below it, done items included, in two to four sentences; edit it, copy it or put it in front of the description. **Z** (or *✨ Sort in loose ideas* at the end of a brainstorm round) looks at the main notes of the category that have no subtasks and suggests where each belongs. Untick what should stay, *Apply* moves the rest; ↶ moves them back. Only the notes of this category go to the AI. **G** (or ✨ *Create map from a topic* on an empty map, ✨ *Create with AI* under 🖼️ ➔ *Insert an outline*) turns a topic or a pasted text into a map with up to three levels; tick and edit in the preview, then add. Unticking a line moves its points up.

**Export and import:** 🖼️ saves the map as a picture (SVG, PNG), as a **PDF** (the picture of the map on the first page, then all notes as an outline with descriptions; *PDF (outline only)* without the picture; emojis are left out) or as an outline: **Markdown** (a nested list, descriptions as a `>` line), **OPML** (for outliners such as Workflowy, OmniOutliner or Logseq) and **FreeMind** (`.mm`, opens in Freeplane, XMind and MindManager). The outline holds all notes of the map, folded ones too; in focus only the branch. Under *Insert an outline* you type or paste a list, one line per note, subtasks indented or with `-`, `*`, `1.` and `#` headings. Or you choose a file (`.md`, `.txt`, `.opml`, `.mm`). `- [x]` adds the item as done. The notes go in as main notes of the category, in focus below the focused note. At most 300 notes at once, and ↶ takes them all out again. **Content templates:** above the text field are ready branches: SWOT analysis, pros and cons, project plan, week plan, party, trip (with packing list), retrospective and room renovation. A tap writes the template into the field; change or add lines, then *Insert*. Automations can use the service `brainstorm.import_outline`.

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
| **B** | brainstorm mode |
| **S** | sort the subtasks (no selection: main notes) |
| **Z** | AI: sort in loose ideas |
| **G** | AI: create a map from a topic or text |
| **R** | rules: color notes that fit a saved filter |
| **M** | overview (minimap) on/off |
| **V** | start or end a vote |
| **P** | presentation mode |
| **Esc** | clear the selection, go up one level in focus, cancel linking |
| **Ctrl+Z** | undo |

In a text field: **Enter** saves, **Shift+Enter** starts a new line, **Esc** cancels.

---

## 4. Set

### 4.0 Operating level

Under **Configure ➔ General Settings & Export ➔ Operating level** you choose how much Brainstorm shows. The level applies to everyone, to both cards and to the configure menu. New installations start with *Normal*, existing ones keep *Pro*, so everything stays as before.

| Level | List card and edit dialog | Mind map | Configure menu |
|---|---|---|---|
| **Beginner** | input, microphone, categories, ticking off, search; in the dialog title, description, category, priority and due date | only *Around the center*, New idea, zoom, full screen | without batteries, lock times, rules per list, Echos & apps and AI text cleanup |
| **Normal** | also subtasks, multi-select, markers, repeating, attachments, sharing, AI suggestions | also *Tree*, *Outline*, *Kanban*, focus, levels, search and filter, multi-select, export as picture, PDF and Markdown | like Beginner |
| **Pro** | everything: progress, numbering and sorting, callout, frame, shape, remind on Echos, original text, "in progress" | everything: *Org chart*, *Timeline*, *Matrix*, rules, cross links, frames, brainstorm and presentation mode, OPML/FreeMind, summing up a branch, all shortcuts | everything |

Hiding deletes nothing: markers, progress or frames that are set stay visible on the cards. In the edit dialog **More fields …** brings the hidden fields back. Each card can have its own level with `level: beginner`, `normal` or `pro`, for example a kitchen tablet that always shows *Beginner*.

### 4.1 Integration

[**Settings ➔ Devices & Services ➔ Brainstorm Hub ➔ Configure**](https://my.home-assistant.io/redirect/integration/?domain=brainstorm) opens a menu. Every field is described in the [README](../README.md#️-all-settings).

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
show_search: true
hide_empty_categories: true
allow_delete: false           # e.g. for a wall tablet
```

| Option | Default | Meaning |
|---|---|---|
| `title` | Brainstorm Hub | card title |
| `sensor` | `sensor.brainstorm_ideen_ubersicht` | data source |
| `level` | as in the settings | operating level of this card only: `beginner`, `normal` or `pro`, see [4.0](#40-operating-level) |
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

### 4.3 Mind map card (`brainstorm-mindmap-card`)

```yaml
type: custom:brainstorm-mindmap-card
map_template: sketch    # standard, clean, sketch, neon
layout: kanban          # radial, tree, org, outline, kanban, timeline, matrix
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
| `level` | as in the settings | operating level of this card only, see [4.0](#40-operating-level) |
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
| `show_images` | `true` | first picture attachment inside the note |
| `show_minimap` | `true` | overview (minimap) and its button 🗺️ |
| `show_fullscreen_btn` | `true` | ⛶ full screen |
| `show_color_toggle` | `true` | 🎨/🌈 |
| `hide_empty_categories` | `true` | hide empty categories |
| `color_mode`, `sensor`, `show_last_alexa`, `last_alexa_entity` | | as in the list card |

---

## 5. Automate

### 5.1 Services

All parameters are in the [README](../README.md#️-services) and under [**Developer tools ➔ Actions**](https://my.home-assistant.io/redirect/tools_actions/).

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
| `brainstorm.sort_children` | sort subtasks: `parent_id: …`, `by: text`, `priority`, `due`, `created` or `votes` |
| `brainstorm.react` | toggle a reaction: `id: …`, `reaction: heart` |
| `brainstorm.start_voting` / `vote` / `end_voting` | voting: `category: Holiday`, `votes: 5`, `hidden: true`; `vote` with `id`, `delta`; `end_voting` responds with the ranking |
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

`sensor.brainstorm_ideen_ubersicht` counts open notes. Its attributes include all notes, the categories, `allowed_echos`, `voice_mode` and `ui_level` (operating level).

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
