🏠 [Start](Home) · 🇬🇧 [English version](Reminders)

Brainstorm erinnert dich von selbst an fällige Einträge, und zwar über die Dienste, die du in Home Assistant ohnehin eingerichtet hast. Alles ist optional und läuft lokal.

**Termin festlegen**
- **Per Sprache (Skill):** *„Alexa, sage Brainstorm erinnere mich morgen um 8 an die Mülltonnen“*. Verstanden werden z. B. *heute Abend*, *morgen früh*, *übermorgen*, *am Freitag*, *nächste Woche*, *am 25.11.*, *in zwei Stunden*, *um halb neun*. Auch ausgesprochene Tage klappen: *„am zweiten Dezember um zwölf Uhr“* oder *„am zweiten Zwölften um zwölf“* speichern den 02.12. um 12:00 Uhr. Liegt das Datum dieses Jahr schon hinter dir, nimmt Brainstorm das nächste Jahr.
- **Per Sprache (nativ):** *„Alexa, erinnere mich morgen um 8 an …“*. Amazon legt dabei eventuell zusätzlich eine eigene Erinnerung an.
- **In den Listen:** Fälligkeitsdatum in den To-do-Listen von Home Assistant setzen. Ein reines Datum bedeutet 9:00 Uhr.
- **Auf der Karte:** Eintrag lange drücken ➔ *Erinnern: heute Abend / morgen früh / nächste Woche / Zeitpunkt wählen*.
- **Im Bearbeiten-Dialog:** Beide Karten zeigen ein Datums- und ein Uhrzeitfeld, ohne Uhrzeit erinnert Brainstorm um 9:00 Uhr. Darunter klappt *Erinnern auf* per Tipp auf, dort wählst du die Echos, die diese Erinnerung sprechen. Ohne Auswahl gelten die Erinnerungs-Einstellungen.
- **In Automationen:** `brainstorm.add_idea` und `brainstorm.update_idea` mit dem Feld `due`.

**Einstellen** unter **Brainstorm Hub ➔ Konfigurieren ➔ Erinnerungen & Benachrichtigungen**. Jede Funktion hat ihren eigenen Schalter:

| Bereich | Schalter | Was es tut |
| :--- | :--- | :--- |
| **Ein/Aus & Kanäle** | Erinnerungen nutzen | Hauptschalter für alles in diesem Menü |
| | Alexa-Ansage | Aus, Echo des Eintrags, zuletzt genutzter Echo oder feste Echos (benötigt Alexa Media) |
| | Benachrichtigungen senden | Beliebige `notify`-Dienste; die Companion-App bekommt die Knöpfe **Erledigt**, **1 Stunde später** und **Morgen** |
| | Wichtige offene Einträge erneut senden | Hohe oder dringende Einträge gehen nach einer Wartezeit an weitere Dienste, z. B. Pushover |
| **Ruhezeit, Briefing & Rückblick** | Ruhezeit nutzen | Erinnerungen warten; Dringendes erreicht das Handy, aber kein Echo spricht |
| | Tägliches Briefing | Zu einer Uhrzeit, optional erst wenn ein Sensor oder eine Person jemanden meldet |
| | Wochenrückblick | Nennt lange offene Einträge |
| **Regeln pro Liste** | Regeln pro Liste nutzen | Pro Liste: normale Kanäle, nur Alexa, nur Benachrichtigungen (privat) oder nichts; eigene Dienste; an bestimmten Tagen senden; an einem Ort senden |
| **Orte & Heimkommen** | Beim Heimkommen erinnern | *„erinnere mich wenn ich heimkomme an den Müll“* |
| | An Orten erinnern | *„erinnere mich wenn ich bei Edeka bin an die Milch“* (nutzt deine Zonen) |
| **Personen** | Erinnerungen für andere nutzen | *„erinnere Frida morgen um 8 an den Termin“* mit eigenen Kanälen pro Person |
| **Kalender & Alexa** | Kalender | Trägt Erinnerungen einmalig in einen Kalender ein; spätere Änderungen werden nicht übertragen |
| | Echte Alexa-Erinnerungen | Legt im Skill zusätzlich eine Amazon-Erinnerung an, dafür muss in der Alexa-Konsole **Build ➔ Permissions ➔ Reminders** eingeschaltet sein und einmal die Zustimmung in der Alexa-App erteilt werden |

Die KI, die Briefing und Rückblick kürzt, stellst du seit v1.6.27 im Hauptmenü unter **Brainstorm Hub ➔ Konfigurieren ➔ KI** ein.

**Listen auf dem Echo Show**

Mit dem Skill zeigt ein Echo mit Bildschirm deine offenen Ideen parallel zur Sprachantwort: eine Seite je Kategorie mit Kacheln, nach links oder rechts wischen wechselt sie, innerhalb einer Seite wird gescrollt. Tippe auf den Kreis vor einer Idee, um sie zu erledigen. Ein Hauptpunkt mit Unterpunkten zeigt *+ 3 Unterpunkte*; Antippen seines Textes klappt sie auf und zu; auf der Karte lässt sie sich wiederherstellen. *„Alexa, sage Brainstorm zeige Alltag“* oder *„… zeige Listen“* zeigt die Listen mit nur einer kurzen Antwort, *„… Ansage“* und *„… alles vorlesen“* zeigen sie beim Vorlesen.

Zur Einrichtung öffnest du in der Alexa-Entwicklerkonsole **Build ➔ Interfaces**, schaltest **Alexa Presentation Language** mit den Echo-Show-Profilen ein und klickst auf **Save**. Kopiere danach die Felder **Sprachmodell** und **Skill-Code** erneut und klicke auf **Build** und **Deploy**. Ohne diese Schritte antwortet der Skill weiter nur per Sprache. Wie lange ein Bildschirm stehen bleibt, entscheidet Amazon; er kann früher als die gewünschten zwei Minuten zum Startbildschirm zurückkehren.

**Weitere Sätze im Skill**
- *„Alexa, sage Brainstorm erledigt Mülltonnen“* oder nur *„… erledigt“* für die letzte Erinnerung
- *„Alexa, sage Brainstorm später“* verschiebt die letzte Erinnerung um eine Stunde
- *„Alexa, sage Brainstorm Ansage Alltag“* liest eine Kategorie vor, *„… Ansage“* nennt nur den Überblick, *„… alles vorlesen“* liest alles vor

**Eigene Automationen:** Jede Erinnerung löst das Ereignis `brainstorm_reminder_due` aus, auch ohne eingerichtete Dienste.
