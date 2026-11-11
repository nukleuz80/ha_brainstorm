🏠 [Home](Home) · 🇩🇪 [Deutsche Version](Dienste-und-Ereignisse)

## 📋 Overview

All parameters are [further down](#brainstormadd_idea) and under [**Developer tools ➔ Actions**](https://my.home-assistant.io/redirect/tools_actions/).

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
| `brainstorm.add_comment` / `delete_comment` | comment: `id: …`, `text: "@Frida can you bring salad?"`; delete with `comment_id` |
| `brainstorm.start_voting` / `vote` / `end_voting` | voting: `category: Holiday`, `votes: 5`, `hidden: true`; `vote` with `id`, `delta`; `end_voting` responds with the ranking |
| `brainstorm.start_round` / `end_round` | hidden round: `category: Holiday`, `minutes: 10`; `end_round` reveals and responds with `revealed` |
| `brainstorm.share` | share a list with people |

With `parse_due: true`, `add_idea` reads a point in time from the text like speech does:

```yaml
action: brainstorm.add_idea
data:
  text: "Remind me tomorrow at 8 to take out the bins"
  parse_due: true
```

Every action stays available while the integration is not loaded and then explains why it cannot run.

## `brainstorm.add_idea`

▶️ [Try it in Home Assistant](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.add_idea)

Adds a new idea and detects the category in the text, such as `Garden: plant flowers` or `#smarthome`.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `text` | Yes | The content of the idea. |
| `category` | No | Category. If empty, it is detected from the text or set to `Inbox`. |
| `priority` | No | Urgency (`low`, `medium`, `high`, `urgent`). Detected automatically if empty. |
| `source` | No | Where the idea comes from, such as `alexa`, `assist` or `dashboard`. Without a source the text counts as typed and keeps its wording. Only a voice source shortens spoken sentences. |
| `device` | No | The device that triggered it, such as `Echo Show Küche`. |
| `tags` | No | Additional keywords. |
| `parent_id` | No | ID of the parent idea, to create a subtask. |
| `due` | No | When Brainstorm should remind you of this idea. |
| `parse_due` | No | Detects phrases like `tomorrow at 8` in the text and uses them as the time. |
| `assignee` | No | The person to remind. |
| `zone` | No | Reminds when entering this zone. |
| `language` | No | Language of the text, such as `de` or `en`. Without it, the language of Home Assistant applies. |

## `brainstorm.update_idea`

▶️ [Try it in Home Assistant](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.update_idea)

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
| `echos` | No | The Echos that speak the reminder of this idea, as a list. `null` goes back to the reminder settings. |
| `result` | No | What came of the idea, usually written when ticking it off (at most 1000 characters). Both cards show it below the text. It stays when the idea is reopened; empty or `null` removes it. |
| `shape` | No | Shape of the note on the mind map: `card`, `cloud`, `bubble`, `thought`, `pill`, `rect`, `ellipse`, `hexagon`, `note` or `underline`. Empty or `null` goes back to the look of the map. |
| `markers` | No | Markers as a list: `question`, `idea`, `warning`, `money`, `star`, `flag`, `check`, `blocked`, `waiting`, `heart`. Replaces the old ones; an empty list or `null` removes them. |
| `progress` | No | Progress of a note without subtasks: `0`, `25`, `50`, `75` or `100`. `0` or `null` removes it. Notes with subtasks work it out themselves. |
| `links` | No | Links to other notes as a list of `{to: <id>, label: <text, up to 40>, blocks: true/false}`, at most 20. `blocks: true` makes the target wait until this note is done. Replaces the old ones; an empty list or `null` removes them. |
| `frame` | No | Name of a frame on the mind map, up to 40 characters. Notes with the same name share one frame. Empty or `null` removes it. |
| `callout` | No | Short remark shown in a speech bubble above the note, up to 200 characters. Empty or `null` removes it. |
| `repeat` | No | Lets the idea come back when it is ticked off: `daily`, `weekdays`, `weekly`, `biweekly`, `monthly` or `yearly`. The new idea is due at the next date after now, with the same details and its subtasks open again. Empty or `null` stops it. |
| `numbering` | No | Numbers the subtasks below the note and theirs: `decimal` (1., 1.1), `alpha` (a), b)) or `roman` (I., II.). Empty or `null` removes it. |

## `brainstorm.delete_idea`

▶️ [Try it in Home Assistant](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.delete_idea)

Removes an idea. Until the next start of Home Assistant, `brainstorm.restore_idea` can bring it back.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `id` | Yes | ID of the idea to delete. |

## `brainstorm.delete_done`

▶️ [Try it in Home Assistant](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.delete_done)

Deletes ideas that are done (ticked off or archived), in one go. With privacy on, only the caller's own ideas. Deleted ideas cannot be brought back. The response says how many were deleted (`deleted`).

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `older_than_days` | No | Only ideas done at least this many days ago. `0` (default) deletes all done ideas. |

## `brainstorm.restore_idea`

