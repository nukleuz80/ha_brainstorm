🏠 [Start](Home) · 🇬🇧 [English version](Services-and-Events)

## 📋 Überblick

Alle Parameter stehen [weiter unten](#brainstormadd_idea) und unter [**Entwicklerwerkzeuge ➔ Aktionen**](https://my.home-assistant.io/redirect/tools_actions/).

| Dienst | Kurzbeispiel |
|---|---|
| `brainstorm.add_idea` | `text: "Filter tauschen"`, `category: Smarthome`, `priority: high`, `due: "2026-12-01 18:00"` |
| `brainstorm.update_idea` | `id: …`, `status: completed`, `in_progress: true`, `markers: [question, money]`, `progress: 50`, `links: [{to: …, label: braucht, blocks: true}]`, `frame: Phase 1` oder `callout: Farbe offen` |
| `brainstorm.delete_idea` | `id: …` |
| `brainstorm.delete_done` | erledigte löschen, optional nur ältere (`older_than_days`) |
| `brainstorm.restore_idea` | gelöschte Notiz zurückholen |
| `brainstorm.get_ideas` | Liste als Antwort, z. B. `category: Einkaufen` |
| `brainstorm.get_announcement` | fertiger Vorlesetext (`speech`) |
| `brainstorm.add_category` / `remove_category` | Kategorie anlegen oder entfernen |
| `brainstorm.set_category_style` | Icon und Farbe |
| `brainstorm.export_markdown` / `export_json` / `import_json` | Sichern und Übertragen |
| `brainstorm.bring_message` | Nachricht an Bring! |
| `brainstorm.reorder_ideas` | Reihenfolge setzen |
| `brainstorm.import_outline` | Gliederung anlegen: `text: …`, `category: …` oder `parent_id: …`, `format: auto` |
| `brainstorm.sort_children` | Unterpunkte sortieren: `parent_id: …`, `by: text`, `priority`, `due`, `created` oder `votes` |
| `brainstorm.react` | Reaktion umschalten: `id: …`, `reaction: heart` |
| `brainstorm.add_comment` / `delete_comment` | Kommentar: `id: …`, `text: "@Frida bringst du Salat?"`; löschen mit `comment_id` |
| `brainstorm.start_voting` / `vote` / `end_voting` | Abstimmung: `category: Urlaub`, `votes: 5`, `hidden: true`; `vote` mit `id`, `delta`; `end_voting` antwortet mit der Rangliste |
| `brainstorm.start_round` / `end_round` | Verdeckte Runde: `category: Urlaub`, `minutes: 10`; `end_round` deckt auf und antwortet mit `revealed` |
| `brainstorm.share` | Liste mit Personen teilen |

Mit `parse_due: true` wertet `add_idea` einen Zeitpunkt im Text aus wie bei Sprache:

```yaml
action: brainstorm.add_idea
data:
  text: "Erinnere mich morgen um 8 an den Müll"
  parse_due: true
```

Jede Aktion bleibt verfügbar, solange die Integration nicht geladen ist, und erklärt dann, warum sie nicht ausgeführt werden kann.

## `brainstorm.add_idea`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.add_idea)

Fügt blitzschnell eine neue Brainstorm-Idee hinzu. Erkennt automatisch Kategorien im Text (z.B. 'Garten: Blumen pflanzen' oder '#smarthome').

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `text` | Ja | Der Inhalt des Gedankens oder der Idee. |
| `category` | Nein | Thema/Kategorie. Bleibt dies leer, wird sie aus dem Text ermittelt oder 'Inbox' zugewiesen. |
| `priority` | Nein | Dringlichkeit der Idee (low, medium, high, urgent). Wird andernfalls automatisch erkannt. |
| `source` | Nein | Woher die Idee stammt (z.B. alexa, assist, dashboard). Ohne Quelle gilt der Text als getippt und behält seinen Wortlaut. Nur mit einer Sprachquelle werden gesprochene Sätze gekürzt. |
| `device` | Nein | Das auslösende Gerät (z.B. "Echo Show Küche", "Wohnzimmer Echo Dot", "Olaf (Handy)"). |
| `tags` | Nein | Zusätzliche Schlagworte. |
| `parent_id` | Nein | ID der übergeordneten Idee für Unteraufgaben/Einrückung (optional). |
| `due` | Nein | Wann Brainstorm an diese Idee erinnern soll. |
| `parse_due` | Nein | Erkennt Angaben wie "morgen um 8" im Text und nimmt sie als Termin. |
| `assignee` | Nein | Wer erinnert werden soll. |
| `zone` | Nein | Erinnert beim Betreten dieser Zone. |
| `language` | Nein | Sprache des Textes (z.B. "de" oder "en"). Ohne Angabe gilt die Sprache von Home Assistant. |

## `brainstorm.update_idea`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.update_idea)

Aktualisiert Text, Kategorie oder Status einer bestehenden Idee.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `id` | Ja | Eindeutige ID der Idee. |
| `text` | Nein | Geänderter Text. |
| `category` | Nein | Neue Kategorie. |
| `priority` | Nein | Neue Priorität (low, medium, high, urgent). |
| `status` | Nein | Neuer Status (active, completed, archived). |
| `device` | Nein | Gerät aktualisieren. |
| `parent_id` | Nein | ID der übergeordneten Idee für Unteraufgaben/Einrückung (leer = Hauptaufgabe). |
| `order` | Nein | Benutzerdefinierter Sortierindex. |
| `due` | Nein | Wann Brainstorm an diese Idee erinnern soll. |
| `assignee` | Nein | Wer erinnert werden soll. |
| `zone` | Nein | Erinnert beim Betreten dieser Zone. |
| `echos` | Nein | Die Echos, die die Erinnerung an diesen Eintrag sprechen, als Liste. `null` gilt wieder die Erinnerungs-Einstellungen. |
| `result` | Nein | Was aus dem Eintrag geworden ist, meist beim Abhaken notiert (höchstens 1000 Zeichen). Beide Karten zeigen es unter dem Text. Bleibt beim Wiederöffnen erhalten, leer oder `null` entfernt es. |
| `shape` | Nein | Form der Notiz auf der Mindmap: `card`, `cloud`, `bubble`, `thought`, `pill`, `rect`, `ellipse`, `hexagon`, `note` oder `underline`. Leer oder `null` nimmt wieder das Aussehen der Map. |
| `markers` | Nein | Marker als Liste: `question`, `idea`, `warning`, `money`, `star`, `flag`, `check`, `blocked`, `waiting`, `heart`. Ersetzt die bisherigen, eine leere Liste oder `null` entfernt sie. |
| `progress` | Nein | Fortschritt einer Notiz ohne Unteraufgaben: `0`, `25`, `50`, `75` oder `100`. `0` oder `null` entfernt ihn. Notizen mit Unteraufgaben berechnen ihn selbst. |
| `links` | Nein | Querverbindungen zu anderen Notizen als Liste von `{to: <id>, label: <Text, bis 40>, blocks: true/false}`, höchstens 20. `blocks: true` lässt das Ziel warten, bis diese Notiz erledigt ist. Ersetzt die bisherigen, eine leere Liste oder `null` entfernt sie. |
| `frame` | Nein | Name eines Rahmens in der Mindmap, bis 40 Zeichen. Notizen mit demselben Namen teilen sich einen Rahmen. Leer oder `null` entfernt ihn. |
| `callout` | Nein | Kurze Anmerkung in einer Sprechblase über der Notiz, bis 200 Zeichen. Leer oder `null` entfernt sie. |
| `repeat` | Nein | Lässt die Idee nach dem Abhaken wiederkommen: `daily`, `weekdays`, `weekly`, `biweekly`, `monthly` oder `yearly`. Die neue Idee ist zum nächsten Termin nach jetzt fällig, mit gleichen Angaben und wieder offenen Unteraufgaben. Leer oder `null` beendet es. |
| `numbering` | Nein | Nummeriert die Unteraufgaben der Notiz und deren Unteraufgaben: `decimal` (1., 1.1), `alpha` (a), b)) oder `roman` (I., II.). Leer oder `null` entfernt sie. |

