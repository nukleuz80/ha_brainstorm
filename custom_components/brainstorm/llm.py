"""LLM API and Function-Calling Tools for Brainstorm Hub."""
from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, llm

from .const import (
    ATTR_CATEGORY,
    ATTR_ID,
    ATTR_PRIORITY,
    ATTR_STATUS,
    ATTR_TEXT,
    DOMAIN,
)
from .store import BrainstormStore

_LOGGER = logging.getLogger(__name__)

BRAINSTORM_LLM_API_ID = "brainstorm"


def _get_active_store(hass: HomeAssistant) -> BrainstormStore | None:
    """Retrieve the active Brainstorm store instance."""
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    if entries:
        return entries[0].runtime_data
    return hass.data.get(DOMAIN, {}).get("primary_store")


def _resolve_category(store: BrainstormStore, category: str | None) -> str | None:
    """Map 'all' to no filter and match a category name case-insensitively."""
    if not category or category.strip().lower() in ("all", "alle"):
        return None
    clean = category.strip()
    for cat in store.categories:
        if cat.lower() == clean.lower():
            return cat
    return clean


def _find_matches(ideas: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    """Find ideas by query, preferring exact text matches over partial ones."""
    clean_query = query.strip().lower()
    if not clean_query:
        return []
    exact = [i for i in ideas if i.get(ATTR_TEXT, "").strip().lower() == clean_query]
    return exact or [i for i in ideas if clean_query in i.get(ATTR_TEXT, "").lower()]


def _error(message: str) -> llm.ToolResult:
    """Return a failed tool result."""
    return llm.ToolResult(data={"error": message}, error=True)


def _ambiguous_result(matches: list[dict[str, Any]]) -> llm.ToolResult:
    """Return an error that lets the agent ask which idea the user means."""
    return llm.ToolResult(
        data={
            "error": (
                "Multiple ideas match. Ask the user which one is meant, "
                "then call this tool again with its idea_id."
            ),
            "matches": [
                {
                    "id": i.get(ATTR_ID),
                    "text": i.get(ATTR_TEXT),
                    "category": i.get(ATTR_CATEGORY),
                    "status": i.get(ATTR_STATUS),
                }
                for i in matches
            ],
        },
        error=True,
    )


class BrainstormAddIdeaTool(llm.Tool):
    """Tool to create or capture a new idea in Brainstorm Hub."""

    name = "brainstorm_add_idea"
    integration = DOMAIN
    annotations = llm.ToolAnnotations(
        read_only=False,
        destructive=False,
        idempotent=False,
        open_world=False,
    )
    description = (
        "Create, capture, or record a new idea, thought, task, or note in Brainstorm Hub. "
        "Use whenever the user wants to add, remember, or save something. "
        "Brainstorm will automatically clean the text and categorize it if category is not provided."
    )

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the tool."""
        self.hass = hass
        self.parameters = vol.Schema(
            {
                vol.Required(
                    "text",
                    description="The idea, note, or task content to record.",
                ): cv.string,
                vol.Optional(
                    "category",
                    description=(
                        "Optional category (e.g. 'Inbox', 'Smarthome', 'Haus & Garten', "
                        "'Projekte', 'Alltag'). If omitted, Brainstorm auto-categorizes."
                    ),
                ): cv.string,
                vol.Optional(
                    "priority",
                    description=(
                        "Optional priority ('low', 'medium', 'high', 'urgent'). "
                        "If omitted, Brainstorm auto-detects urgency from text."
                    ),
                ): vol.In(["low", "medium", "high", "urgent"]),
                vol.Optional(
                    "tags",
                    description="Optional list of tags or keywords for this note.",
                ): vol.All(cv.ensure_list, [cv.string]),
            }
        )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> llm.ToolResult:
        """Execute the tool."""
        store = _get_active_store(hass)
        if not store:
            return _error("Brainstorm store is not initialized")

        args = tool_input.tool_args
        text = str(args.get("text", "")).strip()
        category = args.get("category")
        priority = args.get("priority")
        tags = args.get("tags")

        if not text:
            return _error("Text cannot be empty")

        idea = await store.async_add_idea(
            text=text,
            category=category,
            priority=priority,
            source="assist_llm",
            tags=tags,
            context=llm_context.context,
        )

        return llm.ToolResult(
            data={
                "success": True,
                "id": idea[ATTR_ID],
                "text": idea[ATTR_TEXT],
                "category": idea[ATTR_CATEGORY],
                "priority": idea.get(ATTR_PRIORITY, "medium"),
                "message": f"Idee erfolgreich in '{idea[ATTR_CATEGORY]}' (Priorität: {idea.get(ATTR_PRIORITY, 'medium')}) erfasst.",
            }
        )


class BrainstormGetIdeasTool(llm.Tool):
    """Tool to fetch or search ideas from Brainstorm Hub."""

    name = "brainstorm_get_ideas"
    integration = DOMAIN
    annotations = llm.ToolAnnotations(
        read_only=True,
        destructive=False,
        idempotent=True,
        open_world=False,
    )
    description = (
        "Fetch, query, or search ideas, notes, and tasks from Brainstorm Hub. "
        "Use when the user asks what is recorded, what tasks exist, or wants to check notes "
        "in a specific category (e.g. 'Haus & Garten', 'Smarthome') or with a keyword."
    )

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the tool."""
        self.hass = hass
        self.parameters = vol.Schema(
            {
                vol.Optional(
                    "category",
                    description="Optional category to filter by (or 'all' for all categories).",
                ): cv.string,
                vol.Optional(
                    "status",
                    description="Filter by status: 'active' (default), 'completed', or 'all'.",
                    default="active",
                ): vol.In(["active", "completed", "all"]),
                vol.Optional(
                    "priority",
                    description="Optional filter by priority: 'urgent', 'high', 'medium', or 'low'.",
                ): vol.In(["urgent", "high", "medium", "low"]),
                vol.Optional(
                    "search",
                    description="Optional search term to filter notes containing this text.",
                ): cv.string,
            }
        )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> llm.ToolResult:
        """Execute the tool."""
        store = _get_active_store(hass)
        if not store:
            return _error("Brainstorm store is not initialized")

        args = tool_input.tool_args
        category = _resolve_category(store, args.get("category"))
        status_filter = args.get("status", "active")
        priority_filter = args.get("priority")
        search_term = args.get("search")

        if status_filter == "all":
            status_filter = None

        ideas = store.get_ideas_by_category(
            category=category, status=status_filter, priority=priority_filter
        )

        if search_term and search_term.strip():
            clean_search = search_term.strip().lower()
            ideas = [
                i
                for i in ideas
                if clean_search in i.get(ATTR_TEXT, "").lower()
                or clean_search in i.get(ATTR_CATEGORY, "").lower()
            ]

        compact_ideas = [
            {
                "id": i.get(ATTR_ID),
                "text": i.get(ATTR_TEXT),
                "category": i.get(ATTR_CATEGORY),
                "priority": i.get(ATTR_PRIORITY, "medium"),
                "status": i.get(ATTR_STATUS),
                "created_at": i.get("created_at"),
            }
            for i in ideas
        ]

        return llm.ToolResult(
            data={
                "count": len(compact_ideas),
                "category": category or "all",
                "ideas": compact_ideas,
                "available_categories": store.categories,
            }
        )


class BrainstormCompleteIdeaTool(llm.Tool):
    """Tool to mark an idea as completed in Brainstorm Hub."""

    name = "brainstorm_complete_idea"
    integration = DOMAIN
    annotations = llm.ToolAnnotations(
        read_only=False,
        destructive=False,
        idempotent=True,
        open_world=False,
    )
    description = (
        "Mark an idea or task as completed / done in Brainstorm Hub. "
        "Use when the user says they finished or completed an idea/task."
    )

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the tool."""
        self.hass = hass
        self.parameters = vol.Schema(
            {
                vol.Optional(
                    "idea_id",
                    description="The exact ID of the idea if known.",
                ): cv.string,
                vol.Optional(
                    "query",
                    description="Keyword or text to find the idea if ID is unknown.",
                ): cv.string,
                vol.Optional(
                    "category",
                    description="Optional category to narrow down the search.",
                ): cv.string,
            }
        )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> llm.ToolResult:
        """Execute the tool."""
        store = _get_active_store(hass)
        if not store:
            return _error("Brainstorm store is not initialized")

        args = tool_input.tool_args
        idea_id = args.get("idea_id")
        query = args.get("query")
        category = _resolve_category(store, args.get("category"))

        target_id = idea_id
        if not target_id and query:
            active_ideas = store.get_ideas_by_category(category=category, status="active")
            matches = _find_matches(active_ideas, query)
            if len(matches) > 1:
                return _ambiguous_result(matches)
            if matches:
                target_id = matches[0].get(ATTR_ID)

        if not target_id:
            return _error("No matching active idea found to complete")

        updated = await store.async_update_idea(
            idea_id=target_id,
            status="completed",
            context=llm_context.context,
        )
        if not updated:
            return _error(f"Idea with ID '{target_id}' could not be updated")

        return llm.ToolResult(
            data={
                "success": True,
                "id": updated.get(ATTR_ID),
                "text": updated.get(ATTR_TEXT),
                "category": updated.get(ATTR_CATEGORY),
                "message": f"'{updated.get(ATTR_TEXT)}' wurde als erledigt markiert.",
            }
        )


class BrainstormDeleteIdeaTool(llm.Tool):
    """Tool to delete an idea from Brainstorm Hub."""

    name = "brainstorm_delete_idea"
    integration = DOMAIN
    annotations = llm.ToolAnnotations(
        read_only=False,
        destructive=True,
        idempotent=False,
        open_world=False,
    )
    description = (
        "Delete or remove an idea from Brainstorm Hub. "
        "Use when the user explicitly asks to delete or discard a note."
    )

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the tool."""
        self.hass = hass
        self.parameters = vol.Schema(
            {
                vol.Optional(
                    "idea_id",
                    description="The exact ID of the idea if known.",
                ): cv.string,
                vol.Optional(
                    "query",
                    description="Keyword or text to find the idea to delete if ID is unknown.",
                ): cv.string,
                vol.Optional(
                    "category",
                    description="Optional category to narrow down search.",
                ): cv.string,
            }
        )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> llm.ToolResult:
        """Execute the tool."""
        store = _get_active_store(hass)
        if not store:
            return _error("Brainstorm store is not initialized")

        args = tool_input.tool_args
        idea_id = args.get("idea_id")
        query = args.get("query")
        category = _resolve_category(store, args.get("category"))

        target_id = idea_id
        target_text = ""
        if not target_id and query:
            all_ideas = store.get_ideas_by_category(category=category, status=None)
            matches = _find_matches(all_ideas, query)
            if len(matches) > 1:
                return _ambiguous_result(matches)
            if matches:
                target_id = matches[0].get(ATTR_ID)
                target_text = matches[0].get(ATTR_TEXT, "")

        if not target_id:
            return _error("No matching idea found to delete")

        deleted = await store.async_delete_idea(
            target_id, context=llm_context.context
        )
        return llm.ToolResult(
            data={
                "success": deleted,
                "id": target_id,
                "message": f"Idee '{target_text or target_id}' wurde gelöscht." if deleted else "Löschen fehlgeschlagen.",
            }
        )


class BrainstormListCategoriesTool(llm.Tool):
    """Tool to list existing categories and note statistics."""

    name = "brainstorm_list_categories"
    integration = DOMAIN
    annotations = llm.ToolAnnotations(
        read_only=True,
        destructive=False,
        idempotent=True,
        open_world=False,
    )
    description = (
        "List all categories in Brainstorm Hub and the number of active notes in each category."
    )

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the tool."""
        self.hass = hass
        self.parameters = vol.Schema({})

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> llm.ToolResult:
        """Execute the tool."""
        store = _get_active_store(hass)
        if not store:
            return _error("Brainstorm store is not initialized")

        counts = store.category_counts
        return llm.ToolResult(
            data={
                "categories": store.categories,
                "category_counts": counts,
                "total_active": sum(counts.values()),
            }
        )


class BrainstormLlmAPI(llm.API):
    """LLM API exposing Brainstorm Hub tools to conversation agents."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the Brainstorm LLM API."""
        super().__init__(
            hass=hass,
            id=BRAINSTORM_LLM_API_ID,
            name="Brainstorm Hub",
        )

    async def async_get_api_instance(
        self, llm_context: llm.LLMContext
    ) -> llm.APIInstance:
        """Return the API instance with fresh tools and context."""
        store = _get_active_store(self.hass)
        cats = ", ".join(store.categories) if store else "Inbox, Smarthome, Haus & Garten, Projekte, Alltag"
        api_prompt = (
            "Brainstorm Hub is the central idea, thought, and note management system in Home Assistant. "
            f"Available categories: {cats}. "
            "Use brainstorm_add_idea to record new thoughts and notes, automatically picking the best category. "
            "Use brainstorm_get_ideas to fetch, query, or search ideas and tasks. "
            "Use brainstorm_complete_idea when a task or note is done. "
            "Use brainstorm_delete_idea to discard an idea. "
            "Use brainstorm_list_categories to see available categories."
        )

        tools: list[llm.Tool] = [
            BrainstormAddIdeaTool(self.hass),
            BrainstormGetIdeasTool(self.hass),
            BrainstormCompleteIdeaTool(self.hass),
            BrainstormDeleteIdeaTool(self.hass),
            BrainstormListCategoriesTool(self.hass),
        ]

        return llm.APIInstance(
            api=self,
            api_prompt=api_prompt,
            llm_context=llm_context,
            tools=tools,
        )


def async_register_llm_api(hass: HomeAssistant) -> Callable[[], None]:
    """Register the Brainstorm Hub LLM API."""
    try:
        api = BrainstormLlmAPI(hass)
        unregister = llm.async_register_api(hass, api)
        _LOGGER.info("Registered Brainstorm Hub LLM API with 5 tools for Assist/Conversation Agents")
        return unregister
    except Exception as err:
        _LOGGER.warning("Could not register Brainstorm Hub LLM API: %s", err)
        return lambda: None

