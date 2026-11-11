🏠 [Home](Home) · 🇩🇪 [Deutsche Version](Entitäten-und-Attribute)

## 🧩 Entities

| Entity | What it shows |
|---|---|
| `sensor.brainstorm_ideen_ubersicht` | Number of open ideas. Attributes: `active_count`, `completed_count`, `category_counts`, `priority_counts`, `categories`, `active_categories`, `latest_idea`, `recent_ideas`, `ideas`, `speech_overview`, `voice_mode`, `allowed_echos`. With privacy switched on, only counts are shown. |
| `todo.<category>` | One to-do list per category. Items can be added, renamed, completed, given a due date and deleted in the to-do panel; changes reach the cards at once. New categories get a list right away, removed ones lose theirs. |

All entities belong to the device **Brainstorm Hub**. [**Settings > Devices & services > Brainstorm Hub > ⋮ > Download diagnostics**](https://my.home-assistant.io/redirect/integration/?domain=brainstorm) gives a file for bug reports. It holds counts and settings, but no idea texts, people or Echos.

## 🔄 How the Data Updates

Brainstorm Hub keeps all ideas locally in `.storage/brainstorm.storage` and does not poll anything. Every change, whether from a card, Alexa, Assist, an action or a to-do list, updates the sensor and the to-do lists at the same moment and is pushed to all open cards over the WebSocket API.

## Sensor attributes

`sensor.brainstorm_ideen_ubersicht` counts open notes. Its attributes include all notes, the categories, `allowed_echos`, `voice_mode` and `ui_level` (operating level).

```yaml
{{ state_attr('sensor.brainstorm_ideen_ubersicht', 'ideas')
   | selectattr('category', 'eq', 'Shopping') | list | count }}
```
