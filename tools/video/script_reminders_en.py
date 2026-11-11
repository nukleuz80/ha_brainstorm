"""Storyboard: Brainstorm reminders and notifications (English)."""
from __future__ import annotations

LANG = "en"
TITLE = "Brainstorm Hub: Reminders & Notifications"
OUT_NAME = "brainstorm-reminders-en"
# Wiki pages this video covers, check them on every release
COVERS = ["Reminders", "Settings"]
SPOKEN: list[tuple[str, str]] = [("Pushover", "Push-over"), ("CalDAV", "Cal Dav")]

PATH = "Settings ➔ Devices & services ➔ Brainstorm Hub ➔ Configure"

CHAPTERS: list[dict] = [
    {
        "title": "Reminders",
        "scenes": [
            {
                "v": ("title", "Reminders & Notifications", "Brainstorm thinks ahead for you"),
                "say": "Brainstorm reminds you of due entries on its own. With an Alexa "
                       "announcement, on your phone, at a place, or as a daily briefing. In this "
                       "video, I'll show you how to set due dates and configure everything.",
            },
        ],
    },
    {
        "title": "Due date by voice",
        "scenes": [
            {
                "v": ("transform", "remind me tomorrow at 8 to take out the bins", "Take out the bins",
                      ["⏰ Tomorrow 8:00", "📂 Daily Life"],
                      "With your own skill: “Alexa, ask Brainstorm to remind me …”"),
                "say": "The simplest way is to use your voice. Say: Alexa, ask Brainstorm to remind me "
                       "tomorrow at 8 to take out the bins. Brainstorm saves the note, due "
                       "tomorrow at eight.",
            },
            {
                "v": ("grid", "What Brainstorm understands", [
                    ("🌙", "Times of day", "tonight, tomorrow morning, the day after tomorrow"),
                    ("📅", "Weekdays", "on Friday, next week"),
                    ("🗓️", "Dates", "on November 25, on December 2nd at noon"),
                    ("⏳", "Intervals", "in two hours, in ten minutes"),
                    ("🕣", "Times", "at 8, at 8:30 am, at 3:15 pm"),
                    ("➡️", "Next year", "If a date has already passed, it means next year"),
                ], "A date without a time means 9:00 am."),
                "say": "It understands times of day like tonight or tomorrow morning, weekdays, "
                       "dates, intervals like in two hours, and times like eight thirty. "
                       "Without a time, Brainstorm reminds you at nine in the morning.",
            },
        ],
    },
    {
        "title": "Due date on the card",
        "scenes": [
            {
                "v": ("bullets", "No voice needed", [
                    ("👆", "<b>Long-press</b> an entry ➔ <i>Remind: tonight, tomorrow morning, next week</i> or <i>pick a time</i>"),
                    ("✏️", "Set date and time in the <b>edit dialog</b>"),
                    ("🔊", "<b>Remind on:</b> picks the Echos that speak this very reminder"),
                    ("📋", "Or the <b>due date</b> in the Home Assistant to-do list"),
                ], "In automations: brainstorm.add_idea and brainstorm.update_idea with the due field."),
                "say": "On the card, long-press an entry and pick a time. In the edit dialog, you "
                       "set the date and time, and Remind on picks the Echos that speak this "
                       "very reminder.",
            },
        ],
    },
    {
        "title": "Turn it on",
        "scenes": [
            {
                "v": ("menu", "Brainstorm › Reminders", [
                    ("On/Off & Channels", True), ("Quiet Hours, Briefing & Weekly Review", False),
                    ("Rules per List", False), ("Places & Coming Home", False), ("People", False),
                    ("Calendar & Alexa Reminders", False), ("Lock times per Echo", False),
                    ("🧪 Test channels now", False),
                ], PATH + " ➔ Reminders & Notifications",
                    "Every feature has its own switch, all of it is optional."),
                "say": "Everything is set up in the integration under Configure, Reminders and "
                       "Notifications. Every feature has its own switch. Let's start with On "
                       "and Off, and the channels.",
            },
            {
                "v": ("switches", "Brainstorm › Reminders › On/Off & Channels", [
                    ("Use reminders", True, True, "Main switch for everything in this menu"),
                    ("Alexa announcement", "Echo where the idea came from", True,
                     "Or: most recently used Echo, fixed Echos, off"),
                    ("Send notifications", True, True, "for example notify.mobile_app_iphone"),
                    ("Wait before sending notifications", "5 minutes", False,
                     "The Echo speaks first, your phone only follows if you don't react"),
                    ("Send important open ideas again", False, False,
                     "High and urgent entries go to more services after a while"),
                ], PATH + " ➔ Reminders", "The Alexa announcement needs Alexa Media Player."),
                "say": "Turn on Use reminders and choose which Echo makes the announcement, for "
                       "example the one you spoke the entry to. Add notification services like "
                       "your phone. With a wait time, your phone only gets it if you don't react "
                       "at the Echo.",
            },
        ],
    },
    {
        "title": "On your phone",
        "scenes": [
            {
                "v": ("phone", "Lock screen", [
                    ('<small>🧠 BRAINSTORM · now</small><b>Reminder: Take out the bins</b><br>Daily Life · 8:00 am'
                     '<div class="act"><span>Done</span><span>1 hour later</span><span>Tomorrow</span></div>', True),
                    ('<small>🧠 BRAINSTORM · yesterday</small>Briefing: 3 things are due today, change the tires is urgent', False),
                ], [
                    ("✅", "<b>Done</b> checks the entry off right away"),
                    ("⏰", "<b>1 hour later</b> or <b>Tomorrow</b> moves it"),
                    ("📣", "Important entries can go out again, for example to Pushover"),
                    ("🧪", "<b>Test channels now</b> sends a test right away"),
                ], "The buttons work in the Home Assistant Companion app."),
                "say": "On your phone, the reminder comes with three buttons: Done, one hour "
                       "later, and Tomorrow. Brainstorm can send important entries again, for "
                       "example to Pushover. Test channels now checks everything right away.",
            },
        ],
    },
    {
        "title": "Quiet hours, briefing & review",
        "scenes": [
            {
                "v": ("switches", "Brainstorm › Reminders › Quiet Hours, Briefing & Review", [
                    ("Use quiet hours", True, False, "From 10:00 pm to 7:00 am reminders wait"),
                    ("Daily briefing", True, True, "An overview of the day at 7:30 am"),
                    ("Only when someone is detected here", "binary_sensor.kitchen_motion", True,
                     "Waits up to 6 hours until someone is there"),
                    ("Weekly review", True, False, "Sundays: entries open for more than 14 days"),
                ], PATH + " ➔ Reminders",
                    "During quiet hours, urgent entries reach your phone, but no Echo speaks."),
                "say": "During quiet hours, reminders wait until morning. Only urgent entries "
                       "reach your phone, and no Echo speaks. The daily briefing gives you an "
                       "overview, if you like only once a motion sensor sees someone. The "
                       "weekly review lists what has been open for a long time.",
            },
            {
                "v": ("bullets", "Lock times per Echo", [
                    ("🛏️", "Up to three <b>lock times</b>, for example for the Echo in the kids' room"),
                    ("🔕", "Brainstorm can also switch <b>Do not disturb</b> on and off there"),
                    ("🌅", "If the end is earlier than the start, it lasts until the next morning"),
                ], "“Do not disturb” needs Alexa Media Player."),
                "say": "You can also lock single Echos, for example in the kids' room in the "
                       "afternoon. Brainstorm can even switch on Do not disturb there, so "
                       "Alexa itself stays quiet.",
            },
        ],
    },
    {
        "title": "Rules per list",
        "scenes": [
            {
                "v": ("switches", "Brainstorm › Reminders › Rules › Shopping", [
                    ("Reminders of this list go to", "Notifications only (private)", True,
                     "Normal channels · Alexa only · Notifications only · Nothing, event only"),
                    ("Own notification services for this list", "notify.mobile_app_pixel", False,
                     "Empty uses the normal services"),
                    ("Send the open ideas on certain days", True, False, "Saturday at 9:00 am"),
                    ("Send the open ideas at a place", True, True, "Zone: Supermarket"),
                ], PATH + " ➔ Reminders", "Perfect for shopping lists: they show up when you're at the store."),
                "say": "Every list can have its own rules. Private lists only go to your phone, "
                       "instead of out loud on the Echo. The shopping list comes every Saturday, "
                       "or as soon as you arrive at the supermarket.",
            },
        ],
    },
    {
        "title": "Places & coming home",
        "scenes": [
            {
                "v": ("speech", [
                    ("du", "Alexa, ask Brainstorm to remind me when I get home to take out the trash."),
                    ("du", "Alexa, ask Brainstorm to remind me when I get to the supermarket to buy milk."),
                    ("ha", "📍 The reminder comes as soon as you enter the zone"),
                ], "Uses your zones in Home Assistant"),
                "say": "Under Places and coming home, you allow reminders at places. Then say: "
                       "remind me when I get home to take out the trash. Or: when I get to the "
                       "supermarket, to buy milk. Brainstorm uses your zones for this.",
            },
        ],
    },
    {
        "title": "For other people",
        "scenes": [
            {
                "v": ("speech", [
                    ("du", "Alexa, ask Brainstorm to remind Frida tomorrow at 8 about the dentist."),
                    ("alexa", "Okay, I will remind Frida tomorrow at 8 am about the dentist."),
                ], "Each person with their own Echos and services"),
                "say": "Reminders can be for others, too: remind Frida tomorrow at 8 about the "
                       "dentist. Under People, you set which Echo and which phone belong to "
                       "each person.",
            },
        ],
    },
    {
        "title": "Answer by voice",
        "scenes": [
            {
                "v": ("speech", [
                    ("alexa", "Reminder: take out the bins."),
                    ("du", "Alexa, ask Brainstorm: done."),
                    ("du", "Alexa, ask Brainstorm: later."),
                ], "With your own Alexa skill"),
                "say": "When Alexa has reminded you, just say: Alexa, ask Brainstorm, done. Or: "
                       "later, and the reminder comes back in an hour.",
            },
        ],
    },
    {
        "title": "Calendar & real Alexa reminders",
        "scenes": [
            {
                "v": ("switches", "Brainstorm › Reminders › Calendar & Alexa", [
                    ("Add reminders to a calendar", True, True,
                     "One way, once per reminder"),
                    ("Calendar", "calendar.family", False, "for example a Google or CalDAV calendar"),
                    ("Also create real Alexa reminders", True, True,
                     "Alexa rings itself, Home Assistant doesn't speak as well"),
                ], PATH + " ➔ Reminders",
                    "Real Alexa reminders need Build ➔ Permissions ➔ Reminders in the Alexa console."),
                "say": "Reminders can also go into a calendar. With the skill, Brainstorm also "
                       "creates real Alexa reminders. For this, switch on Reminders under "
                       "Permissions in the Alexa console, and allow it once in the Alexa app.",
            },
        ],
    },
    {
        "title": "Your own automations",
        "scenes": [
            {
                "v": ("yaml", "Every reminder is an event",
                      "trigger:\n  - trigger: event\n    event_type: brainstorm_reminder_due\naction:\n"
                      "  - action: light.turn_on\n    target:\n      entity_id: light.hallway\n"
                      "    data:\n      color_name: orange",
                      "The event fires even without any channels set up."),
                "say": "Every reminder also fires the event brainstorm reminder due. Use it for "
                       "your own automations, for example to turn the hallway light orange.",
            },
        ],
    },
    {
        "title": "Have fun",
        "scenes": [
            {
                "v": ("bullets", "In short", [
                    ("🗣️", "Say a due date or set it on the card"),
                    ("🔊", "Echo, phone, place, calendar or automation"),
                    ("🌙", "Quiet hours, lock times and rules per list"),
                ], "Every switch explained: wiki ➔ Reminders"),
                "say": "Those were the reminders in Brainstorm. Every switch is explained in the "
                       "wiki on GitHub. Have fun!",
            },
        ],
    },
]
