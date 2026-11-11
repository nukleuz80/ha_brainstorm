"""Storyboard: iPhone shortcut with Siri, Action button or Back Tap (English)."""
from __future__ import annotations

LANG = "en"
TITLE = "Brainstorm Hub: Ideas with an iPhone Shortcut"
OUT_NAME = "brainstorm-iphone-en"
# Wiki pages this video covers, check them on every release
COVERS = ["Voice-Control"]
SPOKEN: list[tuple[str, str]] = [("JSON", "Jason")]

CHAPTERS: list[dict] = [
    {
        "title": "Shortcut",
        "scenes": [
            {
                "v": ("title", "Ideas with an iPhone Shortcut", "Trigger, speak, done"),
                "say": "The fastest way from your iPhone to Brainstorm: trigger, speak, done, "
                       "without opening an app. In two minutes, you'll build a shortcut for it.",
            },
            {
                "v": ("bullets", "What you need", [
                    ("📱", "The <b>Home Assistant Companion app</b>, signed in to your Home Assistant"),
                    ("⚡", "The <b>Shortcuts</b> app, built into every iPhone"),
                    ("🧠", "Brainstorm Hub, set up as in the installation video"),
                ], "The shortcut calls the brainstorm.add_idea action."),
                "say": "All you need is the Home Assistant Companion app, and the Shortcuts app, "
                       "which is already on every iPhone.",
            },
        ],
    },
    {
        "title": "Create the shortcut",
        "scenes": [
            {
                "v": ("phone", "Shortcuts ➔ ＋", [
                    ("<small>Name</small><b>Brainstorm</b>", True),
                    ("<small>Action 1</small>🎙️ <b>Dictate Text</b><br>Language: English<br>"
                     "Stop Listening: After Pause", True),
                    ("<small>Action 2</small>…", False),
                ], [
                    ("1", "Create a new shortcut and name it <b>Brainstorm</b>"),
                    ("2", "Add the <b>Dictate Text</b> action"),
                    ("3", "Language <b>English</b>, Stop Listening <b>After Pause</b>"),
                ], "The name is also your Siri phrase."),
                "say": "Open the Shortcuts app, tap plus, and name the shortcut Brainstorm. The "
                       "name is also your Siri phrase. Add the Dictate Text action, with your "
                       "language, and Stop Listening set to After Pause.",
            },
        ],
    },
    {
        "title": "Call Home Assistant",
        "scenes": [
            {
                "v": ("phone", "Shortcut: Brainstorm", [
                    ("<small>Action 1</small>🎙️ Dictate Text", False),
                    ("<small>Action 2 · Home Assistant</small><b>Perform Action</b><br>"
                     "Add idea<br><small>brainstorm.add_idea</small>", True),
                ], [
                    ("4", "Add <b>Perform Action</b> from <b>Home Assistant</b>"),
                    ("5", "Choose <b>Add idea</b> as the action"),
                ], "Can't find it? Open the Companion app once."),
                "say": "Next, find the Home Assistant action Perform Action, and choose Add "
                       "idea from Brainstorm.",
            },
            {
                "v": ("yaml", "The data field",
                      '{"text": "", "source": "siri", "device": "iPhone"}\n\n'
                      '          ^\n          insert the “Dictated Text” variable here',
                      "You can choose any device name after device."),
                "say": "The data field gets this short JSON text. Put the Dictated Text "
                       "variable between the quotes after text. You can pick any device name "
                       "at the end.",
            },
            {
                "v": ("bullets", "Important: straight quotes", [
                    ("⚠️", "Error <b>“The data couldn't be read”</b>? Then the JSON is invalid"),
                    ("❝", "When you type, the iPhone likes to insert <b>curly quotes</b>"),
                    ("📋", "Best to <b>copy and paste</b> the text"),
                    ("⚙️", "Or turn it off for a moment: Settings ➔ General ➔ Keyboard ➔ <b>Smart Punctuation</b>"),
                ], "The template to copy is in the wiki."),
                "say": "A common pitfall: when you type, the iPhone replaces straight quotes with "
                       "curly ones. Then the shortcut says the data couldn't be read. So it's "
                       "best to copy the text from the guide.",
            },
        ],
    },
    {
        "title": "Choose a trigger",
        "scenes": [
            {
                "v": ("grid", "Three ways to start it", [
                    ("🔘", "Action button", "Settings ➔ Action Button ➔ Shortcut ➔ Brainstorm"),
                    ("👆", "Back Tap", "Accessibility ➔ Touch ➔ Back Tap ➔ Double Tap"),
                    ("🗣️", "Siri", "“Hey Siri, Brainstorm”"),
                ], "The Action button is on iPhone 15 Pro and newer."),
                "say": "Now you just need a trigger. On newer iPhones, put the shortcut on the "
                       "Action button. Or double tap the back of your iPhone. And of course, "
                       "this always works: Hey Siri, Brainstorm.",
            },
        ],
    },
    {
        "title": "Try it",
        "scenes": [
            {
                "v": ("transform", "fix the dripping faucet in the bathroom", "Fix dripping faucet in the bathroom",
                      ["🍎 Siri (iPhone)", "📂 House & Garden"],
                      "The note shows the Apple logo and the device name."),
                "say": "Let's try it: press the Action button and say, fix the dripping "
                       "faucet in the bathroom. Seconds later, the note is in Brainstorm, with "
                       "an Apple logo and the name of your iPhone.",
            },
            {
                "v": ("shot", "crop_list.png", 450, [
                    ("🧠", "Brainstorm sorts as always: <b>category, priority, due date</b>"),
                    ("🗣️", "Whole sentences work too: <i>“urgently call the doctor tomorrow”</i>"),
                    ("🏷️", "Source <b>Siri (iPhone)</b> on the note"),
                ], "Due dates in the sentence are detected too."),
                "say": "Brainstorm sorts the note as usual. Whole sentences with a due date or "
                       "priority work too, like: urgently call the doctor tomorrow.",
            },
        ],
    },
    {
        "title": "Have fun",
        "scenes": [
            {
                "v": ("bullets", "In short", [
                    ("1", "Shortcut <b>Brainstorm</b> with <b>Dictate Text</b>"),
                    ("2", "Home Assistant: <b>Add idea</b> with the JSON data field"),
                    ("3", "Put it on the Action button, Back Tap or Siri"),
                ], "Guide: wiki ➔ Voice Control ➔ iPhone"),
                "say": "And that's all. Create the shortcut, add the Home Assistant action, and choose a trigger. "
                       "You'll find the written guide on GitHub. Have fun!",
            },
        ],
    },
]
