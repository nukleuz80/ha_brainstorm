🏠 [Home](Home) · 🇩🇪 [Deutsche Version](KI-Funktionen)

## ✨ What the AI can do

- 🤖 **Assist LLM Tools & Function-Calling API:**
  - **Natural Conversational AI:** Native integration with Home Assistant's LLM API (`homeassistant.helpers.llm`). Works with OpenAI, Google Gemini, Ollama, and local models.
  - **5 AI Tools Included:** `brainstorm_add_idea`, `brainstorm_get_ideas`, `brainstorm_complete_idea`, `brainstorm_delete_idea`, and `brainstorm_list_categories`.
- **Subtasks from the AI (v1.6.26):** With an AI task entity set under *Configure ➔ AI*, ✨ on a note asks it for up to 8 subtasks. You untick what you do not want, can change the texts, and only what you save is added under the note. Only this note and its subtasks go to the AI, and only when you press the button. One undo removes them all again. The list card has ✨ too (v1.6.28): next to ✎ on every main task, and in the menu on a long press or right click. If the AI's provider refuses because it is overloaded, Brainstorm asks once more after 2 seconds and otherwise says that the AI cannot be reached right now (v1.6.29).
- **AI: map from a topic or text (v1.11.1):** ✨ *Create map from a topic* on an empty map, key **G**, or ✨ *Create with AI* under 🖼️ ➔ *Insert an outline*. A topic such as “Plan a summer party” or a pasted text becomes a preview with up to three levels below a title. Untick what you do not want (its points move up), edit the texts, add them; ↶ takes it all back. It lands in the focused branch or the chosen category.
- **AI: group into themes (v1.11.4):** lots of loose notes in a category? Key **K**, ✨ *Group into themes* at the end of a brainstorm round, or in the *Sort in loose ideas* dialog when nothing fits there: the AI groups the main notes without subtasks into three to seven themes. In the preview you tick themes and notes and change the titles; each theme becomes a new parent note in the place of the first note, with the notes below it. ↶ takes it back. Needs at least four loose notes.
- **AI help on the map (v1.8.9):** with an AI task entity, ✨ on a note with subtasks can also **summarize the branch** in a few sentences, which can become the description. **Sort in loose ideas** (key **Z**, or at the end of a brainstorm round) suggests a parent for every loose main note of the category; you tick what to keep. Nothing changes before you confirm, ↶ takes it back.

## AI assistant (LLM)

A conversation agent such as OpenAI, Google Gemini or Ollama can use Brainstorm when you also select **Brainstorm Hub** under **Control Home Assistant** in its options. It gets these tools:

| Tool | Example |
|---|---|
| `brainstorm_add_idea` | "Write down that we need charcoal for Saturday." |
| `brainstorm_get_ideas` | "What is still on my garden list?" |
| `brainstorm_complete_idea` | "I bought the charcoal." |
| `brainstorm_delete_idea` | "Delete the note about the bike lock." |
| `brainstorm_list_categories` | "Which lists are there?" |

Under **Configure ➔ AI** you can also pick an AI service that cleans up spoken text.

## 🤖 Brainstorm as a task list for coding AIs

A category can be the backlog of a programming project: you collect tasks by Alexa, card or Assist, and a coding AI such as Claude Code reads them over an MCP server for Home Assistant, implements them and ticks them off with a **result note**. Both cards show this note below the idea, so you see what came of it without asking.

**Setup**

1. **A user of its own for the AI:** Under [**Settings ➔ People**](https://my.home-assistant.io/redirect/people/), add a user, for example *Claude*. If its person gets a picture, the cards show it on the ideas the AI adds.
2. **Token:** Log in as this user, create a long-lived access token under [**Profile ➔ Security**](https://my.home-assistant.io/redirect/profile_security/) and connect the MCP server with it, for example [ha-mcp](https://github.com/homeassistant-ai/ha-mcp). Whether the user needs admin rights depends on how ha-mcp runs, see the note below.
3. **Switch privacy on** (see above) and share the backlog category with the AI user: *view* to read, *edit* if it may tick ideas off. Everything else stays invisible to it.
4. **Install the skill:** Copy the folder [`examples/claude-code/skills/brainstorm-backlog`](https://github.com/nukleuz80/ha_brainstorm/blob/main/examples/claude-code/skills/brainstorm-backlog/SKILL.md) to `~/.claude/skills/` (for all projects) or to `.claude/skills/` in the project.
5. **Name the category:** Write it into the project's `CLAUDE.md` or `AGENTS.md`, for example: *"The backlog is the Brainstorm category 'Brainstorm'."*

**Working rules of the skill**

- It reads only over `brainstorm.get_ideas`, never the file in `.storage`. This way the AI only sees what is shared.
- Subtasks are done in their order, conditions in the text ("check first whether …") come first.
- When it starts on an idea, it marks it with `in_progress: true`. Both cards then show **🔧 In progress** with the AI user's name, and hovering over the badge shows since when. Ticking off removes the mark; if the AI stops early, it removes it with `in_progress: false`. You can set and remove the mark yourself in the long-press menu (v1.7.10).
- It ticks off only what is implemented, tested and committed, with `status: completed` and a short `result` (version, change, test, open points). The reply names every idea it ticked off.
- Deleting, shares and settings stay with you. When an action is refused, the AI tells you which share is missing instead of trying another way.

> [!NOTE]
> **Admin or not?** Brainstorm itself needs no admin rights to read, add, edit and tick off; only removing categories and the Markdown export require them while privacy is on. A user without admin rights is the safer choice, because an admin can read private ideas in other ways, such as file access. Whether that works depends on how you run ha-mcp (checked in the code of ha-mcp 9.1.0, not yet tried live):
>
> - **ha-mcp as its own server or app (add-on)**, connected with `HOMEASSISTANT_TOKEN`: a token of a user without admin rights works. ha-mcp does not officially support it and warns about it; its admin-only tools (automations, configuration, logs and the like) fail. Service calls go over the WebSocket, so `brainstorm.get_ideas` and `brainstorm.update_idea` work. ha-mcp avoids the admin-only REST routes, so the refused requests are not counted as failed logins and do not get its address banned.
> - **HA-MCP custom component (server inside Home Assistant, via HACS):** it always talks to Home Assistant with the token of an administrator and checks this on every start, so the AI user has to be an administrator here. Create the token as that user anyway: Brainstorm then shows the AI only the shared categories, and the cards show its ideas under its name. File access stays open to it.
