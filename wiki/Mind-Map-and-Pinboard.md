🏠 [Home](Home) · 🇩🇪 [Deutsche Version](Mindmap-und-Pinnwand)

## Mindmap View (`brainstorm-mindmap-card`)
```yaml
type: custom:brainstorm-mindmap-card
title: Brainstorm Mindmap
sensor: sensor.brainstorm_ideen_ubersicht
color_mode: multicolor
height: 650px
show_grid: true
show_bulb_watermark: true
hide_empty_categories: true
map_template: standard
show_export_btn: true
```

**Looks with templates:** Pick a template in the card editor and change shape, lines or colors on their own if you like. `template` means: as in the template.

| Option | Values | Meaning |
| :--- | :--- | :--- |
| `layout` | `radial`, `tree`, `org`, `outline`, `pin`, `kanban`, `timeline`, `matrix` | View of the notes: around the center, tree, org chart, outline, pinboard, Kanban by state, timeline by due date or Eisenhower matrix. The button at the bottom right switches it too and remembers the choice in the browser. Default `radial`. |
| `map_template` | `standard`, `clean`, `sketch`, `neon` | **Standard:** cards, curves, category colors. **Clean:** rectangles, angled lines. **Sketch:** pills, dashed, pastel. **Neon:** dark background with glowing edges. |
| `node_shape` | `template`, `card`, `cloud`, `bubble`, `thought`, `pill`, `rect`, `ellipse`, `hexagon`, `note`, `underline` | Shape of the notes: card, cloud, speech bubble, thought bubble, pill, rectangle, ellipse, hexagon, note slip or underlined text. The tail of the speech bubble and the puffs of the thought bubble point to the parent note or to the center; the lines meet an underlined note at the end of its underline. A note can have its own shape (edit dialog or `shape` of `brainstorm.update_idea`). |
| `voice_bubbles` | `true`, `false` | Notes said to Alexa, Siri or Assist show as speech bubbles, unless they have their own shape. Default `true`. |
| `line_style` | `template`, `curve`, `straight`, `angled`, `dashed` | Lines: curve, straight, angled or dashed. |
| `color_scheme` | `template`, `category`, `pastel`, `mono`, `neon` | Colors: category colors, pastel (softly tinted), single color or neon. |

Click `⛶` at the top right to enlarge the mindmap to the full screen.

## ✨ Features at a glance

