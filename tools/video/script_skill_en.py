"""Storyboard of the Brainstorm Alexa skill video (English)."""
from __future__ import annotations

LANG = "en"
# Wiki pages this video covers, check them on every release
COVERS = ["Voice-Control", "Reminders"]
TITLE = "Brainstorm: Set Up Your Own Alexa Skill"
OUT_NAME = "brainstorm-alexa-skill-en"
SPOKEN: list[tuple[str, str]] = [
    ("HTTPS", "H T T P S"), ("JSON", "Jason"), ("Node.js", "Node J S"), ("APL", "A P L"),
]

# Every chapter is one setting. Visual kinds: title, bullets, wizard, console, ha,
# speech, code, alexa_app.
CHAPTERS: list[dict] = [
    {
        "title": "Introduction",
        "scenes": [
            {
                "v": ("title", "Your own Alexa skill for Brainstorm",
                      "Step by step through every important setting"),
                "say": "Welcome! In this video, you'll set up your own Alexa skill for "
                       "Brainstorm. We'll go through each important setting in its own "
                       "chapter.",
            },
            {
                "v": ("speech", [
                    ("du", "Alexa, ask Brainstorm to note dim the basement light."),
                    ("alexa", "Saved under Smart Home."),
                ], "With a skill: one sentence, one answer"),
                "say": "The advantage: without a skill, Alexa often reports an error first. "
                       "With your skill, there's exactly one answer, and the idea lands in the "
                       "right category right away.",
            },
        ],
    },
    {
        "title": "Requirements",
        "scenes": [
            {
                "v": ("bullets", "What you need", [
                    ("✅", "Brainstorm Hub is installed in Home Assistant"),
                    ("🔑", "A free Amazon developer account, <b>the same account as your Echos</b>"),
                    ("🌐", "Home Assistant reachable over <b>HTTPS from the internet</b>, for example through Home Assistant Cloud"),
                    ("📡", "Optional: the <b>Alexa Media</b> integration for device detection and free sentences"),
                ], "Using the same Amazon account is the most common pitfall."),
                "say": "You need a free Amazon developer account. Important: it has to be the "
                       "same Amazon account your Echos are signed in with. Home Assistant also "
                       "has to be reachable over HTTPS from the internet, for example through "
                       "Home Assistant Cloud.",
            },
            {
                "v": ("bullets", "Check the external address", [
                    ("⚙️", "Settings ➔ System ➔ Network"),
                    ("🔗", "The <b>Internet</b> field is set, or Home Assistant Cloud is active"),
                    ("🧩", "Brainstorm builds the secret webhook address in the skill code from it"),
                ], "Without an external address, the skill can't reach Home Assistant."),
                "say": "Under Settings, System, Network, check that an internet address is set, "
                       "or that Home Assistant Cloud is active. Brainstorm uses this address to "
                       "build the secret address in the skill code.",
            },
        ],
    },
    {
        "title": "Home Assistant: voice input",
        "scenes": [
            {
                "v": ("ha", "Brainstorm › Alexa", [
                    ("Voice input", "Skill", True,
                     "Native (without skill) · <u>Skill</u> · Both"),
                ], "Settings ➔ Devices & services ➔ Brainstorm Hub ➔ Configure ➔ "
                   "Alexa Voice Input & Skill", "Submit"),
                "say": "In Home Assistant, open Settings, Devices and services, Brainstorm Hub, "
                       "Configure, and then Alexa Voice Input and Skill. Set Voice input to "
                       "Skill or Both, and continue.",
            },
            {
                "v": ("ha", "Brainstorm › Alexa › Skill", [
                    ("Skill code (lambda_function.py)", "WEBHOOK_URL = \"https://•••••/api/webhook/brainstorm_•••\"", True, ""),
                    ("Voice model (JSON editor)", "{ \"interactionModel\": { \"languageModel\": …", True, ""),
                    ("Create a new secret address …", "off", False, ""),
                ], "Keep this window open, you'll need both fields in a moment", "Submit"),
                "say": "Now you see the two fields, Skill code and Voice model. Keep this window "
                       "open, you'll copy them into the developer console in a moment. Both "
                       "come in English and German, matching the language of Home Assistant. "
                       "And don't click Submit yet.",
            },
        ],
    },
    {
        "title": "Skill name",
        "scenes": [
            {
                "v": ("wizard", 1, "Name, Locale", [
                    ("Skill name", "Brainstorm", True),
                    ("Primary locale", "English (US)", False),
                ], "The name only shows in the console and the Alexa app."),
                "say": "In the Alexa developer console, click Create Skill. Enter Brainstorm as "
                       "the name. The name only shows in the console and in the Alexa app. "
                       "How you call the skill is set later by the voice model.",
            },
        ],
    },
    {
        "title": "Language (primary locale)",
        "scenes": [
            {
                "v": ("wizard", 1, "Name, Locale", [
                    ("Skill name", "Brainstorm", False),
                    ("Primary locale", "English (US)", True),
                ], "Same language as your Echo, or Alexa won't find the skill."),
                "say": "For the language, choose the one your Echo uses, for example English, "
                       "U S. It has to match your Echo, or Alexa won't find the skill. If your "
                       "Echo speaks German, choose German and the German voice model from "
                       "Home Assistant.",
            },
        ],
    },
    {
        "title": "Experience & model: Custom",
        "scenes": [
            {
                "v": ("wizard", 2, "Experience, Model, Hosting service", [
                    ("Type of experience", "Other", False),
                    ("Model", "Custom", True),
                    ("Hosting services", "Alexa-hosted (Python)", False),
                ], "Only the Custom model allows your own voice model."),
                "say": "In the next step, the type of experience doesn't matter, Other is fine. "
                       "What matters is the model: choose Custom. Only that lets you paste "
                       "Brainstorm's own voice model.",
            },
        ],
    },
    {
        "title": "Hosting: Alexa-hosted (Python)",
        "scenes": [
            {
                "v": ("wizard", 2, "Experience, Model, Hosting service", [
                    ("Model", "Custom", False),
                    ("Hosting services", "Alexa-hosted (Python)", True),
                    ("Hosting region", "US East (N. Virginia)", True),
                ], "Python, not Node.js: Brainstorm's skill code is Python."),
                "say": "For hosting, choose Alexa-hosted, Python. Not Node.js, because "
                       "Brainstorm's skill code is Python. Amazon then runs the code for you "
                       "for free. Pick the region closest to you. Amazon fills in the "
                       "endpoint by itself, so you don't need to change it.",
            },
        ],
    },
    {
        "title": "Template: Start from Scratch",
        "scenes": [
            {
                "v": ("wizard", 3, "Templates", [
                    ("Template", "Start from Scratch", True),
                    ("Review", "Create Skill", False),
                ], "Other templates bring sample intents that would get in the way."),
                "say": "For the template, take Start from Scratch. Other templates bring sample "
                       "intents that Brainstorm's voice model replaces anyway. Check the review "
                       "and click Create Skill. Creating it takes about a minute.",
            },
        ],
    },
    {
        "title": "Interfaces: Alexa Presentation Language",
        "scenes": [
            {
                "v": ("console", "Build", "Interfaces", "apl",
                      "Only needed for lists on the Echo Show."),
                "say": "Do you have an Echo Show? Then open Interfaces in the Build tab, and "
                       "turn on Alexa Presentation Language. Choose the Hub profiles for the "
                       "Echo Show, and click Save at the top. Your Echo Show then shows your "
                       "lists. Tapping checks an idea off or unfolds its subtasks.",
            },
        ],
    },
    {
        "title": "Permissions: Reminders",
        "scenes": [
            {
                "v": ("console", "Build", "Permissions", "perm",
                      "Only needed for real Alexa reminders."),
                "say": "If you want real Alexa reminders, open Permissions under Build and turn "
                       "on Reminders. You'll give your consent once in the Alexa app later. "
                       "Without this permission, Home Assistant still reminds you, just not "
                       "through Amazon.",
            },
        ],
    },
    {
        "title": "Voice model: JSON Editor",
        "scenes": [
            {
                "v": ("console", "Build", "JSON Editor", "json",
                      "Save first, then Build Skill, and wait for the success message."),
                "say": "Now the heart of it: open Interaction Model, then JSON Editor. Select "
                       "the whole content, delete it, and paste the Voice model field from Home "
                       "Assistant. Click Save, and then Build Skill. Wait until the success "
                       "message appears.",
            },
            {
                "v": ("bullets", "What the voice model contains", [
                    ("🗣️", "<b>note …</b>: save an idea"),
                    ("⏰", "<b>remind me …</b> · <b>done</b> · <b>later</b>"),
                    ("📢", "<b>read</b> · <b>read everything</b> · <b>show daily life</b>"),
                    ("🧩", "Fallback: Home Assistant takes free sentences from the Alexa history"),
                ], "After a Brainstorm update with a new voice model: paste it again and build."),
                "say": "The voice model knows every sentence: note, remind me, done, later, "
                       "read and show. If a Brainstorm update brings a new voice model, paste "
                       "it again and click Build once more.",
            },
        ],
    },
    {
        "title": "Invocation name",
        "scenes": [
            {
                "v": ("console", "Build", "Invocations", "inv",
                      "Comes from the voice model, don't change it."),
                "say": "Under Invocations, check the Skill Invocation Name. It now says "
                       "brainstorm, in lower case. The voice model set it. Don't change it, or "
                       "the sentences from the guide won't work anymore.",
            },
        ],
    },
    {
        "title": "Skill code: lambda_function.py",
        "scenes": [
            {
                "v": ("console", "Code", "lambda_function.py", "code",
                      "Replace the whole content, then Deploy."),
                "say": "Next, go to the Code tab and open the file lambda_function.py. "
                       "Replace its whole content with the Skill code field from Home "
                       "Assistant, and click Deploy. Leave the other files as they are.",
                "speak": "Next, go to the Code tab, and open the Python file called lambda "
                         "function. Replace its whole content with the Skill code field from "
                         "Home Assistant, and click Deploy. Leave the other files as they are.",
            },
            {
                "v": ("bullets", "The skill code is secret", [
                    ("🔒", "It contains your <b>secret webhook address</b>"),
                    ("🚫", "Don't share it, don't show it in screenshots"),
                    ("♻️", "Leaked? <b>Create a new secret address</b> and copy the code again"),
                ], "After a Brainstorm update with new skill code: paste it again and deploy."),
                "say": "Keep the skill code secret, it contains your secret address. If it "
                       "leaks, create a new one in Home Assistant and copy the skill code "
                       "again.",
            },
        ],
    },
    {
        "title": "Test: Development",
        "scenes": [
            {
                "v": ("console", "Test", "Test", "test",
                      "If this says Off, your Echo doesn't know the skill."),
                "say": "Open the Test tab and set it to Development at the top. This makes the "
                       "skill active on all Echos of your Amazon account, without publishing "
                       "it. If it says Off, your Echo doesn't know the skill.",
            },
            {
                "v": ("console", "Test", "Test", "testrun",
                      "Test here first, then on your Echo."),
                "say": "To test it, type into the input field: ask brainstorm to note test "
                       "idea. If Alexa answers correctly here, your Echo will work too.",
            },
        ],
    },
    {
        "title": "Link with Home Assistant",
        "scenes": [
            {
                "v": ("speech", [
                    ("ha", "Submit in Home Assistant"),
                    ("du", "Alexa, ask Brainstorm to note test idea."),
                    ("alexa", "Saved under Inbox."),
                ], "The first request links your skill"),
                "say": "Click Submit in Home Assistant, and say to your Echo: Alexa, ask "
                       "Brainstorm to note test idea. The first request links your skill. After "
                       "that, Home Assistant rejects all other skills.",
            },
            {
                "v": ("ha", "Brainstorm › Alexa › Skill", [
                    ("Skill linked", "Yes", True, ""),
                    ("Last skill request", "today, 8:15 pm", True, ""),
                    ("Name for this unknown device", "Alexa App iPhone", False,
                     "For requests from the Alexa app"),
                ], "Configure shows the link and the last request", "Submit"),
                "say": "Under Configure, you now see the link and the last request. If a "
                       "request came from the Alexa app, you can give that device a name here.",
            },
        ],
    },
    {
        "title": "Alexa app: skill & permission",
        "scenes": [
            {
                "v": ("alexa_app",),
                "say": "In the Alexa app, you'll find the skill under More, Skills and Games, "
                       "Your Skills, in the section for developer skills. If you turned on "
                       "Reminders, grant the reminders permission once in the skill's "
                       "settings there.",
            },
        ],
    },
    {
        "title": "Clean up old routines",
        "scenes": [
            {
                "v": ("bullets", "Only in Skill mode", [
                    ("🧹", "Delete Alexa routines for <b>“Alexa, brainstorm”</b> from the dialog setup"),
                    ("⚠️", "Otherwise the old dialog starts instead of the skill"),
                    ("🔀", "Your own automations: check <code>voice_mode</code> of "
                           "<code>sensor.brainstorm_ideen_ubersicht</code>"),
                ], "In Both mode, routines and the skill can live side by side."),
                "say": "If you use Skill mode, delete the old Alexa routines for Alexa, "
                       "brainstorm. Otherwise the old dialog starts instead of the skill. Your "
                       "own automations check the voice mode attribute and switch themselves "
                       "off.",
            },
        ],
    },
    {
        "title": "Troubleshooting",
        "scenes": [
            {
                "v": ("bullets", "“I don't know how to help with that”", [
                    ("🔨", "The <b>Build</b> in the JSON Editor is missing"),
                    ("🧪", "The Test tab isn't set to <b>Development</b>"),
                    ("👤", "Console and Echo use <b>different Amazon accounts</b>"),
                    ("🌐", "“not saved”: check Skill/Both mode and that Home Assistant is reachable"),
                ], "Free sentences without a command word only work on an Echo, not in the Alexa app."),
                "say": "If Alexa says: I don't know how to help with that, usually the Build is "
                       "missing, the Test tab isn't on Development, or the console and the Echo "
                       "use different accounts. If Alexa says the idea wasn't saved, check the "
                       "mode and whether Home Assistant is reachable.",
            },
        ],
    },
    {
        "title": "Summary",
        "scenes": [
            {
                "v": ("bullets", "All settings at a glance", [
                    ("1", "Name <b>Brainstorm</b> · language <b>like your Echo</b> · model <b>Custom</b>"),
                    ("2", "Hosting <b>Alexa-hosted (Python)</b> · template <b>Start from Scratch</b>"),
                    ("3", "Optional: <b>Interfaces ➔ APL</b> · <b>Permissions ➔ Reminders</b>"),
                    ("4", "<b>JSON Editor</b>: voice model, Save, Build"),
                    ("5", "<b>Code</b>: skill code, Deploy · <b>Test</b>: Development"),
                    ("6", "Home Assistant: <b>Submit</b>, the first sentence links"),
                ], "Have fun collecting your ideas!"),
                "say": "To sum up: name Brainstorm, the language of your Echo, model Custom, "
                       "hosting Alexa-hosted Python, template Start from Scratch. Optionally, "
                       "Presentation Language and Reminders. Then the voice model, Build, the "
                       "skill code, Deploy, Test on Development, and Submit in Home Assistant. "
                       "Have fun collecting your ideas!",
            },
        ],
    },
]
