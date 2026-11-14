🏠 [Home](Home) · 🇩🇪 [Deutsche Version](Einstellungen)

An overview with typical examples per menu is [further down](#integration). For events, the sensor and services see [Services & Events](Services-and-Events) and [Entities & Attributes](Entities-and-Attributes).

## During Setup

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

## After Setup

Find these under [**Settings ➔ Devices & Services ➔ Brainstorm Hub ➔ Configure**](https://my.home-assistant.io/redirect/integration/?domain=brainstorm).

### Brainstorm › Categories

| Field | What it does |
| :--- | :--- |
| ➕ Add new category (optional) | Name of a category to add. Leave empty to add none. |
| 🗑️ Delete existing category (optional) | The ideas of a deleted category move to Inbox. |
| ✏️ Edit full list (comma-separated) | All categories, separated by commas. Change this list to rename, reorder or remove several at once. |
| Hide categories without notes (0) | Hides categories that have no notes from the cards. |

### Brainstorm › Category Design

| Field | What it does |
| :--- | :--- |
| Select Category | The category whose icon and color you want to change. |

### Brainstorm › Category Design

| Field | What it does |
| :--- | :--- |
| Category Icon (Home Assistant / MDI) | Shown for this category on the cards. |
| Category Color | Color of this category on the cards. |
| Reset to default icon and color | Removes the icon and color of this category and ignores the two fields above. |

### Brainstorm › General

| Field | What it does |
| :--- | :--- |
| Operating level | How many controls the cards and these settings show: Beginner, Normal or Pro. New installations start with Normal, existing ones keep Pro. Hiding deletes nothing, and each card can set its own `level`. Details [below](#operating-level). |
| Default category for new ideas | Used when an idea cannot be assigned to a category. |
| Smart Text Optimization (grammar, capitalization, infinitive formatting) | Corrects capitalization and grammar of new ideas and removes filler words. |
| Take dates from spoken text as a due date | A spoken "tomorrow" or "on 25.11." moves out of the text and becomes a due date. A due date leads to a reminder at that time, without a time of day at 09:00. |
| Own terms for spoken text | One term per line, for example Lenia, or a correction, for example fehler = Richtig. Names of people and categories are known automatically. |
| Auto-export ideas to Markdown files | Writes one Markdown file per category to the folder below whenever ideas change. |
| File path for Markdown files | Folder for the Markdown files, for example /config/brainstorm. |
| Echo devices for voice input | Only these Echos can capture ideas and open Brainstorm by voice. Leave empty to use all Echos. |

### Brainstorm › Alexa

| Field | What it does |
| :--- | :--- |
| Voice input | Native uses the Alexa Media sentence without a skill. Skill and Both use your own Alexa skill. |

### Brainstorm › Alexa › Skill

| Field | What it does |
| :--- | :--- |
| Skill code (lambda_function.py) | Copy this into lambda_function.py of your skill. Keep it private, it contains your secret address. |
| Voice model (JSON editor) | Paste this into the JSON editor of the Alexa developer console. |
| Create a new secret address and remove the skill link | Use this if the address leaked or you built a new skill. Copy the new skill code afterwards. |
| Name for this unknown device | For example Alexa App iPhone. Home Assistant cannot detect the Alexa app by itself. The name applies to the last idea and all later ones from this device. |

### Brainstorm › Reminders › On/Off & Channels

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

### Brainstorm › Reminders › Quiet Hours, Briefing & Review

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

### Brainstorm › Reminders › Rules per List

| Field | What it does |
| :--- | :--- |
| Use rules per list | Off makes all lists use the normal settings and keeps the rules. |
| List to edit | Choose a list to edit its rule on the next page. |

### Brainstorm › Reminders › Rules › …

| Field | What it does |
| :--- | :--- |
| Reminders of this list go to | Normal channels follow the general settings of the reminders. |
| Own notification services for this list | Replace the normal services for this list. Empty uses the normal ones. |
| Send the open ideas on certain days | Sends the open entries of this list on the days and at the time below. |
| Days | The days on which the list is sent. |
| Time | When the list is sent on these days. |
| Send the open ideas at a place | Sent once a day when someone arrives there. Needs the switch for places. |
| Place | The zone in which the open entries of this list are sent. |

### Brainstorm › Reminders › Places & Coming Home

| Field | What it does |
| :--- | :--- |
| Remind when coming home | Lets you say that a reminder should come when you get home. |
| Remind at places (zones) | Lets you name a zone for a reminder, for example a supermarket. |
| Who is meant by "ich" | Without a person, anyone arriving there triggers the reminder. |

### Brainstorm › Reminders › People

| Field | What it does |
| :--- | :--- |
| Use reminders for other people | Lets a reminder be meant for someone else, such as: remind Alex. |
| Person to edit | Choose a person to set their channels on the next page. |

### Brainstorm › Reminders › People › …

| Field | What it does |
| :--- | :--- |
| Notification services | This person's notification services. |
| Echos | The Echos that speak this person's reminders. |

### Brainstorm › Reminders › Calendar & Alexa

| Field | What it does |
| :--- | :--- |
| Add reminders to a calendar | One way, once per reminder. Later changes are not transferred. |
| Calendar | The calendar that receives the reminders. |
| Also create real Alexa reminders | In the Alexa console, also switch on Reminders under Build ➔ Permissions. Alexa then rings itself and Home Assistant does not speak as well. |

### Brainstorm › AI

Brainstorm uses an AI task entity of Home Assistant, such as Google Gemini, OpenAI or Ollama. Without one, all of this stays off.

| Field | What it does |
| :--- | :--- |
| AI task entity | When set, ✨ on a note of the mind map suggests subtasks. Only this note, its category and its subtasks are sent, and only when you press the button. |
| Improve spoken entries with AI | Each spoken entry is stored first and improved a few seconds later. The result is dropped if it adds words or changes a negation. The text is sent to the provider of the chosen AI. |
| Shorten the briefing and review with AI | The morning briefing and weekly review of the reminders are shortened. Your ideas are sent to the provider of the chosen AI. |

### Brainstorm › Delete done entries

The page shows how many done (ticked off or archived) entries there are. Deleted entries cannot be brought back, export them first if you want to keep them.

| Field | What it does |
| :--- | :--- |
| Delete done entries after (days) | Entries done for this many days are deleted by themselves, checked every six hours and once right when saving. 0 (default) keeps them. Open subtasks stay as main tasks, attachments go with them. |
| Delete all done entries now | Deletes every done entry when saving, no matter how long ago it was done. The menu then shows how many went. |

### Brainstorm › Link To-do Lists

One field per category. Pick a to-do list of another integration, such as Bring!, Google Tasks, Todoist or a local to-do list, and both stay the same:

| What happens | On the list | In Brainstorm |
| :--- | :--- | :--- |
| Something is added | becomes a note in the category | an active note is added to the list |
| Something is renamed or ticked off | the note follows | the item follows |
| Something is deleted | removing an item ticks off its note | deleting a note removes its item |

- **When:** at once after a change in Brainstorm or a new item on the list, and every 5 minutes for renames, which lists do not announce.
- **Both changed:** If the same entry was renamed on both sides between two syncs, the name on the list wins.
- **First link:** Open items with the same text are linked instead of doubled, and the spelling on the list wins. Notes that are done already are not added.
- **Due times** go to the list if it supports them, as a date and time or as a date. Changes of due dates on the list are not taken over.
- **Privacy:** With privacy on, only notes shared with everyone are synced, as everyone with access to the other list sees them. Items from the list are shared with everyone.
- **Unlinking:** Clearing a field unlinks the list. Its items stay where they are.
- Each list can be linked to one category only, and Brainstorm's own lists cannot be chosen.

### Brainstorm › 🛒 Bring!

Only shown when the [Bring!](https://www.home-assistant.io/integrations/bring/) integration is set up. All your Bring lists land in one category: each list becomes a main note, and its items become its subtasks.

```
🛒 Einkauf
├─ 🏠 Zu Hause
│   ├─ Milch
│   └─ Brot
└─ 🚐 Camper
    └─ Gas
```

| Field | What it does |
| :--- | :--- |
| Sync Bring! | Switches the sync on or off. Switched off, notes and items stay where they are. |
| Category | Pick a category or type a new name, which is created when you save. |
| Lists | Leave empty to sync all lists, including lists added later. |
| Default list | Notes that land in the category without a list, for example *"we need milk"* by voice, go to this list and hang under its note. |
| Hide bought items after (days) | Ticked off items leave the completed view after this many days (default 3) and are archived. In Bring they stay in the recent list for buying again. 0 keeps them. |
| Share the category with everyone | Only shown with privacy on. Only notes shared with everyone are synced, as everyone with access to Bring sees them. |

- **Both ways:** New items, ticks and deletions travel between Brainstorm and Bring. Ticking off moves the item to *Recently used* in Bring.
- **Moving:** Hang a subtask under another list note, and the item moves to that list.
- **Bought before:** A note with the name of an item in *Recently used* brings that item back instead of adding it twice, as Bring allows each name only once per list.
- **Amounts:** The specification of a Bring item, such as *1.5 l*, is kept with the note (field `spec`).
- **List notes** take their name from Bring. A deleted list note comes back with its items, and the note of a list that is no longer synced is archived.
- **Fast:** Changes by others are picked up through Bring's activity events, and everything is compared every 5 minutes as well.

### Brainstorm › Reminders › Lock times per Echo

Keeps single Echos silent for Brainstorm at set times, such as nights in the children's room (v1.7.7). Up to three lock times, each for one or more Echos, and they may span midnight.

| Field | What it does |
| :--- | :--- |
| Echos 1 | The Echos of lock time 1. Empty removes it. |
| From 1 | Start of lock time 1. |
| Until 1 | End of lock time 1. Earlier than the start means the next morning. |
| Also Do not disturb 1 | Switches Do not disturb of these Echos on at the start and off at the end, so Alexa itself is silent too. Needs Alexa Media Player. |
| Echos 2 | The Echos of lock time 2. Empty removes it. |
| From 2 | Start of lock time 2. |
| Until 2 | End of lock time 2. Earlier than the start means the next morning. |
| Also Do not disturb 2 | Switches Do not disturb of these Echos on at the start and off at the end, so Alexa itself is silent too. Needs Alexa Media Player. |
| Echos 3 | The Echos of lock time 3. Empty removes it. |
| From 3 | Start of lock time 3. |
| Until 3 | End of lock time 3. Earlier than the start means the next morning. |
| Also Do not disturb 3 | Switches Do not disturb of these Echos on at the start and off at the end, so Alexa itself is silent too. Needs Alexa Media Player. |

- **Other Echos keep speaking:** A reminder still goes to the Echos of the reminder that are not locked.
- **Phone as fallback:** If no Echo is left, the reminder goes to the phone right away instead of after the waiting time.
- **Test:** *🧪 Test channels now* speaks in a lock time too, as you start it yourself.

### Brainstorm › 🔋 Batteries

Turns low batteries into tasks (v1.7.5). Every battery sensor counts: a level in percent, or a sensor that only reports a weak battery.

| Field | What it does |
| :--- | :--- |
| Create battery tasks | Switches battery tasks on or off. Switched off, no new tasks are made and existing ones stay. |
| Threshold | A task is created at this level or below (default 20 %). |
| Category | Pick a category or type a new name, which is created when you save. Suggested is *Smarthome*. |
| Leave out | Batteries that should never create a task, such as a home battery. Leaving out one sensor leaves out its whole device. |
| Include phones and tablets | Devices of the Companion app are charged every day, so they are left out unless switched on. |

- **One task per device**, even if integrations like Battery Notes add more sensors for the same battery. It is named after its device, e.g. *Replace the battery: Motion sensor hall (18 %)*.
- **Ticks itself off:** Once no sensor of the device reports a weak battery and the level is 10 points above the threshold, the task is ticked off. The gap keeps a battery around the threshold from creating and closing tasks.
- **Ticked off by hand** before the battery is replaced, the task does not come back. The next weak battery makes a new one.
- **After a restart**, all batteries are checked once.

### Brainstorm › 📟 Sensor tasks

Turns a sensor value into a task (v1.11.10), such as *Change the water filter* after 300 operating hours, *Water the monstera* when soil moisture falls below 20 %, or *Empty the washing machine* once it has finished. The first page lists your rules:

| Field | What it does |
| :--- | :--- |
| Rule | Choose a rule to change or delete it, or *➕ New rule*. |

A rule has these fields:

| Field | What it does |
| :--- | :--- |
| Entity | Any entity, such as a sensor, a counter, a number helper or a binary sensor. |
| Condition | *Reaches or exceeds* and *Reaches or falls below* compare numbers, *Is exactly (state)* compares the state as text, ignoring upper and lower case. |
| Value | A number for limits, such as `300` or `19.5`, or a state, such as `off` or `finished`. |
| Task | The text of the task. Its description names the sensor and its value, such as *Triggered by Water filter operating hours: 300 h*. |
| Category | Choose a category or type a new name, it is created on saving. *Smarthome* is suggested. |
| Tick off by itself | Ticks the task off once the sensor is back to normal (on by default). |
| Back to normal at | Optional, numbers only: only this value counts as back to normal, such as `0` for a counter you reset after changing the filter. It must lie on the normal side of the limit. Without it, anything beyond the limit counts as normal. |
| Delete this rule | Only when editing: removes the rule. Its open task stays. |

- **One task per occurrence:** while the condition stays met, no second task is created. Only once the sensor has been back to normal and the condition is met again is there a new one.
- **Ticked off by hand** before the sensor is back to normal, the task does not come straight back.
- **Without *Tick off by itself*** the task stays open until you tick it off, and also stands for the next occurrence until then.
- **After a restart** and after saving, every rule is checked once; a rule already met creates its task at once. *Unavailable* and *Unknown* are skipped.
- The task carries the source 📟 *Sensor* with the name of the entity and reaches reminders and automations like any new note.

### Brainstorm › Privacy & Users

| Field | What it does |
| :--- | :--- |
| Keep ideas private | Each person then sees only their own entries and what is shared with them. |
| Main user | Owns all existing ideas, and everything said to an Echo. Voice, briefing and review only mention this person's ideas. |
| Keep exporting to Markdown files | These files contain all ideas and can be read by anyone with access to the config folder. |
| Offer these users for sharing | Leave empty to offer everyone. Use this to hide technical accounts such as MQTT. |

### Brainstorm › Assign Echos & Apps

| Field | What it does |
| :--- | :--- |
| Echo or Alexa app | The Echo or Alexa app you want to assign. You can also type a name. |
| Person | Leave empty to remove the assignment. |

## Operating level

Under **Configure ➔ General Settings & Export ➔ Operating level** you choose how much Brainstorm shows. The level applies to everyone, to both cards and to the configure menu. New installations start with *Normal*, existing ones keep *Pro*, so everything stays as before.

| Level | List card and edit dialog | Mind map | Configure menu |
|---|---|---|---|
| **Beginner** | input, microphone, categories, ticking off, search; in the dialog title, description, category, priority and due date | only *Around the center*, New idea, zoom, full screen | without batteries, sensor tasks, lock times, rules per list, Echos & apps and AI text cleanup |
| **Normal** | also subtasks, multi-select, markers, repeating, attachments, sharing, AI suggestions | also *Tree*, *Outline*, *Kanban*, focus, levels, search and filter, multi-select, export as picture, PDF and Markdown | like Beginner |
| **Pro** | everything: progress, numbering and sorting, callout, frame, shape, remind on Echos, original text, "in progress" | everything: *Org chart*, *Timeline*, *Matrix*, rules, cross links, frames, brainstorm and presentation mode, OPML/FreeMind, summing up a branch, all shortcuts | everything |

Hiding deletes nothing: markers, progress or frames that are set stay visible on the cards. In the edit dialog **More fields …** brings the hidden fields back. Each card can have its own level with `level: beginner`, `normal` or `pro`, for example a kitchen tablet that always shows *Beginner*.

## Integration

[**Settings ➔ Devices & Services ➔ Brainstorm Hub ➔ Configure**](https://my.home-assistant.io/redirect/integration/?domain=brainstorm) opens a menu. Every field is described [above](#during-setup).

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
| **📟 Sensor tasks** | from 300 operating hours the task *Change the water filter*, completes itself once the counter is reset |
| **🧹 Delete done entries** | remove done notes after 30 days automatically |
