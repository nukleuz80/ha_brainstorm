"""Constants for the Brainstorm Hub integration."""

DOMAIN = "brainstorm"

STORAGE_KEY = "brainstorm.storage"
STORAGE_VERSION = 1
SKILL_STORAGE_KEY = "brainstorm.alexa_skill"
SKILL_STORAGE_VERSION = 1
REMINDERS_STORAGE_KEY = "brainstorm.reminders"
REMINDERS_STORAGE_VERSION = 1

CONF_AUTO_EXPORT_MARKDOWN = "auto_export_markdown"
CONF_MARKDOWN_PATH = "markdown_path"
CONF_SMART_FORMATTING = "smart_formatting"
CONF_VOICE_DUE = "voice_due"
CONF_GLOSSARY = "glossary"
CONF_HIDE_EMPTY_CATEGORIES = "hide_empty_categories"
CONF_ALLOWED_ECHOS = "allowed_echos"
CONF_VOICE_MODE = "voice_mode"
CONF_UI_LEVEL = "ui_level"
UI_LEVEL_BEGINNER = "beginner"
UI_LEVEL_NORMAL = "normal"
UI_LEVEL_PRO = "pro"
UI_LEVELS = [UI_LEVEL_BEGINNER, UI_LEVEL_NORMAL, UI_LEVEL_PRO]
# Installations from before the levels keep seeing everything, new ones start normal
DEFAULT_UI_LEVEL = UI_LEVEL_PRO
NEW_UI_LEVEL = UI_LEVEL_NORMAL
# Menu entries of the settings that only pros see
PRO_MENU_STEPS = frozenset(
    {"battery", "sensor_rules", "privacy_voice", "reminder_lists", "reminder_locks"}
)
CONF_PRIVACY_ENABLED = "privacy_enabled"
CONF_PRIVACY_OWNER = "privacy_owner"
CONF_PRIVACY_EXPORT = "privacy_export"
CONF_SHARE_USERS = "share_users"
CONF_VOICE_OWNERS = "voice_owners"
CONF_REMINDERS_ENABLED = "reminders_enabled"
CONF_NOTIFY_ENABLED = "notify_enabled"
CONF_QUIET_ENABLED = "quiet_enabled"
CONF_URGENT_ENABLED = "urgent_enabled"
CONF_URGENT_NOTIFY = "urgent_notify"
CONF_URGENT_DELAY = "urgent_delay"
CONF_DIGEST_PRESENCE = "digest_presence"
CONF_LIST_RULES_ENABLED = "list_rules_enabled"
CONF_LIST_RULES = "list_rules"
CONF_PLACES_ENABLED = "places_enabled"
CONF_ARRIVAL_ENABLED = "arrival_enabled"
CONF_DEFAULT_PERSON = "default_person"
CONF_PERSONS_ENABLED = "persons_enabled"
CONF_PERSON_RULES = "person_rules"
CONF_CALENDAR_ENABLED = "calendar_enabled"
CONF_CALENDAR_ENTITY = "calendar_entity"
CONF_CALENDAR_CATEGORIES = "calendar_categories"
CONF_AI_ENABLED = "ai_enabled"
CONF_AI_ENTITY = "ai_entity"
CONF_AI_TEXT_CLEANUP = "ai_text_cleanup"
# Days after which done ideas are deleted by themselves, 0 keeps them
CONF_DELETE_DONE_DAYS = "delete_done_days"
CONF_NATIVE_REMINDERS = "native_reminders"
CONF_REMINDER_ALEXA = "reminder_alexa"
CONF_REMINDER_ECHOS = "reminder_echos"
CONF_REMINDER_NOTIFY = "reminder_notify"
CONF_REMINDER_DELAY = "reminder_delay"
CONF_QUIET_START = "quiet_start"
CONF_QUIET_END = "quiet_end"
CONF_DIGEST_ENABLED = "digest_enabled"
CONF_DIGEST_TIME = "digest_time"
CONF_REVIEW_ENABLED = "review_enabled"
CONF_REVIEW_WEEKDAY = "review_weekday"
CONF_REVIEW_TIME = "review_time"
CONF_REVIEW_DAYS = "review_days"
# Category name -> to-do entity of another integration kept in step with it
CONF_TODO_SYNC = "todo_sync"
# Settings page of Local To-do: a category that gets a new list of its own
CONF_LOCAL_TODO_NEW = "local_todo_new"
# Bring!: all lists in one category, each list a main note with its items below
CONF_BRING_ENABLED = "bring_enabled"
CONF_BRING_CATEGORY = "bring_category"
CONF_BRING_LISTS = "bring_lists"
CONF_BRING_DEFAULT_LIST = "bring_default_list"
CONF_BRING_SHARE_ALL = "bring_share_all"
CONF_BRING_DONE_DAYS = "bring_done_days"
DEFAULT_BRING_DONE_DAYS = 3
CONF_CHOREOPS_ENABLED = "choreops_enabled"
CONF_CHOREOPS_POINTS = "choreops_points"
DEFAULT_CHOREOPS_POINTS = 10
# The daily briefing names the points of every ChoreOps person
CONF_CHOREOPS_DIGEST = "choreops_digest"
# Bonus points when the streak of a habit reaches a milestone, 0 for none
CONF_CHOREOPS_STREAK_BONUS = "choreops_streak_bonus"
DEFAULT_CHOREOPS_STREAK_BONUS = 0
STREAK_MILESTONES = (7, 30, 100)
CONF_ECHO_LOCKS = "echo_locks"
CONF_BATTERY_ENABLED = "battery_enabled"
CONF_BATTERY_THRESHOLD = "battery_threshold"
CONF_BATTERY_CATEGORY = "battery_category"
CONF_BATTERY_EXCLUDE = "battery_exclude"
CONF_BATTERY_PHONES = "battery_phones"
DEFAULT_BATTERY_THRESHOLD = 20
# Rules that turn a sensor reaching a value into a task
CONF_SENSOR_RULES = "sensor_rules"
RULE_ID = "id"
RULE_ENTITY = "sensor_entity"
RULE_CONDITION = "sensor_condition"
RULE_VALUE = "sensor_value"
RULE_TEXT = "sensor_text"
RULE_CATEGORY = "sensor_category"
RULE_AUTO_DONE = "sensor_auto_done"
RULE_RESET = "sensor_reset"
# Entity set back when a sensor task is ticked off by hand
RULE_RESET_ENTITY = "sensor_reset_entity"
# A task of the rule goes to ChoreOps for this person, with these points
RULE_CHOREOPS_USER = "sensor_choreops_user"
RULE_CHOREOPS_POINTS = "sensor_choreops_points"
RESET_DOMAINS = ["counter", "button", "input_button", "input_number", "number", "script"]
CONDITION_ABOVE = "above"
CONDITION_BELOW = "below"
CONDITION_STATE = "state"
SENSOR_CONDITIONS = [CONDITION_ABOVE, CONDITION_BELOW, CONDITION_STATE]

