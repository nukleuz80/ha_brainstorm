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


