🏠 [Start](Home) · 🇬🇧 [English version](Settings)

Eine Übersicht mit typischen Beispielen pro Menü steht [weiter unten](#integration). Was Ereignisse, Sensor und Dienste angeht, siehe [Dienste & Ereignisse](Dienste-und-Ereignisse) und [Entitäten & Attribute](Entitäten-und-Attribute).

## Bei der Einrichtung

Du kannst sie später unter **Neu konfigurieren** ändern. Keine davon ist Pflicht, die Vorgaben funktionieren für alle.

| Feld | Was es bewirkt |
| :--- | :--- |
| Kategorien ohne Notizen (0) ausblenden | Blendet Kategorien ohne Notizen auf den Karten aus. |
| Ideen automatisch als Markdown-Dateien exportieren | Schreibt bei jeder Änderung pro Kategorie eine Markdown-Datei in den unten genannten Ordner. |
| Dateipfad für Markdown-Dateien | Ordner für die Markdown-Dateien, zum Beispiel /config/brainstorm. |

Neu konfigurieren bietet zusätzlich:

| Feld | Was es bewirkt |
| :--- | :--- |
| Intelligente Text-Optimierung | Korrigiert Groß-/Kleinschreibung und Grammatik neuer Ideen und entfernt Füllwörter. |

## Nach der Einrichtung

Du findest sie unter [**Einstellungen ➔ Geräte & Dienste ➔ Brainstorm Hub ➔ Konfigurieren**](https://my.home-assistant.io/redirect/integration/?domain=brainstorm).

### Brainstorm › Kategorien

| Feld | Was es bewirkt |
| :--- | :--- |
| ➕ Neue Kategorie anlegen (optional) | Name einer neuen Kategorie. Leer lassen, um keine anzulegen. |
| 🗑️ Kategorie löschen (optional) | Die Ideen einer gelöschten Kategorie wandern in die Inbox. |
| ✏️ Komplette Liste anpassen (durch Komma getrennt) | Alle Kategorien, durch Komma getrennt. Ändere die Liste, um mehrere auf einmal umzubenennen, umzusortieren oder zu entfernen. |
| Kategorien ohne Notizen (0) ausblenden | Blendet Kategorien ohne Notizen auf den Karten aus. |

### Brainstorm › Kategorie-Design

| Feld | Was es bewirkt |
| :--- | :--- |
| Kategorie auswählen | Die Kategorie, deren Icon und Farbe du ändern möchtest. |

### Brainstorm › Kategorie-Design

| Feld | Was es bewirkt |
| :--- | :--- |
| Kategorie-Icon (Home Assistant / MDI) | Wird für diese Kategorie auf den Karten angezeigt. |
| Kategorie-Farbe | Farbe dieser Kategorie auf den Karten. |
| Auf Standard-Icon und -Farbe zurücksetzen | Entfernt Icon und Farbe dieser Kategorie und ignoriert die beiden Felder darüber. |

### Brainstorm › Allgemein

| Feld | Was es bewirkt |
| :--- | :--- |
| Bedienstufe | Wie viele Bedienelemente die Karten und diese Einstellungen zeigen: Einsteiger, Normal oder Profi. Neue Installationen starten mit Normal, bestehende behalten Profi. Ausblenden löscht nichts, und jede Karte kann mit `level` ihre eigene Stufe haben. Details [unten](#bedienstufe). |
| Standard-Kategorie für neue Ideen | Wird genutzt, wenn eine Idee keiner Kategorie zugeordnet werden kann. |
| Intelligente Text-Optimierung (Grammatik, Groß-/Kleinschreibung, Infinitiv) | Korrigiert Groß-/Kleinschreibung und Grammatik neuer Ideen und entfernt Füllwörter. |
| Datum aus gesprochenem Text als Termin übernehmen | Ein gesprochenes „morgen“ oder „am 25.11.“ wandert aus dem Text in den Termin. Ein Termin löst zu dieser Zeit eine Erinnerung aus, ohne Uhrzeit um 9 Uhr. |
| Eigene Begriffe für gesprochenen Text | Ein Begriff pro Zeile, zum Beispiel Lenia, oder eine Korrektur, zum Beispiel fehler = Richtig. Namen von Personen und Kategorien sind automatisch bekannt. |
| Ideen automatisch als Markdown exportieren | Schreibt bei jeder Änderung pro Kategorie eine Markdown-Datei in den unten genannten Ordner. |
| Dateipfad für Markdown-Dateien | Ordner für die Markdown-Dateien, zum Beispiel /config/brainstorm. |
| Echo-Geräte für die Spracheingabe | Nur diese Echos können Ideen per Sprache erfassen und Brainstorm öffnen. Leer lassen, um alle Echos zu nutzen. |

### Brainstorm › Alexa

| Feld | Was es bewirkt |
| :--- | :--- |
| Spracheingabe | Nativ nutzt den Satz über Alexa Media ohne Skill. Skill und Beide nutzen deinen eigenen Alexa-Skill. |

### Brainstorm › Alexa › Skill

| Feld | Was es bewirkt |
| :--- | :--- |
| Skill-Code (lambda_function.py) | Kopiere das in die lambda_function.py deines Skills. Halte es geheim, es enthält deine geheime Adresse. |
| Sprachmodell (JSON-Editor) | Füge das im JSON-Editor der Alexa Developer Console ein. |
| Neue geheime Adresse erzeugen und Skill-Kopplung entfernen | Nutze das, wenn die Adresse bekannt wurde oder du einen neuen Skill gebaut hast. Kopiere danach den neuen Skill-Code. |
| Name für dieses unbekannte Gerät | Zum Beispiel Alexa App iPhone. Home Assistant kann die Alexa-App nicht selbst erkennen. Der Name gilt für den letzten Eintrag und alle späteren von diesem Gerät. |

### Brainstorm › Erinnerungen › Ein/Aus & Kanäle

| Feld | Was es bewirkt |
| :--- | :--- |
| Erinnerungen nutzen | Aus stoppt alle Erinnerungen, das Briefing, den Rückblick und alles andere in diesem Menü. |
| Alexa-Ansage | Welcher Echo eine Erinnerung ansagt. Aus bedeutet keine Ansage. |
| Echos für Ansagen | Für feste Echos, als Ersatz sowie für Briefing und Rückblick. |
| Benachrichtigungen senden | Aus stoppt die Benachrichtigungen, die gewählten Dienste bleiben erhalten. |
| Benachrichtigungsdienste | Diese Dienste erhalten Erinnerungen, zum Beispiel dein Handy. |
| Wartezeit vor Benachrichtigungen (Minuten) | Nur mit Alexa: Du hast Zeit zu reagieren, bevor das Handy benachrichtigt wird. Bei 0 kommt beides sofort. |
| Wichtige offene Einträge erneut senden | Sendet Einträge mit hoher oder dringender Priorität erneut, solange sie offen sind. |
| Dienste für wichtige Einträge | Diese Dienste erhalten die wiederholte Nachricht. |
| Erneut senden nach (Minuten) | Gilt für noch offene Einträge mit hoher oder dringender Priorität. |

### Brainstorm › Erinnerungen › Ruhezeit, Briefing & Rückblick

| Feld | Was es bewirkt |
| :--- | :--- |
| Ruhezeit nutzen | Aus ignoriert die Zeiten darunter, sie bleiben aber erhalten. |
| Ruhezeit von | Erinnerungen warten bis zum Ende der Ruhezeit. Dringende Einträge erreichen die Benachrichtigungsdienste trotzdem, aber kein Echo spricht. |
| Ruhezeit bis | Zu dieser Zeit werden wartende Erinnerungen gesendet. |
| Tägliches Briefing | Sendet einmal täglich eine Übersicht des Tages. |
| Uhrzeit des Briefings | Wann das Briefing gesendet wird. |
| Nur wenn hier jemand erkannt wird | Optional: Das Briefing wartet nach seiner Uhrzeit bis zu 6 Stunden, bis ein Sensor oder eine Person hier jemanden meldet. |
| Wochenrückblick | Sendet einmal pro Woche eine Übersicht älterer offener Einträge. |
| Tag des Rückblicks | Der Wochentag des Rückblicks. |
| Uhrzeit des Rückblicks | Wann der Rückblick gesendet wird. |
| Einträge nennen, die länger offen sind als (Tage) | Einträge, die länger offen sind, erscheinen im Rückblick. |

### Brainstorm › Erinnerungen › Regeln pro Liste

| Feld | Was es bewirkt |
| :--- | :--- |
| Regeln pro Liste nutzen | Aus lässt alle Listen die normalen Einstellungen nutzen, die Regeln bleiben erhalten. |
| Liste bearbeiten | Wähle eine Liste, um ihre Regel auf der nächsten Seite zu bearbeiten. |

### Brainstorm › Erinnerungen › Regeln › …

| Feld | Was es bewirkt |
| :--- | :--- |
| Erinnerungen dieser Liste gehen an | Normale Kanäle folgen den allgemeinen Einstellungen der Erinnerungen. |
| Eigene Benachrichtigungsdienste für diese Liste | Ersetzen die normalen Dienste für diese Liste. Leer nutzt die normalen. |
| Offene Einträge an bestimmten Tagen senden | Sendet die offenen Einträge dieser Liste an den Tagen und zur Uhrzeit darunter. |
| Tage | Die Tage, an denen die Liste gesendet wird. |
| Uhrzeit | Wann die Liste an diesen Tagen gesendet wird. |
| Offene Einträge an einem Ort senden | Wird einmal am Tag gesendet, wenn jemand dort ankommt. Braucht den Schalter für Orte. |
| Ort | Die Zone, in der die offenen Einträge dieser Liste gesendet werden. |

### Brainstorm › Erinnerungen › Orte & Heimkommen

| Feld | Was es bewirkt |
| :--- | :--- |
| Beim Heimkommen erinnern | Damit kannst du sagen, dass eine Erinnerung beim Heimkommen kommen soll. |
| An Orten (Zonen) erinnern | Damit kannst du für eine Erinnerung eine Zone nennen, zum Beispiel einen Supermarkt. |
| Wer mit "ich" gemeint ist | Ohne Person löst jeder aus, der dort ankommt. |

### Brainstorm › Erinnerungen › Personen

| Feld | Was es bewirkt |
| :--- | :--- |
| Erinnerungen für andere Personen nutzen | Damit kann eine Erinnerung für jemand anderen sein, zum Beispiel: erinnere Alex. |
| Person bearbeiten | Wähle eine Person, um ihre Kanäle auf der nächsten Seite einzustellen. |

### Brainstorm › Erinnerungen › Personen › …

| Feld | Was es bewirkt |
| :--- | :--- |
| Benachrichtigungsdienste | Die Benachrichtigungsdienste dieser Person. |
| Echos | Die Echos, die die Erinnerungen dieser Person ansagen. |

### Brainstorm › Erinnerungen › Kalender & Alexa

| Feld | Was es bewirkt |
| :--- | :--- |
| Erinnerungen in einen Kalender eintragen | Nur in eine Richtung und einmal pro Erinnerung. Spätere Änderungen werden nicht übertragen. |
| Kalender | Der Kalender, der die Erinnerungen erhält. |
| Zusätzlich echte Alexa-Erinnerungen anlegen | Schalte in der Alexa-Konsole zusätzlich Reminders unter Build ➔ Permissions ein. Alexa klingelt dann selbst, und Home Assistant spricht nicht zusätzlich. |

### Brainstorm › KI

Brainstorm nutzt eine KI-Aufgaben-Entität von Home Assistant, etwa Google Gemini, OpenAI oder Ollama. Ohne Entität bleibt alles aus.

| Feld | Was es bewirkt |
| :--- | :--- |
| KI-Aufgaben-Entität | Ist sie gewählt, schlägt ✨ an einer Notiz der Mindmap Unteraufgaben vor. Gesendet werden nur diese Notiz, ihre Kategorie und ihre Unteraufgaben, und nur, wenn du den Knopf drückst. |
| Gesprochene Einträge per KI verbessern | Jeder gesprochene Eintrag wird zuerst gespeichert und wenige Sekunden später verbessert. Das Ergebnis wird verworfen, wenn es Wörter hinzufügt oder eine Verneinung ändert. Der Text geht an den Anbieter der gewählten KI. |
| Briefing und Rückblick per KI kürzen | Morgen-Briefing und Wochenrückblick der Erinnerungen werden gekürzt. Deine Einträge gehen dafür an den Anbieter der gewählten KI. |

### Brainstorm › Erledigte Einträge löschen

Die Seite zeigt, wie viele erledigte (abgehakte oder archivierte) Einträge es gibt. Gelöschte Einträge lassen sich nicht zurückholen, exportiere sie vorher, wenn du sie behalten willst.

| Feld | Was es bewirkt |
| :--- | :--- |
| Erledigte Einträge löschen nach (Tagen) | Einträge, die so viele Tage erledigt sind, werden von selbst gelöscht, geprüft alle sechs Stunden und einmal direkt beim Speichern. 0 (Standard) behält sie. Offene Unteraufgaben bleiben als Hauptaufgaben, Anhänge gehen mit. |
| Alle erledigten Einträge jetzt löschen | Löscht beim Speichern jeden erledigten Eintrag, egal wie lange er schon erledigt ist. Das Menü zeigt danach, wie viele es waren. |

### Brainstorm › To-do-Listen koppeln

Ein Feld pro Kategorie. Wähle eine To-do-Liste einer anderen Integration, etwa Bring!, Google Tasks, Todoist oder eine lokale To-do-Liste, und beide bleiben gleich:

| Was passiert | Auf der Liste | In Brainstorm |
| :--- | :--- | :--- |
| Etwas kommt dazu | wird zur Notiz in der Kategorie | eine aktive Notiz landet auf der Liste |
| Etwas wird umbenannt oder abgehakt | die Notiz zieht mit | der Eintrag zieht mit |
| Etwas wird gelöscht | ein entfernter Eintrag hakt seine Notiz ab | eine gelöschte Notiz entfernt ihren Eintrag |

- **Wann:** sofort nach einer Änderung in Brainstorm oder einem neuen Eintrag auf der Liste, und alle 5 Minuten für Umbenennungen, die Listen nicht melden.
- **Beide geändert:** Wurde derselbe Eintrag zwischen zwei Abgleichen auf beiden Seiten umbenannt, gewinnt der Name auf der Liste.
- **Erstes Koppeln:** Offene Einträge mit gleichem Text werden verbunden statt verdoppelt, und die Schreibweise der Liste gewinnt. Erledigte Notizen kommen nicht auf die Liste.
- **Fälligkeiten** gehen auf die Liste, wenn sie welche kennt, als Datum mit Uhrzeit oder als Datum. Geänderte Fälligkeiten auf der Liste werden nicht übernommen.
- **Privatsphäre:** Ist sie an, werden nur Notizen abgeglichen, die mit allen geteilt sind, denn jeder mit Zugriff auf die andere Liste sieht sie. Einträge von der Liste sind mit allen geteilt.
- **Entkoppeln:** Ein geleertes Feld entkoppelt die Liste. Ihre Einträge bleiben, wo sie sind.
- Jede Liste lässt sich nur mit einer Kategorie koppeln, und die eigenen Listen von Brainstorm stehen nicht zur Wahl.

### Brainstorm › 🛒 Bring!

Erscheint nur, wenn die Integration [Bring!](https://www.home-assistant.io/integrations/bring/) eingerichtet ist. Alle Bring-Listen landen in einer Kategorie: Jede Liste wird eine Hauptnotiz, ihre Artikel werden zu Unteraufgaben.

```
🛒 Einkauf
├─ 🏠 Zu Hause
│   ├─ Milch
│   └─ Brot
└─ 🚐 Camper
    └─ Gas
```

| Feld | Was es bewirkt |
| :--- | :--- |
| Bring! synchronisieren | Schaltet den Abgleich ein oder aus. Ausgeschaltet bleiben Notizen und Artikel, wo sie sind. |
| Kategorie | Wähle eine Kategorie oder tippe einen neuen Namen, sie wird beim Speichern angelegt. |
| Listen | Leer lassen, um alle Listen abzugleichen, auch später hinzugefügte. |
| Standardliste | Notizen, die ohne Liste in die Kategorie kommen, etwa *„wir brauchen Milch“* per Sprache, landen auf dieser Liste und hängen unter ihrer Notiz. |
| Gekauftes ausblenden nach (Tagen) | Abgehakte Einträge verschwinden nach so vielen Tagen (Standard 3) aus der Erledigt-Ansicht und werden archiviert. In Bring bleiben sie in den zuletzt gekauften Einträgen zum erneuten Kaufen. 0 behält sie. |
| Kategorie mit allen teilen | Nur mit Privatsphäre sichtbar. Abgeglichen werden nur Notizen, die mit allen geteilt sind, denn jeder mit Zugriff auf Bring sieht sie. |

- **Beide Richtungen:** Neue Artikel, Abhaken und Löschen gehen zwischen Brainstorm und Bring hin und her. Abhaken schiebt den Artikel in Bring unter *Zuletzt verwendet*.
- **Verschieben:** Hängst du eine Unteraufgabe unter eine andere Listen-Notiz, wandert der Artikel auf diese Liste.
- **Schon mal gekauft:** Eine Notiz mit dem Namen eines Artikels aus *Zuletzt verwendet* holt diesen zurück, statt ihn doppelt anzulegen, denn Bring erlaubt jeden Namen nur einmal pro Liste.
- **Mengen:** Die Spezifikation eines Bring-Artikels, etwa *1,5 l*, wird an der Notiz gespeichert (Feld `spec`).
- **Listen-Notizen** übernehmen ihren Namen von Bring. Eine gelöschte Listen-Notiz kommt mit ihren Artikeln zurück, die Notiz einer nicht mehr abgeglichenen Liste wird archiviert.
- **Schnell:** Änderungen anderer werden über die Aktivitäts-Ereignisse von Bring erkannt, zusätzlich wird alle 5 Minuten verglichen.

### Brainstorm › Erinnerungen › Sperrzeiten pro Echo

Hält einzelne Echos zu festen Zeiten für Brainstorm still, etwa nachts im Kinderzimmer (v1.7.7). Bis zu drei Sperrzeiten, jede für ein oder mehrere Echos, auch über Mitternacht.

| Feld | Was es bewirkt |
| :--- | :--- |
| Echos 1 | Die Echos von Sperrzeit 1. Leer entfernt sie. |
| Von 1 | Beginn von Sperrzeit 1. |
| Bis 1 | Ende von Sperrzeit 1. Früher als der Beginn heißt am nächsten Morgen. |
| Auch „Nicht stören“ 1 | Schaltet „Nicht stören“ dieser Echos zu Beginn ein und am Ende aus, dann ist auch Alexa selbst still. Braucht Alexa Media Player. |
| Echos 2 | Die Echos von Sperrzeit 2. Leer entfernt sie. |
| Von 2 | Beginn von Sperrzeit 2. |
| Bis 2 | Ende von Sperrzeit 2. Früher als der Beginn heißt am nächsten Morgen. |
| Auch „Nicht stören“ 2 | Schaltet „Nicht stören“ dieser Echos zu Beginn ein und am Ende aus, dann ist auch Alexa selbst still. Braucht Alexa Media Player. |
| Echos 3 | Die Echos von Sperrzeit 3. Leer entfernt sie. |
| Von 3 | Beginn von Sperrzeit 3. |
| Bis 3 | Ende von Sperrzeit 3. Früher als der Beginn heißt am nächsten Morgen. |
| Auch „Nicht stören“ 3 | Schaltet „Nicht stören“ dieser Echos zu Beginn ein und am Ende aus, dann ist auch Alexa selbst still. Braucht Alexa Media Player. |

- **Andere Echos sprechen weiter:** Eine Erinnerung geht weiter an die Echos der Erinnerung, die nicht gesperrt sind.
- **Handy als Ersatz:** Ist kein Echo mehr übrig, geht die Erinnerung sofort aufs Handy statt erst nach der Wartezeit.
- **Test:** *🧪 Kanäle jetzt testen* spricht auch in einer Sperrzeit, weil du ihn selbst startest.

### Brainstorm › 🔋 Batterien

Macht aus schwachen Batterien Aufgaben (v1.7.5). Jeder Batterie-Sensor zählt: ein Stand in Prozent oder ein Sensor, der nur „Batterie schwach“ meldet.

| Feld | Was es bewirkt |
| :--- | :--- |
| Batterie-Aufgaben anlegen | Schaltet die Batterie-Aufgaben ein oder aus. Ausgeschaltet entstehen keine neuen, vorhandene bleiben. |
| Schwelle | Bei diesem Stand oder darunter entsteht eine Aufgabe (Standard 20 %). |
| Kategorie | Wähle eine Kategorie oder tippe einen neuen Namen, sie wird beim Speichern angelegt. Vorgeschlagen wird *Smarthome*. |
| Auslassen | Batterien, die nie eine Aufgabe anlegen sollen, etwa ein Hausakku. Ein ausgelassener Sensor lässt sein ganzes Gerät aus. |
| Handys und Tablets einbeziehen | Geräte der Companion-App werden täglich geladen und bleiben deshalb außen vor, außer du schaltest es ein. |

- **Eine Aufgabe pro Gerät**, auch wenn Integrationen wie Battery Notes weitere Sensoren für dieselbe Batterie anlegen. Sie ist nach dem Gerät benannt, z. B. *Batterie wechseln: Bewegungsmelder Flur (18 %)*.
- **Hakt sich selbst ab:** Meldet kein Sensor des Geräts mehr eine schwache Batterie und liegt der Stand 10 Punkte über der Schwelle, wird die Aufgabe abgehakt. Der Abstand verhindert, dass eine Batterie an der Schwelle ständig Aufgaben anlegt und schließt.
- **Von Hand abgehakt**, bevor die Batterie gewechselt ist, kommt die Aufgabe nicht wieder. Erst die nächste schwache Batterie legt eine neue an.
- **Nach einem Neustart** werden alle Batterien einmal geprüft.

### Brainstorm › 📟 Sensor-Aufgaben

Macht aus einem Sensorwert eine Aufgabe (v1.11.10), etwa *Wasserfilter wechseln* nach 300 Betriebsstunden, *Monstera gießen*, wenn die Bodenfeuchte unter 20 % fällt, oder *Waschmaschine ausräumen*, sobald sie fertig ist. Die erste Seite listet deine Regeln:

| Feld | Was es bewirkt |
| :--- | :--- |
| Regel | Wähle eine Regel, um sie zu ändern oder zu löschen, oder *➕ Neue Regel*. |

Eine Regel hat diese Felder:

| Feld | Was es bewirkt |
| :--- | :--- |
| Entität | Jede Entität, etwa ein Sensor, ein Zähler, ein Zahlen-Helfer oder ein Binärsensor. |
| Bedingung | *Erreicht oder übersteigt* und *Erreicht oder unterschreitet* vergleichen Zahlen, *Ist genau (Zustand)* vergleicht den Zustand als Text, ohne auf Groß- und Kleinschreibung zu achten. |
| Wert | Eine Zahl für Grenzen, etwa `300` oder `19,5`, oder ein Zustand, etwa `off` oder `Fertig`. |
| Aufgabe | Der Text der Aufgabe. Ihre Beschreibung nennt Sensor und Wert, etwa *Ausgelöst von Wasserfilter Betriebsstunden: 300 h*. |
| Kategorie | Wähle eine Kategorie oder tippe einen neuen Namen, sie wird beim Speichern angelegt. Vorgeschlagen wird *Smarthome*. |
| Selbst abhaken | Hakt die Aufgabe ab, sobald der Sensor wieder im Normalbereich ist (Standard an). |
| Wieder normal ab | Optional, nur für Zahlen: Erst dieser Wert gilt als wieder normal, etwa `0` für einen Zähler, den du nach dem Filterwechsel zurücksetzt. Er muss auf der normalen Seite der Grenze liegen. Ohne ihn gilt alles jenseits der Grenze als normal. |
| Diese Regel löschen | Nur beim Bearbeiten: entfernt die Regel. Ihre offene Aufgabe bleibt stehen. |

- **Eine Aufgabe pro Fall:** Solange die Bedingung erfüllt bleibt, entsteht keine zweite Aufgabe. Erst wenn der Sensor wieder normal war und die Bedingung erneut erfüllt ist, kommt eine neue.
- **Von Hand abgehakt**, bevor der Sensor wieder normal ist, kommt die Aufgabe nicht sofort wieder.
- **Ohne *Selbst abhaken*** bleibt die Aufgabe offen, bis du sie abhakst, und steht dann auch für den nächsten Fall.
- **Nach einem Neustart** und nach dem Speichern werden alle Regeln einmal geprüft; ist eine schon erfüllt, entsteht die Aufgabe sofort. *Nicht verfügbar* und *Unbekannt* werden übergangen.
- Die Aufgabe trägt die Quelle 📟 *Sensor* mit dem Namen der Entität und kommt wie jede neue Notiz in Erinnerungen und Automationen an.

### Brainstorm › Privatsphäre & Benutzer

| Feld | Was es bewirkt |
| :--- | :--- |
| Einträge privat halten | Dann sieht jede Person nur ihre eigenen Einträge und was mit ihr geteilt wurde. |
| Hauptbenutzer | Besitzt alle vorhandenen Einträge und alles, was an einem Echo gesagt wird. Sprache, Briefing und Rückblick nennen nur die Einträge dieser Person. |
| Weiter in Markdown-Dateien exportieren | Diese Dateien enthalten alle Einträge und sind für alle mit Zugriff auf den Config-Ordner lesbar. |
| Diese Benutzer für Freigaben anbieten | Leer bedeutet alle. Damit blendest du technische Konten wie MQTT aus. |

### Brainstorm › Echos & Apps zuordnen

| Feld | Was es bewirkt |
| :--- | :--- |
| Echo oder Alexa-App | Der Echo oder die Alexa-App, die du zuordnen möchtest. Du kannst auch einen Namen eintippen. |
| Person | Leer lassen, um die Zuordnung zu entfernen. |

## Bedienstufe

Unter **Konfigurieren ➔ Allgemeine Einstellungen & Export ➔ Bedienstufe** wählst du, wie viel Brainstorm zeigt. Die Stufe gilt für alle Personen, für beide Karten und für das Konfigurieren-Menü. Neue Installationen starten mit *Normal*, bestehende behalten *Profi*, also alles wie bisher.

| Stufe | Listenkarte und Bearbeiten-Dialog | Mindmap | Konfigurieren-Menü |
|---|---|---|---|
| **Einsteiger** | Eingabe, Mikrofon, Kategorien, Abhaken, Suche; im Dialog Titel, Beschreibung, Kategorie, Priorität und Termin | nur *Rund um die Mitte*, Neue Idee, Zoom, Vollbild | ohne Batterien, Sensor-Aufgaben, Sperrzeiten, Regeln pro Liste, Echos & Apps und KI-Textaufräumen |
| **Normal** | zusätzlich Unterpunkte, Mehrfachauswahl, Marker, Wiederholen, Anhänge, Freigeben, KI-Vorschläge | zusätzlich *Baum*, *Gliederung*, *Kanban*, Fokus, Ebenen, Suche und Filter, Mehrfachauswahl, Export als Bild, PDF und Markdown | wie Einsteiger |
| **Profi** | alles: Fortschritt, Nummerierung und Sortieren, Callout, Rahmen, Form, Erinnern auf Echos, Originaltext, „In Arbeit“ | alles: *Organigramm*, *Zeitleiste*, *Matrix*, Regeln, Querverbindungen, Rahmen, Brainstorm- und Präsentationsmodus, OPML/FreeMind, Ast zusammenfassen, alle Tastenkürzel | alles |

Ausblenden löscht nichts: Gesetzte Marker, Fortschritt oder Rahmen bleiben auf den Karten sichtbar. Im Bearbeiten-Dialog holt **Mehr Felder …** die ausgeblendeten Felder zurück. Jede Karte kann mit `level: beginner`, `normal` oder `pro` ihre eigene Stufe haben, zum Beispiel ein Küchentablet immer *Einsteiger*.

## Integration

[**Einstellungen ➔ Geräte & Dienste ➔ Brainstorm Hub ➔ Konfigurieren**](https://my.home-assistant.io/redirect/integration/?domain=brainstorm) öffnet ein Menü. Alle Felder sind [oben](#bei-der-einrichtung) einzeln beschrieben.

| Menü | Typische Einstellung |
|---|---|
| **Kategorien verwalten** | Kategorie „Urlaub“ anlegen, „Projekte“ umbenennen, leere ausblenden |
| **Kategorie-Design** | „Urlaub“ bekommt ☀️ `mdi:beach` und Orange |
| **Allgemeine Einstellungen & Export** | Standardkategorie, Intelligente Formatierung, Gesprochene Termine, Glossar, Markdown-Export nach `/config/brainstorm.md`, erlaubte Echos |
| **Alexa-Spracheingabe & Skill** | Modus *Routinen*, *Skill* oder *Beide*; Skill-Code und Sprachmodell zum Kopieren |
| **To-do-Listen koppeln** | Kategorie *Einkauf* mit Todoist oder Google Tasks abgleichen, in beide Richtungen |
| **Erinnerungen ➔ Ein/Aus & Kanäle** | Ansage auf Echo Küche, Push aufs Handy 5 Min. später, dringende Notizen sofort |
| **Erinnerungen ➔ Ruhezeit, Briefing & Wochenrückblick** | Ruhe 22–7 Uhr, Briefing 7:30 nur wenn jemand zu Hause ist, Rückblick sonntags 18 Uhr |
| **Erinnerungen ➔ Regeln pro Liste** | „Einkaufen“ nur im Laden (Zone) ansagen, „Alltag“ montags 8 Uhr |
| **Erinnerungen ➔ Orte & Heimkommen** | „Vergiss nicht, beim Baumarkt Schrauben“ meldet sich beim Betreten der Zone Baumarkt |
| **Erinnerungen ➔ Personen** | Olafs Erinnerungen auf Olafs Handy und den Echo im Büro |
| **Erinnerungen ➔ Kalender & Alexa-Erinnerungen** | Termine in `calendar.familie` eintragen, zusätzlich echte Alexa-Erinnerung stellen |
| **Erinnerungen ➔ Sperrzeiten pro Echo** | Kinderzimmer-Echo 19–7 Uhr stumm, optional mit Nicht stören |
| **Erinnerungen ➔ Kanäle jetzt testen** | Probeansage und Probe-Push |
| **KI** | Gesprochenes von einem KI-Dienst aufräumen lassen |
| **Privatsphäre & Benutzer** | Jeder sieht nur eigene Notizen, Listen gezielt teilen |
| **Echos & Apps Personen zuordnen** | Echo Schlafzimmer gehört zu Anna |
| **🛒 Bring!** | Bring-Listen als Hauptnotizen, Einträge als Unteraufgaben, in beide Richtungen (nur mit Bring-Integration) |
| **🔋 Batterien** | unter 20 % die Aufgabe *Batterie wechseln: Bewegungsmelder Flur (18 %)*, hakt sich nach dem Wechsel selbst ab |
| **📟 Sensor-Aufgaben** | ab 300 Betriebsstunden die Aufgabe *Wasserfilter wechseln*, hakt sich nach dem Zurücksetzen des Zählers selbst ab |
| **🧹 Erledigte Einträge löschen** | Erledigte nach 30 Tagen automatisch entfernen |
