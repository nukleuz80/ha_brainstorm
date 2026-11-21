"""Storyboard: installing Brainstorm Hub (English)."""
from __future__ import annotations

LANG = "en"
TITLE = "Installing Brainstorm Hub"
OUT_NAME = "brainstorm-installation-en"
# Wiki pages this video covers, check them on every release
COVERS = ["Installation-and-Setup", "Quick-Start", "Settings"]
SPOKEN: list[tuple[str, str]] = [("HACS", "hacks"), ("Marketplace", "market place"), ("YAML", "yammel"), ("Markdown", "Mark down")]

CHAPTERS: list[dict] = [
    {
        "title": "Introduction",
        "scenes": [
            {
                "v": ("title", "Installing Brainstorm Hub",
                      "From the Marketplace to your first idea in five minutes"),
                "say": "In this video, you'll install Brainstorm Hub. In just a few minutes, "
                       "you'll go from installing to your first idea on the dashboard.",
            },
        ],
    },
    {
        "title": "Requirements",
        "scenes": [
            {
                "v": ("bullets", "What you need", [
                    ("🏠", "<b>Home Assistant 2026.10</b> or newer"),
                    ("📦", "The <b>Marketplace</b> in Settings, built in since 2026.11"),
                    ("🗣️", "Optional: <b>Alexa Media Player</b> for voice input with Alexa"),
                    ("🔒", "No account, no password: Brainstorm doesn't connect to any outside service"),
                ], "On 2026.10 you install through HACS, the steps are almost the same."),
                "say": "You need Home Assistant 2026 point 10 or newer. You install it from the "
                       "Marketplace in Settings. For Alexa, "
                       "you can add the Alexa Media Player integration. You don't need an "
                       "account or a password, Brainstorm doesn't connect to any outside "
                       "service.",
            },
        ],
    },
    {
        "title": "Open the Marketplace",
        "scenes": [
            {
                "v": ("menu", "Settings", [
                    ("Devices & services", False),
                    ("Automations & scenes", False),
                    ("Apps", False),
                    ("Marketplace", True),
                    ("Dashboards", False),
                ], "Settings ➔ Marketplace ➔ Browse",
                   "Brainstorm Hub is in the default list, so you don't need to add a repository."),
                "say": "Next, open Settings and click Marketplace. Switch to Browse at the "
                       "bottom and search for Brainstorm Hub. It's in the default list, so you "
                       "don't need to add a repository.",
            },
        ],
    },
    {
        "title": "Install",
        "scenes": [
            {
                "v": ("ha", "Brainstorm Hub", [
                    ("Status", "Not installed", False, "The latest version is ready to install"),
                    ("Type", "Integration", False, "Made by the community, source code on GitHub"),
                ], "Marketplace ➔ Browse ➔ Brainstorm Hub", "Install"),
                "say": "Now open the entry and click Install. You always get the latest "
                       "version. If you need an older one, pick it from the three dot menu.",
            },
        ],
    },
    {
        "title": "Restart",
        "scenes": [
            {
                "v": ("bullets", "Restart Home Assistant", [
                    ("🔁", "Settings ➔ System ➔ <b>Restart</b> at the top right"),
                    ("🧩", "Only then does Home Assistant know the integration"),
                    ("🎴", "The <b>cards come along</b>: no copying, no resource entry"),
                ], "After that, Brainstorm Hub shows up under Devices & services."),
                "say": "Now restart Home Assistant, under Settings, System, Restart. The cards "
                       "come with the integration. You don't have to copy anything or add a "
                       "resource.",
            },
        ],
    },
    {
        "title": "Add the integration",
        "scenes": [
            {
                "v": ("ha", "Add integration", [
                    ("Search", "Brainstorm", True, ""),
                    ("Result", "💡 Brainstorm Hub", True, ""),
                ], "Settings ➔ Devices & services ➔ Add integration", "Select"),
                "say": "Open Settings, Devices and services, and click Add integration at the "
                       "bottom right. Search for Brainstorm and pick Brainstorm Hub.",
            },
        ],
    },
    {
        "title": "First setup",
        "scenes": [
            {
                "v": ("ha", "Brainstorm Hub", [
                    ("Hide categories without notes (0)", "on", False,
                     "Hides categories that have no notes from the cards."),
                    ("Auto-export ideas to Markdown files", "off", True,
                     "One file per category, for example for Obsidian"),
                    ("File path for Markdown files", "/config/brainstorm", False, ""),
                ], "Nothing is required, the defaults work for everyone", "Submit"),
                "say": "The first setup only asks two things: whether to hide empty "
                       "categories, and whether Brainstorm should export your ideas to "
                       "Markdown files. None of it is required. Just click Submit.",
            },
        ],
    },
    {
        "title": "Add the card",
        "scenes": [
            {
                "v": ("shot", "crop_list.png", 450, [
                    ("✏️", "Dashboard ➔ <b>Edit</b>"),
                    ("➕", "<b>Add card</b> and search for “Brainstorm”"),
                    ("🎴", "Pick the <b>Brainstorm Card</b> and save"),
                    ("⚙️", "Options in the card editor, like title and colors"),
                ], "The card editor shows a preview right away."),
                "say": "Open your dashboard, click Edit, then Add card. Search for Brainstorm "
                       "and pick the Brainstorm Card. And there's your list card, with quick "
                       "input and categories.",
            },
            {
                "v": ("yaml", "Or with YAML", "type: custom:brainstorm-card\ntitle: Brainstorm Hub",
                      "All card options are in the wiki."),
                "say": "If you prefer YAML, you only need two lines: the type "
                       "custom:brainstorm-card, and a title.",
                "speak": "If you prefer YAML, you only need two lines: the type custom "
                         "brainstorm card, and a title.",
            },
        ],
    },
    {
        "title": "Mind map card",
        "scenes": [
            {
                "v": ("shot", "crop_mindmapzoom.png", 450, [
                    ("🧠", "Add the <b>Brainstorm Mindmap Card</b> the same way"),
                    ("🖥️", "Best as a <b>panel view</b> on a tablet or monitor"),
                    ("🎨", "Styles, color schemes and seven views"),
                    ("⛶", "Full screen with the button at the top right"),
                ], "The list card also has a built-in mind map button."),
                "say": "Add the mind map card the same way. It works best as a panel view on "
                       "a tablet or a monitor.",
            },
        ],
    },
    {
        "title": "Your first idea",
        "scenes": [
            {
                "v": ("transform", "Garden: cut the tree", "Cut the tree",
                      ["📂 House & Garden", "🟡 Medium", "💻 Dashboard"],
                      "A word with a colon at the start picks the category."),
                "say": "Time for your first idea. Type into the card: garden, colon, cut the "
                       "tree, and press Enter. Brainstorm files cut the tree under House and "
                       "Garden.",
            },
        ],
    },
    {
        "title": "Configure",
        "scenes": [
            {
                "v": ("grid", "Brainstorm Hub ➔ Configure", [
                    ("📁", "Categories", "Add, rename, sort"),
                    ("🎨", "Category design", "Icon and color per category"),
                    ("⚙️", "General", "Default category, text optimization, Echos"),
                    ("🗣️", "Alexa", "Voice input and your own skill"),
                    ("⏰", "Reminders", "Channels, quiet hours, briefing"),
                    ("👥", "Privacy", "Owners and sharing"),
                ], "Settings ➔ Devices & services ➔ Brainstorm Hub ➔ Configure"),
                "say": "Everything else is under Configure: categories and their colors, text "
                       "optimization, Alexa, reminders and privacy. But the defaults already "
                       "work as they are.",
            },
        ],
    },
    {
        "title": "Updates",
        "scenes": [
            {
                "v": ("bullets", "Stay up to date", [
                    ("🔔", "New versions show up as an update under <b>Settings</b>"),
                    ("⬇️", "Click <b>Update</b>, then restart"),
                    ("📜", "What's new is in the <b>changelog</b>"),
                    ("🧰", "Without the Marketplace: download the release, copy <code>custom_components/brainstorm</code> to <code>/config/custom_components/</code>"),
                ], "Your ideas are kept with every update."),
                "say": "New versions show up as an update under Settings. Click Update, restart, done. "
                       "Your ideas are always kept.",
            },
        ],
    },
    {
        "title": "What's next?",
        "scenes": [
            {
                "v": ("bullets", "Next steps", [
                    ("🎬", "Video: <b>The key features</b>"),
                    ("🗣️", "Video: <b>Your own Alexa skill</b>"),
                    ("📘", "The <b>wiki</b> with guides and examples"),
                    ("💬", "Questions and ideas as an <b>issue on GitHub</b>"),
                ], "github.com/nukleuz80/ha_brainstorm"),
                "say": "That's it! The videos about the key features and your own Alexa skill "
                       "show what's next. Have fun with Brainstorm!",
            },
        ],
    },
]