DEFAULT_CATEGORIES = [
    "Inbox",
    "Smarthome",
    "Haus & Garten",
    "Projekte",
    "Alltag",
]
DEFAULT_MARKDOWN_PATH = "/config/brainstorm"
DEFAULT_HIDE_EMPTY_CATEGORIES = True

# How Alexa voice input reaches Brainstorm
VOICE_MODE_NATIVE = "native"
VOICE_MODE_SKILL = "skill"
VOICE_MODE_BOTH = "both"
VOICE_MODES = [VOICE_MODE_NATIVE, VOICE_MODE_SKILL, VOICE_MODE_BOTH]

# Which Echo speaks a reminder
REMINDER_ALEXA_OFF = "off"
REMINDER_ALEXA_ORIGIN = "origin"
REMINDER_ALEXA_LAST = "last"
REMINDER_ALEXA_FIXED = "fixed"
REMINDER_ALEXA_MODES = [
    REMINDER_ALEXA_OFF,
    REMINDER_ALEXA_ORIGIN,
    REMINDER_ALEXA_LAST,
    REMINDER_ALEXA_FIXED,
]
DEFAULT_REVIEW_DAYS = 21
DEFAULT_URGENT_DELAY = 60

# What a list rule does
RULE_CHANNEL = "channel"
RULE_NOTIFY = "notify"
RULE_SCHEDULE_ENABLED = "schedule_enabled"
RULE_SCHEDULE_WEEKDAYS = "schedule_weekdays"
RULE_SCHEDULE_TIME = "schedule_time"
RULE_ZONE_ENABLED = "zone_enabled"
RULE_ZONE = "zone"
RULE_CHANNEL_DEFAULT = "default"
RULE_CHANNEL_ALEXA = "alexa"
RULE_CHANNEL_NOTIFY = "notify"
RULE_CHANNEL_NONE = "none"
RULE_CHANNELS = [
    RULE_CHANNEL_DEFAULT,
    RULE_CHANNEL_ALEXA,
    RULE_CHANNEL_NOTIFY,
    RULE_CHANNEL_NONE,
]

