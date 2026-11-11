🏠 [Home](Home) · 🇩🇪 [Deutsche Version](Zusammenarbeit)

## 👥 Privacy & Sharing

By default, all users of your Home Assistant see all ideas. Change this under **Brainstorm Hub ➔ Configure ➔ Privacy & Users**, and choose a **main user** who owns all existing ideas.

- **When on:** Every idea belongs to its creator, and only they and people it is shared with can see it.
- **Single ideas:** Long-press an idea ➔ **Share**, for each person to view or edit, or for all users.
- **Categories:** Select a category ➔ **👥 Share …**. This covers your own ideas in it, including later ones.
- **Several ideas:** **☑️ Select**, then complete, move, share or delete them at once. This also works without privacy.
- **Rights:** Edit allows changing and completing. Deleting and passing on stay with the owner.
- **Writing into someone else's list:** If someone shares a category with you personally to *edit*, your new ideas in it go into their list and belong to them. The same goes for subtasks of their ideas. A share with *all users* does not count, and if several people shared the same category with you, the idea stays yours.
- **Who added it:** If an idea in your list comes from someone else, both cards show a badge with their name, such as *✍️ Claude*. If their person in Home Assistant has a picture, the list card shows it instead of ✍️. This way you see at a glance what an AI added through its own user.
- **Echos and Alexa apps:** Under **Assign Echos & Apps to People**, each device belongs to one person. What is said there is theirs, and only their ideas are read out. Home Assistant cannot recognize voices, and everyone in the room can hear it.

Admins and anyone with file access can still read everything. Home Assistant's to-do lists only show what is shared with everyone, because all users can read them. Existing Markdown exports stay in place when you switch this on, and new ones are only created if you allow it.

## 🗳️ Together on the map

- **Voting and reactions (v1.10.7):** 🗳️ at the bottom right or **V** starts a vote in a category: everyone gets, say, 5 votes and hands them out with − / + on the notes, in the mind map and in the list. Hidden, everyone sees only their own votes until the end. Ending it shows the ranking with 🥇🥈🥉, and one tap sorts the category by it. Plus reactions 👍 ❤️ 😂 ❗ on every note (context menu, or ⋯ in the mind map); people who may only view a shared note may still react and vote.
- **Comments (v1.11.2):** 💬 in the list's context menu or under ⋯ in the mind map opens the thread of a note: who, when, what, with formatting. A note with comments shows 💬 and the count; tap it to open the thread. **@Name** tells that person over their channels under *Reminders ➔ Persons*. You can delete your own comments; whoever may change the note can delete any. People who may only view a shared note may still comment.
- **Live presence (v1.11.8):** the top left of the mind map shows who has the same list open right now, as a circle with their initials, a person with two devices only once. When somebody edits a note, their circle gets a ring and the note shows ✏️ with the name; the tooltip names the note. It runs over the Home Assistant WebSocket connection, nothing of it is stored.
- **Hidden brainstorm round (v1.11.5):** tick *🙈 Hidden* in the ⚡ brainstorm dialog: until the reveal, everyone sees only their own new ideas in that category, so nobody sways the others. A bar above the map offers *Join* and *Reveal*; with a timer the round reveals itself when time is up. Whoever cannot see a hidden idea cannot change it either; Alexa notes without a person stay visible.
