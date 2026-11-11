🏠 [Home](Home) · 🇩🇪 [Deutsche Version](Fehlerbehebung-und-FAQ)

## 🩺 Common Problems

| Problem | Solution |
|---|---|
| The skill says it cannot reach Home Assistant | Check [**Settings > Repairs**](https://my.home-assistant.io/redirect/repairs/). Home Assistant needs a public HTTPS address, for example Home Assistant Cloud. Then copy the skill code again. |
| Alexa keeps giving the hint to start with *note* | Copy the current voice model into the Alexa developer console, then **Save** and **Build**. |
| *"Alexa, open Brainstorm"* starts the old dialog | Delete the Alexa routines for *open Brainstorm* in the Alexa app. |
| An idea lands in the wrong category | Name the category at the start: *"note for shopping milk"*. A category of your own wins over standard words with its name. |
| A card still shows an old version | Set the resource to the current `?v=` number and reload the page without cache. |
| An Echo is not recognised or ignored | Check the Echo choice under [**Configure**](https://my.home-assistant.io/redirect/integration/?domain=brainstorm). [**Settings > Repairs**](https://my.home-assistant.io/redirect/repairs/) lists chosen Echos that no longer exist. |
| Something else is wrong | Download the diagnostics (see *Entities*) and open an [issue](https://github.com/nukleuz80/ha_brainstorm/issues). |

## ⚠️ Known Limitations

- **Free sentences in the skill:** Alexa only passes text to a skill when the sentence starts with a known word, such as *note*, *we need* or *I have to*. Other sentences end in a short hint to start with *note*.
- **Echo recognition** needs the Alexa Media integration. Without it, ideas from the skill are still saved, but without the Echo they came from.
- **The name "Brainstorm"** is also a band. Without your own skill or routines, Alexa may start music instead.
- **Reminders on Echos** are spoken through Alexa Media. Real Alexa reminders also need the reminder permission of your skill.
- **One installation:** Only one Brainstorm Hub can be set up per Home Assistant.

## ❓ Frequently Asked Questions

**Does Brainstorm Hub cost anything or need a cloud?**
No. Brainstorm Hub is free (MIT license), runs locally in your Home Assistant and does not connect to any external service on its own. You need no account. Only your own Alexa skill needs a public HTTPS address, for example through Home Assistant Cloud.

**Do I need Amazon Alexa?**
No. Ideas come in just as well through the dashboard cards, the microphone in the list card, Home Assistant Assist, an iPhone shortcut with Siri, the Home Assistant to-do lists or automations. See [Voice Control](Voice-Control).

**Do I need an AI?**
No. Brainstorm finds category, priority and due date with its own rules. An AI task entity is optional and adds extras such as subtask suggestions, a mind map from a topic or grouping into themes. See [AI Features](AI-Features).

**Can I share lists with my family?**
Yes. Without privacy every user sees everything. With privacy on, every idea belongs to its person and can be shared per idea or per category to view or to edit. See [Collaboration](Collaboration).

**Does Brainstorm stay in sync with Bring!, Todoist or Google Tasks?**
Yes. A category can be linked to a to-do list of another integration, and Bring! has its own connection. See [Import, Export & Storage](Import-Export-and-Storage).

**Does it work with Obsidian, Logseq or Nextcloud?**
Yes, through the automatic Markdown export into a folder of your choice. The mind map also exports OPML and FreeMind (`.mm`) for Freeplane, XMind and MindManager.

**Which languages are there?**
German and English, for the settings, cards, Alexa skill, Assist sentences and reminders. How to add another language is in [`CONTRIBUTING.md`](https://github.com/nukleuz80/ha_brainstorm/blob/main/CONTRIBUTING.md).

**Where is my data, and is it in the backup?**
In `/config/.storage/brainstorm.storage`, attachments in `/config/brainstorm_attachments/`. Both are part of every normal Home Assistant backup. See [Import, Export & Storage](Import-Export-and-Storage).