# Event constants
EVENT_IDEA_ADDED = "brainstorm_idea_added"
EVENT_IDEA_COMPLETED = "brainstorm_idea_completed"
EVENT_IDEA_DELETED = "brainstorm_idea_deleted"
EVENT_IDEA_UPDATED = "brainstorm_idea_updated"
EVENT_REMINDER_DUE = "brainstorm_reminder_due"
EVENT_COMMENT_ADDED = "brainstorm_comment_added"
EVENT_ROUND_ENDED = "brainstorm_round_ended"
# A note no longer waits: the last open note blocking it was ticked off
EVENT_IDEA_UNBLOCKED = "brainstorm_idea_unblocked"

# Attributes
ATTR_ID = "id"
ATTR_TEXT = "text"
ATTR_RAW_TEXT = "raw_text"
ATTR_LANGUAGE = "language"
ATTR_CATEGORY = "category"
ATTR_SOURCE = "source"
# Sources whose text was typed by hand, everything else is treated as spoken
TYPED_SOURCES = frozenset({"dashboard", "todo_list"})
# Text from a conversation agent was already written by an AI
SOURCE_ASSIST_LLM = "assist_llm"
ATTR_DEVICE = "device"
ATTR_TAGS = "tags"
ATTR_PRIORITY = "priority"
ATTR_PARENT_ID = "parent_id"
ATTR_ORDER = "order"
ATTR_STATUS = "status"
ATTR_CREATED_AT = "created_at"
ATTR_UPDATED_AT = "updated_at"
ATTR_DUE = "due"
ATTR_RESULT = "result"
RESULT_MAX_LENGTH = 1000
# A longer text below the title of an idea
ATTR_DESCRIPTION = "description"
DESCRIPTION_MAX_LENGTH = 4000
# Files attached to an idea, kept below the config folder
ATTR_ATTACHMENTS = "attachments"
# When an idea was ticked off, so its attachments can go after a while
ATTR_COMPLETED_AT = "completed_at"
# The Home Assistant user who ticked an idea off, for the statistics
ATTR_COMPLETED_BY = "completed_by"
# Someone, often a coding AI, is working on an idea right now
ATTR_IN_PROGRESS = "in_progress"
# A running timer on a note {since, by}, and the finished [start, end, user]
ATTR_TIMER = "timer"
ATTR_TIME_LOG = "time_log"
# How a note looks on the mind map; none means the look of the map
ATTR_SHAPE = "shape"
NODE_SHAPES = (
    "card",
    "cloud",
    "bubble",
    "thought",
    "pill",
    "rect",
    "ellipse",
    "hexagon",
    "note",
    "underline",
)
# Small signs on a note, like the markers of MindManager
ATTR_MARKERS = "markers"
MARKERS = (
    "question",
    "idea",
    "warning",
    "money",
    "star",
    "flag",
    "check",
    "blocked",
    "waiting",
    "heart",
)
# How far a note without subtasks is, in steps of a quarter
ATTR_PROGRESS = "progress"
PROGRESS_STEPS = (0, 25, 50, 75, 100)
# What the cards get about the subtasks of a note
ATTR_SUBTASKS = "subtasks"
# Lines to notes in other branches; one that blocks keeps its target waiting
ATTR_LINKS = "links"
LINK_LABEL_MAX_LENGTH = 40
LINKS_MAX_COUNT = 20
# What the cards get about the notes a note waits for
ATTR_BLOCKED_BY = "blocked_by"
# A named frame around notes of a list that belong together
ATTR_FRAME = "frame"
FRAME_MAX_LENGTH = 40
# A short remark in a bubble next to the note
ATTR_CALLOUT = "callout"
CALLOUT_MAX_LENGTH = 200
# How the subtasks below a note are numbered: 1. 1.1, a. b. or I. II.
ATTR_NUMBERING = "numbering"
NUMBERING_STYLES = ("decimal", "alpha", "roman")
# How often a note comes back after it is ticked off
ATTR_REPEAT = "repeat"
REPEAT_RULES = ("daily", "weekdays", "weekly", "biweekly", "monthly", "yearly")
# The new note a repeating one was followed by, so reopening can take it back
ATTR_REPEATED_AS = "repeated_as"
# Open subtasks that were ticked off together with a repeating note
ATTR_REPEAT_CLOSED = "repeat_closed"
# At most this many subtasks come along with a repeating note
REPEAT_MAX_SUBTASKS = 100
# Picked for today in "My day": {date, part}, only counting on that date
ATTR_MY_DAY = "my_day"
# A habit is ticked off once a day and never ends: {"days": [ISO dates]}
ATTR_HABIT = "habit"
HABIT_MAX_DAYS = 400
# The days of a habit the cards get for the calendar
HABIT_RECENT_DAYS = 126
MY_DAY_PARTS = ("morning", "day", "evening")
# Who a repeating note goes to in the next round: mode and the people (person
# entities) taking turns
ATTR_ROTATION = "rotation"
ROTATION_TURN = "turn"
ROTATION_FEWEST = "fewest"
ROTATION_RANDOM = "random"
ROTATION_MODES = (ROTATION_TURN, ROTATION_FEWEST, ROTATION_RANDOM)
ROTATION_MAX_PEOPLE = 10
# How far back "who did the least" counts the done notes of each person
ROTATION_FEWEST_DAYS = 30
# What the subtasks of a note can be sorted by
SORT_KEYS = ("text", "priority", "due", "created", "votes")
# Quick reactions of people to a note: reaction -> user IDs
ATTR_REACTIONS = "reactions"
REACTIONS = ("like", "heart", "laugh", "important")
# Points people gave a note in a voting round: user ID -> points
ATTR_VOTES = "votes"
# How many votes each person may give in one round
VOTING_MAX_VOTES = 20
# Comments on a note: id, by (user ID), at, text; the overview only counts them
ATTR_COMMENTS = "comments"
ATTR_COMMENT_COUNT = "comment_count"
# Written during a hidden brainstorm round: user ID of the author, the others
# do not see the note until the round of its category ends
ATTR_ROUND_BY = "round_by"
ROUND_MAX_MINUTES = 60
COMMENT_MAX_LENGTH = 2000
COMMENTS_MAX = 200
ATTACHMENT_DIR = "brainstorm_attachments"
ATTACHMENT_MAX_SIZE = 10 * 1024 * 1024
ATTACHMENT_MAX_COUNT = 20
ATTACHMENT_RETENTION_DAYS = 30
# Only types a browser shows safely; SVG and HTML could run scripts
ATTACHMENT_TYPES: dict[str, str] = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".heic": "image/heic",
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".log": "text/plain",
    ".md": "text/plain",
    ".csv": "text/csv",
    ".json": "application/json",
    ".yaml": "text/plain",
    ".yml": "text/plain",
    ".zip": "application/zip",
}
ATTR_REMINDED_AT = "reminded_at"
ATTR_ESCALATED = "escalated"
ATTR_PARSE_DUE = "parse_due"
ATTR_ASSIGNEE = "assignee"
# Hand-over to ChoreOps: chore_id, user, points, status, since
ATTR_CHOREOPS = "choreops"
ATTR_CHOREOPS_REWARD = "choreops_reward"
# Streak milestones a habit already earned bonus points for, as "start:days"
ATTR_HABIT_BONUS = "habit_bonus"
ATTR_OWNER = "owner"
ATTR_CREATED_BY = "created_by"
ATTR_MAP_POS = "map_pos"
# Place and colour of a note on the pinboard, free of the tree
ATTR_PIN = "pin"
PIN_COLORS = ("yellow", "pink", "green", "blue", "orange", "purple")
# Freehand drawing on the map of a category
DRAW_KINDS = ("pen", "arrow", "ellipse")
DRAW_COLORS = ("red", "orange", "green", "blue", "purple", "gray")
DRAW_MAX_STROKES = 300