## `brainstorm.delete_idea`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.delete_idea)

Entfernt eine Idee. Bis zum nächsten Start von Home Assistant holt `brainstorm.restore_idea` sie zurück.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `id` | Ja | ID der zu löschenden Idee. |

## `brainstorm.delete_done`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.delete_done)

Löscht erledigte (abgehakte oder archivierte) Einträge auf einmal. Mit eingeschalteter Privatsphäre nur die eigenen. Gelöschte Einträge lassen sich nicht zurückholen. Die Antwort nennt die Anzahl (`deleted`).

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `older_than_days` | Nein | Nur Einträge, die mindestens so viele Tage erledigt sind. `0` (Standard) löscht alle erledigten. |

## `brainstorm.restore_idea`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.restore_idea)

Holt eine Idee zurück, die seit dem letzten Start von Home Assistant gelöscht wurde, samt der Verbindung zu ihren Unteraufgaben. Das kann nur, wer sie gelöscht hat. Die Mindmap-Karte nutzt das für „Rückgängig“.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `id` | Ja | ID der gelöschten Idee. |

## `brainstorm.get_ideas`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.get_ideas)

Gibt eine Liste gespeicherter Ideen zurück (für Templates oder Automationen).

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `category` | Nein | Optional nach Kategorie filtern. |
| `priority` | Nein | Optional nach Priorität filtern (low, medium, high, urgent). |
| `status` | Nein | Status-Filter (active, completed oder all). |

