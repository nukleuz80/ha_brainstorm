🏠 [Start](Home) · 🇬🇧 [English version](Automations-and-Examples)

**Jeden Morgen die offenen Ideen vorlesen:**
```yaml
triggers:
  - trigger: time
    at: "07:30:00"
actions:
  - action: brainstorm.get_announcement
    response_variable: ueberblick
  - action: notify.alexa_media
    data:
      target: media_player.echo_kuche
      data:
        type: announce
      message: "{{ ueberblick.speech }}"
```

**Notieren, wenn die Waschmaschine fertig ist:**
```yaml
triggers:
  - trigger: state
    entity_id: binary_sensor.waschmaschine_lauft
    to: "off"
actions:
  - action: brainstorm.add_idea
    data:
      text: Wäsche aufhängen
      category: Alltag
      priority: high
```

Weitere Beispiele für Assist und Alexa liegen im Ordner [`examples/`](https://github.com/nukleuz80/ha_brainstorm/tree/main/examples/).

## Fertige Rezepte

**Morgens vorlesen, was offen ist**

```yaml
triggers:
  - trigger: time
    at: "07:30:00"
actions:
  - action: brainstorm.get_announcement
    response_variable: ueberblick
  - action: notify.alexa_media
    data:
      target: media_player.echo_kuche
      data:
        type: announce
      message: "{{ ueberblick.speech }}"
```

**Notiz, wenn die Waschmaschine fertig ist**

```yaml
triggers:
  - trigger: state
    entity_id: binary_sensor.waschmaschine_lauft
    to: "off"
actions:
  - action: brainstorm.add_idea
    data:
      text: Wäsche aufhängen
      category: Alltag
      priority: high
```

**Erledigte jeden Sonntag aufräumen**

```yaml
triggers:
  - trigger: time
    at: "03:00:00"
conditions:
  - condition: time
    weekday: sun
actions:
  - action: brainstorm.delete_done
    data:
      older_than_days: 14
```

Weitere Vorlagen für Alexa und Assist liegen in [`examples/`](https://github.com/nukleuz80/ha_brainstorm/tree/main/examples/).
