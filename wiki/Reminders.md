🏠 [Home](Home) · 🇩🇪 [Deutsche Version](Erinnerungen)

> 🎬 **Prefer to watch?** The [reminders video](https://github.com/nukleuz80/ha_brainstorm/blob/main/docs/videos_en.md#reminders--notifications-3-minutes) shows due dates, announcements, places and quiet hours in three minutes.

Brainstorm reminds you of due ideas on its own, over the services you have already set up in Home Assistant. Everything is optional and runs locally.

**Setting a time**
- **By voice (skill):** *"Alexa, ask Brainstorm to remind me tomorrow at 8 to take out the bins"*. Phrases like *tonight*, *tomorrow morning*, *on Friday*, *next week*, *March 15th*, *in two hours* are understood. Numeric dates like 3/4 are not, because countries read them differently, and *at 5* without am or pm means the next time it comes up.
- **In the lists:** Set a due date in the Home Assistant to-do lists. A plain date means 09:00.
- **On the card:** Long-press an idea ➔ choose a reminder.
- **In the edit dialog:** Both cards show a date and a time field, without a time Brainstorm reminds you at 09:00. Below, *Remind on* opens with a tap and chooses the Echos that speak this reminder. Without a choice, the reminder settings apply.
- **In automations:** `brainstorm.add_idea` and `brainstorm.update_idea` with the `due` field.

**Configure** under **Brainstorm Hub ➔ Configure ➔ Reminders & Notifications**. Every feature has its own switch:

- **On/Off & Channels:** a master switch, the Alexa announcement (origin, most recent or fixed Echos, needs Alexa Media), any `notify` services (the companion app gets **Done**, **1 hour later** and **Tomorrow** buttons) and sending important open ideas to further services after a waiting time.
- **Quiet Hours, Briefing & Weekly Review:** Urgent ideas still reach your notification services during quiet hours, but no Echo speaks. The briefing can wait until a sensor or person detects someone.
- **Rules per List:** normal channels, Alexa only, notifications only (private) or nothing, own services, sending a list on certain days or at a place.
- **Places & Coming Home:** *"remind me to take out the trash when I get home"*, *"remind me of the milk when I get to the market"*, using your zones.
- **People:** *"remind Alex tomorrow at 8 to call the dentist"*, with own channels per person.
- **Calendar & Alexa Reminders:** adds reminders once to a calendar (later changes are not transferred) and optionally creates real Amazon reminders in the skill (switch on **Build ➔ Permissions ➔ Reminders** in the Alexa console and grant consent once in the Alexa app).

The AI that shortens the briefing and review is set in the main menu under **Brainstorm Hub ➔ Configure ➔ AI** (since v1.6.27).

**Lists on an Echo Show:** With the skill, an Echo with a screen shows your open ideas next to the voice answer: one page per category with tiles, swipe left or right to change it and scroll within a page. Touch the circle in front of an idea to complete it. A main task with subtasks shows *+ 3 subtasks*; touching its text opens and closes them; a completed idea can be restored on the card. *"show daily life"* or *"show my lists"* shows the lists with only a short answer, while *"read"* and *"read everything"* show them while reading aloud.

To set this up, open **Build ➔ Interfaces** in the Alexa developer console, switch on **Alexa Presentation Language** with the Echo Show profiles, and click **Save**. Then copy the **Voice model** and **Skill code** fields again, click **Build** and **Deploy**. Without these steps, the skill keeps answering by voice only. Amazon decides how long a screen stays visible, and it can return to the home screen earlier than the requested two minutes.

**More skill sentences:** *"done bins"* or just *"done"* for the last reminder, *"later"* moves it one hour, *"read daily life"* reads a category, *"read"* gives only the overview, *"read everything"* reads everything.

**Your own automations:** Every reminder fires the `brainstorm_reminder_due` event, also without any services.