▶️ [Try it in Home Assistant](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.restore_idea)

Brings back an idea deleted since the last start of Home Assistant, with the links to its subtasks. Only the person who deleted it can do this. The mind map card uses it for undo.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `id` | Yes | ID of the deleted idea. |

## `brainstorm.get_ideas`

▶️ [Try it in Home Assistant](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.get_ideas)

Returns stored ideas as a response, for templates and automations.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `category` | No | Only this category. |
| `priority` | No | Only this priority (`low`, `medium`, `high`, `urgent`). |
| `status` | No | Status filter (`active`, `completed` or `all`). |

## `brainstorm.get_announcement`

▶️ [Try it in Home Assistant](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.get_announcement)

Returns a spoken text about all categories or one of them as a response, for Alexa or Assist.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `category` | No | Only this category, such as `Smarthome`. Empty means all. |
| `device` | No | The device that asked. With privacy on, it decides whose entries are named. |

## `brainstorm.add_category`

▶️ [Try it in Home Assistant](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.add_category)

Creates a new category and its to-do list.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `name` | Yes | Name of the new category. |
| `icon` | No | Optional Home Assistant / MDI icon. |
| `color` | No | Optional accent color as hexadecimal, such as `#ff7800`. |

## `brainstorm.set_category_style`

▶️ [Try it in Home Assistant](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.set_category_style)

Sets a custom icon and accent color for a category.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `category` | Yes | Name of the category. |
| `icon` | No | Home Assistant / MDI icon. |
| `color` | No | Accent color as hexadecimal, such as `#06b6d4`. |
| `reset` | No | Removes the custom icon and color. |

## `brainstorm.remove_category`

▶️ [Try it in Home Assistant](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.remove_category)

Removes a category. Its ideas move to `Inbox`.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `name` | Yes | Name of the category. |

## `brainstorm.export_markdown`

▶️ [Try it in Home Assistant](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.export_markdown)

Writes all categories and ideas as Markdown files.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `path` | No | Target folder. Default: the Markdown folder from the options (`/config/brainstorm`). Only admins may choose a folder, and it must lie in `/config/brainstorm`, the Markdown folder from the options or `allowlist_external_dirs`. |

## `brainstorm.export_json`

▶️ [Try it in Home Assistant](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.export_json)

Returns the ideas you may see, with their categories, icons and colors, as JSON. Use it as a backup, to move to another Home Assistant or to share a category.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `category` | No | Only export this category. Default: all categories. |
| `path` | No | Also write the export to this file, such as `brainstorm/backup.json` (relative to `/config`). The name must end in `.json`. Only `/config/brainstorm`, the Markdown folder from the options and `allowlist_external_dirs` are allowed. Only admins may write files. |

```yaml
action: brainstorm.export_json
data:
  path: brainstorm/backup.json
response_variable: backup
```

## `brainstorm.import_json`

▶️ [Try it in Home Assistant](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.import_json)

Adds the ideas of a JSON export that are not here yet. Ideas whose ID exists are skipped, so importing the same file twice changes nothing. Missing categories are created, and icons and colors are taken over where a category has none.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `data` | One of both | The response of `brainstorm.export_json`. |
| `path` | One of both | A file written by `brainstorm.export_json`, relative to `/config`, from the same folders as the export. Only admins may read files. |

Owners and shares only stay for users of this Home Assistant, and owners only when an admin imports. Otherwise the ideas belong to whoever imports them. The response says how many ideas were `added` and `skipped`, and which categories were added.

## `brainstorm.bring_message`

▶️ [Try it in Home Assistant](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.bring_message)

Tells everyone on a Bring list something, through Bring's own notifications. In the card, the 🛒 button of a list note offers *I'm going shopping*, *Shopping done* and *List changed*; the menu of an item on a list offers *Report as urgent in Bring!*.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `id` | Yes | ID of a Bring list note, or of an item on such a list. |
| `message` | Yes | `going_shopping`, `changed_list`, `shopping_done` or `urgent_message`. An urgent message needs an item, whose text Bring sends along. |

## `brainstorm.reorder_ideas`

▶️ [Try it in Home Assistant](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.reorder_ideas)

Saves the custom order of the ideas.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `idea_ids` | Yes | Ordered list of idea IDs. |

## `brainstorm.import_outline`

▶️ [Try it in Home Assistant](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.import_outline)

Adds a tree of notes from a Markdown outline, indented text, OPML or a FreeMind/Freeplane map (`.mm`), at most 300 notes. Returns `added` and the new `ids`.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `text` | Yes | The outline: headings, `-`/`*`/`1.` lists or indented lines; `- [x]` adds an item as done, a `>` line below an item is its description. Or the content of an OPML or `.mm` file. |
| `format` | No | `auto` (default), `markdown`, `opml` or `freemind`. |
| `category` | No | Where the notes go; without it, the default category. |
| `parent_id` | No | Puts the outline below this note, in its category. |

## `brainstorm.sort_children`

