🏠 [Home](Home) · 🇩🇪 [Deutsche Version](Automationen-und-Beispiele)

**Read the open ideas aloud every morning:**
```yaml
triggers:
  - trigger: time
    at: "07:30:00"
actions:
  - action: brainstorm.get_announcement
    response_variable: overview
  - action: notify.alexa_media
    data:
      target: media_player.echo_kitchen
      data:
        type: announce
      message: "{{ overview.speech }}"
```

**Note something when the washing machine is done:**
```yaml
triggers:
  - trigger: state
    entity_id: binary_sensor.washing_machine_running
    to: "off"
actions:
  - action: brainstorm.add_idea
    data:
      text: Hang up the laundry
      category: Alltag
      priority: high
```

More examples for Assist and Alexa are in the [`examples/`](https://github.com/nukleuz80/ha_brainstorm/tree/main/examples/) folder.

## Ready-made recipes

**Read out open notes in the morning**

```yaml
triggers:
  - trigger: time
    at: "07:30:00"
actions:
  - action: brainstorm.get_announcement
    response_variable: overview
  - action: notify.alexa_media
    data:
      target: media_player.echo_kitchen
      data:
        type: announce
      message: "{{ overview.speech }}"
```

**A note when the washing machine is done**

```yaml
triggers:
  - trigger: state
    entity_id: binary_sensor.washing_machine_running
    to: "off"
actions:
  - action: brainstorm.add_idea
    data:
      text: Hang up the laundry
      category: Daily Life
      priority: high
```

**Clean up done notes every Sunday**

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

More templates for Alexa and Assist are in [`examples/`](https://github.com/nukleuz80/ha_brainstorm/tree/main/examples/).
