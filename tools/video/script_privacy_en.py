"""Storyboard: privacy, sharing and the backlog for coding AIs (English)."""
from __future__ import annotations

LANG = "en"
TITLE = "Brainstorm Hub: Privacy, Sharing & AI Backlog"
OUT_NAME = "brainstorm-privacy-en"
# Wiki pages this video covers, check them on every release
COVERS = ["Collaboration", "Settings", "AI-Features"]
SPOKEN: list[tuple[str, str]] = [("MCP", "M C P"), ("MQTT", "M Q T T"), ("ha-mcp", "H A M C P"), ("Markdown", "Mark down")]

PATH = "Settings ➔ Devices & services ➔ Brainstorm Hub ➔ Configure"

CHAPTERS: list[dict] = [
    {
        "title": "Privacy",
        "scenes": [
            {
                "v": ("title", "Privacy, Sharing & AI Backlog", "Everyone gets their own list, shared where it fits"),
                "say": "In many homes, several people share one Home Assistant. In this video, "
                       "I'll show you how everyone gets their own entries, how to share on "
                       "purpose, and how a coding AI like Claude Code only sees its own tasks.",
            },
        ],
    },
    {
        "title": "Turn it on",
        "scenes": [
            {
                "v": ("switches", "Brainstorm › Privacy & Users", [
                    ("Keep ideas private", True, True,
                     "Each person then sees only their own entries and what is shared with them"),
                    ("Main user", "Olaf", True, "Owns all existing ideas"),
                    ("Keep exporting to Markdown files", False, False,
                     "These files can be read by anyone with access to the config folder"),
                    ("Offer these users for sharing", "Olaf, Frida, Claude", False,
                     "Hides technical accounts such as MQTT"),
                ], PATH + " ➔ Privacy & Users", "When it's off, every user sees every entry."),
                "say": "By default, everyone sees everything. Under Privacy and Users, turn on "
                       "Keep ideas private and choose a main user, who owns all existing "
                       "entries. From then on, every new entry belongs to the person who "
                       "creates it.",
            },
        ],
    },
    {
        "title": "Share",
        "scenes": [
            {
                "v": ("grid", "Share on purpose", [
                    ("👆", "One entry", "Long-press ➔ 👥 Share"),
                    ("📂", "A category", "Pick the category ➔ 👥 share, also covers later entries"),
                    ("☑️", "Several entries", "Select, then complete, move or share them at once"),
                    ("👀", "View", "Read only"),
                    ("✏️", "Edit", "Change and check off"),
                    ("🔑", "Owner", "Deleting and handing over stay with you"),
                ], "Share with single people or with all users."),
                "say": "You can share a single entry, a whole category, or several entries at "
                       "once. For each person, choose View or Edit. Deleting and handing over "
                       "always stay with the owner.",
            },
            {
                "v": ("bullets", "Writing into other people's lists", [
                    ("🛒", "Frida shares her <b>Shopping</b> category with you to <i>edit</i>"),
                    ("➕", "What you add there lands in <b>her</b> list and belongs to her"),
                    ("✍️", "A badge shows <b>who added it</b>, with the person's picture"),
                ], "Sharing with all users doesn't count for this."),
                "say": "If someone shares a category with you personally to edit, your new "
                       "entries land in their list. A small badge with a name or picture then "
                       "shows who wrote the entry.",
            },
        ],
    },
    {
        "title": "Assign Echos to people",
        "scenes": [
            {
                "v": ("switches", "Brainstorm › Assign Echos & Apps", [
                    ("Echo or Alexa app", "Kids' Room Echo", True, "You can also type a name"),
                    ("Person", "Frida", True, "Leave empty to remove the assignment"),
                ], PATH + " ➔ Assign Echos & Apps to People",
                    "Home Assistant doesn't recognize voices, and everyone in the room can hear."),
                "say": "You can also assign Echos and Alexa apps to people. Whatever is said to "
                       "the Echo in the kids' room then belongs to Frida, and Alexa only reads "
                       "her entries there. Home Assistant doesn't recognize voices, though.",
            },
        ],
    },
    {
        "title": "What privacy can't do",
        "scenes": [
            {
                "v": ("bullets", "To be honest", [
                    ("🛡️", "<b>Administrators</b> and anyone with file access can still read everything"),
                    ("📋", "The Home Assistant <b>to-do lists</b> only show what's shared with everyone"),
                    ("📝", "Old <b>Markdown exports</b> stay, new ones only with your permission"),
                ], "Privacy in Brainstorm protects against curiosity, not against administrators."),
                "say": "Good to know: administrators and anyone with access to the files can "
                       "still read everything. That's why the Home Assistant to-do lists only "
                       "show what's shared with everyone.",
            },
        ],
    },
    {
        "title": "Backlog for coding AIs",
        "scenes": [
            {
                "v": ("grid", "A category as a task list for the AI", [
                    ("🗣️", "Collect", "Tasks by Alexa, card or Assist"),
                    ("🔌", "Read", "The AI reads them through an MCP server for Home Assistant"),
                    ("🔧", "In progress", "Badge with the AI's name"),
                    ("✅", "Check off", "With a result note: what was done"),
                    ("👀", "Shared only", "Everything else stays invisible to the AI"),
                    ("🛑", "Your call", "Deleting, sharing and settings stay with you"),
                ], "Example: Claude Code with ha-mcp."),
                "say": "Brainstorm even works as a task list for coding AIs like Claude Code. "
                       "You collect tasks by voice, the AI reads them through an MCP server, "
                       "does the work, and checks them off with a result note.",
            },
            {
                "v": ("bullets", "Set up in five steps", [
                    ("1", "Under <b>Settings ➔ People</b>, create a user for the AI, for example <i>Claude</i>"),
                    ("2", "As that user, create a <b>long-lived access token</b> and connect the MCP server with it"),
                    ("3", "<b>Turn on privacy</b> and share the backlog category with the AI"),
                    ("4", "Copy the <code>brainstorm-backlog</code> skill from <code>examples/claude-code</code>"),
                    ("5", "Name the category in <code>CLAUDE.md</code>"),
                ], "View to read, Edit if the AI may check things off."),
                "say": "Create a separate user for the AI, and as that user, create a token for "
                       "the MCP server. Turn on privacy, and share only the backlog category. "
                       "You'll find the matching skill for Claude Code in the examples folder.",
            },
            {
                "v": ("shot", "crop_done.png", 330, [
                    ("🔧", "<b>In progress</b> shows what the AI is working on"),
                    ("📌", "The <b>result note</b> says what came of it"),
                    ("↩️", "Completed entries can be <b>restored</b>"),
                ], "So you can see what the AI has done without asking."),
                "say": "On the card, you then see what the AI is working on, and once it's "
                       "checked off, the result note shows what came of it.",
            },
        ],
    },
    {
        "title": "Have fun",
        "scenes": [
            {
                "v": ("bullets", "In short", [
                    ("🔒", "Turn on privacy, choose a main user"),
                    ("👥", "Share entries and categories on purpose"),
                    ("🗣️", "Assign Echos to people"),
                    ("🤖", "A separate user for the AI, share only the backlog"),
                ], "Guide: wiki ➔ Collaboration"),
                "say": "That was privacy in Brainstorm. You'll find all the details in the wiki "
                       "on GitHub. Have fun!",
            },
        ],
    },
]
