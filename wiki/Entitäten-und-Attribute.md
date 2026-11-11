🏠 [Start](Home) · 🇬🇧 [English version](Entities-and-Attributes)

## 🧩 Entitäten

| Entität | Was sie zeigt |
|---|---|
| `sensor.brainstorm_ideen_ubersicht` | Anzahl offener Ideen. Attribute: `active_count`, `completed_count`, `category_counts`, `priority_counts`, `categories`, `active_categories`, `latest_idea`, `recent_ideas`, `ideas`, `speech_overview`, `voice_mode`, `allowed_echos`. Mit eingeschalteter Privatsphäre sind nur Zahlen zu sehen. |
| `todo.<kategorie>` | Eine To-do-Liste pro Kategorie. Einträge lassen sich in der To-do-Ansicht anlegen, umbenennen, erledigen, mit Termin versehen und löschen; die Karten zeigen das sofort. Neue Kategorien bekommen gleich eine Liste, gelöschte verlieren ihre. |

Alle Entitäten gehören zum Gerät **Brainstorm Hub**. Unter [**Einstellungen > Geräte & Dienste > Brainstorm Hub > ⋮ > Diagnose herunterladen**](https://my.home-assistant.io/redirect/integration/?domain=brainstorm) gibt es eine Datei für Fehlerberichte. Sie enthält Zahlen und Einstellungen, aber keine Ideen-Texte, Personen oder Echos.

## 🔄 Wie die Daten aktualisiert werden

Brainstorm Hub speichert alle Ideen lokal in `.storage/brainstorm.storage` und fragt nichts in Abständen ab. Jede Änderung, ob von einer Karte, Alexa, Assist, einer Aktion oder einer To-do-Liste, aktualisiert Sensor und To-do-Listen im selben Moment und geht über die WebSocket-API an alle offenen Karten.

## Sensor-Attribute

`sensor.brainstorm_ideen_ubersicht` zählt offene Notizen. In den Attributen stehen u. a. alle Notizen, Kategorien, `allowed_echos`, `voice_mode` und `ui_level` (Bedienstufe).

```yaml
{{ state_attr('sensor.brainstorm_ideen_ubersicht', 'ideas')
   | selectattr('category', 'eq', 'Einkaufen') | list | count }}
```