# Saved map views (tabs above the mind map)
MAP_TABS_MAX = 40
MAP_TAB_NAME_MAX = 40
# How much the notes of a tab show: by zoom, titles only or everything
MAP_TAB_DETAILS = ("auto", "compact", "normal")
MAP_TAB_LAYOUTS = (
    "radial",
    "tree",
    "org",
    "outline",
    "pin",
    "kanban",
    "timeline",
    "matrix",
)
DRAW_MAX_POINTS = 400
ATTR_SHARES = "shares"
SHARE_ALL = "all"
SHARE_VIEW = "view"
SHARE_EDIT = "edit"
ACCESS_OWNER = "owner"
ATTR_TRIGGER = "trigger"
ATTR_ZONE = "zone"
ATTR_ECHOS = "echos"
ATTR_URGENT_SENT = "urgent_sent"
ATTR_ALEXA_NATIVE = "alexa_native"
ATTR_CALENDAR_SYNCED = "calendar_synced"
# The 📅 switch of a task: True, False, or missing for the rule of the settings
ATTR_CALENDAR = "calendar"
# The event a task has in a calendar: entity, uid, start and summary
ATTR_CALENDAR_EVENT = "calendar_event"
# Item of a linked to-do list, with what that list said at the last sync
ATTR_TODO_LINK = "todo_link"
# Ideas taken over from a linked to-do list
SOURCE_TODO_SYNC = "todo_sync"
# The main note that stands for a Bring! list, and where it came from
ATTR_BRING_LIST = "bring_list"
# The Bring! list a note was sent to, with the items it gave there
ATTR_BRING_SENT = "bring_sent"
# The device (or sensor) a battery task is for, and whether it got a new battery
ATTR_BATTERY = "battery"
ATTR_BATTERY_DONE = "battery_done"
# Battery Notes: the battery type of a device and when it was replaced
BATTERY_NOTES_DOMAIN = "battery_notes"
CONF_BATTERY_NOTES = "battery_notes_enabled"
CONF_BATTERY_NOTES_REPLACED = "battery_notes_replaced"
SOURCE_BRING = "bring"
SOURCE_BATTERY = "battery"
# The sensor rule a task is for, and whether its sensor is back to normal
ATTR_SENSOR_RULE = "sensor_rule"
ATTR_SENSOR_RULE_DONE = "sensor_rule_done"
SOURCE_SENSOR = "sensor"
# Waste collection: a task on the eve of every pickup, ticked off after it
WASTE_DOMAIN = "waste_collection_schedule"
CONF_WASTE_ENABLED = "waste_enabled"
CONF_WASTE_CALENDARS = "waste_calendars"
CONF_WASTE_CATEGORY = "waste_category"
CONF_WASTE_TIME = "waste_time"
CONF_WASTE_CHOREOPS_USERS = "waste_choreops_users"
CONF_WASTE_CHOREOPS_POINTS = "waste_choreops_points"
DEFAULT_WASTE_TIME = "18:00:00"
# The pickup a task is for: {"date": ISO date, "key": waste type, "user": person}
ATTR_WASTE = "waste"
ATTR_WASTE_DONE = "waste_done"
SOURCE_WASTE = "waste"
# WhatsApp: the messages a bridge such as ha-whatsapp receives become notes
CONF_WHATSAPP_ENABLED = "whatsapp_enabled"
CONF_WHATSAPP_EVENT = "whatsapp_event"
CONF_WHATSAPP_TEXT_FIELD = "whatsapp_text_field"
CONF_WHATSAPP_SENDER_FIELD = "whatsapp_sender_field"
# {number in digits: person}, only these numbers may add notes
CONF_WHATSAPP_SENDERS = "whatsapp_senders"
CONF_WHATSAPP_CATEGORY = "whatsapp_category"
CONF_WHATSAPP_PREFIX = "whatsapp_prefix"
CONF_WHATSAPP_REPLY = "whatsapp_reply"
CONF_WHATSAPP_REPLY_SERVICE = "whatsapp_reply_service"
DEFAULT_WHATSAPP_EVENT = "whatsapp_message_received"
DEFAULT_WHATSAPP_REPLY_SERVICE = "whatsapp.send_message"
SOURCE_WHATSAPP = "whatsapp"
# The amount or note of an item on a linked list, such as "1,5 l"
ATTR_SPEC = "spec"
# Format of the JSON export, raised when its layout changes incompatibly
JSON_EXPORT_FORMAT = "brainstorm_hub"
JSON_EXPORT_VERSION = 1

