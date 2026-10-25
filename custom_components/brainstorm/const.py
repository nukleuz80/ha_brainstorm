"""Constants for the Brainstorm Hub integration."""

DOMAIN = "brainstorm"

STORAGE_KEY = "brainstorm.storage"
STORAGE_VERSION = 1

CONF_CATEGORIES = "categories"
CONF_AUTO_EXPORT_MARKDOWN = "auto_export_markdown"
CONF_MARKDOWN_PATH = "markdown_path"
CONF_SMART_FORMATTING = "smart_formatting"

DEFAULT_CATEGORIES = [
    "Inbox",
    "Smarthome",
    "Haus & Garten",
    "Projekte",
    "Alltag",
]
DEFAULT_MARKDOWN_PATH = "/config/brainstorm"

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
ATTR_STATUS = "status"
ATTR_CREATED_AT = "created_at"
ATTR_UPDATED_AT = "updated_at"

# Priorities
PRIORITY_LOW = "low"
PRIORITY_MEDIUM = "medium"
PRIORITY_HIGH = "high"
PRIORITY_URGENT = "urgent"
VALID_PRIORITIES = [PRIORITY_LOW, PRIORITY_MEDIUM, PRIORITY_HIGH, PRIORITY_URGENT]
DEFAULT_PRIORITY = PRIORITY_MEDIUM

# Platforms
PLATFORMS = ["todo", "sensor"]