## `brainstorm.get_announcement`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.get_announcement)

Erzeugt einen flüssigen, gesprochenen Ansagetext für Alexa oder Assist über alle oder eine bestimmte Kategorie.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `category` | Nein | Optional nach einer bestimmten Kategorie filtern (z.B. Smarthome). Ohne Angabe werden alle aktiven Kategorien vorgelesen. |
| `device` | Nein | Das Gerät, das gefragt hat. Bei eingeschalteter Privatsphäre bestimmt es, wessen Einträge genannt werden. |

## `brainstorm.add_category`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.add_category)

Erstellt eine neue Brainstorm-Kategorie und die dazugehörige To-do-Liste.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `name` | Ja | Name der neuen Kategorie. |
| `icon` | Nein | Optionales Home Assistant / MDI Icon. |
| `color` | Nein | Optionale Akzentfarbe (Hexadezimal wie #ff7800). |

## `brainstorm.set_category_style`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.set_category_style)

Legt ein benutzerdefiniertes Icon und/oder eine Akzentfarbe für eine Kategorie fest.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `category` | Ja | Name der zu formatierenden Kategorie. |
| `icon` | Nein | Home Assistant / MDI Icon. |
| `color` | Nein | Akzentfarbe für Notizen und Filter (Hexadezimal wie #06b6d4). |
| `reset` | Nein | Falls aktiviert, werden benutzerdefiniertes Icon und Farbe entfernt und auf Standard zurückgesetzt. |

## `brainstorm.remove_category`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.remove_category)

Entfernt eine Kategorie (verbleibende Ideen werden nach 'Inbox' verschoben).

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `name` | Ja | Name der Kategorie. |

## `brainstorm.export_markdown`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.export_markdown)

Schreibt alle Kategorien und Ideen als Markdown-Dateien ins Dateisystem.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `path` | Nein | Zielordner (Standard: der Markdown-Ordner aus den Optionen, `/config/brainstorm`). Nur Admins dürfen einen Ordner wählen; er muss in `/config/brainstorm`, im Markdown-Ordner aus den Optionen oder in `allowlist_external_dirs` liegen. |

## `brainstorm.export_json`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.export_json)

Gibt die Ideen, die du sehen darfst, samt Kategorien, Icons und Farben als JSON zurück. Zum Sichern, für den Umzug auf ein anderes Home Assistant oder zum Teilen einer Kategorie.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `category` | Nein | Nur diese Kategorie exportieren. Standard: alle Kategorien. |
| `path` | Nein | Den Export zusätzlich in diese Datei schreiben, etwa `brainstorm/sicherung.json` (relativ zu `/config`). Der Name muss auf `.json` enden. Erlaubt sind nur `/config/brainstorm`, der Markdown-Ordner aus den Optionen und `allowlist_external_dirs`. Nur Admins dürfen Dateien schreiben. |

```yaml
action: brainstorm.export_json
data:
  path: brainstorm/sicherung.json
response_variable: sicherung
```

## `brainstorm.import_json`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.import_json)

Fügt die Ideen eines JSON-Exports hinzu, die es hier noch nicht gibt. Ideen mit vorhandener ID werden übersprungen, zweimal dieselbe Datei zu importieren ändert also nichts. Fehlende Kategorien werden angelegt, Icons und Farben übernommen, wo eine Kategorie noch keine hat.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `data` | Eins von beiden | Die Antwort von `brainstorm.export_json`. |
| `path` | Eins von beiden | Eine von `brainstorm.export_json` geschriebene Datei, relativ zu `/config`, aus denselben Ordnern wie beim Export. Nur Admins dürfen Dateien lesen. |

Besitzer und Freigaben bleiben nur für Benutzer dieses Home Assistant erhalten, Besitzer nur, wenn ein Admin importiert. Sonst gehören die Ideen dem, der importiert. Die Antwort nennt, wie viele Ideen hinzugefügt (`added`) und übersprungen (`skipped`) wurden und welche Kategorien neu sind.

## `brainstorm.bring_message`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.bring_message)

Sagt allen auf einer Bring-Liste etwas, über die Benachrichtigungen von Bring selbst. In der Karte bietet der 🛒-Knopf einer Listen-Notiz *Ich gehe einkaufen*, *Einkauf erledigt* und *Liste geändert*; das Menü eines Eintrags auf einer Liste bietet *Dringend in Bring melden*.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `id` | Ja | ID einer Bring-Listen-Notiz oder eines Eintrags auf so einer Liste. |
| `message` | Ja | `going_shopping`, `changed_list`, `shopping_done` oder `urgent_message`. Eine dringende Nachricht braucht einen Eintrag, dessen Text Bring mitschickt. |

## `brainstorm.reorder_ideas`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.reorder_ideas)

Aktualisiert die benutzerdefinierte Sortierreihenfolge der Notizen anhand einer Liste von IDs.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `idea_ids` | Ja | Geordnete Liste der Notiz-IDs. |

## `brainstorm.import_outline`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.import_outline)

Legt einen Baum von Notizen aus einer Markdown-Gliederung, eingerücktem Text, OPML oder einer FreeMind-/Freeplane-Map (`.mm`) an, höchstens 300 Notizen. Gibt `added` und die neuen `ids` zurück.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `text` | Ja | Die Gliederung: Überschriften, Listen mit `-`/`*`/`1.` oder eingerückte Zeilen; `- [x]` legt einen Punkt als erledigt an, eine `>`-Zeile unter einem Punkt ist seine Beschreibung. Oder der Inhalt einer OPML- oder `.mm`-Datei. |
| `format` | Nein | `auto` (Standard), `markdown`, `opml` oder `freemind`. |
| `category` | Nein | Wohin die Notizen kommen; ohne Angabe die Standardkategorie. |
| `parent_id` | Nein | Hängt die Gliederung unter diese Notiz, in deren Kategorie. |

## `brainstorm.sort_children`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.sort_children)

Sortiert die Unteraufgaben einer Notiz oder die Hauptnotizen einer Kategorie innerhalb der Plätze, die sie schon haben. Andere Notizen bleiben, wo sie sind.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `parent_id` | Nein | Die Notiz, deren Unteraufgaben sortiert werden. |
| `category` | Nein | Ohne `parent_id`: die Kategorie, deren Hauptnotizen sortiert werden. |
| `by` | Nein | `text` (A–Z), `priority` (dringend zuerst), `due` (früheste zuerst, Notizen ohne Datum am Ende) oder `created` (älteste zuerst), `votes` (meiste Stimmen zuerst). |
| `ids` | Nein | Statt `by`: die Unteraufgaben in fester Reihenfolge, etwa um ein Sortieren rückgängig zu machen. |
| `reverse` | Nein | Sortiert andersherum. |

## `brainstorm.react`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.react)

Setzt oder entfernt die eigene Reaktion an einer Notiz. Jede Person hat pro Reaktion eine Stimme; wer eine Notiz sehen darf, darf auch reagieren.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `id` | Ja | ID der Notiz. |
| `reaction` | Ja | `like` 👍, `heart` ❤️, `laugh` 😂 oder `important` ❗ |
| `active` | Nein | `true` setzt, `false` entfernt; ohne Angabe wird umgeschaltet. |

## `brainstorm.add_comment`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.add_comment)

Schreibt einen Kommentar an eine Notiz. Wer die Notiz sehen darf, darf kommentieren. Mit `@Name` genannte Personen bekommen eine Nachricht über ihre Kanäle unter *Erinnerungen ➔ Personen*, mit Privatsphäre nur, wenn sie die Notiz sehen dürfen. Antwortet mit `comment` und `notified` (benachrichtigte Personen). Löst das Ereignis `brainstorm_comment_added` aus.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `id` | Ja | ID der Notiz. |
| `text` | Ja | Der Kommentar, bis 2000 Zeichen. `@Frida` oder `@Frida Sommer` benachrichtigt diese Person. |
| `notify` | Nein | `false` schreibt den Kommentar ohne Benachrichtigung. |

## `brainstorm.delete_comment`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.delete_comment)

Entfernt einen Kommentar. Das darf, wer ihn geschrieben hat oder die Notiz ändern darf.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `id` | Ja | ID der Notiz. |
| `comment_id` | Ja | ID des Kommentars. |

## `brainstorm.group_ideas`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.group_ideas)

Hängt Notizen einer Kategorie unter eine neue Notiz mit diesem Titel, zum Beispiel ein Thema, das die KI vorgeschlagen hat. Die neue Notiz nimmt den Platz der ersten Notiz ein, die Notizen behalten Reihenfolge und Unterpunkte. Antwortet mit der ID der neuen Notiz (`id`).

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `title` | Ja | Text der neuen Oberpunkt-Notiz. |
| `ids` | Ja | Die Notizen, die darunter kommen, alle aus derselben Kategorie. |

## `brainstorm.start_round`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.start_round)

Startet eine verdeckte Brainstorm-Runde in einer Kategorie: Neue Notizen sieht bis zum Aufdecken nur, wer sie geschrieben hat. Läuft schon eine Runde, bleibt sie, wie sie ist. Antwortet mit der Runde (`round`: `since`, `by`, `ends_at`).

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `category` | Ja | Die Kategorie der Runde. |
| `minutes` | Nein | Nach so vielen Minuten deckt die Runde von selbst auf (1–60, 0 = bis zum Aufdecken). |

## `brainstorm.end_round`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.end_round)

Deckt die verdeckte Runde einer Kategorie auf. Antwortet mit der Zahl der aufgedeckten Notizen (`revealed`) und löst das Ereignis `brainstorm_round_ended` aus.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `category` | Ja | Die Kategorie der Runde. |

## `brainstorm.start_voting`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.start_voting)

Startet eine Abstimmung in einer Kategorie. Jede Person bekommt gleich viele Stimmen und verteilt sie auf die Notizen, auch mehrere auf eine.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `category` | Ja | Die Kategorie, über deren Notizen abgestimmt wird. |
| `votes` | Nein | Stimmen pro Person (1–20, Standard 5). |
| `hidden` | Nein | Verdeckt: Jeder sieht bis zum Ende nur die eigenen Stimmen. |
| `clear` | Nein | Löscht die Punkte einer früheren Runde. |

## `brainstorm.vote`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.vote)

Gibt einer Notiz in einer laufenden Abstimmung Stimmen oder nimmt sie zurück. Antwortet mit `votes` (eigene an dieser Notiz), `used` und `allowed`.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `id` | Ja | ID der Notiz. |
| `delta` | Nein | Wie viele Stimmen dazu (Standard 1), negativ nimmt zurück. |

## `brainstorm.end_voting`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.end_voting)

Beendet die Abstimmung einer Kategorie und antwortet mit der Rangliste (`ranking`: `id`, `text`, `points`, `voters`). Die Punkte bleiben an den Notizen, `sort_children` mit `by: votes` sortiert danach.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `category` | Ja | Die Kategorie der Abstimmung. |

## `brainstorm.share`

▶️ [In Home Assistant ausprobieren](https://my.home-assistant.io/redirect/tools_perform_action/?service=brainstorm.share)

Gibt mehrere Einträge oder eine ganze Kategorie für Personen frei. Braucht eingeschaltete Privatsphäre.

| Feld | Pflicht | Bedeutung |
| :--- | :--- | :--- |
| `ids` | Nein | IDs der freizugebenden Einträge. |
| `category` | Nein | Alle eigenen Einträge dieser Kategorie freigeben, auch spätere. |
| `shares` | Ja | Benutzer-ID (oder "all") und Stufe, z. B. {"all": "view"}. Stufen sind view und edit; null entfernt die Freigabe. |

## Ereignisse

| Ereignis | Wann |
|---|---|
| `brainstorm_idea_added` | neue Notiz |
| `brainstorm_idea_updated` | Notiz geändert |
| `brainstorm_idea_completed` | Notiz abgehakt |
| `brainstorm_idea_deleted` | Notiz gelöscht |
| `brainstorm_reminder_due` | Erinnerung ist fällig |
| `brainstorm_comment_added` | neuer Kommentar (`idea_id`, `idea_text`, `text`, `by`, `mentions`) |
| `brainstorm_round_ended` | verdeckte Runde aufgedeckt (`category`, `revealed`) |

In den Ereignisdaten steckt die ganze Notiz (`id`, `text`, `category`, `priority`, `source`, …):

```yaml
triggers:
  - trigger: event
    event_type: brainstorm_idea_added
    event_data:
      priority: urgent
actions:
  - action: light.turn_on
    target:
      entity_id: light.flur
    data:
      color_name: red
```
