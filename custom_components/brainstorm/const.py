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
CONF_HIDE_EMPTY_CATEGORIES = "hide_empty_categories"
CONF_ALLOWED_ECHOS = "allowed_echos"
CONF_VOICE_MODE = "voice_mode"
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
CONF_AI_ENABLED = "ai_enabled"
CONF_AI_ENTITY = "ai_entity"
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

# Attributes
ATTR_ID = "id"
ATTR_TEXT = "text"
ATTR_CATEGORY = "category"
ATTR_SOURCE = "source"
ATTR_DEVICE = "device"
ATTR_TAGS = "tags"
ATTR_PRIORITY = "priority"
ATTR_PARENT_ID = "parent_id"
ATTR_ORDER = "order"
ATTR_STATUS = "status"
ATTR_CREATED_AT = "created_at"
ATTR_UPDATED_AT = "updated_at"
ATTR_DUE = "due"
ATTR_REMINDED_AT = "reminded_at"
ATTR_ESCALATED = "escalated"
ATTR_PARSE_DUE = "parse_due"
ATTR_ASSIGNEE = "assignee"
ATTR_TRIGGER = "trigger"
ATTR_ZONE = "zone"
ATTR_URGENT_SENT = "urgent_sent"
ATTR_ALEXA_NATIVE = "alexa_native"
ATTR_CALENDAR_SYNCED = "calendar_synced"

SERVICE_REORDER_IDEAS = "reorder_ideas"
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


