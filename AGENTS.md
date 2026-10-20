# Home Assistant Development Standards & Guidelines

This project strictly adheres to the official Home Assistant developer documentation and standards as specified at [contributors.home-assistant.io](https://contributors.home-assistant.io/).

## 1. Code Style & Standards
- **Typing**: Always include `from __future__ import annotations` at the top of every Python file. Use strict, modern type hints (`dict[str, Any]`, `list[str]`, `Callable[[], None]`, `Awaitable[None]`).
- **Formatting**: Follow PEP 8 and Home Assistant conventions (conforming to `ruff` / `black`, 88 char line length, double quotes, standard import sorting: stdlib -> 3rd-party -> homeassistant -> relative local imports).
- **Asynchronous Execution**: Never run blocking operations inside the main event loop. All I/O, storage calls, and heavy computations must use `asyncio` or be offloaded via `await hass.async_add_executor_job(...)`.

## 2. Integration Architecture
- **Manifest (`manifest.json`)**:
  - Maintain complete metadata (`integration_type`, `iot_class`, `documentation`, `issue_tracker`, `codeowners`, `single_config_entry: true` if applicable).
- **Config Flow & Options Flow**:
  - Implement configuration flows inheriting from `config_entries.ConfigFlow` and `config_entries.OptionsFlowWithConfigEntry` (or `OptionsFlow`).
  - Never hardcode user-facing texts; manage all schema labels, error messages, and descriptions via `strings.json` and `translations/{lang}.json`.
  - Use `async_show_menu` for multi-step configuration tasks.
- **Entity Platform Design**:
  - Always enable `_attr_has_entity_name = True`.
  - Assign deterministic, unique identifiers via `_attr_unique_id`.
  - Provide complete device information via `device_info = DeviceInfo(...)`.
  - Leverage `_attr_translation_key` for entity naming and states.
- **Data Storage & State Management**:
  - Persist integration state through `homeassistant.helpers.storage.Store`.
  - Never modify files inside `custom_components/` at runtime. User data lives strictly in `/config/` or `.storage/`.
- **Exception Handling & Logging**:
  - Use `_LOGGER = logging.getLogger(__name__)`.
  - Raise standard exceptions (`HomeAssistantError`, `ConfigEntryNotReady`, `ServiceValidationError`) from `homeassistant.exceptions`.
  - Do not use bare `except:` or swallow exceptions silently.

## 3. Frontend & Custom Cards
- Follow official Home Assistant Lovelace Custom Card specifications:
  - Register components with `customElements.define(...)`.
  - Implement `setConfig`, `getCardSize`, and `getStubConfig`.
  - Use official theme CSS custom properties (`var(--primary-color)`, `var(--card-background-color)`, `var(--primary-text-color)`, etc.) to support both light and dark themes seamlessly.
  - Ensure full responsiveness on mobile screens (responsive wraps, minimum touch target sizes).