SERVICE_REORDER_IDEAS = "reorder_ideas"
SERVICE_SORT_CHILDREN = "sort_children"
SERVICE_TRACK_TIME = "track_time"
SERVICE_REACT = "react"
SERVICE_VOTE = "vote"
SERVICE_START_VOTING = "start_voting"
SERVICE_END_VOTING = "end_voting"
SERVICE_ADD_COMMENT = "add_comment"
SERVICE_DELETE_COMMENT = "delete_comment"
SERVICE_GROUP_IDEAS = "group_ideas"
SERVICE_MOVE_BRANCH = "move_branch"
SERVICE_SEND_REWARD_TO_CHOREOPS = "send_reward_to_choreops"
SERVICE_START_ROUND = "start_round"
SERVICE_END_ROUND = "end_round"
SERVICE_IMPORT_OUTLINE = "import_outline"
SERVICE_DELETE_DONE = "delete_done"
SERVICE_SET_CATEGORY_STYLE = "set_category_style"
ATTR_ICON = "icon"
ATTR_COLOR = "color"
ATTR_RESET = "reset"

# Priorities
PRIORITY_LOW = "low"
PRIORITY_MEDIUM = "medium"
PRIORITY_HIGH = "high"
PRIORITY_URGENT = "urgent"
VALID_PRIORITIES = [PRIORITY_LOW, PRIORITY_MEDIUM, PRIORITY_HIGH, PRIORITY_URGENT]
DEFAULT_PRIORITY = PRIORITY_MEDIUM

# Platforms
PLATFORMS = ["todo", "sensor"]
OVERVIEW_ENTITY_ID = "sensor.brainstorm_ideen_ubersicht"