- Interactive radial synapse layout with glowing central category hub and floating idea clouds.
- Smooth pan & zoom with synchronized background dot grid and canvas transparency.
- Instant category filtering without ghost lines or orphaned connections.
- **Branches:** Subtasks hang on their parent idea, and their lines start there instead of at the center. 🌿 on a note adds a subidea.
- **Saved layout:** In a single list, notes you drag keep their place on every device. A parent takes its subtasks along. The overview of all lists arranges itself.
- **Fold branches:** The round button on a note with subtasks folds its branch and shows how many notes it hides. Each device remembers what is folded.
- **Tree layout:** Every branch gets its own slice of the circle, so lines do not cross. 🪄 puts notes placed by hand back to their automatic place.
- **Keyboard:** A click selects a note. **Tab** adds a subtask, **Enter** a note beside it, **Delete** removes it after asking, **F2** or a double click edits the text. The arrow keys walk along the branches: left to the parent, right to the first subtask, up and down to the neighbours.
- **Edit in place:** A click on the text opens it right in the cloud. **Enter** saves, **Shift+Enter** adds a line, **Esc** cancels. Due date, priority and Echos stay in the dialog behind ✏️.
- **Pick several notes:** **Shift+drag** on the empty map draws a frame, **Shift+click** or **Ctrl+click** adds a note or takes it out again. On a phone or tablet, tap ⬚ at the bottom right, then drag a frame or tap notes. Dragging one picked note moves all of them, with their subtasks. The bar above the map ticks them off, moves them to another category or deletes them after asking, and one undo takes back the whole step. **Esc** or ✕ clears the selection.
- **Undo:** **Ctrl+Z** or the ↶ button at the bottom right takes back the last steps of this session: new notes, text changes, done, priority, category, moving, arranging again and deleting too. Home Assistant keeps deleted notes until its next restart.
- **Search, filter and tags (v1.8.0):** 🔍 at the top right, or **/** and **Ctrl+F** on the map, opens a search bar. Hits stay bright, their parents half, the rest of the map fades. Chips filter by priority, *Overdue*, *7 days*, *In progress* and the tags of the list. **Enter** jumps from hit to hit and unfolds its branch. Write `#garten` in a note or say *"hashtag garden"* and the tag shows as a chip; a tap on it filters the map. See [Mouse, touch, keyboard](#mind-map-mouse-touch-keyboard).
- **Repeating tasks (v1.8.15):** *Repeat* in the edit dialog of both cards: every day, every weekday, every week, every 2 weeks, every month or every year. Tick the note off and it comes back right away, due at the next date, with its details and its subtasks open again; the done round stays under *Done*. Ticked off late, it skips the dates that passed. Reopening the done round takes the new one back. Notes that repeat show 🔁. Action: `repeat` in `brainstorm.update_idea`.
- **PDF export (v1.8.14):** 🖼️ ➔ *PDF* saves a PDF with the picture of the map on the first page and all notes as an outline with their descriptions after it, ready to print or send. *PDF (outline only)* leaves out the picture. Made in the browser, nothing leaves Home Assistant.
- **Pictures in notes (v1.8.13):** the first picture attached to a note (📎 in the edit dialog, also pasted or dropped) shows right inside it on the map, so a mood board or a sketch is visible at a glance. A tap opens it in full size. `show_images: false` turns it off.
- **Rules (v1.8.12):** 🎨 in the search bar, or **R**, turns the current filter into a rule with a color and a sign, like SmartRules in MindManager: *everything 🔥 urgent red*, *#garden green with ⭐*… Every fitting note is painted in the map and in the list card, the first rule that fits wins. Rules can be switched off, moved up, edited and deleted (↶ brings one back). They are stored with your Home Assistant user, so they follow you to every device.
- **Markers and progress (v1.8.1):** ❓ 💡 ⚠️ 💰 ⭐ 🚩 ✅ ⛔ ⏳ ❤️ as small signs on a note, in both cards, chosen in the edit dialog and filterable in the search bar. Notes with subtasks show a ring with *3/5* that fills from the subtasks like in MindManager; without subtasks a tap on the ring moves it on in quarters.
- **Focus and levels (v1.8.2):** 🎯 on a note with subtasks, or **F4**, shows only that branch with the note in the middle; a breadcrumb above the map leads back, **Shift+F4** or **Esc** go up one step. ∞ at the bottom right, or the keys **1–9**, fold the map down to that many levels, **0** shows all again.
- **Links, frames and callouts (v1.8.2):** 🔗 on a note, or **L**, and then a tap on another note draws a dashed arrow between them, also across branches. A tap on the line gives it a label or marks it as *blocking*: the target turns grey with ⛔ *Waiting* until the first note is done. Pick some notes and tap ▢ *Frame* to draw a named frame around them. A *callout* is a short remark in a speech bubble above the note. Both are set in the edit dialog too, and the list card shows them as well.
- **Numbering and sorting (v1.8.3):** in ✏️ Edit of a note with subtasks, *Number the subtasks* puts 1., 1.1 … or a), b) or I., II. in front of them, in both cards. *Sort the subtasks* orders them by title, priority, due date or age right away; **S** on the map opens the same choice, without a selection for the main notes. ↶ undoes it.
- **Outline export and import (v1.8.4):** 🖼️ also saves the map as a Markdown outline, OPML or FreeMind `.mm` (opens in Freeplane, XMind, MindManager). *Insert an outline* turns pasted lists or a file (`.md`, `.txt`, `.opml`, `.mm`) into a branch of notes, below the focused note if there is one.
- **Brainstorm mode (v1.8.5):** ⚡ or **B** opens a fast input with a 3–15 minute timer. Every Enter is a note at once, shown as a coloured slip; ↶ takes the whole round out again.
- **Views (v1.8.6–v1.8.8):** the view button at the bottom right shows the notes ◎ around the center, as ⇶ a tree, ⊤ an org chart, ☰ an indented outline, ▥ Kanban by state (open, in progress, waiting, done), 📅 timeline by due date (overdue, today, tomorrow, this week, later, no date) or ⊞ Eisenhower matrix (do now, schedule, delegate, later or never). On the boards, dragging a note to another column changes its state, due date or priority, and ↶ takes it back. The choice stays in the browser; `layout` sets the default.
- **Overview / minimap (v1.10.6):** 🗺️ at the bottom right or **M** shows the whole map small at the bottom left, in the category colors, with the visible part as a frame. Tap or drag in it to jump there. On wide cards it starts open, on phones closed; each browser remembers the choice. Works in every view, the boards too. `show_minimap: false` hides it along with its button.
- **Presentation mode (v1.8.10):** **P** (or ▶ in the view choice) shows the map full screen and walks through it note by note, branch by branch, with the description below. → / space for the next note, ← back, Esc ends it.
- **Freehand drawing (v1.11.7):** 🖍️ in the controls or **D** puts a pen over the round map of a category: free strokes, ➚ arrows and ◯ circles in six colours and three widths, 🧽 erases the strokes you tap, 🗑️ deletes all, ↶ takes back every step. The drawing is kept per category, shows on every device and goes into the picture, the PDF and the JSON export. Esc or ✓ ends drawing.
- **Pinboard (v1.11.6):** 📌 in the view choice shows the notes of a category as coloured sticky notes, without tree or lines, subtasks included. Drag a note anywhere and it stays there, on every device; notes not placed yet line up in rows below. Pick the colour (yellow, pink, green, blue, orange, purple) under ⋯; groups get a frame as on the map (▢ in the selection bar). ↶ takes back moves and colours.
- **Content templates (v1.8.8):** 🖼️ ➔ *Insert an outline* has ready branches such as SWOT analysis, pros and cons, project plan, week plan or packing list for a trip. Adjust the text, then insert.
- **Templates and picture export:** Four templates (Standard, Clean, Sketch, Neon) set shape, lines and colors. Ten shapes are available, from card, cloud, speech and thought bubble to ellipse, hexagon, note slip and underlined text, for the whole map or per note. 🖼️ at the top right saves the map as SVG or PNG.

## Mind map: mouse, touch, keyboard

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
| Comment | ⋯ on the note ➔ 💬 *Comments*, or tap 💬 on the note; `@Name` tells that person |
| Overview (minimap) | 🗺️ at the bottom right or **M**; tap or drag in the overview at the bottom left to jump there |
| Link two notes | 🔗 on the note or **L**, then tap the target note; two picked notes ➔ 🔗 *Link* |
| Label or delete a link | tap the dashed line |
| Frame around notes | pick notes ➔ ▢ *Frame*, or ✏️ Edit ➔ *Frame*; tapping the frame name renames it |
| Callout | ✏️ Edit ➔ *Callout* |
| Brainstorm: collect many ideas fast | ⚡ at the bottom right or **B** |
| Tree, org chart, outline, pinboard, Kanban, timeline or Eisenhower matrix | view button above ⚡ |
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

**Who is there:** the top left shows who has the same list open right now, as a circle with initials. When somebody edits a note, the circle gets a ring and the note shows ✏️ with the name. Nothing of it is stored.

**Drawing:** 🖍️ or **D** opens a bar at the top with pen, arrow, circle and eraser, six colours and three widths. Drag to draw, the eraser deletes the strokes you tap, ↶ takes back every step, Esc or ✓ ends. It works on the round map of a single category; there the drawing is kept and goes into the picture and the export.

**Pinboard:** 📌 shows the notes as coloured sticky notes, without tree or lines. Drag a note anywhere and it stays there on every device; notes not placed yet line up in rows below. Pick the colour under ⋯; for groups, select notes and put a frame around them with ▢.

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
| **K** | AI: group loose notes into themes |
| **D** | Draw: pen, arrow, circle and eraser over the map |
| **G** | AI: create a map from a topic or text |
| **R** | rules: color notes that fit a saved filter |
| **M** | overview (minimap) on/off |
| **V** | start or end a vote |
| **P** | presentation mode |
| **Esc** | clear the selection, go up one level in focus, cancel linking |
| **Ctrl+Z** | undo |

In a text field: **Enter** saves, **Shift+Enter** starts a new line, **Esc** cancels.

## ⚙️ Mind map card options (`brainstorm-mindmap-card`)

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
| `level` | as in the settings | operating level of this card only, see [4.0](Settings#operating-level) |
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
