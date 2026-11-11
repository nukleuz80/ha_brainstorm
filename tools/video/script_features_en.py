"""Storyboard: Brainstorm Hub feature overview (English)."""
from __future__ import annotations

LANG = "en"
TITLE = "Brainstorm Hub: The Key Features"
OUT_NAME = "brainstorm-features-en"
# Wiki pages this video covers, check them on every release
COVERS = ["List-Card", "Mind-Map-and-Pinboard", "Collaboration", "AI-Features", "Reminders", "Voice-Control"]
# Spoken replacements for terms the English voice gets wrong
SPOKEN: list[tuple[str, str]] = [
    ("PDFs", "P D Fs"), ("PDF", "P D F"), ("OPML", "O P M L"), ("HACS", "hacks"),
    ("Todoist", "Todo-ist"), ("asap", "A, S, A, P"), ("Kanban", "Kahn-bahn"),
    ("Markdown", "Mark down"), ("at sign and", "symbol at, and"),
]

CHAPTERS: list[dict] = [
    {
        "title": "What is Brainstorm?",
        "scenes": [
            {
                "v": ("shot", "crop_list.png", 450, [
                    ("💡", "Ideas, tasks and shopping <b>in one place</b> in Home Assistant"),
                    ("🗣️", "Capture by <b>voice</b>, card or phone"),
                    ("🧠", "Brainstorm <b>sorts it for you</b>: category, priority, due date"),
                    ("🔒", "Runs locally, your data stays with you"),
                ], "An integration for Home Assistant, available in HACS."),
                "say": "This is Brainstorm Hub. Brainstorm collects your ideas, tasks and "
                       "shopping in one place in Home Assistant. Just say or type whatever "
                       "comes to mind, and Brainstorm sorts it for you.",
            },
        ],
    },
    {
        "title": "Capture by voice",
        "scenes": [
            {
                "v": ("grid", "Wherever you are", [
                    ("🗣️", "Alexa", "“Alexa, ask Brainstorm to note dim the basement light”"),
                    ("✨", "Assist", "“Note create a database backup”"),
                    ("🍎", "Siri", "Shortcut, Action button or Back Tap"),
                    ("🎙️", "Microphone", "Speak right into the card"),
                    ("🤖", "AI assistant", "“The hedge is trimmed” checks it off"),
                    ("⌨️", "Quick idea", "Type, press Enter, done"),
                ], "Every entry remembers where it came from, down to the single Echo."),
                "say": "You can capture from anywhere: with Alexa on your Echo, with Assist, "
                       "with Siri on your iPhone, through the microphone in the card, or with "
                       "an AI assistant. Every entry remembers where it came from, down to the "
                       "single Echo.",
            },
        ],
    },
    {
        "title": "Understands whole sentences",
        "scenes": [
            {
                "v": ("transform", "I really need to call the doctor tomorrow asap", "Call doctor",
                      ["⏰ Tomorrow 9:00", "🔥 Urgent", "📂 Daily Life"],
                      "Filler words removed, due date and priority detected."),
                "say": "Brainstorm understands whole sentences. I really need to call the "
                       "doctor tomorrow asap, becomes: call doctor. Due tomorrow morning, "
                       "and marked as urgent.",
            },
            {
                "v": ("transform", "urgent garden: repair the lawn mower", "Repair lawn mower",
                      ["🔥 Urgent", "📂 House & Garden"],
                      "Brainstorm picks categories from keywords like garden, heating or lamp."),
                "say": "Signal words like urgent or important set the priority, and keywords "
                       "like garden pick the right category.",
            },
        ],
    },
    {
        "title": "The list card",
        "scenes": [
            {
                "v": ("shot", "crop_list.png", 450, [
                    ("⚡", "Type a <b>quick idea</b> at the top"),
                    ("🏷️", "<b>Categories</b> as filters with counters"),
                    ("🎨", "<b>Priorities</b> in color, one click cycles them"),
                    ("🔍", "<b>Search</b> as you type, including #tags"),
                ], "Check off with the circle, everything else is behind the three dots."),
                "say": "The list card shows everything on your dashboard. Type a quick idea at "
                       "the top, filter by category below, and search finds any note as you "
                       "type, even by tag. Click the circle to check a note off, and the three "
                       "dots open everything else.",
            },
            {
                "v": ("grid", "As much as you need", [
                    ("🌱", "Beginner", "Input, categories, checking off, search"),
                    ("🙂", "Normal", "Adds subtasks, markers, attachments and views"),
                    ("🚀", "Pro", "Every field and feature"),
                    ("📱", "Per card", "The kitchen tablet stays simple"),
                    ("🔒", "Nothing gets lost", "Values you set stay visible"),
                    ("➕", "More fields …", "Still shows everything in the dialog"),
                ], "Set it under Configure, General Settings."),
                "say": "You decide how much the cards show. Beginners only see the essentials. "
                       "Normal adds subtasks, markers and views, and Pro shows everything. "
                       "Each card can have its own level, for example a simple kitchen tablet.",
            },
        ],
    },
    {
        "title": "Subtasks & details",
        "scenes": [
            {
                "v": ("shot", "crop_projekte.png", 450, [
                    ("🌿", "<b>Subtasks</b> right below the main task"),
                    ("✨", "The <b>AI suggests subtasks</b>, you pick"),
                    ("📝", "<b>Description</b> with links and some Markdown"),
                    ("📎", "<b>Attachments</b>: photos, PDFs, screenshots"),
                ], "Long lists can be collapsed."),
                "say": "Split big plans into subtasks. With an AI in Home Assistant, the star "
                       "button suggests the right steps. Add a description with links, and "
                       "attachments like photos or PDFs.",
            },
        ],
    },
    {
        "title": "The mind map",
        "scenes": [
            {
                "v": ("shot", "crop_mmprojekte.png", 450, [
                    ("🧠", "All your ideas as a <b>mind map</b>"),
                    ("⭐", "<b>Markers</b>, progress and <b>numbering</b> 1., 1.1"),
                    ("🔗", "<b>Cross links</b> and callouts"),
                    ("🎯", "<b>Focus</b> on a single branch"),
                ], "Each note: ✓ done, 🌿 sub-idea, ✏️ edit, ⋯ for the rest."),
                "say": "The mind map shows your ideas as a map. Subtasks hang as branches from "
                       "their idea and can be numbered. Markers like a star or a question mark, "
                       "cross links and callouts keep it clear, and focus mode shows a single "
                       "branch.",
            },
            {
                "v": ("shot", "crop_kanban.png", 450, [
                    ("◎", "<b>Around the center</b>, tree or org chart"),
                    ("☰", "<b>Outline</b> like in an outliner"),
                    ("▥", "<b>Kanban</b>: open, in progress, waiting, done"),
                    ("📅", "<b>Timeline</b> and Eisenhower matrix"),
                ], "A button at the bottom right switches the view."),
                "say": "The same notes come in seven views: around the center, as a tree, an "
                       "org chart or an outline, as a Kanban board by status, as a timeline by "
                       "due date, or as an Eisenhower matrix.",
            },
            {
                "v": ("grid", "Even more on the mind map", [
                    ("🔍", "Search & filter", "By priority, markers, tags and due date"),
                    ("🎨", "Rules", "Everything urgent in red, #garden green with a star"),
                    ("▶️", "Present", "Full screen, note by note"),
                    ("⚡", "Brainstorm mode", "With a timer, every Enter is a note"),
                    ("📄", "Export", "Image, PDF, Markdown, OPML and FreeMind"),
                    ("✨", "AI help", "Summarizes branches, sorts notes, builds whole maps"),
                ], "Templates like a SWOT analysis or a packing list add ready-made branches."),
                "say": "There's also search and filters, rules that color matching notes, a "
                       "presentation mode, and a brainstorm mode with a timer. Export as an "
                       "image, PDF, Markdown, OPML or FreeMind, and let the AI sum up a whole "
                       "branch in a few sentences.",
            },
        ],
    },
    {
        "title": "Together & with AI",
        "scenes": [
            {
                "v": ("shot", "crop_social.png", 450, [
                    ("🗳️", "<b>Voting</b> with votes per person, hidden if you like"),
                    ("❤️", "<b>Reactions</b> like heart, thumbs up or important"),
                    ("🗺️", "The <b>minimap</b> shows where you are on the map"),
                    ("🏆", "After the round, <b>sort by votes</b>"),
                ], "Start a vote: 🗳️ at the bottom right or the V key."),
                "say": "Brainstorm is made for the whole family, too. Start a vote, and "
                       "everyone spreads their votes across the best ideas, hidden if you like. "
                       "Reactions like a heart or a thumbs up show quickly what you like. On "
                       "big maps, the minimap helps you find your way.",
            },
            {
                "v": ("shot", "crop_comments.png", 450, [
                    ("💬", "<b>Comments</b> on every note, in the list card too"),
                    ("📣", "<b>@name</b> mentions a person"),
                    ("📱", "Mentioned people get a <b>notification</b>"),
                    ("🔒", "Only people who can see the note are notified"),
                ], "The speech bubble on the note shows how many comments there are."),
                "say": "Discuss right on any note. Mention someone with an at sign and their "
                       "name, and they get a notification on their phone, but only if they're "
                       "allowed to see the note.",
            },
            {
                "v": ("shot", "crop_aimap.png", 450, [
                    ("✨", "<b>Map from a topic</b>: a keyword or a long text"),
                    ("🌳", "The AI builds up to <b>three levels</b>"),
                    ("☑️", "<b>Pick and rename</b> before you add"),
                    ("🔁", "<b>New suggestions</b> if it doesn't fit yet"),
                ], "Needs an AI in Home Assistant, for example through AI Task."),
                "say": "And if you don't know where to start, give the AI a topic like plan a "
                       "summer party in the garden, and it sketches out a whole mind map. Uncheck what "
                       "you don't want, change the texts, and add the rest with one click.",
            },
        ],
    },
    {
        "title": "Reminders",
        "scenes": [
            {
                "v": ("grid", "Brainstorm thinks ahead", [
                    ("⏰", "Due dates", "“remind me tomorrow at 8 to take out the bins”"),
                    ("🔊", "Alexa announcement", "Your Echo says it, your phone follows if needed"),
                    ("📱", "Notification", "With buttons for Done and Later"),
                    ("🏠", "Places", "“when I'm at the store, remind me of the milk”"),
                    ("🔁", "Recurring", "Daily, weekly, monthly: check it off and it comes back"),
                    ("🌙", "Quiet hours", "Everything stays silent at night"),
                ], "Optionally as a real Alexa reminder or in your calendar."),
                "say": "When a note has a due date, Brainstorm reminds you: with an Alexa "
                       "announcement, a notification on your phone, or when you arrive "
                       "somewhere. Recurring tasks come back on their own after you check them "
                       "off, and everything stays silent at night.",
            },
        ],
    },
    {
        "title": "Alexa skill & Echo Show",
        "scenes": [
            {
                "v": ("speech", [
                    ("du", "Alexa, ask Brainstorm to read shopping."),
                    ("alexa", "In Shopping: milk and shower gel."),
                    ("du", "Alexa, ask Brainstorm: done milk."),
                ], "With your own skill: one sentence, one answer"),
                "say": "With your own Alexa skill, Alexa answers with exactly one sentence. "
                       "Have your lists read out, and check things off by voice. An Echo Show "
                       "even shows your lists to tap. A separate video shows how to set it up.",
            },
        ],
    },
    {
        "title": "Done & result",
        "scenes": [
            {
                "v": ("shot", "crop_done.png", 330, [
                    ("✅", "Completed notes stay visible and can be <b>restored</b>"),
                    ("📌", "<b>Result note</b>: what came of it"),
                    ("🔧", "<b>In progress</b> badge with a name"),
                    ("🤖", "Great as a <b>backlog for coding AIs</b> like Claude Code"),
                ], "Brainstorm can clean up completed notes after a number of days."),
                "say": "Completed notes stay visible and can be restored. A result note shows "
                       "what came of it. That even makes a category a great task list for "
                       "coding AIs like Claude Code.",
            },
        ],
    },
    {
        "title": "Connected to everything",
        "scenes": [
            {
                "v": ("grid", "Fits your smart home", [
                    ("📋", "To-do lists", "Every category is a real to-do list in Home Assistant"),
                    ("🛒", "Bring!", "Shopping lists in both directions"),
                    ("🔁", "Linked lists", "Google Tasks, Todoist and others"),
                    ("📝", "Markdown", "Export for Obsidian and friends"),
                    ("💾", "JSON", "Back up and move to another system"),
                    ("🧩", "Automations", "Services, events and a sensor"),
                ], "Built following the Home Assistant guidelines."),
                "say": "Every category is a real to-do list in Home Assistant. Brainstorm talks "
                       "to Bring, Google Tasks and Todoist, exports to Markdown, and offers "
                       "services and events for your automations.",
            },
        ],
    },
    {
        "title": "Privacy & sharing",
        "scenes": [
            {
                "v": ("bullets", "To each their own", [
                    ("👤", "Every entry belongs to the person who created it"),
                    ("👥", "<b>Share</b> per entry or category: view or edit"),
                    ("🗣️", "<b>Assign Echos to people</b>: each hears only their own"),
                    ("☑️", "Complete, move or share several entries at once"),
                ], "When it's off, every user sees every entry."),
                "say": "For families, there's privacy: every entry belongs to its person and "
                       "can be shared on purpose. Assign your Echos to people, and Alexa reads "
                       "each person only their own entries.",
            },
        ],
    },
    {
        "title": "Get started",
        "scenes": [
            {
                "v": ("bullets", "Ready in three steps", [
                    ("1", "Search <b>HACS</b> for <b>Brainstorm Hub</b> and install it"),
                    ("2", "Restart Home Assistant, add the <b>Brainstorm Hub</b> integration"),
                    ("3", "Add the <b>Brainstorm Card</b> to your dashboard, done"),
                ], "Guide and videos: github.com/nukleuz80/ha_brainstorm"),
                "say": "Brainstorm installs in a few minutes through HACS. Then add the "
                       "integration and drop the card onto your dashboard. You'll find the "
                       "guide on GitHub. Have fun with your ideas!",
            },
        ],
    },
]
