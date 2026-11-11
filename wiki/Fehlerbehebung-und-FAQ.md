🏠 [Start](Home) · 🇬🇧 [English version](Troubleshooting-and-FAQ)

## 🩺 Häufige Probleme

| Problem | Lösung |
|---|---|
| Der Skill sagt, er erreicht Home Assistant nicht | Sieh unter [**Einstellungen > Reparaturen**](https://my.home-assistant.io/redirect/repairs/) nach. Home Assistant braucht eine öffentliche HTTPS-Adresse, z. B. über Home Assistant Cloud. Danach den Skill-Code neu kopieren. |
| Alexa sagt immer wieder, ich soll mit *notiere* anfangen | Das aktuelle Sprachmodell in die Alexa-Entwicklerkonsole kopieren, dann **Save** und **Build**. |
| *„Alexa, öffne Brainstorm“* startet den alten Dialog | Die Alexa-Routinen für *öffne Brainstorm* in der Alexa-App löschen. |
| Eine Idee landet in der falschen Kategorie | Die Kategorie vorne nennen: *„notiere für den Einkauf Milch“*. Eine eigene Kategorie hat Vorrang vor Standard-Begriffen mit ihrem Namen. |
| Eine Karte zeigt noch eine alte Version | Die Ressource auf die aktuelle `?v=`-Nummer setzen und die Seite ohne Cache neu laden. |
| Ein Echo wird nicht erkannt oder ignoriert | Die Echo-Auswahl unter [**Konfigurieren**](https://my.home-assistant.io/redirect/integration/?domain=brainstorm) prüfen. [**Einstellungen > Reparaturen**](https://my.home-assistant.io/redirect/repairs/) nennt gewählte Echos, die es nicht mehr gibt. |
| Etwas anderes klappt nicht | Die Diagnose herunterladen (siehe *Entitäten*) und ein [Issue](https://github.com/nukleuz80/ha_brainstorm/issues) eröffnen. |

## ⚠️ Bekannte Einschränkungen

- **Freie Sätze im Skill:** Alexa gibt einem Skill nur Text weiter, wenn der Satz mit einem bekannten Wort beginnt, z. B. *notiere*, *wir brauchen* oder *ich muss*. Andere Sätze enden in einem kurzen Hinweis, mit *notiere* anzufangen.
- **Echo-Erkennung** braucht die Integration Alexa Media. Ohne sie werden Ideen aus dem Skill trotzdem gespeichert, nur ohne den Echo, von dem sie kamen.
- **Der Name „Brainstorm“** ist auch eine Band. Ohne eigenen Skill oder Routinen startet Alexa womöglich Musik.
- **Erinnerungen auf Echos** werden über Alexa Media gesprochen. Echte Alexa-Erinnerungen brauchen zusätzlich die Erinnerungs-Berechtigung deines Skills.
- **Eine Installation:** Pro Home Assistant lässt sich nur ein Brainstorm Hub einrichten.

## ❓ Häufige Fragen

**Kostet Brainstorm Hub etwas oder braucht es eine Cloud?**
Nein. Brainstorm Hub ist kostenlos (MIT-Lizenz), läuft lokal in deinem Home Assistant und verbindet sich von selbst mit keinem externen Dienst. Ein Konto brauchst du nicht. Nur ein eigener Alexa-Skill braucht eine öffentliche HTTPS-Adresse, zum Beispiel über Home Assistant Cloud.

**Brauche ich Amazon Alexa?**
Nein. Ideen kommen genauso über die Dashboard-Karten, das Mikrofon in der Listenkarte, Home Assistant Assist, einen iPhone-Kurzbefehl mit Siri, die To-do-Listen von Home Assistant oder Automationen. Siehe [Sprachsteuerung](Sprachsteuerung).

**Brauche ich eine KI?**
Nein. Kategorie, Priorität und Termin erkennt Brainstorm mit eigenen Regeln. Eine KI-Aufgaben-Entität ist optional und schaltet Extras frei, etwa Unteraufgaben-Vorschläge, eine Mindmap aus einem Thema oder das Gruppieren nach Themen. Siehe [KI-Funktionen](KI-Funktionen).

**Kann ich Listen mit der Familie teilen?**
Ja. Ohne Privatsphäre sehen alle Benutzer alles. Mit eingeschalteter Privatsphäre gehört jeder Eintrag seiner Person und lässt sich pro Eintrag oder Kategorie zum Ansehen oder Bearbeiten freigeben. Siehe [Zusammenarbeit](Zusammenarbeit).

**Bleibt Brainstorm mit Bring!, Todoist oder Google Tasks synchron?**
Ja. Eine Kategorie lässt sich mit einer To-do-Liste einer anderen Integration koppeln, für Bring! gibt es eine eigene Anbindung. Siehe [Import, Export & Speicherung](Import-Export-und-Speicherung).

**Funktioniert es mit Obsidian, Logseq oder Nextcloud?**
Ja, über den automatischen Markdown-Export in einen Ordner deiner Wahl. Die Mindmap exportiert außerdem OPML und FreeMind (`.mm`) für Freeplane, XMind und MindManager.

**Welche Sprachen gibt es?**
Deutsch und Englisch, für Einstellungen, Karten, Alexa-Skill, Assist-Sätze und Erinnerungen. Wie eine weitere Sprache dazukommt, steht in [`CONTRIBUTING.md`](https://github.com/nukleuz80/ha_brainstorm/blob/main/CONTRIBUTING.md).

**Wo liegen meine Daten, und sind sie im Backup?**
In `/config/.storage/brainstorm.storage`, Anhänge in `/config/brainstorm_attachments/`. Beides ist Teil jedes normalen Home-Assistant-Backups. Siehe [Import, Export & Speicherung](Import-Export-und-Speicherung).
