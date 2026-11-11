🏠 [Home](Home) · 🇩🇪 [Deutsche Version](Sprachsteuerung)

## 🗣️ Voice Commands

Which language applies depends on where you speak: the skill follows the language of your Echo, everything else the language of Home Assistant. The German commands are in the [German documentation](https://github.com/nukleuz80/ha_brainstorm).

### Alexa Skill (Recommended)

Your own skill is the most reliable way. The setup is in the chapter *Optional: Your Own Alexa Skill* below. Start each sentence with *"Alexa, ask Brainstorm to"*:

| You say | What happens |
| :--- | :--- |
| *"note dim the basement light"* | Saves a note. Also: *idea*, *remember*, *add*, *write down* |
| *"remind me tomorrow at 8 to take out the bins"* | Saves a note with a reminder |
| *"done take out the bins"* or *"done"* | Completes a note, or the last reminder |
| *"later"* | Moves the last reminder by one hour |
| *"read"* or *"read daily life"* | Gives the overview, or reads a category |
| *"read everything"* | Reads all notes |
| *"show my lists"* or *"show daily life"* | Shows the lists on an Echo with a screen |

### Alexa Dialog

Say *"Alexa, brainstorm"*, Alexa asks for your note and confirms the category. It needs the Alexa Actionable Notifications skill. Copy the script and automation from [`examples/alexa_dialog.en.yaml`](https://github.com/nukleuz80/ha_brainstorm/blob/main/examples/alexa_dialog.en.yaml) and create a routine in the Alexa app with the script as its scene, because **Brainstorm** is also the name of a band and Alexa would otherwise try to play music. Routines take priority over music search.

### Alexa Direct Commands

Say everything in one sentence: *"Alexa, note dim the basement light"*, *"Alexa, idea repair the sprinkler"*, *"Alexa, remember to fertilize the tomatoes"*. An automation stops any skill or music that started and confirms the entry. Copy it from [`examples/alexa_direct_commands.en.yaml`](https://github.com/nukleuz80/ha_brainstorm/blob/main/examples/alexa_direct_commands.en.yaml). Alexa does not know these commands, so it may answer with an error first.

### Home Assistant Assist

**Brainstorm sentences** need your own custom sentences. Copy [`examples/custom_sentences/en/brainstorm.yaml`](https://github.com/nukleuz80/ha_brainstorm/blob/main/examples/custom_sentences/en/brainstorm.yaml) to `/config/custom_sentences/en/`, add [`examples/intent_script.en.yaml`](https://github.com/nukleuz80/ha_brainstorm/blob/main/examples/intent_script.en.yaml) to your `intent_script`, and restart Home Assistant:

- 🗣️ *"Add mow the lawn to Brainstorm"*
- 🗣️ *"New idea water the flowers"*
- 🗣️ *"Note create a database backup"*
- 🗣️ *"Remember to change the tires"*
- 🗣️ *"What is in daily life in Brainstorm?"*

**To-do list sentences** use Home Assistant's built-in commands:

- 🗣️ *"Add milk to the Brainstorm Hub Inbox list"*
- 🗣️ *"Check off milk on the Brainstorm Hub Inbox list"*

## 🎙️ Using Only Selected Echos

By default, every Echo can capture ideas. To limit this, go to [**Settings ➔ Devices & Services ➔ Brainstorm Hub ➔ Configure ➔ General Settings & Export**](https://my.home-assistant.io/redirect/integration/?domain=brainstorm) and select the Echos under **Echo devices for voice input**. An empty list means all Echos.

The Alexa voice flows run as automations and scripts in your own Home Assistant configuration, so each entry point needs this condition (`echo_device` holds the calling Echo):

```yaml
- condition: template
  value_template: >-
    {% set allowed = state_attr('sensor.brainstorm_ideen_ubersicht', 'allowed_echos') %}
    {{ not allowed or echo_device in allowed }}
```

## 🎙️ Optional: Your Own Alexa Skill (One Sentence, One Answer)

Without a skill, Alexa often reports an error first when you say *"Alexa, note ..."*, because it does not know that command. Your own skill gives a single answer: *"Alexa, ask Brainstorm to note dim the basement light."* ➔ *"Saved under Smart Home."*

The skill belongs to you and only talks to your own Home Assistant. **Requirements:** a free [Amazon developer account](https://developer.amazon.com/alexa/console/ask) on the same account as your Echos and a Home Assistant reachable over public HTTPS (for example through Home Assistant Cloud). Home Assistant offers the voice model in its own language. German and English exist, and other languages get the English one. The skill answers in the language of the request.

> 🎬 **Prefer to watch?** The [setup video](https://github.com/nukleuz80/ha_brainstorm/blob/main/docs/video-alexa-skill.md) shows every setting in its own chapter (6 minutes, German narration, English console labels on screen).

1. In Home Assistant, go to **Brainstorm Hub ➔ Configure ➔ Alexa Voice Input & Skill**, choose **Skill** or **Both** and continue. Keep this window open, it shows the two fields to copy.
2. In the [Alexa developer console](https://developer.amazon.com/alexa/console/ask), click **Create Skill** and choose: name `Brainstorm`, the language of your Echo, such as **English (US)**, type **Custom**, hosting **Alexa-hosted (Python)**, template **Start from Scratch**.
3. Open **Build ➔ Interaction Model ➔ JSON Editor**, replace the content with the **Voice model** field, click **Save**, then **Build**, and wait for the success message.
4. In the **Code** tab, replace `lambda_function.py` with the **Skill code** field and click **Deploy**.
5. In the **Test** tab, set the stage to **Development**.
6. Click **Submit** in Home Assistant and say *"Alexa, ask Brainstorm to note test idea."* The first request links your skill, other skills are rejected afterwards. **Configure** shows the link and the last request.

**Notes:** Keep the skill code private, it contains your secret address. If it leaks, create a new one there and copy the skill code again. The Echo selection and device display apply to the skill too. For this, Home Assistant learns each Echo from the Alexa history on its first sentence (this needs the Alexa Media integration), which can take up to 3.5 seconds longer. If the history entry arrives later, the idea is still saved and the Echo is added afterwards. In the menu you need a command word such as *"note ..."*. Alexa does not pass **free sentences without a command word** to a skill. Since v1.6.20, Home Assistant takes such sentences from the Echo's Alexa history (through Alexa Media) and saves them anyway. Alexa answers right away with *"Okay, noted"*. Alexa writes the sentence to its history only together with this answer, so the idea appears a few seconds later. Home Assistant finds the right history entry by exactly this answer. If none arrives within a minute, Home Assistant shows a notification instead of losing the sentence silently. The Alexa app reports no history, so it keeps asking for a command word. This needs the skill code to be copied once more. For **Skill** mode to turn off the existing capture, your automation has to check the `voice_mode` attribute:

```yaml
- condition: template
  value_template: "{{ state_attr('sensor.brainstorm_ideen_ubersicht', 'voice_mode') != 'skill' }}"
```

**Troubleshooting:** *"I don't know how to help with that"* usually means the **Build** is missing, the **Test** tab is not set to **Development**, or the console and Echo use different Amazon accounts. Try the sentence in the **Test** tab first. If Alexa says the idea was not saved, check the mode and whether Home Assistant is reachable.

## 📱 iPhone: Shortcut with Siri, Action Button or Back Tap

The fastest way from an iPhone: trigger, speak, done, without opening an app. It needs the Home Assistant companion app.

1. In the **Shortcuts** app, create a shortcut named **Brainstorm**. The name is also your Siri phrase.
2. Add **Dictate Text**, choose your language, and stop listening **After Pause**.
3. Add the Home Assistant action **Perform Action** and choose `brainstorm.add_idea`.
4. Paste this JSON into the data field and put the **Dictated Text** variable between the quotes after `"text":`:
   ```json
   {"text": "", "source": "siri", "device": "iPhone"}
   ```
5. Choose a trigger: **Settings ➔ Action Button ➔ Shortcut**, **Settings ➔ Accessibility ➔ Touch ➔ Back Tap ➔ Double Tap**, or *"Hey Siri, Brainstorm"*.

The note appears as **Siri (iPhone)** with an Apple logo. You can choose any device name in the JSON. If the shortcut reports that the data could not be read, the field is not valid JSON, often because the iPhone typed curly quotes. Paste the text or temporarily turn off **Settings ➔ General ➔ Keyboard ➔ Smart Punctuation**.

## 🎙️ Microphone in the Quick Input

The list card has a **🎙️** next to the quick input. Tap, speak, and the text appears in the field for checking. Recording ends on a pause, on another tap or after 30 seconds. It uses your preferred Assist pipeline, which needs a speech-to-text engine. The microphone only appears over HTTPS, so in the companion app or through an HTTPS address such as Home Assistant Cloud. Turn it off in the card settings or with `show_mic: false`.

## 💬 Examples


### Alexa without a skill

This needs the Alexa Media integration and the automations in [`examples/`](https://github.com/nukleuz80/ha_brainstorm/tree/main/examples/).

**Dialog** ([`alexa_dialog.en.yaml`](https://github.com/nukleuz80/ha_brainstorm/blob/main/examples/alexa_dialog.en.yaml))

> 🗣️ "Alexa, brainstorm"
> 🤖 "Brainstorm is ready. Speak your note."
> 🗣️ "The roses in the garden need cutting."
> 🤖 "Saved under House & Garden."

**Direct, in one sentence** ([`alexa_direct_commands.en.yaml`](https://github.com/nukleuz80/ha_brainstorm/blob/main/examples/alexa_direct_commands.en.yaml))

| You say | Result |
|---|---|
| "Alexa, **idea** repair the sprinkler" | House & Garden |
| "Alexa, **note** dim the basement light" | Smart Home |
| "Alexa, **remember to** fertilize the tomatoes" | House & Garden |

Alexa does not know these commands, so it may answer with an error first. The skill avoids that.

### Alexa with your own skill

With the skill Alexa answers only once. The setup is [above](#️-optional-your-own-alexa-skill-one-sentence-one-answer). A 🎬 [video walkthrough](https://github.com/nukleuz80/ha_brainstorm/blob/main/docs/video-alexa-skill.md) with one chapter per setting is available in German, the console labels on screen are in English. Start each sentence with **"Alexa, ask Brainstorm to …"**.

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

### Home Assistant Assist

The custom sentences are in [`examples/custom_sentences/en/brainstorm.yaml`](https://github.com/nukleuz80/ha_brainstorm/blob/main/examples/custom_sentences/en/brainstorm.yaml), the script in [`examples/intent_script.en.yaml`](https://github.com/nukleuz80/ha_brainstorm/blob/main/examples/intent_script.en.yaml).

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

### iPhone and Siri

A shortcut with **Dictate Text** and the Home Assistant action `brainstorm.add_idea`:

```json
{"text": "<Dictated Text>", "source": "siri", "device": "iPhone"}
```

> 🗣️ "Hey Siri, Brainstorm" → "buy a bike lock, very urgent" → note with priority **Urgent**.

The Action button or a back tap can start it too. The steps are [above](#-iphone-shortcut-with-siri-action-button-or-back-tap).

### Microphone in the card

Tap 🎙️ next to the quick input and speak. The text then appears in the field for checking. Recording ends on a pause, on another tap or after 30 seconds. It only works over HTTPS and with an Assist pipeline that has speech-to-text.

## What Brainstorm reads from a sentence

Category, leading words and `!` tags work for any text, spoken or typed. Priority words in the middle of a sentence and due dates are only read from spoken sentences. Typed text is otherwise only corrected for spelling.

### Category

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

### Priority

| Priority | At the start (spoken and typed) | Anywhere in a spoken sentence | Tag (anywhere) |
|---|---|---|---|
| 🔥 Urgent | "Urgent: …", "ASAP …", "Immediately …", "Top priority …" | "urgent", "very urgent", "asap", "right away", "immediately" | `!urgent` |
| 🔴 High | "Important: …", "High priority …", "Priority 1 …" | "important", "very important", "definitely" | `!high` |
| 🟡 Medium | "Normal priority …" | – | `!medium`, `!normal` |
| 🟢 Low | "Someday …", "Eventually …", "No rush, …", "Low priority …" | "someday", "eventually", "whenever there's time", "no rush" | `!low` |

Without any of these, **Medium** applies. Negations and questions do not count: *"not that urgent"* or *"is it important?"* leave the priority alone. The word found is removed from the text: *"Urgent: fix the tap"* becomes *Fix tap* with 🔥.

### Reminders and due dates

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

Without any time, **9:00** applies. How and where you are reminded is set under [Reminders](Settings#integration).