▶️ [Try it in Home Assistant](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.sort_children)

Sorts the subtasks of a note, or the main notes of a category, within the places they already take. Other notes keep their place.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `parent_id` | No | The note whose subtasks are sorted. |
| `category` | No | Without `parent_id`: the category whose main notes are sorted. |
| `by` | No | `text` (A–Z), `priority` (urgent first), `due` (earliest first, notes without a date last) or `created` (oldest first), `votes` (most votes first). |
| `ids` | No | Instead of `by`: the subtasks in a fixed order, for example to undo a sort. |
| `reverse` | No | Sorts the other way round. |

## `brainstorm.react`

▶️ [Try it in Home Assistant](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.react)

Sets or removes your own reaction on a note. Each person counts once per reaction; whoever may see a note may react to it.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `id` | Yes | ID of the note. |
| `reaction` | Yes | `like` 👍, `heart` ❤️, `laugh` 😂 or `important` ❗ |
| `active` | No | `true` sets, `false` removes; without it the reaction toggles. |

## `brainstorm.add_comment`

▶️ [Try it in Home Assistant](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.add_comment)

Adds a comment to a note. Whoever may see the note may comment. People named with `@Name` get a message over their channels under *Reminders ➔ Persons*; with privacy only when they may see the note. Responds with `comment` and `notified` (the people told). Fires the event `brainstorm_comment_added`.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `id` | Yes | ID of the note. |
| `text` | Yes | The comment, up to 2000 characters. `@Frida` or `@Frida Sommer` tells that person. |
| `notify` | No | `false` adds the comment without telling anyone. |

## `brainstorm.delete_comment`

▶️ [Try it in Home Assistant](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.delete_comment)

Removes a comment. Its author may, and whoever may change the note.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `id` | Yes | ID of the note. |
| `comment_id` | Yes | ID of the comment. |

## `brainstorm.group_ideas`

▶️ [Try it in Home Assistant](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.group_ideas)

Puts notes of one category below a new note with this title, for example a theme the AI suggested. The new note takes the place of the first note; the notes keep their order and subtasks. Answers with the ID of the new note (`id`).

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `title` | Yes | Text of the new parent note. |
| `ids` | Yes | The notes that go below it, all from the same category. |

## `brainstorm.start_round`

▶️ [Try it in Home Assistant](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.start_round)

Starts a hidden brainstorm round in a category: until the reveal, new notes are seen only by whoever wrote them. If a round is already running, it stays as it is. Answers with the round (`round`: `since`, `by`, `ends_at`).

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `category` | Yes | The category of the round. |
| `minutes` | No | The round reveals itself after this many minutes (1–60, 0 = until revealed). |

## `brainstorm.end_round`

▶️ [Try it in Home Assistant](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.end_round)

Reveals the hidden round of a category. Answers with the number of revealed notes (`revealed`) and fires the event `brainstorm_round_ended`.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `category` | Yes | The category of the round. |

## `brainstorm.start_voting`

▶️ [Try it in Home Assistant](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.start_voting)

Starts a vote in a category. Everyone gets the same number of votes and spreads them over the notes, several on one if they like.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `category` | Yes | The category whose notes are voted on. |
| `votes` | No | Votes per person (1–20, default 5). |
| `hidden` | No | Hidden: everyone sees only their own votes until the end. |
| `clear` | No | Removes the points of an earlier round. |

## `brainstorm.vote`

▶️ [Try it in Home Assistant](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.vote)

Gives a note votes in a running vote, or takes them back. Responds with `votes` (yours on this note), `used` and `allowed`.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `id` | Yes | ID of the note. |
| `delta` | No | How many votes to add (default 1); negative takes them back. |

## `brainstorm.end_voting`

▶️ [Try it in Home Assistant](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.end_voting)

Ends the vote of a category and responds with the ranking (`ranking`: `id`, `text`, `points`, `voters`). The points stay on the notes, and `sort_children` with `by: votes` sorts by them.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `category` | Yes | The category of the vote. |

## `brainstorm.share`

▶️ [Try it in Home Assistant](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.share)

Shares several ideas or a whole category. Needs privacy to be switched on.

| Field | Required | Meaning |
| :--- | :--- | :--- |
| `ids` | No | IDs of the ideas to share. |
| `category` | No | Shares all your ideas in this category, including later ones. |
| `shares` | Yes | User ID (or `all`) and level, such as `{"all": "view"}`. Levels are `view` and `edit`; `null` removes a share. |

## Events

| Event | When |
|---|---|
| `brainstorm_idea_added` | new note |
| `brainstorm_idea_updated` | note changed |
| `brainstorm_idea_completed` | note completed |
| `brainstorm_idea_deleted` | note deleted |
| `brainstorm_reminder_due` | a reminder is due |
| `brainstorm_comment_added` | a new comment (`idea_id`, `idea_text`, `text`, `by`, `mentions`) |
| `brainstorm_round_ended` | a hidden round was revealed (`category`, `revealed`) |

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
