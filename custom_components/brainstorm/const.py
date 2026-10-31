"""Constants for the Brainstorm Hub integration."""

DOMAIN = "brainstorm"

STORAGE_KEY = "brainstorm.storage"
STORAGE_VERSION = 1
SKILL_STORAGE_KEY = "brainstorm.alexa_skill"
SKILL_STORAGE_VERSION = 1

CONF_AUTO_EXPORT_MARKDOWN = "auto_export_markdown"
CONF_MARKDOWN_PATH = "markdown_path"
CONF_SMART_FORMATTING = "smart_formatting"
CONF_HIDE_EMPTY_CATEGORIES = "hide_empty_categories"
CONF_ALLOWED_ECHOS = "allowed_echos"
CONF_VOICE_MODE = "voice_mode"

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

# Event constants
EVENT_IDEA_ADDED = "brainstorm_idea_added"
EVENT_IDEA_COMPLETED = "brainstorm_idea_completed"
EVENT_IDEA_DELETED = "brainstorm_idea_deleted"
EVENT_IDEA_UPDATED = "brainstorm_idea_updated"

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


