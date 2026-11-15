/**
 * Brainstorm Hub - texts of the cards.
 *
 * The German text is the key, so the cards read naturally and German needs no
 * dictionary. To add a language, add a dictionary below; a missing text shows the
 * English one.
 */
const DICTIONARIES = {
  en: {
    "🔓 „{text}“ kann jetzt losgehen": "🔓 \"{text}\" can start now",
    "🔓 {count} Notizen können jetzt losgehen": "🔓 {count} notes can start now",
    "Notizen: kompakt (nur Titel) – tippen für normal": "Notes: compact (titles only) – tap for normal",
    "Notizen: mit allen Angaben – tippen für automatisch": "Notes: with all details – tap for automatic",
    "Notizen: automatisch nach Zoom – tippen für kompakt": "Notes: automatic by zoom – tap for compact",
    "Notizen auf der Map": "Notes on the map",
    "Automatisch nach Zoom": "Automatic by zoom",
    "Kompakt (nur Titel, Tipp klappt auf)": "Compact (titles only, a tap opens one)",
    "Normal (alle Angaben)": "Normal (all details)",
    "Bring!-Tab zeigen (öffnet die Einkaufslisten)": "Show Bring! tab (opens the shopping lists)",
    "Auf der Bring!-Liste {name}: alles gekauft": "On the Bring! list {name}: all bought",
    "Auf der Bring!-Liste {name}: {open} von {total} noch offen": "On the Bring! list {name}: {open} of {total} still open",
    "Was kommt auf die Liste?": "What goes on the list?",
    "Unteraufgaben ({count})": "Subtasks ({count})",
    "Diese Notiz als ein Artikel": "This note as one item",
    "Liste": "List",
    "Was auf der Liste schon offen ist, kommt nicht doppelt dazu. Gekaufte Artikel werden hier abgehakt.": "What is already open on the list is not added twice. Bought items are ticked off here.",
    "🛒 Senden": "🛒 Send",
    "Bitte mindestens eine Unteraufgabe auswählen.": "Please choose at least one subtask.",
    "Steht schon alles auf {name}.": "Everything is already on {name}.",
    "1 Artikel auf {name}": "1 item on {name}",
    "{count} Artikel auf {name}": "{count} items on {name}",
    "{count} war schon drauf": "{count} already there",
    "Die Bring!-Listen als Map": "The Bring! lists as a map",
    "An Bring! senden": "Send to Bring!",
    "🛒 An Bring! senden": "🛒 Send to Bring!",
    "ChoreOps-Tab zeigen (live, nur zum Ansehen)": "Show ChoreOps tab (live, view only)",
    "erledigt": "done",
    "gemeldet, wartet auf Freigabe": "reported, waiting for approval",
    "offen": "open",
    "ChoreOps zeigt noch keine Personen.": "ChoreOps shows no people yet.",
    "{count} offen": "{count} open",
    "{count} gemeldet": "{count} reported",
    "{count} erledigt": "{count} done",
    "{points} P": "{points} pts",
    "Aus Brainstorm übergeben": "Handed over from Brainstorm",
    "fällig {date}": "due {date}",
    "Keine Aufgaben": "No chores",
    "Alles erledigt 🎉": "All done 🎉",
    "Punktestand": "Points balance",
    "Noch offen": "Still open",
    "+ {count} erledigt": "+ {count} done",
    "Erledigte ausblenden": "Hide done",
    "Erledigte zeigen": "Show done",
    "Nur zum Ansehen: Freigeben und Punkte vergeben passiert in ChoreOps.": "View only: approving and giving points happens in ChoreOps.",
    "Live aus ChoreOps, nur zum Ansehen": "Live from ChoreOps, view only",
    "🏅 Übergeben": "🏅 Hand over",
    "An ChoreOps übergeben": "Hand over to ChoreOps",
    "🏅 An ChoreOps übergeben": "🏅 Hand over to ChoreOps",
    "Die Person meldet in ChoreOps „erledigt“. Sobald ein Elternteil freigibt, gibt es die Punkte und die Notiz wird hier abgehakt.": "The person reports “done” in ChoreOps. As soon as a parent approves it, the points are given and the note is ticked off here.",
    "{user} hat es als erledigt gemeldet, wartet auf Freigabe in ChoreOps": "{user} reported it done, waiting for approval in ChoreOps",
    "Wer erledigt es?": "Who does it?",
    "Punkte": "Points",
    "Von ChoreOps freigegeben: {points} Punkte für {user}": "Approved in ChoreOps: {points} points for {user}",
    "Bei ChoreOps für {user}: {points} Punkte": "At ChoreOps for {user}: {points} points",
    "Map-Tabs": "Map tabs",
    "Map": "Map",
    "Nur für mich": "Only for me",
    "Noch einmal tippen: Tab bearbeiten": "Tap again: edit tab",
    "Ansicht als Tab speichern": "Save view as tab",
    "Im eigenen Tab öffnen: {name}": "Open in its own tab: {name}",
    "In eigenen Tab auslagern": "Move to its own tab",
    "Der Zweig dieses Tabs ist nicht mehr da, die ganze Liste wird gezeigt.": "The branch of this tab is gone, the whole list is shown.",
    "Der Tab konnte nicht gespeichert werden.": "The tab could not be saved.",
    "Zweig": "Branch",
    "Zweig liegt jetzt im Tab „{name}“": "Branch now lives in the tab “{name}”",
    "📑 Tab bearbeiten": "📑 Edit tab",
    "📑 Ansicht als Tab speichern": "📑 Save view as tab",
    "Symbol": "Icon",
    "Aktuelle Ansicht übernehmen": "Use the current view",
    "Dieser Tab zeigt einen ausgelagerten Zweig. Löschst du ihn, steht der Zweig wieder ganz in der Map.": "This tab shows a branch moved out of the map. Delete it and the branch is back in the map in full.",
    "Gespeichert werden Liste, Zweig, Filter, Ansicht und Ausschnitt. Ohne „Nur für mich“ sieht jeder im Haushalt den Tab.": "The list, branch, filter, layout and visible area are saved. Without “Only for me” everyone in the household sees the tab.",
    "Zurück in die Map": "Back into the map",
    "Nach links": "Move left",
    "Nach rechts": "Move right",
    "Tab „{name}“ gespeichert": "Tab “{name}” saved",
    "Gespeicherte Ansichten als Tabs über der Map zeigen": "Show saved views as tabs above the map",
    "1 Kommentar": "1 comment",
    "{count} Kommentare": "{count} comments",
    "Kommentar löschen": "Delete comment",
    "Noch keine Kommentare.": "No comments yet.",
    "🗑️ Papierkorb": "🗑️ Trash",
    "Papierkorb: gelöschte Notizen zurückholen": "Trash: bring deleted notes back",
    "Gelöschte Notizen bleiben {days} Tage hier, dann sind sie mit ihren Anhängen endgültig weg.": "Deleted notes stay here for {days} days, then they are gone for good with their attachments.",
    "Der Papierkorb ist leer.": "The trash is empty.",
    "Wiederherstellen": "Restore",
    "Endgültig löschen": "Delete for good",
    "Papierkorb leeren": "Empty trash",
    "Wirklich alle {count} Notizen endgültig löschen?": "Really delete all {count} notes for good?",
    "Ja, endgültig löschen": "Yes, delete for good",
    "gelöscht {when}": "deleted {when}",
    "+ {count} Unterpunkte": "+ {count} subitems",
    "{count} Anhänge": "{count} attachments",
    "Wiederhergestellt: {text}": "Restored: {text}",
    "Kommentar schreiben … @Name benachrichtigt die Person": "Write a comment … @Name tells that person",
    "Senden": "Send",
    "Das hat nicht geklappt.": "That did not work.",
    "Lädt …": "Loading …",
    "💬 Kommentare": "💬 Comments",
    "Kommentare": "Comments",
    "Map aus Thema erzeugen": "Create map from a topic",
    "✨ Map aus Thema erzeugen": "✨ Create map from a topic",
    "Mit KI erzeugen": "Create with AI",
    "Ein Thema wie „Sommerfest planen“ oder einen längeren Text einfügen. Die KI macht daraus eine Map mit bis zu drei Ebenen, du wählst vor dem Übernehmen aus.": "Enter a topic such as “Plan a summer party” or paste a longer text. The AI turns it into a map with up to three levels, and you pick what to keep.",
    "Thema oder Text": "Topic or text",
    "Erzeugen": "Create",
    "Haken weg bei allem, was du nicht willst. Unterpunkte rücken dann nach oben. Du kannst die Texte noch ändern.": "Untick whatever you do not want; its points move up. You can still change the texts.",
    "Die KI hat keine Map geliefert.": "The AI did not return a map.",
    "Abstimmen: Stimmen pro Person verteilen (V)": "Vote: hand out votes per person (V)",
    "Abstimmung in {category}: noch {left} von {total} Stimmen": "Voting in {category}: {left} of {total} votes left",
    "Abstimmung in „{category}“ beenden? Danach zeigt Brainstorm das Ergebnis, die Stimmen bleiben an den Notizen.": "End the voting in “{category}”? Brainstorm then shows the result, the votes stay on the notes.",
    "Abstimmung läuft: {votes} Stimmen pro Person": "Voting started: {votes} votes per person",
    "Beenden": "End",
    "Das ging nicht.": "That did not work.",
    "Gefällt mir": "Like",
    "Jede Person setzt ihre Stimmen mit + an den Notizen, auch mehrere auf eine. Wer die Liste sieht, darf mitstimmen.": "Everyone places their votes with + on the notes, several on one if they like. Whoever sees the list may vote.",
    "Liebe ich": "Love",
    "Lustig": "Funny",
    "Nach Stimmen sortieren": "Sort by votes",
    "Niemand hat abgestimmt.": "Nobody voted.",
    "Noch {left} von {total} Stimmen": "{left} of {total} votes left",
    "Starten": "Start",
    "Stimme geben": "Give a vote",
    "Stimme zurücknehmen": "Take a vote back",
    "Stimmen": "Votes",
    "Stimmen früherer Runden löschen": "Clear the votes of earlier rounds",
    "Stimmen pro Person": "Votes per person",
    "Unbekannt": "Unknown",
    "Verdeckt: jede Person sieht bis zum Ende nur ihre eigenen Stimmen": "Hidden: everyone sees only their own votes until the end",
    "Wichtig": "Important",
    "läuft": "running",
    "verdeckt": "hidden",
    "{points} Stimmen": "{points} votes",
    "🏆 Ergebnis: {category}": "🏆 Result: {category}",
    "🗳️ Abstimmung beenden": "🗳️ End voting",
    "🗳️ Abstimmung starten": "🗳️ Start voting",
    "+ Kategorie": "+ Category",
    "0 Ideen": "0 ideas",
    "0 Notizen": "0 notes",
    "Abbrechen": "Cancel",
    "Aktionen für Notiz": "Actions for note",
    "Akzentfarbe:": "Accent color:",
    "Alle": "All",
    "Alle Benutzer": "All users",
    "Als erledigt markieren": "Mark as done",
    "Ansehen": "View",
    "Aufnahme beenden": "Stop recording",
    "Ausrücken": "Outdent",
    "Ausrücken (zu Hauptaufgabe)": "Outdent (to main task)",
    "Auto (Erkennen)": "Auto (detect)",
    "Bearbeiten": "Edit",
    "Bearbeiten von Notizen erlauben (Klick & Stift-Icon)": "Allow editing notes (click and pencil icon)",
    "Bitte im Format {format} eingeben.": "Please use the format {format}.",
    "Blitz-Idee tippen... (z.B. 'Garten: Baum schneiden')": "Type a quick idea... (for example 'Garden: cut the tree')",
    "Brainstorm Hub – Visuelle Kartenkonfiguration": "Brainstorm Hub – visual card configuration",
    "Brainstorm Logo in Toolbar anzeigen": "Show the Brainstorm logo in the toolbar",
    "Brainstorm Mindmap – Visuelle Kartenkonfiguration": "Brainstorm Mindmap – visual card configuration",
    "Das Mikrofon ist nicht erlaubt. Bitte im Browser freigeben.": "The microphone is not allowed. Please allow it in your browser.",
    "Design für '{name}' anpassen": "Change the design of '{name}'",
    "Die Spracherkennung konnte nicht starten.": "Speech recognition could not start.",
    "Enthaltene Notizen werden automatisch in die Kategorie <em>Inbox</em> verschoben.": "Notes in it are moved to the category <em>Inbox</em> automatically.",
    "Ergebnis": "Result",
    "Erinnern: Zeitpunkt wählen": "Remind: choose a time",
    "Erinnern: heute Abend": "Remind: this evening",
    "Erinnern: morgen früh": "Remind: tomorrow morning",
    "Erinnern: nächste Woche": "Remind: next week",
    "Erinnert an diesem Ort": "Reminds at this place",
    "Erinnerung": "Reminder",
    "Erinnerung entfernen": "Remove reminder",
    "Erledigt": "Completed",
    "Erledigte Ideen anzeigen": "Show completed ideas",
    "Farbmodus": "Color mode",
    "Farbmodus-Umschalter (🎨/🌈) im Header anzeigen": "Show the color mode switch (🎨/🌈) in the header",
    "Farbmodus-Umschalter (🎨/🌈) in Toolbar anzeigen": "Show the color mode switch (🎨/🌈) in the toolbar",
    "Farbmodus: Bunt aktiv (Klicken für Theme-Farben)": "Color mode: multicolor on (click for theme colors)",
    "Farbmodus: Theme-Farben aktiv (Klicken für Bunt)": "Color mode: theme colors on (click for multicolor)",
    "Freigeben": "Share",
    "Für andere freigegeben": "Shared with others",
    "Für diese Person": "For this person",
    "Gerät": "Device",
    "Gerät: {device}": "Device: {device}",
    "Geteilt": "Shared",
    "Geteilt von {name}, du darfst ansehen": "Shared by {name}, you may view it",
    "Geteilt von {name}, du darfst bearbeiten": "Shared by {name}, you may edit it",
    "Eingetragen von {name}": "Added by {name}",
    "Unteridee anlegen": "Add a subidea",
    "Bring-Nachricht senden": "Send Bring! message",
    "Anhänge:": "Attachments:",
    "Anhänge anzeigen": "Show attachments",
    "Anhang löschen": "Delete attachment",
    "Keine Anhänge.": "No attachments.",
    "Wird hochgeladen …": "Uploading …",
    "📎 Datei anhängen": "📎 Attach file",
    "Bilder auch per Einfügen oder Ziehen. Nach dem Erledigen bleiben Anhänge 30 Tage.": "Images can also be pasted or dropped. Attachments stay for 30 days after an idea is done.",
    "„{name}“ löschen?": "Delete “{name}”?",
    "Der Anhang konnte nicht gespeichert werden ({status}).": "The attachment could not be saved ({status}).",
    "📎 Anhänge: {title}": "📎 Attachments: {title}",
    "Schließen": "Close",
    "In Arbeit": "In progress",
    "In Arbeit seit {time}": "In progress since {time}",
    "{name} arbeitet daran seit {time}": "{name} has been working on it since {time}",
    "Als „In Arbeit“ markieren": "Mark as “in progress”",
    "Markierung „In Arbeit“ entfernen": "Remove the “in progress” mark",
    "Unteraufgaben einklappen": "Collapse subtasks",
    "Batterie": "Battery",
    "Titel:": "Title:",
    "Beschreibung:": "Description:",
    "Optional: Details, Links, Notizen …": "Optional: details, links, notes …",
    "Antippen zum Auf- und Zuklappen": "Tap to expand or collapse",
    "Unteraufgaben ausklappen": "Expand subtasks",
    "Dringend in Bring melden": "Report as urgent in Bring!",
    "Alle auf der Liste bekommen eine Nachricht": "Everyone on the list gets a message",
    "Ich gehe einkaufen": "I'm going shopping",
    "Einkauf erledigt": "Shopping done",
    "Liste geändert": "List changed",
    "Bring-Nachricht gesendet": "Bring! message sent",
    "Bring-Nachricht fehlgeschlagen: {error}": "Bring! message failed: {error}",
    "🌿 Neue Unteridee": "🌿 New subidea",
    "Unter: {text}": "Below: {text}",
    "Neue Unteridee …": "New subtask …",
    "Neue Idee …": "New note …",
    "↶ Rückgängig: {text}": "↶ Undone: {text}",
    "↶ Rückgängig": "↶ Undone",
    "Rückgängig ging nicht": "Could not undo",
    "Rückgängig (Strg+Z)": "Undo (Ctrl+Z)",
    "Gespeichert wird, was gerade auf der Map steht, ohne eingeklappte Zweige.": "The picture shows what is on the map right now, without folded branches.",
    "SVG (Vektor)": "SVG (vector)",
    "PNG (Bild)": "PNG (image)",
    "Auf der Map ist nichts zum Speichern": "There is nothing on the map to save",
    "Speichern als Bild ging nicht": "Could not save the picture",
    "Schaltfläche zum Speichern als Bild (🖼️) anzeigen": "Show the button to save as a picture (🖼️)",
    "Vorlage für das Aussehen": "Template for the look",
    "Standard: Karten, Kurven, Kategoriefarben": "Standard: cards, curves, category colors",
    "Klar: Rechtecke, eckige Linien": "Clean: rectangles, angled lines",
    "Skizze: Kapseln, gestrichelt, Pastell": "Sketch: pills, dashed, pastel",
    "Neon: dunkel und leuchtend": "Neon: dark and glowing",
    "Form der Notizen": "Shape of the notes",
    "Wie die Vorlage": "As in the template",
    "Karte": "Card",
    "Wolke": "Cloud",
    "Sprechblase": "Speech bubble",
    "Gedankenblase": "Thought bubble",
    "Ellipse": "Ellipse",
    "Sechseck": "Hexagon",
    "Notizzettel": "Note slip",
    "Unterstrichen": "Underlined",
    "Sprachnotizen als Sprechblase zeigen": "Show voice notes as speech bubbles",
    "Automatisch": "Automatic",
    "Form auf der Mindmap:": "Shape on the mind map:",
    "Automatisch: Sprachnotizen als Sprechblase, sonst die Form der Map.": "Automatic: voice notes as speech bubbles, otherwise the shape of the map.",
    "Kapsel": "Pill",
    "Rechteck": "Rectangle",
    "Linien": "Lines",
    "Kurve": "Curve",
    "Gerade": "Straight",
    "Eckig": "Angled",
    "Gestrichelt": "Dashed",
    "Farbschema": "Color scheme",
    "Kategoriefarben": "Category colors",
    "Pastell": "Pastel",
    "Einfarbig": "Single color",
    "Neon": "Neon",
    "Zweig aufklappen": "Unfold branch",
    "Zweig einklappen": "Fold branch",
    "Ordnen": "Arrange",
    "🪄 Map neu ordnen?": "🪄 Arrange the map again?",
    "{count} von Hand verschobene Notizen kommen wieder an ihren automatischen Platz, auf allen Geräten.": "{count} notes you placed by hand go back to their automatic place, on every device.",
    "Neu ordnen: von Hand verschobene Notizen wieder automatisch platzieren": "Arrange again: place notes you moved by hand automatically",
    "Halten & Ziehen zum Sortieren oder Unteraufgabe zuordnen": "Hold and drag to sort or to make a subtask",
    "Handy": "Phone",
    "Heute {clock}": "Today {clock}",
    "Hinzufügen": "Add",
    "Höhe der Mindmap (z.B. 600px, 75vh, calc(100vh - 32px))": "Height of the mindmap (for example 600px, 75vh, calc(100vh - 32px))",
    "Ich höre zu … Zum Beenden nochmal tippen.": "Listening … Tap again to stop.",
    "Icon (Home Assistant / MDI):": "Icon (Home Assistant / MDI):",
    "Idee": "idea",
    "Idee / Gedanke:": "Idea / thought:",
    "Idee erfassen": "Capture idea",
    "Idee sprechen": "Speak an idea",
    "Ideen": "ideas",
    "Interaktive Mindmap-Darstellung für deine Brainstorm Hub Notizen und Ideen.": "Interactive mindmap of your Brainstorm Hub notes and ideas.",
    "Kartentitel": "Card title",
    "Kategorie": "Category",
    "Kategorie '{name}' löschen": "Delete category '{name}'",
    "Kategorie erstellen": "Create category",
    "Kategorie wählen:": "Choose a category:",
    "Kategorie ändern": "Change category",
    "Kategorie-Leiste (Filter-Pills) anzeigen": "Show the category bar (filter pills)",
    "Kategorie:": "Category:",
    "Kategorien ohne Notizen (0) ausblenden": "Hide categories without notes (0)",
    "Kategoriename...": "Category name...",
    "Keine Freigabe": "Not shared",
    "Keine Ideen in der Kategorie \"{category}\".": "No ideas in the category \"{category}\".",
    "Keine aktiven Notizen in dieser Kategorie.<br>Klicke unten links auf \"+ Idee\", um eine hinzuzufügen.": "No active notes in this category.<br>Click \"+ Idea\" at the bottom left to add one.",
    "Keine erledigten Ideen vorhanden.": "No completed ideas yet.",
    "Klicken zum Bearbeiten": "Click to edit",
    "Klicken zum Bearbeiten (Lange drücken für Kontextmenü)": "Click to edit (long press for the menu)",
    "Kompakte Zeilenhöhe (mehr Aufgaben auf einen Blick)": "Compact rows (more tasks at a glance)",
    "Last Alexa Entität": "Last Alexa entity",
    "Last Alexa Entität (Echo / Sensor)": "Last Alexa entity (Echo / sensor)",
    "Leuchtende Glühbirne im Zentrum als Wasserzeichen anzeigen": "Show the glowing bulb in the center as a watermark",
    "Logo im Header anzeigen": "Show the logo in the header",
    "Löschen": "Delete",
    "Löschen von Notizen erlauben (✕-Schaltfläche)": "Allow deleting notes (✕ button)",
    "Maximale Notizenanzahl (0 = Unbegrenzt)": "Maximum number of notes (0 = unlimited)",
    "Meine": "Mine",
    "Mikrofon im Schnelleingabe-Feld anzeigen (nur über HTTPS)": "Show the microphone in the quick input (HTTPS only)",
    "Mindmap als Layer öffnen": "Open mindmap as a layer",
    "Mindmap schließen (ESC)": "Close mindmap (ESC)",
    "Mindmap-Schaltfläche (🧠) im Header anzeigen": "Show the mindmap button (🧠) in the header",
    "Mindmap-Titel": "Mindmap title",
    "Mit mir geteilt": "Shared with me",
    "Moderne Schnellerfassung und Themen-Filter für Brainstorm Hub": "Modern quick capture and topic filters for Brainstorm Hub",
    "Morgen {clock}": "Tomorrow {clock}",
    "Möchtest du die Kategorie <strong>\"{name}\"</strong> wirklich löschen?": "Do you really want to delete the category <strong>\"{name}\"</strong>?",
    "Möchtest du diese Notiz wirklich unwiderruflich aus Brainstorm entfernen?": "Do you really want to remove this note from Brainstorm for good?",
    "Nach oben verschieben": "Move up",
    "Nach unten verschieben": "Move down",
    "Name der neuen Kategorie:": "Name of the new category:",
    "Neue Idee": "New idea",
    "Neue Kategorie erstellen": "Create a new category",
    "Neue Notiz-Schaltfläche (+ Idee) anzeigen": "Show the new note button (+ Idea)",
    "Nicht geändert: {items}": "Not changed: {items}",
    "Nicht ändern": "Do not change",
    "Notiz": "Note",
    "Notiz bearbeiten": "Edit note",
    "Notiz in \"{category}\" verfassen...": "Write a note in \"{category}\"...",
    "Notiz löschen": "Delete note",
    "Obere Werkzeugleiste (Titel & Filter-Pills) anzeigen": "Show the top toolbar (title and filter pills)",
    "Oder neue Kategorie anlegen:": "Or create a new category:",
    "Original gesprochen:": "Originally spoken:",
    "Priorität festlegen": "Set priority",
    "Priorität:": "Priority:",
    "Priorität: 🔥 Dringend (Klicken zum Umschalten)": "Priority: 🔥 Urgent (click to change)",
    "Priorität: 🔴 Hoch (Klicken zum Umschalten)": "Priority: 🔴 High (click to change)",
    "Priorität: 🟡 Mittel (Klicken zum Umschalten)": "Priority: 🟡 Medium (click to change)",
    "Priorität: 🟢 Niedrig (Klicken zum Umschalten)": "Priority: 🟢 Low (click to change)",
    "Punktraster im Hintergrund anzeigen": "Show the dot grid in the background",
    "Quelle": "Source",
    "Quelle: {name}": "Source: {name}",
    "Quelle: {name} • Gerät: {device}": "Source: {name} • Device: {device}",
    "Quellen-Icons anzeigen (Alexa, Assist, Handy, Dashboard)": "Show source icons (Alexa, Assist, phone, dashboard)",
    "Relative Zeitangaben anzeigen (z.B. 'vor 5 Min.')": "Show relative times (for example '5 min ago')",
    "Schließen (ESC)": "Close (ESC)",
    "Schnelleingabe-Feld für neue Notizen anzeigen": "Show the quick input for new notes",
    "Sensor-Entität": "Sensor entity",
    "Speichern": "Save",
    "Sprache": "Voice",
    "Standard-Farbmodus": "Default color mode",
    "Standard-Filterkategorie beim Öffnen": "Category selected when opening",
    "Standard-Kategorie im Fokus": "Category in focus by default",
    "Titel": "Title",
    "Unter vorherige Aufgabe einrücken": "Indent under the previous task",
    "Unteraufgabe": "Subtask",
    "Unteraufgabe einrücken": "Indent as a subtask",
    "Vergrößern": "Zoom in",
    "Verkleinern": "Zoom out",
    "Verschieben": "Move",
    "Vollbild beenden": "Leave full screen",
    "Vollbild umschalten (ESC zum Beenden)": "Toggle full screen (ESC to leave)",
    "Vollbild-Schaltfläche (⛶) anzeigen": "Show the full screen button (⛶)",
    "Wann soll Brainstorm erinnern? ({format})": "When should Brainstorm remind you? ({format})",
    "Was möchtest du festhalten?...": "What do you want to keep?...",
    "Wieder als aktiv markieren": "Mark as active again",
    "Wieder zur Hauptaufgabe machen": "Make it a main task again",
    "Zentrieren / Anordnen": "Center / arrange",
    "Ziel-Kategorie auswählen": "Choose a target category",
    "Zoom- & Zentrieren-Schaltflächen anzeigen": "Show the zoom and center buttons",
    "Zuhause": "Home",
    "Zuletzt aktive Alexa (Last Alexa) anzeigen": "Show last active Alexa",
    "Zuletzt aktive Alexa: {name} (Klicken für Details)": "Last active Alexa: {name} (click for details)",
    "Zurücksetzen": "Reset",
    "Zähler-Badge im Header anzeigen": "Show the counter badge in the header",
    "gerade eben": "just now",
    "vor {count} Min.": "{count} min ago",
    "vor {count} Std.": "{count} h ago",
    "vor {count}h": "{count}h ago",
    "vor {count}m": "{count}m ago",
    "z. B. Smart Home, Finanzen, Einkaufen...": "For example Smart Home, Finances, Shopping...",
    "z. B. mdi:home-automation": "For example mdi:home-automation",
    "{count} Ideen": "Ideas: {count}",
    "{active} aktiv • {done} erledigt": "{active} active • {done} completed",
    "{count} ausgewählt": "{count} selected",
    "{count} fremde Einträge bleiben erhalten.": "Entries of other people that stay: {count}",
    "{count} fremde Einträge werden ausgelassen.": "Entries of other people that are skipped: {count}",
    "Überfällig": "Overdue",
    "Übergeordnete Aufgabe:": "Parent task:",
    "Erinnern auf:": "Remind on:",
    "Ohne Auswahl gelten die Einstellungen der Erinnerungen.": "Without a choice, the reminder settings apply.",
    "Ohne Uhrzeit erinnert Brainstorm um 9:00.": "Without a time, Brainstorm reminds you at 9:00.",
    "Termin:": "Due:",
    "Wie in den Einstellungen": "As in the settings",
    "Termin entfernen": "Remove due date",
    "Übernehmen": "Use it",
    "— Keine (Hauptaufgabe) —": "— None (main task) —",
    "☑️ Auswählen": "☑️ Select",
    "⚠️ Bitte gib einen Kategorienamen ein.": "⚠️ Please enter a category name.",
    "⚠️ Der Text darf nicht leer sein.": "⚠️ The text must not be empty.",
    "⚠️ Die Kategorie \"{name}\" existiert bereits.": "⚠️ The category \"{name}\" already exists.",
    "✏️ Notiz bearbeiten": "✏️ Edit note",
    "✓ Erledigen": "✓ Complete",
    "✨ Noch keine aktiven Ideen. Tippe oben eine Idee ein oder sprich mit Alexa!": "✨ No active ideas yet. Type one above or talk to Alexa!",
    "➕ Erstellen": "➕ Create",
    "➕ Neue Kategorie": "➕ New category",
    "🌈 Bunt (Multicolor)": "🌈 Multicolor",
    "🌈 Bunt (Multicolor-Kategoriefarben)": "🌈 Multicolor (category colors)",
    "🌟 Alle Kategorien (Gesamtübersicht)": "🌟 All categories (overview)",
    "🌟 Alle Kategorien (Standard)": "🌟 All categories (default)",
    "🎨 Design für „{name}“": "🎨 Design of “{name}”",
    "🎨 Theme-Farben": "🎨 Theme colors",
    "🎨 Theme-Farben (Dynamisch nach Home Assistant Theme)": "🎨 Theme colors (follow the Home Assistant theme)",
    "🏷️ Kategorie auswählen": "🏷️ Choose a category",
    "🏷️ Verschieben": "🏷️ Move",
    "🏷️ {count} Einträge verschieben": "🏷️ Move entries: {count}",
    "👥 Freigeben": "👥 Share",
    "👥 {category} freigeben": "👥 Share {category}",
    "👥 {count} Einträge freigeben": "👥 Share entries: {count}",
    "💡 Neue Idee erfassen": "💡 Capture a new idea",
    "🔥 Dringend": "🔥 Urgent",
    "🔴 Hoch": "🔴 High",
    "🗑️ Kategorie löschen?": "🗑️ Delete category?",
    "🗑️ Löschen": "🗑️ Delete",
    "🗑️ Notiz löschen?": "🗑️ Delete note?",
    "🗑️ {count} Einträge löschen?": "🗑️ Delete entries: {count}?",
    "🟡 Mittel": "🟡 Medium",
    "🟢 Niedrig": "🟢 Low",
    "Abhaken": "Done",
    "Alle abhaken": "Mark all as done",
    "Auswahl": "Selection",
    "Auswahl aufheben (ESC)": "Clear selection (ESC)",
    "Auswählen: Rahmen um mehrere Notizen ziehen (oder Umschalt+Ziehen)": "Select: drag a frame around several notes (or Shift+drag)",
    "Möchtest du diese Notizen wirklich aus Brainstorm entfernen?": "Do you really want to remove these notes from Brainstorm?",
    "Rahmen ziehen oder Notizen antippen": "Drag a frame or tap notes",
    "{count} Notizen": "{count} notes",
    "{count} Notizen erledigt": "{count} notes done",
    "{count} Notizen gelöscht": "{count} notes deleted",
    "🗑️ {count} Notizen löschen?": "🗑️ Delete {count} notes?",
    "… und {count} weitere": "… and {count} more",
    "Unteraufgaben von der KI vorschlagen lassen": "Let the AI suggest subtasks",
    "✨ Unteraufgaben vorschlagen": "✨ Suggest subtasks",
    "Die KI denkt nach …": "The AI is thinking …",
    "Nochmal versuchen": "Try again",
    "Haken weg bei allem, was du nicht willst. Du kannst die Texte noch ändern.": "Untick what you do not want. You can still change the texts.",
    "Neue Vorschläge": "New suggestions",
    "{count} übernehmen": "Add {count}",
    "{count} Unteraufgaben angelegt": "{count} subtasks added",
    "{count} Unteraufgaben": "{count} subtasks",
    "Die KI hat keine Unteraufgaben geliefert.": "The AI gave no subtasks.",
    "Die KI ist gerade nicht erreichbar. Versuch es gleich nochmal.": "The AI cannot be reached right now. Try again in a moment.",
    "Wähle zuerst eine KI-Aufgaben-Entität unter Brainstorm Hub ➔ Konfigurieren ➔ KI.": "First choose an AI task entity under Brainstorm Hub ➔ Configure ➔ AI.",
    "Du darfst diese Notiz nicht ändern.": "You may not change this note.",
    "Suchen und filtern (/)": "Search and filter (/)",
    "Suchen … (#tag)": "Search … (#tag)",
    "Suchen": "Search",
    "Filter zurücksetzen und schließen (ESC)": "Clear the filter and close (ESC)",
    "Überfällig": "Overdue",
    "Termin ist vorbei": "The due date has passed",
    "7 Tage": "7 days",
    "Termin in den nächsten 7 Tagen": "Due in the next 7 days",
    "Als „In Arbeit“ markiert": "Marked as “in progress”",
    "Nur Notizen mit #{tag}": "Only notes with #{tag}",
    "{hits} von {total}": "{hits} of {total}",
    "{index}/{hits} von {total}": "{index}/{hits} of {total}",
    "Suche und Filter (🔍) anzeigen": "Show search and filter (🔍)",
    "Frage": "Question",
    "Achtung": "Warning",
    "Geld": "Money",
    "Stern": "Star",
    "Flagge": "Flag",
    "Haken": "Check",
    "Blockiert": "Blocked",
    "Wartet": "Waiting",
    "Herz": "Heart",
    "{done} von {total} Unteraufgaben erledigt, {percent} % geschafft": "{done} of {total} subtasks done, {percent} % complete",
    "Fortschritt {percent} % (antippen für den nächsten Schritt)": "Progress {percent} % (tap for the next step)",
    "Nur Notizen mit {marker}": "Only notes with {marker}",
    "Marker:": "Markers:",
    "Fortschritt:": "Progress:",
    "Kommt aus den Unteraufgaben: {done} von {total} erledigt, {percent} %.": "Comes from the subtasks: {done} of {total} done, {percent} %.",
    "Alle Ebenen": "All levels",
    "Ebenen bis {level}": "Levels up to {level}",
    "Ganze Map zeigen (Umschalt+F4)": "Show the whole map (Shift+F4)",
    "Eine Ebene zurück (Umschalt+F4)": "One level up (Shift+F4)",
    "Nur diesen Zweig zeigen (F4)": "Show only this branch (F4)",
    "Ebenen zeigen: 1, 2, 3 oder alle (Tasten 1–9, 0 = alle)": "Show levels: 1, 2, 3 or all (keys 1–9, 0 = all)",
    "Fokus": "Focus",
    "Beschriftung:": "Label:",
    "Callout": "Callout",
    "Callout:": "Callout:",
    "Die Verbindung konnte nicht gespeichert werden.": "The link could not be saved.",
    "Die zwei ausgewählten Notizen verbinden": "Link the two selected notes",
    "Höchstens 20 Verbindungen pro Notiz.": "At most 20 links per note.",
    "Mit einer anderen Notiz verbinden (L)": "Link to another note (L)",
    "Name des Rahmens:": "Frame name:",
    "Notizen mit demselben Namen teilen sich einen Rahmen.": "Notes with the same name share one frame.",
    "Optional: Name eines Rahmens": "Optional: name of a frame",
    "Optional: kurze Anmerkung in einer Sprechblase": "Optional: short remark in a speech bubble",
    "Rahmen": "Frame",
    "Rahmen bearbeiten": "Edit frame",
    "Rahmen entfernen": "Remove frame",
    "Rahmen um die Auswahl legen": "Put a frame around the selection",
    "Rahmen:": "Frame:",
    "Verbinden": "Link",
    "Verbindung bearbeiten": "Edit link",
    "Verbindung löschen": "Delete link",
    "Verbunden. Die Linie antippen, um sie zu beschriften.": "Linked. Tap the line to label it.",
    "Wartet auf: {names}": "Waiting for: {names}",
    "Ziel-Notiz antippen … (Esc bricht ab)": "Tap the target note … (Esc cancels)",
    "z. B. Phase 1, Später, Erdgeschoss": "e.g. Phase 1, Later, Ground floor",
    "z. B. gehört zu, braucht, siehe auch": "e.g. belongs to, needs, see also",
    "„{from}“ blockiert „{to}“: das Ziel wartet, bis die erste Notiz erledigt ist": "“{from}” blocks “{to}”: the target waits until the first note is done",
    "▢ Rahmen bearbeiten": "▢ Edit frame",
    "▢ Rahmen um {count} Notizen": "▢ Frame around {count} notes",
    "🔗 Verbindung": "🔗 Link",
    "1, 1.1, 1.2": "1, 1.1, 1.2",
    "A → Z": "A → Z",
    "Die Reihenfolge gilt in beiden Karten. ↶ macht es rückgängig.": "The order applies to both cards. ↶ undoes it.",
    "Fälligkeit": "Due date",
    "I, II, III": "I, II, III",
    "Keine": "None",
    "Neueste zuerst": "Newest first",
    "Nichts zu sortieren.": "Nothing to sort.",
    "Priorität": "Priority",
    "Sortieren hat nicht geklappt.": "Sorting did not work.",
    "Sortiert sofort, ↶ macht es rückgängig.": "Sorts right away, ↶ undoes it.",
    "Sortiert.": "Sorted.",
    "Sortiert. 🪄 ordnet die Map passend neu.": "Sorted. 🪄 arranges the map to match.",
    "Unterpunkte nummerieren:": "Number the subtasks:",
    "Unterpunkte sortieren:": "Sort the subtasks:",
    "Z → A": "Z → A",
    "a, b, c": "a, b, c",
    "Älteste zuerst": "Oldest first",
    "↕ Hauptnotizen sortieren": "↕ Sort the main notes",
    "↕ Unterpunkte von „{text}“ sortieren": "↕ Sort the subtasks of “{text}”",
    "Alle Notizen dieser Map, auch eingeklappte, für andere Mindmap- und Gliederungsprogramme.": "All notes of this map, folded ones too, for other mind map and outline apps.",
    "Als Bild:": "As a picture:",
    "Als Gliederung:": "As an outline:",
    "Datei wählen": "Choose a file",
    "Die Datei ist zu groß (höchstens 200 KB).": "The file is too big (200 KB at most).",
    "Eine Zeile pro Notiz, Unterpunkte eingerückt oder als Markdown-Liste. Oder eine Datei wählen.": "One line per note, subtasks indented or as a Markdown list. Or choose a file.",
    "Einfügen": "Insert",
    "Einfügen hat nicht geklappt.": "Inserting did not work.",
    "FreeMind (.mm)": "FreeMind (.mm)",
    "Gliederung einfügen:": "Insert an outline:",
    "Landet als Hauptnotizen in „{category}“.": "Goes in as main notes of “{category}”.",
    "Landet in der Standardkategorie.": "Goes into the default category.",
    "Landet unter „{text}“.": "Goes below “{text}”.",
    "Map speichern oder Gliederung einfügen": "Save the map or insert an outline",
    "Markdown": "Markdown",
    "OPML": "OPML",
    "{count} Notizen eingefügt.": "{count} notes inserted.",
    "🖼️ Map speichern und einfügen": "🖼️ Save and insert",
    "Brainstorm: schnell viele Ideen sammeln (B)": "Brainstorm: collect many ideas fast (B)",
    "Die Idee konnte nicht gespeichert werden.": "The idea could not be saved.",
    "Fertig": "Done",
    "Einsteiger": "Beginner",
    "Normal": "Normal",
    "Profi": "Pro",
    "Mehr Felder …": "More fields …",
    "Bedienstufe dieser Karte": "Operating level of this card",
    "Knöpfe in den Zeilen": "Buttons in the rows",
    "Automatisch: Handy ⋯, Maus beim Darüberfahren": "Automatic: ⋯ on phones, on hover with a mouse",
    "Immer alle Knöpfe zeigen": "Always show all buttons",
    "Immer nur ⋯": "Always only ⋯",
    "Aktionen": "Actions",
    "Idee eintippen und Enter …": "Type an idea and press Enter …",
    "Ideen landen in der passenden Kategorie.": "Ideas go into the matching category.",
    "Ideen landen in „{category}“.": "Ideas go into “{category}”.",
    "Ideen landen unter „{text}“.": "Ideas go below “{text}”.",
    "Nicht bewerten, nur sammeln: Enter speichert und das Feld ist sofort wieder frei.": "Do not judge, just collect: Enter saves and the field is free again at once.",
    "Sammeln": "Collect",
    "Wieder löschen": "Delete again",
    "Zeit!": "Time!",
    "{count} Ideen gesammelt": "{count} ideas collected",
    "{count} Ideen gesammelt. 🪄 ordnet die Map neu, ↶ nimmt alle heraus.": "{count} ideas collected. 🪄 arranges the map, ↶ takes them all out.",
    "{minutes} Min.": "{minutes} min",
    "⚡ Brainstorm": "⚡ Brainstorm",
    "Ansicht wählen": "Choose a view",
    "Übersicht ein- oder ausblenden (M)": "Show or hide the overview (M)",
    "Übersicht: tippen oder ziehen, um dorthin zu springen": "Overview: tap or drag to jump there",
    "Übersicht (Minimap) anzeigen": "Show the overview (minimap)",
    "Diese Woche": "This week",
    "Eisenhower-Matrix": "Eisenhower matrix",
    "Fällig in den nächsten drei Tagen bleibt dringend, ändere dafür das Datum": "Due within three days stays urgent, change the date for that",
    "Heute": "Today",
    "Hierher ziehen zum Abhaken": "Drag here to tick off",
    "In Kanban, Zeitleiste und Matrix ändert das Ziehen in eine andere Spalte Status, Fälligkeit oder Priorität.": "On Kanban, timeline and matrix, dragging a note to another column changes its state, due date or priority.",
    "Kanban nach Status": "Kanban by state",
    "Morgen": "Tomorrow",
    "Ohne Datum": "No date",
    "Später": "Later",
    "Zeitleiste nach Fälligkeit": "Timeline by due date",
    "Überfällig ergibt sich aus dem Datum": "Overdue follows from the date",
    "„Wartet“ ergibt sich aus blockierenden Verbindungen": "“Waiting” follows from blocking links",
    "⚠️ Überfällig": "⚠️ Overdue",
    "⛔ Wartet": "⛔ Waiting",
    "✅ Erledigt": "✅ Done",
    "👥 Abgeben": "👥 Delegate",
    "📅 Einplanen": "📅 Schedule",
    "📝 Offen": "📝 Open",
    "🔥 Sofort erledigen": "🔥 Do now",
    "🔧 In Arbeit": "🔧 In progress",
    "🗑️ Später oder gar nicht": "🗑️ Later or never",
    "Gliederung": "Outline",
    "↶ Sortieren rückgängig": "↶ Undo sorting",
    "Jeden Tag": "Every day",
    "Jeden Werktag (Mo–Fr)": "Every weekday (Mon–Fri)",
    "Jede Woche": "Every week",
    "Alle 2 Wochen": "Every 2 weeks",
    "Jeden Monat": "Every month",
    "Jedes Jahr": "Every year",
    "Nicht wiederholen": "Do not repeat",
    "Zuständig: {mode}": "Assigned: {mode}",
    "Morgens": "Morning",
    "Tagsüber": "During the day",
    "Abends": "Evening",
    "Nicht für heute": "Not for today",
    "Mein Tag: {part}": "My day: {part}",
    "Mein Tag:": "My day:",
    "Gewohnheit: {streak} Tage in Folge, beste Serie {best}. Antippen zeigt den Kalender.": "Habit: {streak} days in a row, best streak {best}. Tap to see the calendar.",
    "🔥 Gewohnheit: jeden Tag abhaken, mit Serie": "🔥 Habit: tick off every day, with a streak",
    "Serie: {count}": "Streak: {count}",
    "Beste Serie: {count}": "Best streak: {count}",
    "Erledigt gesamt: {count}": "Done in total: {count}",
    "Tippe auf einen Tag, um ihn nachzutragen oder zu entfernen.": "Tap a day to add or remove it.",
    "Heute erledigt – nochmal tippen nimmt es zurück": "Done today – tap again to take it back",
    "Für heute abhaken, die Gewohnheit bleibt": "Tick off for today, the habit stays",
    "🔥 Kalender": "🔥 Calendar",
    "Einfach drauflos reden oder tippen, auch mehrere Aufgaben auf einmal, mit Termin und wer sie übernimmt. Die KI macht daraus einzelne Notizen, die du vor dem Anlegen prüfst.": "Just talk or type away, several tasks at once too, with a date and who takes them. The AI turns it into single notes that you check before they are created.",
    "z. B. Morgen um zehn den Klempner anrufen, Anna kauft am Freitag Milch und dann noch den Keller aufräumen": "e.g. Call the plumber tomorrow at ten, Anna buys milk on Friday and then tidy up the basement",
    "✨ Zerlegen": "✨ Split",
    "Zerlege …": "Splitting …",
    "Darin habe ich keine Aufgabe gefunden.": "I found no task in it.",
    "Niemand": "Nobody",
    "So hat die KI es verstanden. Ändere, was nicht passt, und wähle ab, was nicht angelegt werden soll.": "This is how the AI understood it. Change what does not fit and untick what should not be created.",
    "Ohne KI Satz für Satz zerlegt. Ändere, was nicht passt, und wähle ab, was nicht angelegt werden soll.": "Split sentence by sentence without the AI. Change what does not fit and untick what should not be created.",
    "Anlegen": "Create",
    "Aufgabe": "Task",
    "Datum": "Date",
    "Uhrzeit": "Time",
    "Zuständig": "Assignee",
    "{count} anlegen": "Create {count}",
    "🗣️ Frei reden": "🗣️ Talk freely",
    "Frei reden: mehrere Aufgaben auf einmal sagen oder tippen, die KI zerlegt sie": "Talk freely: say or type several tasks at once, the AI splits them",
    "Aus „Mein Tag“ nehmen": "Take out of My day",
    "Für heute vornehmen": "Pick for today",
    "☀️ Mein Tag": "☀️ My day",
    "Nur Notizen, die du dir für heute vorgenommen hast": "Only notes you picked for today",
    "Für heute vornehmen: morgens, tagsüber oder abends. Gilt nur heute und kommt ins Briefing.": "Pick it for today: morning, during the day or evening. Counts only today and goes into the briefing.",
    "Reihum": "Taking turns",
    "Wer am wenigsten erledigt hat": "Whoever did the least",
    "Zufällig": "At random",
    "Zuständig im Wechsel:": "Changing assignee:",
    "Nicht wechseln": "Do not change",
    "Abgehakt geht die nächste Runde an die nächste Person. Wähle mindestens zwei.": "Once ticked off, the next round goes to the next person. Choose at least two.",
    "⚠️ Für den Wechsel mindestens zwei Personen wählen oder „Nicht wechseln“ einstellen.": "⚠️ Choose at least two people for the rotation, or set it to “Do not change”.",
    "Wiederholt sich: {rule}": "Repeats: {rule}",
    "Wiederholen:": "Repeat:",
    "Abgehakt kommt die Notiz mit ihren Unteraufgaben zum nächsten Termin wieder.": "When ticked off, the note comes back with its subtasks at the next date.",
    "Als PDF:": "As PDF:",
    "Zum Drucken oder Weitergeben: das Bild der Map und danach alle Notizen als Gliederung mit Beschreibung.": "For printing or passing on: the picture of the map, then all notes as an outline with their descriptions.",
    "PDF (Map und Gliederung)": "PDF (map and outline)",
    "PDF (nur Gliederung)": "PDF (outline only)",
    "Speichern als PDF ging nicht": "Saving as PDF did not work",
    "Bild öffnen": "Open picture",
    "Bilder aus den Anhängen in den Notizen zeigen": "Show pictures from the attachments in the notes",
    "Zurück": "Back",
    "Name": "Name",
    "Regeln: passende Notizen färben (R)": "Rules: color fitting notes (R)",
    "Die Regeln konnten nicht gespeichert werden.": "The rules could not be saved.",
    "🎨 Regeln": "🎨 Rules",
    "Regeln färben jede Notiz, die zu einem gespeicherten Filter passt, und setzen ein Zeichen daran. Die erste passende Regel gilt. Sie gelten für dich auf allen Geräten.": "Rules color every note that fits a saved filter and put a sign on it. The first rule that fits wins. They apply to you on every device.",
    "Regel an oder aus": "Rule on or off",
    "Regel {number}": "Rule {number}",
    "Nach oben": "Move up",
    "Noch keine Regeln.": "No rules yet.",
    "Für eine neue Regel stelle zuerst in der Suche 🔍 einen Filter ein, z. B. 🔥 Dringend oder #garten, und tippe dann hier auf ＋.": "For a new rule, first set a filter in the search 🔍, e.g. 🔥 Urgent or #garden, then tap ＋ here.",
    "Aktuellen Filter als Regel": "Current filter as a rule",
    "🎨 Neue Regel": "🎨 New rule",
    "🎨 Regel bearbeiten": "🎨 Edit rule",
    "Wenn": "When",
    "z. B. Brennt": "e.g. On fire",
    "Farbe": "Color",
    "Keine Farbe": "No color",
    "Zeichen": "Sign",
    "Kein Zeichen": "No sign",
    "Wähle eine Farbe oder ein Zeichen.": "Pick a color or a sign.",
    " oder ": " or ",
    "überfällig oder in 7 Tagen fällig": "overdue or due within 7 days",
    "überfällig": "overdue",
    "in 7 Tagen fällig": "due within 7 days",
    "in Arbeit": "in progress",
    "Suchen … (#tag möglich)": "Search … (#tag works)",
    "Notizen durchsuchen": "Search notes",
    "Suche leeren": "Clear search",
    "Nichts gefunden für „{query}“.": "Nothing found for “{query}”.",
    "Suchfeld über der Liste anzeigen": "Show the search field above the list",
    "Keine Notizen zum Präsentieren.": "No notes to present.",
    "Präsentation beenden (Esc)": "End the presentation (Esc)",
    "Präsentieren (P)": "Present (P)",
    "Weiter (→ oder Leertaste)": "Next (→ or space)",
    "Zurück (←)": "Back (←)",
    "Überblick · {total} Notizen": "Overview · {total} notes",
    "→ oder Leertaste: weiter · Esc: beenden": "→ or space: next · Esc: end",
    "Als Beschreibung übernehmen": "Use as description",
    "Ast zusammenfassen": "Summarize the branch",
    "Die KI hat für keine lose Notiz einen passenden Platz gefunden.": "The AI found no fitting place for any loose note.",
    "Die KI hat keine Zuordnung geliefert.": "The AI gave no suggestions.",
    "Die KI hat keine Zusammenfassung geliefert.": "The AI gave no summary.",
    "Du kannst den Text noch ändern.": "You can still change the text.",
    "Haken weg bei allem, was bleiben soll, wo es ist.": "Untick everything that should stay where it is.",
    "In dieser Kategorie gibt es keine losen Notizen.": "This category has no loose notes.",
    "Kopieren": "Copy",
    "Kopiert": "Copied",
    "Neu schreiben": "Write again",
    "Unteraufgaben vorschlagen": "Suggest subtasks",
    "Wähle zuerst eine Kategorie.": "Pick a category first.",
    "Zusammenfassung gespeichert": "Summary saved",
    "{count} Notizen zugeordnet": "{count} notes sorted in",
    "✨ KI-Hilfe": "✨ AI help",
    "✨ Lose Ideen zuordnen": "✨ Sort in loose ideas",
    "{name} bearbeitet „{text}“": "{name} is editing “{text}”",
    "{name} schaut sich die Map an": "{name} is looking at the map",
    "{name} bearbeitet diese Notiz gerade": "{name} is editing this note right now",
    "Zeichnen": "Draw",
    "Stift": "Pen",
    "Pfeil": "Arrow",
    "Kreis": "Circle",
    "Radierer: Striche antippen": "Eraser: tap strokes",
    "Strichstärke": "Line width",
    "Rückgängig": "Undo",
    "Alles löschen": "Delete all",
    "Fertig (Esc)": "Done (Esc)",
    "Zeichnen: Pfeile, Kreise und Skizzen auf der Map (D)": "Draw: arrows, circles and sketches on the map (D)",
    "Zeichnen geht auf der runden Map einer einzelnen Kategorie.": "Drawing works on the round map of a single category.",
    "Zeichnung": "Drawing",
    "Die Map hat schon sehr viele Zeichnungen. Lösche zuerst welche.": "The map already has a lot of drawings. Delete some first.",
    "Die Zeichnung konnte nicht gespeichert werden.": "The drawing could not be saved.",
    "Zeichnung gelöscht. ↶ holt sie zurück.": "Drawing deleted. ↶ brings it back.",
    "Pinnwand mit Haftzetteln": "Pinboard with sticky notes",
    "Auf der Pinnwand bleibt jeder Zettel, wo du ihn hinziehst. Die Farbe wählst du unter ⋯, Gruppen bekommen einen Rahmen.": "On the pinboard every sticky note stays where you drag it. Pick its colour under ⋯; groups get a frame.",
    "Der Zettel konnte nicht gespeichert werden.": "The sticky note could not be saved.",
    "Gelb": "Yellow",
    "Rosa": "Pink",
    "Grün": "Green",
    "Blau": "Blue",
    "Lila": "Purple",
    "Orange": "Orange",
    "✨ Zuordnen": "✨ Sort in",
    "✨ Themen": "✨ Themes",
    "Aufgedeckt: {count} Ideen": "Revealed: {count} ideas",
    "bis {time}": "until {time}",
    "{count} Ideen anderer verdeckt": "{count} ideas of others hidden",
    "Verdeckte Runde in {category}": "Hidden round in {category}",
    "Mitmachen": "Join",
    "Aufdecken": "Reveal",
    "Verdeckte Runde läuft: Deine Ideen sieht bis zum Aufdecken nur du.": "Hidden round running: only you see your ideas until they are revealed.",
    "Verdeckt: Jeder sieht bis zum Ende nur die eigenen Ideen": "Hidden: everyone sees only their own ideas until the end",
    "✨ Nach Themen gruppieren": "✨ Group into themes",
    "Zum Gruppieren braucht es mindestens vier lose Notizen ohne Unterpunkte.": "Grouping needs at least four loose notes without subtasks.",
    "Die KI hat keine Themen geliefert.": "The AI gave no themes.",
    "Die KI hat keine Themen gefunden, in die mehrere Notizen passen.": "The AI found no themes that several notes fit into.",
    "Jedes Thema wird ein Oberpunkt, die Notizen kommen darunter. Haken weg bei allem, was bleiben soll, wo es ist. Die Titel kannst du ändern.": "Each theme becomes a parent note with the notes below it. Untick whatever should stay where it is. You can change the titles.",
    "{count} Themen anlegen": "Create {count} themes",
    "Gruppieren hat nicht geklappt.": "Grouping did not work.",
    "{count} Themen angelegt": "{count} themes created",
    "{count} Themen": "{count} themes",
    "🧾 Ast zusammenfassen": "🧾 Summarize the branch",
    "Ablauf": "Schedule",
    "Anreise": "Getting there",
    "Aufgaben": "Tasks",
    "Ausflüge": "Trips",
    "Ausmessen": "Measure",
    "Budget": "Budget",
    "Chancen": "Opportunities",
    "Contra": "Con",
    "Deko": "Decoration",
    "Dienstag": "Tuesday",
    "Dokumente": "Documents",
    "Donnerstag": "Thursday",
    "Einkauf": "Shopping",
    "Entscheidung": "Decision",
    "Essen und Getränke": "Food and drinks",
    "Feier": "Party",
    "Feier planen": "Plan a party",
    "Freitag": "Friday",
    "Gäste": "Guests",
    "Handwerker": "Tradespeople",
    "Kleidung": "Clothes",
    "Material": "Material",
    "Mittwoch": "Wednesday",
    "Montag": "Monday",
    "Musik": "Music",
    "Offene Fragen": "Open questions",
    "Packliste": "Packing list",
    "Planung": "Planning",
    "Pro": "Pro",
    "Pro und Contra": "Pros and cons",
    "Projekt": "Project",
    "Projektplan": "Project plan",
    "Raum renovieren": "Renovate a room",
    "Reihenfolge": "Order of work",
    "Reise": "Trip",
    "Reise planen": "Plan a trip",
    "Renovierung": "Renovation",
    "Risiken": "Threats",
    "Rückblick": "Retrospective",
    "SWOT-Analyse": "SWOT analysis",
    "Schwächen": "Weaknesses",
    "Stärken": "Strengths",
    "Technik": "Gadgets",
    "Termine": "Dates",
    "Test": "Testing",
    "Umsetzung": "Doing",
    "Unterkunft": "Accommodation",
    "Vorlage wählen, anpassen und einfügen:": "Pick a template, adjust it and insert it:",
    "Was lief gut": "What went well",
    "Was lief nicht gut": "What went badly",
    "Was wir ändern": "What we change",
    "Werkzeug": "Tools",
    "Woche": "Week",
    "Wochenende": "Weekend",
    "Wochenplan": "Week plan",
    "Ziel": "Goal",
    "Anordnung der Notizen": "Arrangement of the notes",
    "Rund um die Mitte": "Around the center",
    "Baum nach rechts": "Tree to the right",
    "Organigramm nach unten": "Org chart downwards",
  },
};

let language = (document.documentElement.lang || navigator.language || "en").toLowerCase();

const code = () => language.split(/[-_]/)[0];

/** Follow the language of the person's Home Assistant profile. */
export function setLanguage(hass) {
  const next = hass && (hass.locale?.language || hass.language);
  if (next) language = next.toLowerCase();
}

/** Return a text in the current language with its values filled in. */
export function t(text, values) {
  let result = text;
  if (code() !== "de") {
    result = DICTIONARIES[code()]?.[text] ?? DICTIONARIES.en[text] ?? text;
  }
  if (values) {
    for (const [name, value] of Object.entries(values)) {
      result = result.split(`{${name}}`).join(String(value));
    }
  }
  return result;
}

/** Return the locale for dates. */
export function dateLocale() {
  return code() === "de" ? "de-DE" : language;
}

const pad = (value) => String(value).padStart(2, "0");

/** Return a day and month, without the year. */
export function shortDate(date) {
  if (code() === "de") return `${pad(date.getDate())}.${pad(date.getMonth() + 1)}.`;
  return date.toLocaleDateString(language, { month: "short", day: "numeric" });
}

/** Return the format a person types a date and time in. */
export function dueInputFormat() {
  return code() === "de" ? "TT.MM.JJJJ HH:MM" : "YYYY-MM-DD HH:MM";
}

/** Return a date and time in the format a person types. */
export function formatDueInput(date) {
  const clock = `${pad(date.getHours())}:${pad(date.getMinutes())}`;
  if (code() === "de") {
    return `${pad(date.getDate())}.${pad(date.getMonth() + 1)}.${date.getFullYear()} ${clock}`;
  }
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${clock}`;
}

/** Return the date a person typed, null if it does not fit the format. */
export function parseDueInput(input) {
  const text = input.trim();
  const german = text.match(/^(\d{1,2})\.(\d{1,2})\.(\d{4})\s+(\d{1,2}):(\d{2})$/);
  if (german) return new Date(+german[3], +german[2] - 1, +german[1], +german[4], +german[5]);
  const iso = text.match(/^(\d{4})-(\d{1,2})-(\d{1,2})\s+(\d{1,2}):(\d{2})$/);
  if (iso) return new Date(+iso[1], +iso[2] - 1, +iso[3], +iso[4], +iso[5]);
  return null;
}

/** Return the values of a date and a time input for a due date. */
export function dueInputValues(due) {
  const date = due ? new Date(due) : null;
  if (!date || Number.isNaN(date.getTime())) return { date: "", time: "" };
  return {
    date: `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`,
    time: `${pad(date.getHours())}:${pad(date.getMinutes())}`,
  };
}

/** Return the due date of a date and a time input, a missing time meaning 09:00. */
export function dueFromInputValues(date, time) {
  if (!date) return null;
  const due = new Date(`${date}T${time || "09:00"}`);
  return Number.isNaN(due.getTime()) ? null : due.toISOString();
}

/** Return the Echos of the Alexa Media Player integration, sorted by name. */
export function alexaEchos(hass) {
  return Object.keys((hass && hass.entities) || {})
    .filter((id) => id.startsWith("media_player.") && hass.entities[id].platform === "alexa_media")
    .map((id) => {
      const state = hass.states[id];
      return { id, name: (state && state.attributes.friendly_name) || id };
    })
    .sort((a, b) => a.name.localeCompare(b.name));
}

const ESCAPES = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" };

function escapeHtml(text) {
  return String(text).replace(/[&<>"']/g, (char) => ESCAPES[char]);
}

/** Return the link target if it is a web or mail address, otherwise null. */
function safeHref(url) {
  try {
    const parsed = new URL(url);
    return ["http:", "https:", "mailto:"].includes(parsed.protocol) ? parsed.href : null;
  } catch (err) {
    return null;
  }
}

function link(url, label) {
  const href = safeHref(url);
  if (!href) return escapeHtml(label);
  return `<a class="bs-link" href="${escapeHtml(href)}" target="_blank" rel="noopener noreferrer">${escapeHtml(label)}</a>`;
}

// `code`, [label](url), bare http(s) addresses, **bold**, ~~strike~~, *italic*
const MARKDOWN =
  /`([^`\n]+)`|\[([^\]\n]+)\]\(((?:https?:\/\/|mailto:)[^\s()]+)\)|(https?:\/\/[^\s<>"']+)|\*\*(?=\S)([^*\n]*?\S)\*\*|~~(?=\S)([^~\n]*?\S)~~|\*(?=[^\s*])([^*\n]*?[^\s*])\*/g;

/**
 * Turn the text of an idea into safe HTML with links and a little Markdown.
 *
 * Everything is escaped; only the tags made here are HTML, and links only go
 * to web or mail addresses.
 */
export function formatText(text) {
  if (text === null || text === undefined) return "";
  const raw = String(text);
  let html = "";
  let last = 0;
  for (const match of raw.matchAll(MARKDOWN)) {
    const [whole, code, label, target, bare, bold, strike, italic] = match;
    html += escapeHtml(raw.slice(last, match.index));
    last = match.index + whole.length;
    if (code !== undefined) {
      html += `<code>${escapeHtml(code)}</code>`;
    } else if (label !== undefined) {
      html += link(target, label);
    } else if (bare !== undefined) {
      // Punctuation after an address belongs to the sentence, and so does a
      // closing bracket without an opening one in the address.
      let url = bare.replace(/[.,;:!?]+$/, "");
      while (url.endsWith(")") && (url.match(/\(/g) || []).length < (url.match(/\)/g) || []).length) {
        url = url.slice(0, -1).replace(/[.,;:!?]+$/, "");
      }
      html += link(url, url);
      last = match.index + url.length;
    } else if (bold !== undefined) {
      html += `<strong>${formatText(bold)}</strong>`;
    } else if (strike !== undefined) {
      html += `<s>${formatText(strike)}</s>`;
    } else {
      html += `<em>${formatText(italic)}</em>`;
    }
  }
  return html + plainText(raw.slice(last));
}

// A tag is a word after #, such as #garten or #3d-druck, with at least one
// letter, so "#1" stays a number. It starts the text or follows a space or a bracket.
const TAG = /(^|[\s(\[,;])#((?=[\p{N}_-]*\p{L})[\p{L}\p{N}_-]+)/gu;
// A color such as #ff7800 is no tag
const COLOR = /^(?=[a-f]*\d)[0-9a-f]{6}(?:[0-9a-f]{2})?$/i;

/** Escape plain text and show its tags as chips. */
function plainText(raw) {
  let html = "";
  let last = 0;
  for (const match of raw.matchAll(TAG)) {
    if (COLOR.test(match[2])) continue;
    const start = match.index + match[1].length;
    html += escapeHtml(raw.slice(last, start));
    const tag = match[2];
    html += `<span class="bs-tag" data-tag="${escapeHtml(tag.toLowerCase())}">#${escapeHtml(tag)}</span>`;
    last = start + 1 + tag.length;
  }
  return html + escapeHtml(raw.slice(last));
}

/** Return the tags of an idea, from its title and its description, in lower case. */
export function ideaTags(idea) {
  const tags = new Set();
  for (const field of [idea && idea.text, idea && idea.description]) {
    if (!field) continue;
    for (const match of String(field).matchAll(TAG)) {
      if (!COLOR.test(match[2])) tags.add(match[2].toLowerCase());
    }
  }
  // Tags given by an action, without # in the text
  for (const tag of (idea && Array.isArray(idea.tags) ? idea.tags : [])) {
    if (typeof tag === "string" && tag.trim()) tags.add(tag.trim().replace(/^#/, "").toLowerCase());
  }
  return [...tags];
}

// Searching ignores case and accents, so "apfel" finds "Äpfel"
const fold = (text) => String(text || "").normalize("NFD").replace(/\p{M}/gu, "").toLowerCase();

/** Return an empty filter: no words, priorities, dates or tags. */
export function emptyFilter() {
  return { query: "", prios: new Set(), overdue: false, soon: false, working: false, myDay: false, tags: new Set(), markers: new Set() };
}

/** Tell whether a filter asks for anything. */
export function filterActive(filter) {
  return Boolean(
    filter &&
      (filter.query.trim() ||
        filter.prios.size ||
        filter.overdue ||
        filter.soon ||
        filter.working ||
        filter.myDay ||
        filter.tags.size ||
        (filter.markers && filter.markers.size)),
  );
}

/**
 * Tell whether an idea fits a filter.
 *
 * Every word of the search must appear in the title, description, result
 * or person, a word with # must start one of its tags. Priorities
 * count if any fits, overdue and next 7 days likewise, the tags all have to be there.
 */
export function ideaMatches(idea, filter, now = new Date()) {
  if (!filterActive(filter)) return true;
  const tags = ideaTags(idea);
  const words = fold(filter.query).split(/\s+/).filter(Boolean);
  if (words.length) {
    const haystack = fold([idea.text, idea.description, idea.result, idea.assignee].join(" "));
    for (const word of words) {
      if (word.startsWith("#") && word.length > 1) {
        const wanted = word.slice(1);
        if (!tags.some((tag) => fold(tag).startsWith(wanted))) return false;
      } else if (!haystack.includes(word)) {
        return false;
      }
    }
  }
  if (filter.prios.size && !filter.prios.has(String(idea.priority || "medium").toLowerCase())) return false;
  if (filter.overdue || filter.soon) {
    const due = idea.due ? new Date(idea.due).getTime() : NaN;
    if (Number.isNaN(due)) return false;
    const overdue = due < now.getTime();
    const soon = !overdue && due <= now.getTime() + 7 * 24 * 3600 * 1000;
    if (!((filter.overdue && overdue) || (filter.soon && soon))) return false;
  }
  if (filter.working && !idea.in_progress) return false;
  if (filter.myDay && !idea.my_day) return false;
  for (const tag of filter.tags) {
    if (!tags.includes(tag)) return false;
  }
  const markers = ideaMarkers(idea);
  for (const marker of filter.markers || []) {
    if (!markers.includes(marker)) return false;
  }
  return true;
}

/** The shapes a note can have on the mind map. */
export const NODE_SHAPES = ["card", "cloud", "bubble", "thought", "pill", "rect", "ellipse", "hexagon", "note", "underline"];

/** Return the name of a shape in the language of the user. */
export function shapeLabel(shape) {
  return {
    card: t("Karte"),
    cloud: t("Wolke"),
    bubble: t("Sprechblase"),
    thought: t("Gedankenblase"),
    pill: t("Kapsel"),
    rect: t("Rechteck"),
    ellipse: t("Ellipse"),
    hexagon: t("Sechseck"),
    note: t("Notizzettel"),
    underline: t("Unterstrichen"),
  }[shape];
}

/** The ways the subtasks of a note can be sorted: field, reversed, label. */
export function sortChoices() {
  return [
    ["text", false, t("A → Z")],
    ["text", true, t("Z → A")],
    ["priority", false, t("Priorität")],
    ["due", false, t("Fälligkeit")],
    ["created", false, t("Älteste zuerst")],
    ["created", true, t("Neueste zuerst")],
    ["votes", false, t("Stimmen")],
  ];
}

/**
 * The options of the parent field in the edit dialogs: every note except
 * this one and its own subtasks, notes of the same category first. The
 * current parent is always there, so saving never drops it unasked.
 */
export function parentOptions(ideas, id, currentParentId, category) {
  const list = ideas || [];
  const below = new Set([id]);
  let grew = true;
  while (grew) {
    grew = false;
    list.forEach((idea) => {
      if (idea.parent_id && below.has(idea.parent_id) && !below.has(idea.id)) {
        below.add(idea.id);
        grew = true;
      }
    });
  }
  const candidates = list
    .filter((idea) => !below.has(idea.id))
    .sort((a, b) => Number(b.category === category) - Number(a.category === category));
  const short = (text) => {
    const plain = String(text || "");
    return escapeHtml(plain.length > 50 ? `${plain.slice(0, 50)}…` : plain);
  };
  return [`<option value="">${t("— Keine (Hauptaufgabe) —")}</option>`]
    .concat(
      candidates.map(
        (idea) =>
          `<option value="${escapeHtml(idea.id)}"${idea.id === currentParentId ? " selected" : ""}>${idea.parent_id ? "↳ " : ""}${short(idea.text)}${idea.category !== category ? ` (${escapeHtml(idea.category || "")})` : ""}</option>`,
      ),
    )
    .join("");
}

/** How often a note can come back after it is ticked off. */
export const REPEATS = ["daily", "weekdays", "weekly", "biweekly", "monthly", "yearly"];

/** Return the name of a repeat rule in the language of the user. */
export function repeatLabel(rule) {
  const labels = {
    daily: t("Jeden Tag"),
    weekdays: t("Jeden Werktag (Mo–Fr)"),
    weekly: t("Jede Woche"),
    biweekly: t("Alle 2 Wochen"),
    monthly: t("Jeden Monat"),
    yearly: t("Jedes Jahr"),
  };
  return labels[rule] || "";
}

/** The options of the repeat field in the edit dialogs. */
export function repeatOptions(current) {
  return [`<option value="">${t("Nicht wiederholen")}</option>`]
    .concat(REPEATS.map((rule) => `<option value="${rule}"${rule === current ? " selected" : ""}>🔁 ${repeatLabel(rule)}</option>`))
    .join("");
}

/** A small 🔁 for notes that come back, saying how the person changes. */
export function repeatBadge(idea) {
  const label = repeatLabel(idea && idea.repeat);
  if (!label) return "";
  let title = t("Wiederholt sich: {rule}", { rule: label });
  const mode = rotationLabel(idea.rotation && idea.rotation.mode);
  if (mode) title += ` · ${t("Zuständig: {mode}", { mode })}`;
  return `<span class="repeat-badge" title="${escapeHtml(title)}">🔁</span>`;
}

/** The parts of today a note can be picked for in "My day". */
export const MY_DAY_PARTS = ["morning", "day", "evening"];
const MY_DAY_ICONS = { morning: "🌅", day: "☀️", evening: "🌙" };

/** Return the name of a part of the day in the language of the user. */
export function myDayLabel(part) {
  return { morning: t("Morgens"), day: t("Tagsüber"), evening: t("Abends") }[part] || "";
}

/** The options of the "My day" field in the edit dialogs. */
export function myDayOptions(current) {
  return [`<option value="">${t("Nicht für heute")}</option>`]
    .concat(MY_DAY_PARTS.map((part) => `<option value="${part}"${part === current ? " selected" : ""}>${MY_DAY_ICONS[part]} ${myDayLabel(part)}</option>`))
    .join("");
}

/** A small sun, sunrise or moon for notes picked for today. */
export function myDayBadge(idea) {
  const part = idea && idea.my_day;
  if (!MY_DAY_ICONS[part]) return "";
  return `<span class="repeat-badge my-day-badge" title="${escapeHtml(t("Mein Tag: {part}", { part: myDayLabel(part) }))}">${MY_DAY_ICONS[part]}</span>`;
}

/** Sort key for "My day": morning first, evening last, the rest after. */
export function myDayRank(idea) {
  const index = MY_DAY_PARTS.indexOf(idea && idea.my_day);
  return index < 0 ? MY_DAY_PARTS.length : index;
}

/** How a repeating note can change hands each round. */
export const ROTATIONS = ["turn", "fewest", "random"];

/** Return the name of a rotation mode in the language of the user. */
export function rotationLabel(mode) {
  const labels = {
    turn: t("Reihum"),
    fewest: t("Wer am wenigsten erledigt hat"),
    random: t("Zufällig"),
  };
  return labels[mode] || "";
}

function personsOf(hass) {
  return Object.values((hass && hass.states) || {})
    .filter((state) => state.entity_id.startsWith("person."))
    .map((state) => ({ id: state.entity_id, name: (state.attributes && state.attributes.friendly_name) || state.entity_id.slice(7) }))
    .sort((a, b) => a.name.localeCompare(b.name));
}

/**
 * The fields that let a repeating note go to someone else every round.
 * Shown below the repeat field once a rule is chosen; empty without two people.
 */
export function rotationFields(hass, idea, prefix = "dialog") {
  const people = personsOf(hass);
  const current = (idea && idea.rotation) || { mode: "", people: [] };
  if (people.length < 2 && !current.mode) return "";
  const chosen = new Set(current.people || []);
  // People of the turn come first in their order, the others after them
  const ordered = (current.people || [])
    .map((id) => people.find((person) => person.id === id) || { id, name: id.slice(7) })
    .concat(people.filter((person) => !chosen.has(person.id)));
  return `<div class="lvl bs-rotation" data-lvl="normal" id="bsRotation">
    <div class="${prefix}-label">${t("Zuständig im Wechsel:")}</div>
    <select class="${prefix}-input" id="bsRotationMode">
      <option value="">${t("Nicht wechseln")}</option>
      ${ROTATIONS.map((mode) => `<option value="${mode}"${mode === current.mode ? " selected" : ""}>🔄 ${rotationLabel(mode)}</option>`).join("")}
    </select>
    <div class="bs-rotation-people" id="bsRotationPeople">
      ${ordered.map((person) => `<label class="bs-rotation-person"><input type="checkbox" value="${escapeHtml(person.id)}"${chosen.has(person.id) ? " checked" : ""}> ${escapeHtml(person.name)}</label>`).join("")}
    </div>
    <div class="${prefix}-hint bs-rotation-hint" id="bsRotationHint" role="status">${ROTATION_HINT()}</div>
  </div>`;
}

const ROTATION_HINT = () => t("Abgehakt geht die nächste Runde an die nächste Person. Wähle mindestens zwei.");

/**
 * Return true and point at the field when a rotation has too few people, so
 * the dialog stays open instead of saving without it.
 */
export function rotationInvalid(body) {
  const box = body.querySelector("#bsRotation");
  const repeat = body.querySelector("#editRepeat");
  if (!box || !repeat || !repeat.value) return false;
  if (!box.querySelector("#bsRotationMode").value || rotationPeople(body).length >= 2) return false;
  box.hidden = false;
  box.querySelector("#bsRotationPeople").hidden = false;
  const hint = box.querySelector("#bsRotationHint");
  hint.hidden = false;
  hint.classList.add("bs-rotation-warn");
  hint.textContent = t("⚠️ Für den Wechsel mindestens zwei Personen wählen oder „Nicht wechseln“ einstellen.");
  if (box.scrollIntoView) box.scrollIntoView({ block: "center", behavior: "smooth" });
  const first = box.querySelector("#bsRotationPeople input:not(:checked)");
  if (first) first.focus();
  return true;
}

function rotationPeople(body) {
  return [...body.querySelectorAll("#bsRotationPeople input:checked")].map((box) => box.value);
}

/** Show the rotation only for repeating notes and warn about too few people. */
export function wireRotation(body) {
  const box = body.querySelector("#bsRotation");
  if (!box) return;
  const repeat = body.querySelector("#editRepeat");
  const mode = box.querySelector("#bsRotationMode");
  const update = () => {
    box.hidden = !(repeat && repeat.value);
    box.querySelector("#bsRotationPeople").hidden = !mode.value;
    const hint = box.querySelector("#bsRotationHint");
    hint.hidden = !mode.value;
    const tooFew = !!mode.value && rotationPeople(body).length < 2;
    hint.classList.toggle("bs-rotation-warn", tooFew);
    // The warning of a refused save stays until enough people are chosen
    if (!tooFew) hint.textContent = ROTATION_HINT();
  };
  if (repeat) repeat.addEventListener("change", update);
  mode.addEventListener("change", update);
  box.querySelector("#bsRotationPeople").addEventListener("change", update);
  update();
}

/**
 * Return what the rotation fields changed: undefined for nothing, null to end
 * the rotation, or the new {mode, people}. Check rotationInvalid first.
 */
export function readRotation(body, idea) {
  const box = body.querySelector("#bsRotation");
  if (!box) return undefined;
  const repeat = body.querySelector("#editRepeat");
  const mode = repeat && repeat.value ? box.querySelector("#bsRotationMode").value : "";
  const before = (idea && idea.rotation) || null;
  if (!mode) return before ? null : undefined;
  const people = rotationPeople(body);
  if (people.length < 2) return undefined;
  if (before && before.mode === mode && before.people.join() === people.join()) return undefined;
  return { mode, people };
}

/** Colors a rule can paint a note with. */
export const RULE_COLORS = ["#e53935", "#fb8c00", "#fdd835", "#43a047", "#00acc1", "#1e88e5", "#8e24aa", "#6d4c41", "#757575"];

/** Store a filter as plain data, so a rule can keep it. */
export function filterToRule(filter) {
  return {
    query: String(filter.query || "").trim(),
    prios: [...filter.prios],
    overdue: Boolean(filter.overdue),
    soon: Boolean(filter.soon),
    working: Boolean(filter.working),
    myDay: Boolean(filter.myDay),
    tags: [...filter.tags],
    markers: [...(filter.markers || [])],
  };
}

/** Turn the condition of a rule back into a filter. */
export function ruleFilter(rule) {
  const filter = emptyFilter();
  const when = (rule && rule.when) || {};
  filter.query = String(when.query || "");
  (when.prios || []).forEach((prio) => filter.prios.add(String(prio)));
  filter.overdue = Boolean(when.overdue);
  filter.soon = Boolean(when.soon);
  filter.working = Boolean(when.working);
  filter.myDay = Boolean(when.myDay);
  (when.tags || []).forEach((tag) => filter.tags.add(String(tag)));
  (when.markers || []).forEach((marker) => filter.markers.add(String(marker)));
  return filter;
}

/** The tabs that fold a branch out of the main map, by the id of that branch. */
export function branchTabs(tabs) {
  const byBranch = new Map();
  (tabs || []).forEach((tab) => {
    if (tab && tab.branch && tab.focus && !byBranch.has(tab.focus)) byBranch.set(tab.focus, tab);
  });
  return byBranch;
}

/** The tab that shows what the map shows now, or null for the main map. */
export function activeMapTab(tabs, activeId, category, focus) {
  const tab = (tabs || []).find((item) => item.id === activeId);
  if (!tab) return null;
  return tab.category === category && (tab.focus || null) === (focus || null) ? tab : null;
}

/** The bar of map tabs, empty while there is no tab yet. */
export function mapTabBar(tabs, active, { chores = false, choreView = false, bring = null } = {}) {
  tabs = tabs || [];
  if (!tabs.length && !chores && !bring) return "";
  const activeId = active && !choreView ? active.id : null;
  const items = tabs.map((tab) => {
    const icon = tab.icon || (tab.branch ? "↗" : "📑");
    const lock = tab.private ? `<span class="map-tab-lock" title="${escapeHtml(t("Nur für mich"))}">🔒</span>` : "";
    return `<button class="map-tab${tab.id === activeId ? " active" : ""}" data-tab="${escapeHtml(tab.id)}" role="tab" aria-selected="${tab.id === activeId}" title="${escapeHtml(t("Noch einmal tippen: Tab bearbeiten"))}"><span class="map-tab-icon">${escapeHtml(icon)}</span><span class="map-tab-name">${escapeHtml(tab.name)}</span>${lock}</button>`;
  });
  const main = !activeId && !choreView;
  const shop = bring
    ? `<button class="map-tab map-tab-bring${bring.id === activeId ? " active" : ""}" data-tab="${escapeHtml(bring.id)}" role="tab" aria-selected="${bring.id === activeId}" title="${escapeHtml(t("Die Bring!-Listen als Map"))}"><span class="map-tab-icon">🛒</span><span class="map-tab-name">Bring!</span></button>`
    : "";
  const chore = chores
    ? `<button class="map-tab map-tab-chores${choreView ? " active" : ""}" data-chore-tab="1" role="tab" aria-selected="${choreView}" title="${escapeHtml(t("Live aus ChoreOps, nur zum Ansehen"))}"><span class="map-tab-icon">🏅</span><span class="map-tab-name">ChoreOps</span></button>`
    : "";
  return `<button class="map-tab map-tab-main${main ? " active" : ""}" data-tab="" role="tab" aria-selected="${main}"><span class="map-tab-icon">🗺️</span><span class="map-tab-name">${escapeHtml(t("Map"))}</span></button>${items.join("")}${shop}${chore}<button class="map-tab map-tab-add" data-tab-add="1" data-lvl="normal" title="${escapeHtml(t("Ansicht als Tab speichern"))}" aria-label="${escapeHtml(t("Ansicht als Tab speichern"))}">＋</button>`;
}

export const MAP_TAB_CSS = `
  .map-tabs {
    display: flex;
    gap: 6px;
    padding: 6px 12px 0;
    overflow-x: auto;
    scrollbar-width: thin;
    -webkit-overflow-scrolling: touch;
  }
  .map-tabs:empty {
    display: none;
  }
  .map-tab {
    flex: 0 0 auto;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    min-height: 36px;
    max-width: 220px;
    padding: 4px 12px;
    border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.3));
    border-bottom: none;
    border-radius: 10px 10px 0 0;
    background: var(--secondary-background-color, rgba(127, 127, 127, 0.08));
    color: var(--secondary-text-color);
    font: inherit;
    font-size: 0.85rem;
    cursor: pointer;
    touch-action: manipulation;
  }
  .map-tab.active {
    background: var(--card-background-color, #fff);
    color: var(--primary-text-color);
    border-color: var(--primary-color);
    box-shadow: inset 0 3px 0 var(--primary-color);
    font-weight: 600;
  }
  .map-tab:focus-visible {
    outline: 2px solid var(--primary-color);
    outline-offset: 1px;
  }
  .map-tab-name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .map-tab-lock {
    font-size: 0.7rem;
    opacity: 0.7;
  }
  .map-tab-add {
    min-width: 36px;
    justify-content: center;
    font-weight: 600;
  }
`;

/** Keep only rules that make sense, so a broken entry cannot hurt the map. */
export function cleanRules(rules) {
  if (!Array.isArray(rules)) return [];
  return rules
    .filter((rule) => rule && typeof rule === "object" && filterActive(ruleFilter(rule)))
    .map((rule) => ({
      id: String(rule.id || Math.random().toString(36).slice(2, 10)),
      name: String(rule.name || "").slice(0, 60),
      color: RULE_COLORS.includes(rule.color) ? rule.color : "",
      icon: String(rule.icon || "").slice(0, 4),
      enabled: rule.enabled !== false,
      when: filterToRule(ruleFilter(rule)),
    }))
    .filter((rule) => rule.color || rule.icon)
    .slice(0, 20);
}

/** Return the first switched-on rule a note fits, or null. */
export function ruleFor(idea, rules, now = new Date()) {
  for (const rule of rules || []) {
    if (rule.enabled === false) continue;
    if (ideaMatches(idea, ruleFilter(rule), now)) return rule;
  }
  return null;
}

const RULES_KEY = "brainstorm_rules";

/**
 * Load the rules of the user: from the user data of Home Assistant, so
 * they follow the user to every device, with the browser as fallback.
 */
export async function loadRules(hass) {
  let rules = null;
  if (hass && hass.callWS) {
    try {
      const result = await hass.callWS({ type: "frontend/get_user_data", key: RULES_KEY });
      if (result && result.value && Array.isArray(result.value.rules)) rules = result.value.rules;
    } catch (err) {
      console.warn("[Brainstorm] Rules could not be loaded from Home Assistant:", err);
    }
  }
  if (!rules) {
    try {
      rules = JSON.parse(localStorage.getItem(RULES_KEY) || "[]");
    } catch {
      rules = [];
    }
  }
  return cleanRules(rules);
}

/** Save the rules for the user and tell the other cards on the page. */
export async function saveRules(hass, rules) {
  const clean = cleanRules(rules);
  try {
    localStorage.setItem(RULES_KEY, JSON.stringify(clean));
  } catch {}
  if (hass && hass.callWS) {
    await hass.callWS({ type: "frontend/set_user_data", key: RULES_KEY, value: { rules: clean } });
  }
  window.dispatchEvent(new CustomEvent("brainstorm-rules-changed", { detail: { rules: clean } }));
  return clean;
}

/** Describe the condition of a rule in a few words. */
export function ruleSummary(rule) {
  const when = (rule && rule.when) || {};
  const prioNames = { urgent: t("🔥 Dringend"), high: t("🔴 Hoch"), medium: t("🟡 Mittel"), low: t("🟢 Niedrig") };
  const parts = [];
  if (when.query) parts.push(`„${when.query}“`);
  if ((when.prios || []).length) parts.push(when.prios.map((prio) => prioNames[prio] || prio).join(t(" oder ")));
  if (when.overdue && when.soon) parts.push(t("überfällig oder in 7 Tagen fällig"));
  else if (when.overdue) parts.push(t("überfällig"));
  else if (when.soon) parts.push(t("in 7 Tagen fällig"));
  if (when.working) parts.push(t("in Arbeit"));
  (when.markers || []).forEach((marker) => parts.push(markerIcon(marker)));
  (when.tags || []).forEach((tag) => parts.push(`#${tag}`));
  return parts.join(" · ");
}

/** The markers a note can carry, in the order the cards show them. */
export const MARKERS = ["question", "idea", "warning", "money", "star", "flag", "check", "blocked", "waiting", "heart"];
const MARKER_ICONS = {
  question: "❓",
  idea: "💡",
  warning: "⚠️",
  money: "💰",
  star: "⭐",
  flag: "🚩",
  check: "✅",
  blocked: "⛔",
  waiting: "⏳",
  heart: "❤️",
};

/** Return the sign of a marker. */
export function markerIcon(marker) {
  return MARKER_ICONS[marker] || "";
}

/** Return the name of a marker in the language of the user. */
export function markerLabel(marker) {
  const labels = {
    question: t("Frage"),
    idea: t("Idee"),
    warning: t("Achtung"),
    money: t("Geld"),
    star: t("Stern"),
    flag: t("Flagge"),
    check: t("Haken"),
    blocked: t("Blockiert"),
    waiting: t("Wartet"),
    heart: t("Herz"),
  };
  return labels[marker] || marker;
}

/** Return the known markers of an idea. */
export function ideaMarkers(idea) {
  const markers = idea && Array.isArray(idea.markers) ? idea.markers : [];
  return MARKERS.filter((marker) => markers.includes(marker));
}

/** Return the markers of an idea as small signs, a tap on one filters by it. */
export function markerBadges(idea) {
  const markers = ideaMarkers(idea);
  if (!markers.length) return "";
  return `<span class="marker-badges">${markers
    .map((marker) => `<span class="marker-badge" data-marker="${marker}" title="${escapeHtml(markerLabel(marker))}">${markerIcon(marker)}</span>`)
    .join("")}</span>`;
}

/** Quick reactions to a note: key and sign. */
export const REACTIONS = [
  ["like", "👍"],
  ["heart", "❤️"],
  ["laugh", "😂"],
  ["important", "❗"],
];

/** The name of a reaction. */
export function reactionLabel(key) {
  return { like: t("Gefällt mir"), heart: t("Liebe ich"), laugh: t("Lustig"), important: t("Wichtig") }[key] || key;
}

/** Whether a card needs the ideas as the signed-in user sees them. */
export function needsPersonalData(attributes) {
  return Boolean(
    attributes &&
      (attributes.privacy || Object.keys(attributes.voting || {}).length || Object.keys(attributes.rounds || {}).length),
  );
}

/** All points a note got. */
export function voteTotal(idea) {
  return Object.values((idea && idea.votes) || {}).reduce((sum, n) => sum + (Number(n) || 0), 0);
}

function peopleList(idea, ids) {
  const people = (idea && idea.people) || {};
  return ids.map((id) => people[id] || t("Unbekannt")).join(", ");
}

/**
 * Return the reactions of a note as small buttons, yours highlighted;
 * a tap switches your own. With picker, a row of all four to choose from.
 */
export function reactionBadges(idea, me, picker = false) {
  const reactions = (idea && idea.reactions) || {};
  const id = escapeHtml(idea.id);
  const chips = REACTIONS.filter(([key]) => picker || (reactions[key] || []).length)
    .map(([key, icon]) => {
      const users = reactions[key] || [];
      const mine = me && users.includes(me);
      const who = users.length ? `: ${peopleList(idea, users)}` : "";
      return `<button type="button" class="bs-react${mine ? " mine" : ""}" data-react="${key}" data-id="${id}" title="${escapeHtml(reactionLabel(key) + who)}" aria-pressed="${mine ? "true" : "false"}">${icon}${users.length ? `<span>${users.length}</span>` : ""}</button>`;
    })
    .join("");
  return chips ? `<span class="bs-social${picker ? " bs-react-picker" : ""}">${chips}</span>` : "";
}

/**
 * Return the points of a note. While its list votes, with − and + for your
 * own points; a hidden round shows only yours.
 */
export function voteBadge(idea, voting, me) {
  const round = idea && idea.status !== "completed" && voting && voting[idea.category];
  const votes = (idea && idea.votes) || {};
  const total = voteTotal(idea);
  const mine = Number(votes[me] || 0);
  const id = escapeHtml(idea.id);
  const voters = Object.keys(votes);
  const who = voters.length && !idea.votes_hidden
    ? voters.map((v) => `${peopleList(idea, [v])} ${votes[v]}`).join(", ")
    : "";
  if (round) {
    const left = Math.max(0, (round.votes || 0) - (round.used || 0));
    const shown = idea.votes_hidden ? mine : total;
    const title = `${t("Noch {left} von {total} Stimmen", { left, total: round.votes || 0 })}${who ? ` · ${who}` : ""}`;
    return `<span class="bs-social bs-vote live${mine ? " mine" : ""}" title="${escapeHtml(title)}">`
      + `<button type="button" class="bs-vote-btn" data-vote="-1" data-id="${id}" ${mine ? "" : "disabled"} aria-label="${escapeHtml(t("Stimme zurücknehmen"))}">−</button>`
      + `<span class="bs-vote-count">● ${shown}${idea.votes_hidden ? "🙈" : ""}</span>`
      + `<button type="button" class="bs-vote-btn" data-vote="1" data-id="${id}" ${left ? "" : "disabled"} aria-label="${escapeHtml(t("Stimme geben"))}">+</button></span>`;
  }
  if (!total) return "";
  return `<span class="bs-social bs-vote${mine ? " mine" : ""}" title="${escapeHtml(`${t("{points} Stimmen", { points: total })}${who ? ` · ${who}` : ""}`)}"><span class="bs-vote-count">● ${total}</span></span>`;
}

/** Styles of reactions and points, the same in both cards. */
export const SOCIAL_CSS = `
  .chore-badge.chore-claimed {
    background: rgba(245, 158, 11, 0.18);
  }
  .chore-badge.chore-done {
    background: rgba(34, 197, 94, 0.18);
  }
  .bs-chore-points {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;
  }
  .bs-chore-chip {
    min-width: 44px;
    min-height: 40px;
    border-radius: 20px;
    border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.3));
    background: var(--secondary-background-color, transparent);
    color: var(--primary-text-color);
    font: inherit;
    font-weight: 600;
    cursor: pointer;
  }
  .bs-chore-chip.selected {
    background: var(--primary-color);
    border-color: var(--primary-color);
    color: var(--text-primary-color, #fff);
  }
  .bs-chore-points .bs-chore-custom {
    width: 96px;
    flex: 0 0 auto;
  }
  .bs-social { display: inline-flex; align-items: center; gap: 3px; flex-wrap: wrap; vertical-align: middle; }
  .bs-react, .bs-vote-btn {
    min-width: 28px; min-height: 26px; padding: 0 6px; display: inline-flex; align-items: center; justify-content: center; gap: 3px;
    border-radius: 13px; cursor: pointer; font: inherit; font-size: 0.78rem; line-height: 1;
    color: var(--primary-text-color, #212121);
    background: color-mix(in srgb, var(--secondary-text-color, #727272) 10%, transparent);
    border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.25));
  }
  .bs-react span { font-size: 0.72rem; font-weight: 600; }
  .bs-react.mine {
    border-color: var(--primary-color, #03a9f4);
    background: color-mix(in srgb, var(--primary-color, #03a9f4) 16%, transparent);
  }
  .bs-react-picker .bs-react { min-width: 40px; min-height: 36px; font-size: 1rem; }
  .bs-vote { padding: 0 2px; border-radius: 13px; }
  .bs-vote-count { font-size: 0.76rem; font-weight: 700; color: var(--primary-color, #03a9f4); padding: 0 4px; white-space: nowrap; }
  .bs-vote.live { background: color-mix(in srgb, var(--primary-color, #03a9f4) 10%, transparent); border: 1px solid color-mix(in srgb, var(--primary-color, #03a9f4) 40%, transparent); }
  .bs-vote.mine .bs-vote-count { text-decoration: underline; text-underline-offset: 2px; }
  .bs-vote-btn { min-width: 26px; font-weight: 700; font-size: 0.9rem; }
  .bs-vote-btn:disabled { opacity: 0.35; cursor: default; }
  @media (pointer: coarse) { .bs-react, .bs-vote-btn { min-width: 34px; min-height: 32px; } }
  .bs-comment {
    min-height: 26px; padding: 0 7px; display: inline-flex; align-items: center; gap: 3px; border-radius: 13px; cursor: pointer;
    font: inherit; font-size: 0.76rem; font-weight: 600; line-height: 1; color: var(--primary-text-color, #212121);
    background: color-mix(in srgb, var(--secondary-text-color, #727272) 10%, transparent);
    border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.25));
  }
  @media (pointer: coarse) { .bs-comment { min-height: 32px; } }
  .bs-comments { display: flex; flex-direction: column; gap: 10px; max-height: min(45vh, 380px); overflow-y: auto; margin: 4px 0 10px; }
  .bs-comments-empty { color: var(--secondary-text-color, #727272); font-size: 0.85rem; padding: 6px 0; }
  .bs-c { display: flex; gap: 8px; align-items: flex-start; }
  .bs-c-avatar {
    flex: 0 0 30px; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
    background: color-mix(in srgb, var(--primary-color, #03a9f4) 18%, transparent); color: var(--primary-color, #03a9f4);
    font-weight: 700; font-size: 0.8rem; background-size: cover; background-position: center;
  }
  .bs-c-body { flex: 1 1 auto; min-width: 0; padding: 6px 10px; border-radius: 12px; background: color-mix(in srgb, var(--secondary-text-color, #727272) 9%, transparent); }
  .bs-c.mine .bs-c-body { background: color-mix(in srgb, var(--primary-color, #03a9f4) 12%, transparent); }
  .bs-c-head { display: flex; gap: 8px; align-items: baseline; font-size: 0.75rem; color: var(--secondary-text-color, #727272); }
  .bs-c-head b { color: var(--primary-text-color, #212121); font-size: 0.8rem; }
  .bs-c-text { font-size: 0.9rem; overflow-wrap: anywhere; color: var(--primary-text-color, #212121); }
  .bs-c-text .bs-mention { color: var(--primary-color, #03a9f4); font-weight: 600; }
  .bs-c-del { margin-left: auto; min-width: 28px; min-height: 28px; border: none; background: none; cursor: pointer; color: var(--secondary-text-color, #727272); font: inherit; border-radius: 14px; }
  .bs-c-del:hover { color: var(--error-color, #db4437); }
  .bs-trash { display: flex; flex-direction: column; gap: 6px; max-height: min(50vh, 420px); overflow-y: auto; margin: 6px 0 10px; }
  .bs-trash-item {
    display: flex; align-items: center; gap: 6px; padding: 6px 8px; border-radius: 10px;
    background: color-mix(in srgb, var(--secondary-text-color, #727272) 8%, transparent);
  }
  .bs-trash-main { flex: 1 1 auto; min-width: 0; }
  .bs-trash-text { font-size: 0.9rem; color: var(--primary-text-color, #212121); overflow-wrap: anywhere; }
  .bs-trash-meta { font-size: 0.75rem; color: var(--secondary-text-color, #727272); }
  .bs-trash-btn {
    flex: 0 0 auto; min-width: 36px; min-height: 36px; border-radius: 18px; cursor: pointer; font: inherit; font-size: 0.95rem;
    border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.25)); background: none; color: var(--primary-text-color, #212121);
  }
  .bs-trash-btn:hover { border-color: var(--primary-color, #03a9f4); }
  .bs-trash-del:hover { border-color: var(--error-color, #db4437); color: var(--error-color, #db4437); }
  .bs-trash-btn:disabled { opacity: 0.4; cursor: default; }
  .bs-rotation[hidden], .bs-rotation [hidden] { display: none; }
  .bs-rotation-people { display: flex; flex-wrap: wrap; gap: 6px; margin: 6px 0 2px; }
  .bs-rotation-person { display: inline-flex; align-items: center; gap: 6px; min-height: 36px; padding: 2px 10px; border: 1px solid var(--divider-color, #ccc); border-radius: 18px; cursor: pointer; font-size: 0.9rem; color: var(--primary-text-color); }
  .bs-rotation-warn { color: var(--error-color, #db4437); }
  .bs-trash-notice { font-size: 0.82rem; color: var(--success-color, #43a047); margin-top: 4px; }
  .bs-speech-text { width: 100%; min-height: 110px; box-sizing: border-box; resize: vertical; font: inherit; }
  .bs-speech-row { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; padding: 8px 0; border-bottom: 1px solid var(--divider-color, rgba(127, 127, 127, 0.2)); }
  .bs-speech-row input[type="checkbox"] { width: 22px; height: 22px; flex: 0 0 auto; }
  .bs-speech-row .bs-speech-task { flex: 1 1 200px; min-width: 0; }
  .bs-speech-row .bs-speech-meta { display: flex; flex-wrap: wrap; gap: 6px; flex: 1 1 100%; padding-left: 28px; }
  .bs-speech-row .bs-speech-meta > * { flex: 1 1 110px; min-width: 0; min-height: 36px; }
  .bs-speech-row.off .bs-speech-task, .bs-speech-row.off .bs-speech-meta { opacity: 0.45; }
  .habit-badge { cursor: pointer; white-space: nowrap; }
  .habit-badge.habit-done { color: var(--success-color, #43a047); }
  .bs-habit-stats { display: flex; flex-wrap: wrap; gap: 8px 16px; margin: 4px 0 10px; font-size: 0.95rem; color: var(--primary-text-color); }
  .bs-habit-grid { display: grid; grid-template-rows: repeat(7, 1fr); grid-auto-flow: column; grid-auto-columns: 1fr; gap: 3px; max-width: 100%; }
  .bs-habit-cell { aspect-ratio: 1; min-width: 0; min-height: 14px; padding: 0; border: none; border-radius: 3px; background: var(--divider-color, #ddd); cursor: pointer; }
  .bs-habit-cell.on { background: var(--success-color, #43a047); }
  .bs-habit-cell.today { outline: 2px solid var(--primary-color); outline-offset: 1px; }
  .bs-habit-cell:disabled { visibility: hidden; cursor: default; }
  .bs-habit-cell:focus-visible { outline: 2px solid var(--primary-text-color); }
`;

/** A small flame with the streak of a habit, green once today is done. */
export function habitBadge(idea) {
  const habit = idea && idea.habit;
  if (!habit) return "";
  const title = t("Gewohnheit: {streak} Tage in Folge, beste Serie {best}. Antippen zeigt den Kalender.", { streak: habit.streak, best: habit.best });
  return `<span class="due-badge habit-badge${habit.today ? " habit-done" : ""}" data-habit="${escapeHtml(idea.id)}" role="button" tabindex="0" title="${escapeHtml(title)}">🔥 ${Number(habit.streak) || 0}</span>`;
}

/** The ChoreOps person for a Brainstorm person, by name or a unique first name. */
export function matchChoreUser(name, users) {
  const wanted = String(name || "").replace(/\s+/g, " ").trim().toLowerCase();
  if (!wanted || !Array.isArray(users)) return null;
  const exact = users.find((user) => user.toLowerCase() === wanted);
  if (exact) return exact;
  const first = wanted.split(" ")[0];
  const matches = users.filter((user) => user.toLowerCase().split(" ")[0] === first);
  return matches.length === 1 ? matches[0] : null;
}

/** 🏅 at a note handed over to ChoreOps: open, reported done, approved. */
export function choreopsBadge(idea) {
  const chore = idea && idea.choreops;
  if (!chore) return "";
  const user = chore.done_by || chore.user || "";
  if (chore.status === "approved") {
    const points = chore.points_earned ?? chore.points ?? 0;
    return `<span class="due-badge chore-badge chore-done" title="${escapeHtml(t("Von ChoreOps freigegeben: {points} Punkte für {user}", { points, user }))}">🏅 +${escapeHtml(points)}</span>`;
  }
  if (chore.status === "claimed") {
    return `<span class="due-badge chore-badge chore-claimed" title="${escapeHtml(t("{user} hat es als erledigt gemeldet, wartet auf Freigabe in ChoreOps", { user }))}">🏅 ✋ ${escapeHtml(chore.points ?? 0)}</span>`;
  }
  return `<span class="due-badge chore-badge" title="${escapeHtml(t("Bei ChoreOps für {user}: {points} Punkte", { user, points: chore.points ?? 0 }))}">🏅 ${escapeHtml(chore.points ?? 0)}</span>`;
}

/** The badge of a note that was sent to a Bring list: how much is still to buy. */
export function bringBadge(idea) {
  const sent = idea && idea.bring_sent;
  if (!sent || !sent.total) return "";
  const name = sent.name || "Bring!";
  if (!sent.open) {
    return `<span class="due-badge bring-badge bring-done" title="${escapeHtml(t("Auf der Bring!-Liste {name}: alles gekauft", { name }))}">🛒 ✓</span>`;
  }
  return `<span class="due-badge bring-badge" title="${escapeHtml(t("Auf der Bring!-Liste {name}: {open} von {total} noch offen", { name, open: sent.open, total: sent.total }))}">🛒 ${escapeHtml(sent.open)}/${escapeHtml(sent.total)}</span>`;
}

/** Whether the menu offers sending a note to Bring: any open note outside the Bring category. */
export function canSendToBring(idea, bring) {
  return Boolean(bring && Array.isArray(bring.lists) && bring.lists.length && idea && !idea.bring_list && idea.category !== bring.category && idea.status === "active");
}

export const BRING_TAB_ID = "__bring__";

/** The tab that opens the Bring category on the map, while Bring is switched on. */
export function bringTab(bring) {
  if (!bring || !bring.category) return null;
  return { id: BRING_TAB_ID, name: "Bring!", icon: "🛒", category: bring.category, focus: null, virtual: true };
}

/**
 * Fill a dialog body with sending a note to Bring: a list, and the note
 * itself or a choice of its open subtasks as items.
 */
export function renderBringSend(body, { hass, idea, bring, children = [], close, done, prefix = "dialog" }) {
  const c = (names) => names.split(" ").map((n) => `${prefix}-${n}`).join(" ");
  const lists = bring.lists || [];
  const open = (children || []).filter((child) => child && child.status === "active");
  const sentTo = idea.bring_sent && idea.bring_sent.entity;
  let list = [sentTo, bring.default].find((entity) => lists.some((item) => item.entity === entity)) || (lists[0] && lists[0].entity);
  let mode = open.length ? "items" : "note";
  const picked = new Set(open.map((child) => child.id));
  let busy = false;
  const draw = (error = "") => {
    if (!body.isConnected) return;
    const choice = open.length
      ? `<div class="${c("label")}">${t("Was kommt auf die Liste?")}</div>
        <div class="bs-bring-modes" role="radiogroup">
          <label class="bs-bring-mode"><input type="radio" name="bsBringMode" value="items"${mode === "items" ? " checked" : ""}> ${t("Unteraufgaben ({count})", { count: open.length })}</label>
          <label class="bs-bring-mode"><input type="radio" name="bsBringMode" value="note"${mode === "note" ? " checked" : ""}> ${t("Diese Notiz als ein Artikel")}</label>
        </div>
        <div class="bs-bring-items" style="display: ${mode === "items" ? "flex" : "none"};">
          ${open.map((child) => `<label class="bs-bring-item"><input type="checkbox" data-bring-item="${escapeHtml(child.id)}"${picked.has(child.id) ? " checked" : ""}> <span>${formatText(child.text || "")}</span></label>`).join("")}
        </div>`
      : "";
    body.innerHTML = `
      <div class="${c("hint")}">${formatText(idea.text || "")}</div>
      <div class="${c("label")}">${t("Liste")}</div>
      <select class="${c("input")}" id="bsBringList">${lists.map((item) => `<option value="${escapeHtml(item.entity)}"${item.entity === list ? " selected" : ""}>${escapeHtml(item.name || item.entity)}</option>`).join("")}</select>
      ${choice}
      <div class="${c("hint")}">${t("Was auf der Liste schon offen ist, kommt nicht doppelt dazu. Gekaufte Artikel werden hier abgehakt.")}</div>
      <div class="${c("error")}" style="display: ${error ? "flex" : "none"};">${escapeHtml(error)}</div>
      <div class="${c("footer")}">
        <button class="${c("btn btn-secondary")}" id="bsBringCancel">${t("Abbrechen")}</button>
        <button class="${c("btn btn-primary")}" id="bsBringSend"${busy ? " disabled" : ""}>${t("🛒 Senden")}</button>
      </div>`;
    body.querySelector("#bsBringList").addEventListener("change", (e) => {
      list = e.target.value;
    });
    body.querySelectorAll('input[name="bsBringMode"]').forEach((radio) => {
      radio.addEventListener("change", () => {
        mode = radio.value;
        const box = body.querySelector(".bs-bring-items");
        if (box) box.style.display = mode === "items" ? "flex" : "none";
      });
    });
    body.querySelectorAll("[data-bring-item]").forEach((box) => {
      box.addEventListener("change", () => {
        if (box.checked) picked.add(box.dataset.bringItem);
        else picked.delete(box.dataset.bringItem);
      });
    });
    body.querySelector("#bsBringCancel").addEventListener("click", () => close());
    body.querySelector("#bsBringSend").addEventListener("click", async () => {
      if (busy) return;
      const data = { id: idea.id, list };
      if (mode === "items") {
        data.items = open.map((child) => child.id).filter((id) => picked.has(id));
        if (!data.items.length) {
          draw(t("Bitte mindestens eine Unteraufgabe auswählen."));
          return;
        }
      }
      busy = true;
      try {
        const result = await hass.callService("brainstorm", "send_to_bring", data, undefined, true, true);
        close();
        if (done) done((result && result.response) || {});
      } catch (err) {
        busy = false;
        draw((err && err.message) || t("Das ging nicht."));
      }
    });
  };
  draw();
}

/** What the toast says after sending to Bring. */
export function bringSentText(response, bring) {
  const item = ((bring && bring.lists) || []).find((entry) => entry.entity === response.entity_id);
  const name = (item && item.name) || "Bring!";
  const added = Number(response.added) || 0;
  const skipped = Array.isArray(response.skipped) ? response.skipped.length : 0;
  if (!added) return t("Steht schon alles auf {name}.", { name });
  const text = added === 1 ? t("1 Artikel auf {name}", { name }) : t("{count} Artikel auf {name}", { count: added, name });
  return skipped ? `${text} · ${t("{count} war schon drauf", { count: skipped })}` : text;
}

export const BRING_SEND_CSS = `
  .bring-badge.bring-done {
    opacity: 0.7;
  }
  .bs-bring-modes {
    display: flex;
    flex-wrap: wrap;
    gap: 6px 16px;
    margin-bottom: 8px;
  }
  .bs-bring-mode,
  .bs-bring-item {
    display: flex;
    align-items: center;
    gap: 8px;
    min-height: 36px;
    cursor: pointer;
  }
  .bs-bring-items {
    flex-direction: column;
    gap: 2px;
    max-height: 40vh;
    overflow: auto;
    padding: 4px 8px;
    border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.3));
    border-radius: 8px;
    margin-bottom: 8px;
  }
  .bs-bring-item input,
  .bs-bring-mode input {
    width: 18px;
    height: 18px;
    flex: 0 0 auto;
  }
`;

/** Whether the menu offers the hand-over for a note. */
export function canHandOver(idea, choreops) {
  return Boolean(choreops && Array.isArray(choreops.users) && choreops.users.length && idea && !idea.choreops && idea.status !== "completed");
}

// What the status sensors of ChoreOps show, sorted by what needs attention first
const CHORE_DONE_STATES = new Set(["approved", "completed", "approved_in_part", "completed_in_part"]);
const CHORE_CLAIMED_STATES = new Set(["claimed", "claimed_in_part"]);
const CHORE_NAME_MAX = 80;

function choreRank(chore) {
  if (chore.done) return 3;
  if (chore.overdue) return 0;
  return chore.claimed ? 1 : 2;
}

/** The people of ChoreOps with their points and chores, read live from its sensors. */
export function choreMapData(states, ideas = []) {
  const people = new Map();
  const person = (name) => {
    if (!people.has(name)) people.set(name, { name, points: null, chores: [] });
    return people.get(name);
  };
  const squeeze = (text) => String(text ?? "").split(/\s+/).filter(Boolean).join(" ");
  for (const [entityId, state] of Object.entries(states || {})) {
    const attrs = state && state.attributes;
    if (!attrs || !entityId.startsWith("sensor.") || typeof attrs.user_name !== "string") continue;
    if (attrs.purpose === "purpose_points") {
      const points = Number(state.state);
      person(attrs.user_name).points = Number.isFinite(points) ? points : null;
    } else if (attrs.purpose === "purpose_chore_status" && attrs.chore_name) {
      const name = squeeze(attrs.chore_name);
      const user = attrs.user_name;
      // A chore Brainstorm handed over keeps the text of the note
      const idea = (ideas || []).find((item) => item && item.choreops && item.choreops.user === user && squeeze(item.text).slice(0, CHORE_NAME_MAX) === name);
      const labels = Array.isArray(attrs.labels) ? attrs.labels : [];
      const points = Number(attrs.default_points);
      const earned = Number(attrs.chore_points_earned);
      person(user).chores.push({
        entity: entityId,
        name,
        state: String(state.state),
        done: CHORE_DONE_STATES.has(state.state),
        claimed: CHORE_CLAIMED_STATES.has(state.state),
        overdue: state.state === "overdue",
        points: Number.isFinite(points) ? points : 0,
        earned: Number.isFinite(earned) ? earned : 0,
        due: typeof attrs.due_date === "string" ? attrs.due_date : null,
        brainstorm: Boolean(idea) || labels.includes("brainstorm"),
        idea: idea ? idea.id : null,
      });
    }
  }
  const list = [...people.values()].sort((a, b) => a.name.localeCompare(b.name));
  for (const item of list) {
    item.chores.sort((a, b) => choreRank(a) - choreRank(b) || String(a.due || "~").localeCompare(String(b.due || "~")) || a.name.localeCompare(b.name));
  }
  return list;
}

function formatPoints(value) {
  return Number.isInteger(value) ? String(value) : String(Math.round(value * 10) / 10);
}

function choreState(chore) {
  if (chore.done) return ["✅", t("erledigt"), "done"];
  if (chore.overdue) return ["⏰", t("überfällig"), "overdue"];
  if (chore.claimed) return ["✋", t("gemeldet, wartet auf Freigabe"), "claimed"];
  return ["○", t("offen"), "open"];
}

/** The read-only map of ChoreOps: a branch per person with the chores and points. */
export function renderChoreMap(people, { showDone = false } = {}) {
  if (!people || !people.length) {
    return `<div class="chore-map-empty">🏅 ${escapeHtml(t("ChoreOps zeigt noch keine Personen."))}</div>`;
  }
  const all = people.flatMap((item) => item.chores);
  const count = (test) => all.filter(test).length;
  const doneCount = count((c) => c.done);
  const summary = [
    t("{count} offen", { count: count((c) => !c.done && !c.claimed) }),
    t("{count} gemeldet", { count: count((c) => c.claimed) }),
    t("{count} erledigt", { count: doneCount }),
  ].join(" · ");
  const branches = people.map((item, index) => {
    const chores = item.chores.filter((c) => showDone || !c.done);
    const rows = chores.map((chore) => {
      const [icon, label, cls] = choreState(chore);
      const due = chore.due && !chore.done ? new Date(chore.due) : null;
      const date = due && !Number.isNaN(due.getTime()) ? shortDate(due) : "";
      const points = chore.done && chore.earned ? `+${formatPoints(chore.earned)}` : formatPoints(chore.points);
      const meta = [t("{points} P", { points }), date].filter(Boolean).join(" · ");
      const from = chore.brainstorm ? `<span class="chore-from" title="${escapeHtml(t("Aus Brainstorm übergeben"))}">💡</span>` : "";
      const title = [chore.name, label, date && t("fällig {date}", { date })].filter(Boolean).join(" – ");
      return `<li class="chore-item chore-is-${cls}" title="${escapeHtml(title)}"><span class="chore-state" aria-label="${escapeHtml(label)}">${icon}</span><span class="chore-name">${escapeHtml(chore.name)}</span>${from}<span class="chore-meta">${escapeHtml(meta)}</span></li>`;
    });
    const hidden = item.chores.length - chores.length;
    let empty = "";
    if (!item.chores.length) empty = `<li class="chore-none">${escapeHtml(t("Keine Aufgaben"))}</li>`;
    else if (!chores.length) empty = `<li class="chore-none">${escapeHtml(t("Alles erledigt 🎉"))}</li>`;
    const points = item.points === null ? "" : `<span class="chore-points" title="${escapeHtml(t("Punktestand"))}">⭐ ${escapeHtml(formatPoints(item.points))}</span>`;
    const open = item.chores.filter((c) => !c.done).length;
    const more = hidden ? `<div class="chore-hidden">${escapeHtml(t("+ {count} erledigt", { count: hidden }))}</div>` : "";
    return `<section class="chore-person" style="--chore-hue: ${(index * 137 + 200) % 360}"><header class="chore-person-head"><span class="chore-avatar" aria-hidden="true">${escapeHtml(item.name.charAt(0).toUpperCase())}</span><span class="chore-person-name">${escapeHtml(item.name)}</span>${points}<span class="chore-open" title="${escapeHtml(t("Noch offen"))}">${open}</span></header><ul class="chore-list">${rows.join("")}${empty}</ul>${more}</section>`;
  });
  const toggle = doneCount
    ? `<button class="chore-toggle" data-chore-done aria-pressed="${showDone}">${escapeHtml(showDone ? t("Erledigte ausblenden") : t("Erledigte zeigen"))}</button>`
    : "";
  return `<div class="chore-root"><span class="chore-root-icon" aria-hidden="true">🏅</span><span class="chore-root-name">ChoreOps</span><span class="chore-root-sum">${escapeHtml(summary)}</span>${toggle}</div><div class="chore-branches">${branches.join("")}</div><p class="chore-note">${escapeHtml(t("Nur zum Ansehen: Freigeben und Punkte vergeben passiert in ChoreOps."))}</p>`;
}

export const CHORE_MAP_CSS = `
  .chore-map {
    display: none;
    flex: 1 1 auto;
    min-height: 0;
    overflow: auto;
    padding: 14px 12px 16px;
    box-sizing: border-box;
  }
  .chore-root {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
    gap: 6px 10px;
    width: fit-content;
    max-width: 100%;
    margin: 0 auto;
    padding: 10px 18px;
    border-radius: 24px;
    background: var(--primary-color, #03a9f4);
    color: var(--text-primary-color, #fff);
    box-sizing: border-box;
  }
  .chore-root-name {
    font-weight: 700;
    font-size: 1.05rem;
  }
  .chore-root-sum {
    font-size: 0.82rem;
    opacity: 0.9;
  }
  .chore-toggle {
    min-height: 32px;
    padding: 2px 12px;
    border: 1px solid currentColor;
    border-radius: 999px;
    background: transparent;
    color: inherit;
    font: inherit;
    font-size: 0.8rem;
    cursor: pointer;
  }
  .chore-branches {
    position: relative;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 14px;
    margin-top: 22px;
  }
  .chore-branches::before {
    content: "";
    position: absolute;
    top: -22px;
    left: 50%;
    height: 22px;
    border-left: 2px solid var(--divider-color, rgba(127, 127, 127, 0.4));
  }
  .chore-person {
    --chore-color: hsl(var(--chore-hue), 60%, 50%);
    border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.25));
    border-top: 4px solid var(--chore-color);
    border-radius: 12px;
    background: var(--secondary-background-color, rgba(127, 127, 127, 0.06));
    padding: 8px 10px 10px;
    min-width: 0;
  }
  .chore-person-head {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
  }
  .chore-avatar {
    flex: 0 0 auto;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: var(--chore-color);
    color: #fff;
    font-weight: 700;
  }
  .chore-person-name {
    flex: 1 1 auto;
    min-width: 0;
    font-weight: 600;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .chore-points {
    font-size: 0.85rem;
    font-weight: 600;
  }
  .chore-open {
    min-width: 22px;
    padding: 1px 6px;
    border-radius: 999px;
    background: var(--chore-color);
    color: #fff;
    font-size: 0.75rem;
    text-align: center;
  }
  .chore-list {
    list-style: none;
    margin: 0;
    padding: 0 0 0 10px;
    border-left: 2px solid var(--chore-color);
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .chore-item {
    display: flex;
    align-items: center;
    gap: 6px;
    min-height: 34px;
    padding: 4px 8px;
    border-radius: 8px;
    background: var(--card-background-color, #fff);
    font-size: 0.88rem;
  }
  .chore-name {
    flex: 1 1 auto;
    min-width: 0;
    overflow-wrap: anywhere;
  }
  .chore-meta {
    flex: 0 0 auto;
    color: var(--secondary-text-color);
    font-size: 0.75rem;
  }
  .chore-is-overdue {
    box-shadow: inset 3px 0 0 var(--error-color, #db4437);
  }
  .chore-is-claimed {
    box-shadow: inset 3px 0 0 var(--warning-color, #ffa600);
  }
  .chore-is-done {
    opacity: 0.6;
  }
  .chore-is-done .chore-name {
    text-decoration: line-through;
  }
  .chore-none,
  .chore-hidden {
    color: var(--secondary-text-color);
    font-size: 0.8rem;
    padding: 4px 2px;
  }
  .chore-note {
    margin: 14px 0 0;
    text-align: center;
    color: var(--secondary-text-color);
    font-size: 0.78rem;
  }
  .chore-map-empty {
    padding: 40px 12px;
    text-align: center;
    color: var(--secondary-text-color);
  }
`;

const CHORE_POINTS = [5, 10, 20, 50];

/** The dialog that hands a note to ChoreOps: who does it and for how many points. */
export function renderChoreHandover(body, { hass, idea, users, points: preset = 10, close, done, prefix = "dialog" }) {
  const c = (names) => names.split(" ").map((n) => `${prefix}-${n}`).join(" ");
  let user = matchChoreUser(idea.assignee, users) || users[0];
  let points = typeof preset === "number" && Number.isFinite(preset) ? preset : 10;
  let busy = false;
  const draw = (error = "") => {
    if (!body.isConnected) return;
    body.innerHTML = `
      <div class="${c("hint")}">${formatText(idea.text || "")}</div>
      <div class="${c("label")}">${t("Wer erledigt es?")}</div>
      <select class="${c("input")}" id="bsChoreUser">${users.map((name) => `<option value="${escapeHtml(name)}"${name === user ? " selected" : ""}>${escapeHtml(name)}</option>`).join("")}</select>
      <div class="${c("label")}">${t("Punkte")}</div>
      <div class="bs-chore-points">
        ${CHORE_POINTS.map((n) => `<button type="button" class="bs-chore-chip${n === points ? " selected" : ""}" data-points="${n}">${n}</button>`).join("")}
        <input type="number" class="${c("input")} bs-chore-custom" id="bsChorePoints" min="0" max="10000" inputmode="numeric" value="${points}" aria-label="${escapeHtml(t("Punkte"))}">
      </div>
      <div class="${c("hint")}">${t("Die Person meldet in ChoreOps „erledigt“. Sobald ein Elternteil freigibt, gibt es die Punkte und die Notiz wird hier abgehakt.")}</div>
      <div class="${c("error")}" style="display: ${error ? "flex" : "none"};">${escapeHtml(error)}</div>
      <div class="${c("footer")}">
        <button class="${c("btn btn-secondary")}" id="bsChoreCancel">${t("Abbrechen")}</button>
        <button class="${c("btn btn-primary")}" id="bsChoreSend"${busy ? " disabled" : ""}>${t("🏅 Übergeben")}</button>
      </div>`;
    const input = body.querySelector("#bsChorePoints");
    body.querySelector("#bsChoreUser").addEventListener("change", (e) => {
      user = e.target.value;
    });
    body.querySelectorAll("[data-points]").forEach((chip) => {
      chip.addEventListener("click", () => {
        points = Number(chip.dataset.points);
        input.value = String(points);
        body.querySelectorAll("[data-points]").forEach((other) => other.classList.toggle("selected", other === chip));
      });
    });
    input.addEventListener("input", () => {
      points = Math.max(0, Math.min(10000, Math.round(Number(input.value) || 0)));
      body.querySelectorAll("[data-points]").forEach((chip) => chip.classList.toggle("selected", Number(chip.dataset.points) === points));
    });
    body.querySelector("#bsChoreCancel").addEventListener("click", () => close());
    body.querySelector("#bsChoreSend").addEventListener("click", async () => {
      if (busy) return;
      busy = true;
      try {
        await hass.callService("brainstorm", "send_to_choreops", { id: idea.id, points, user });
        close();
        if (done) done(user, points);
      } catch (err) {
        busy = false;
        draw((err && err.message) || t("Das ging nicht."));
      }
    });
  };
  draw();
}

/** The switch in the edit dialogs that turns a note into a daily habit. */
export function habitField(idea, prefix = "dialog") {
  return `<label class="${prefix}-label bs-habit-switch" style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
    <input type="checkbox" id="editHabit"${idea && idea.habit ? " checked" : ""}> ${t("🔥 Gewohnheit: jeden Tag abhaken, mit Serie")}
  </label>`;
}

/** Return true or false when the habit switch changed, undefined if not. */
export function readHabit(body, idea) {
  const box = body.querySelector("#editHabit");
  if (!box) return undefined;
  return box.checked === Boolean(idea && idea.habit) ? undefined : box.checked;
}

const isoDay = (date) => `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;

/**
 * Fill a dialog body with the calendar of a habit: the streak, the best one,
 * all days done, and the last 18 weeks to tick off or take back day by day.
 */
export function renderHabit(body, { hass, idea, close, prefix = "dialog", today = new Date() }) {
  const c = (names) => names.split(" ").map((n) => `${prefix}-${n}`).join(" ");
  let data = idea.habit || { days: [], streak: 0, best: 0, total: 0, today: false };
  let busy = false;
  const first = new Date(today.getFullYear(), today.getMonth(), today.getDate());
  // Weeks run from Monday, the last column is the current week
  first.setDate(first.getDate() + (6 - ((first.getDay() + 6) % 7)) - 18 * 7 + 1);
  const todayIso = isoDay(today);
  const draw = (error = "") => {
    if (!body.isConnected) return;
    const done = new Set(data.days || []);
    const cells = [];
    for (let i = 0; i < 18 * 7; i += 1) {
      const day = new Date(first.getFullYear(), first.getMonth(), first.getDate() + i);
      const iso = isoDay(day);
      const label = day.toLocaleDateString(dateLocale(), { weekday: "short", day: "numeric", month: "short" });
      const on = done.has(iso);
      cells.push(`<button type="button" class="bs-habit-cell${on ? " on" : ""}${iso === todayIso ? " today" : ""}" data-day="${iso}" aria-pressed="${on}" title="${escapeHtml(label)}" aria-label="${escapeHtml(label)}"${iso > todayIso ? " disabled" : ""}></button>`);
    }
    body.innerHTML = `
      <div class="${c("hint")}">${formatText(idea.text || "")}</div>
      <div class="bs-habit-stats">
        <span>🔥 ${escapeHtml(t("Serie: {count}", { count: data.streak }))}</span>
        <span>🏆 ${escapeHtml(t("Beste Serie: {count}", { count: data.best }))}</span>
        <span>✅ ${escapeHtml(t("Erledigt gesamt: {count}", { count: data.total }))}</span>
      </div>
      <div class="bs-habit-grid">${cells.join("")}</div>
      <div class="${c("hint")}">${t("Tippe auf einen Tag, um ihn nachzutragen oder zu entfernen.")}</div>
      <div class="${c("error")}" style="display: ${error ? "flex" : "none"};">${escapeHtml(error)}</div>
      <div class="${c("footer")}"><button class="${c("btn btn-primary")}" id="bsHabitClose">${t("Schließen")}</button></div>
    `;
    body.querySelector("#bsHabitClose").addEventListener("click", close);
    body.querySelectorAll(".bs-habit-cell").forEach((cell) =>
      cell.addEventListener("click", async () => {
        if (busy || cell.disabled) return;
        busy = true;
        const day = cell.getAttribute("data-day");
        try {
          await hass.callService("brainstorm", "update_idea", { id: idea.id, habit_done: !done.has(day), habit_date: day });
          data = await hass.callWS({ type: "brainstorm/habit", idea_id: idea.id });
          busy = false;
          draw();
        } catch (err) {
          busy = false;
          draw((err && err.message) || t("Das hat nicht geklappt."));
        }
      })
    );
  };
  draw();
}

/**
 * Fill a dialog body for free speech: what was said or typed goes to the AI,
 * which splits it into notes with due date and person. The person checks and
 * changes the list before anything is created.
 */
export function renderSpeech(body, { hass, category = null, text = "", close, created = () => {}, prefix = "dialog", language }) {
  const c = (names) => names.split(" ").map((n) => `${prefix}-${n}`).join(" ");
  const people = personsOf(hass);
  let draft = text;
  const ask = (error = "") => {
    body.innerHTML = `
      <div class="${c("hint")}">${t("Einfach drauflos reden oder tippen, auch mehrere Aufgaben auf einmal, mit Termin und wer sie übernimmt. Die KI macht daraus einzelne Notizen, die du vor dem Anlegen prüfst.")}</div>
      <textarea class="${c("input")} bs-speech-text" id="bsSpeechText" placeholder="${escapeHtml(t("z. B. Morgen um zehn den Klempner anrufen, Anna kauft am Freitag Milch und dann noch den Keller aufräumen"))}">${escapeHtml(draft)}</textarea>
      <div class="${c("error")}" style="display: ${error ? "flex" : "none"};">${escapeHtml(error)}</div>
      <div class="${c("footer")}">
        <button class="${c("btn btn-secondary")}" id="bsSpeechCancel">${t("Abbrechen")}</button>
        <button class="${c("btn btn-primary")}" id="bsSpeechSplit">${t("✨ Zerlegen")}</button>
      </div>`;
    const area = body.querySelector("#bsSpeechText");
    area.focus();
    body.querySelector("#bsSpeechCancel").addEventListener("click", close);
    body.querySelector("#bsSpeechSplit").addEventListener("click", async (event) => {
      draft = area.value.trim();
      if (!draft) return;
      event.currentTarget.disabled = true;
      event.currentTarget.textContent = t("Zerlege …");
      try {
        const result = await hass.callWS({ type: "brainstorm/split_speech", text: draft, language: language || code() });
        if (!body.isConnected) return;
        if (!result.tasks || !result.tasks.length) {
          ask(t("Darin habe ich keine Aufgabe gefunden."));
          return;
        }
        review(result.tasks, result.ai);
      } catch (err) {
        if (body.isConnected) ask((err && err.message) || t("Das hat nicht geklappt."));
      }
    });
  };
  const review = (tasks, ai, error = "") => {
    const personOptions = (selected) =>
      `<option value="">${t("Niemand")}</option>` +
      people.map((p) => `<option value="${escapeHtml(p.id)}"${p.id === selected ? " selected" : ""}>${escapeHtml(p.name)}</option>`).join("");
    body.innerHTML = `
      <div class="${c("hint")}">${ai ? t("So hat die KI es verstanden. Ändere, was nicht passt, und wähle ab, was nicht angelegt werden soll.") : t("Ohne KI Satz für Satz zerlegt. Ändere, was nicht passt, und wähle ab, was nicht angelegt werden soll.")}</div>
      <div class="bs-speech-list">${tasks.map((task, index) => {
        const due = dueInputValues(task.due);
        return `<div class="bs-speech-row" data-index="${index}">
          <input type="checkbox" class="bs-speech-on" checked aria-label="${escapeHtml(t("Anlegen"))}">
          <input type="text" class="${c("input")} bs-speech-task" value="${escapeHtml(task.text)}" aria-label="${escapeHtml(t("Aufgabe"))}">
          <div class="bs-speech-meta">
            <input type="date" class="${c("input")} bs-speech-date" value="${due.date}" aria-label="${escapeHtml(t("Datum"))}">
            <input type="time" class="${c("input")} bs-speech-time" value="${due.time}" aria-label="${escapeHtml(t("Uhrzeit"))}">
            ${people.length ? `<select class="${c("input")} bs-speech-person" aria-label="${escapeHtml(t("Zuständig"))}">${personOptions(task.assignee)}</select>` : ""}
          </div>
        </div>`;
      }).join("")}</div>
      <div class="${c("error")}" style="display: ${error ? "flex" : "none"};">${escapeHtml(error)}</div>
      <div class="${c("footer")}">
        <button class="${c("btn btn-secondary")}" id="bsSpeechBack">${t("Zurück")}</button>
        <button class="${c("btn btn-primary")}" id="bsSpeechCreate"></button>
      </div>`;
    const rows = [...body.querySelectorAll(".bs-speech-row")];
    const create = body.querySelector("#bsSpeechCreate");
    const count = () => {
      const n = rows.filter((row) => row.querySelector(".bs-speech-on").checked).length;
      create.textContent = t("{count} anlegen", { count: n });
      create.disabled = n === 0;
      rows.forEach((row) => row.classList.toggle("off", !row.querySelector(".bs-speech-on").checked));
    };
    rows.forEach((row) => row.querySelector(".bs-speech-on").addEventListener("change", count));
    count();
    body.querySelector("#bsSpeechBack").addEventListener("click", () => ask());
    create.addEventListener("click", async () => {
      create.disabled = true;
      const left = [];
      for (const row of rows) {
        const task = tasks[Number(row.dataset.index)];
        const textValue = row.querySelector(".bs-speech-task").value.trim();
        if (!row.querySelector(".bs-speech-on").checked || !textValue) continue;
        const person = row.querySelector(".bs-speech-person");
        const payload = { text: textValue, source: "dashboard" };
        if (category) payload.category = category;
        const due = dueFromInputValues(row.querySelector(".bs-speech-date").value, row.querySelector(".bs-speech-time").value);
        if (due) payload.due = due;
        if (person && person.value) payload.assignee = person.value;
        try {
          await hass.callService("brainstorm", "add_idea", payload);
        } catch (err) {
          left.push({ ...task, text: textValue, error: (err && err.message) || "" });
        }
      }
      if (!body.isConnected) return;
      if (left.length) {
        review(left, ai, left[0].error || t("Das hat nicht geklappt."));
        return;
      }
      created();
      close();
    });
  };
  ask();
}

/**
 * Fill a dialog body with the trash: deleted notes with their age, to restore
 * or delete for good one by one, or to empty all at once. Both cards use it.
 */
export function renderTrash(body, { hass, close, prefix = "dialog" }) {
  const c = (names) => names.split(" ").map((n) => `${prefix}-${n}`).join(" ");
  const when = (iso) => {
    const date = new Date(iso);
    if (Number.isNaN(date.getTime())) return "";
    return date.toLocaleString(dateLocale(), { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
  };
  let items = [];
  let days = 30;
  let notice = "";
  let confirming = false;
  const draw = (error = "") => {
    if (!body.isConnected) return;
    body.innerHTML = `
      <div class="${c("hint")}">${t("Gelöschte Notizen bleiben {days} Tage hier, dann sind sie mit ihren Anhängen endgültig weg.", { days })}</div>
      ${notice ? `<div class="bs-trash-notice">${escapeHtml(notice)}</div>` : ""}
      <div class="bs-trash">
        ${
          items.length
            ? items
                .map(
                  (item) => `
          <div class="bs-trash-item">
            <div class="bs-trash-main">
              <div class="bs-trash-text">${formatText(item.text || "")}</div>
              <div class="bs-trash-meta">${escapeHtml(item.category || "")} · ${escapeHtml(t("gelöscht {when}", { when: when(item.deleted_at) }))}${
                item.subtasks ? ` · ${escapeHtml(t("+ {count} Unterpunkte", { count: item.subtasks }))}` : ""
              }${item.attachments ? ` · 📎 ${escapeHtml(t("{count} Anhänge", { count: item.attachments }))}` : ""}</div>
            </div>
            <button type="button" class="bs-trash-btn" data-restore="${escapeHtml(item.id)}" title="${t("Wiederherstellen")}" aria-label="${t("Wiederherstellen")}">↩️</button>
            <button type="button" class="bs-trash-btn bs-trash-del" data-purge="${escapeHtml(item.id)}" title="${t("Endgültig löschen")}" aria-label="${t("Endgültig löschen")}">✕</button>
          </div>`
                )
                .join("")
            : `<div class="bs-comments-empty">${t("Der Papierkorb ist leer.")}</div>`
        }
      </div>
      <div class="${c("error")}" style="display: ${error ? "flex" : "none"};">${escapeHtml(error)}</div>
      ${
        confirming
          ? `<div class="${c("hint")}">${t("Wirklich alle {count} Notizen endgültig löschen?", { count: items.length })}</div>`
          : ""
      }
      <div class="${c("footer")}">
        ${
          confirming
            ? `<button class="${c("btn btn-cancel")}" id="bsTrashNo">${t("Abbrechen")}</button>
               <button class="${c("btn btn-primary")}" id="bsTrashYes" style="background: var(--error-color, #db4437);">${t("Ja, endgültig löschen")}</button>`
            : `${items.length ? `<button class="${c("btn btn-cancel")}" id="bsTrashEmpty" style="color: var(--error-color, #db4437);">${t("Papierkorb leeren")}</button>` : ""}
               <button class="${c("btn btn-primary")}" id="bsTrashClose">${t("Schließen")}</button>`
        }
      </div>
    `;
    const on = (id, handler) => {
      const el = body.querySelector(id);
      if (el) el.addEventListener("click", handler);
    };
    on("#bsTrashClose", close);
    on("#bsTrashEmpty", () => {
      confirming = true;
      draw();
    });
    on("#bsTrashNo", () => {
      confirming = false;
      draw();
    });
    on("#bsTrashYes", () => run({ type: "brainstorm/trash/delete", ids: items.map((item) => item.id) }));
    body.querySelectorAll("[data-restore]").forEach((btn) =>
      btn.addEventListener("click", () => {
        const item = items.find((entry) => entry.id === btn.dataset.restore);
        run({ type: "brainstorm/trash/restore", ids: [btn.dataset.restore] }, item ? t("Wiederhergestellt: {text}", { text: item.text || "" }) : "");
      })
    );
    body.querySelectorAll("[data-purge]").forEach((btn) =>
      btn.addEventListener("click", () => run({ type: "brainstorm/trash/delete", ids: [btn.dataset.purge] }))
    );
  };
  const load = async () => {
    try {
      const result = await hass.callWS({ type: "brainstorm/trash" });
      items = (result && result.items) || [];
      days = (result && result.days) || days;
      draw();
    } catch (err) {
      draw((err && err.message) || t("Das hat nicht geklappt."));
    }
  };
  const run = async (message, done = "") => {
    body.querySelectorAll("button").forEach((btn) => (btn.disabled = true));
    try {
      await hass.callWS(message);
      notice = done;
      confirming = false;
      await load();
    } catch (err) {
      draw((err && err.message) || t("Das hat nicht geklappt."));
    }
  };
  body.innerHTML = `<div class="${c("label")}">${t("Lädt …")}</div>`;
  load();
}

/** Return the 💬 badge with the number of comments, nothing without any. */
export function commentBadge(idea) {
  const count = Number(idea && idea.comment_count) || 0;
  if (!count) return "";
  const label = count === 1 ? t("1 Kommentar") : t("{count} Kommentare", { count });
  return `<button type="button" class="bs-comment" data-comment="${escapeHtml(idea.id)}" title="${escapeHtml(label)}">💬 ${count}</button>`;
}

/**
 * Fill a dialog body with the comments of a note: load them, write a new one
 * (Ctrl+Enter sends) and delete your own. Both cards use it.
 */
export function renderComments(body, { hass, idea, close, prefix = "dialog" }) {
  const c = (names) => names.split(" ").map((n) => `${prefix}-${n}`).join(" ");
  const when = (iso) => {
    const date = new Date(iso);
    if (Number.isNaN(date.getTime())) return "";
    return date.toLocaleString(dateLocale(), { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
  };
  const initials = (name) => String(name || "?").trim().split(/\s+/).map((w) => w[0] || "").join("").slice(0, 2).toUpperCase() || "?";
  const mention = (html) => html.replace(/(^|[\s(>])@([\p{L}\p{N}_-]+)/gu, '$1<span class="bs-mention">@$2</span>');
  let draft = "";
  const draw = (comments, error = "") => {
    if (!body.isConnected) return;
    body.innerHTML = `
      <div class="${c("hint")}">${formatText(idea.text)}</div>
      <div class="bs-comments">
        ${
          comments.length
            ? comments
                .map(
                  (item) => `
          <div class="bs-c${item.mine ? " mine" : ""}">
            <div class="bs-c-avatar"${item.picture ? ` style="background-image: url('${escapeHtml(item.picture)}'); color: transparent;"` : ""}>${escapeHtml(initials(item.name))}</div>
            <div class="bs-c-body">
              <div class="bs-c-head"><b>${escapeHtml(item.name || t("Unbekannt"))}</b><span>${escapeHtml(when(item.at))}</span>
                ${item.can_delete ? `<button type="button" class="bs-c-del" data-del="${escapeHtml(item.id)}" title="${t("Kommentar löschen")}" aria-label="${t("Kommentar löschen")}">✕</button>` : ""}
              </div>
              <div class="bs-c-text">${mention(formatText(item.text))}</div>
            </div>
          </div>`
                )
                .join("")
            : `<div class="bs-comments-empty">${t("Noch keine Kommentare.")}</div>`
        }
      </div>
      <textarea class="${c("input textarea")}" id="bsCommentText" rows="3" maxlength="2000" placeholder="${t("Kommentar schreiben … @Name benachrichtigt die Person")}"></textarea>
      <div class="${c("error")}" style="display: ${error ? "flex" : "none"};">${escapeHtml(error)}</div>
      <div class="${c("footer")}">
        <button class="${c("btn btn-cancel")}" id="bsCommentClose">${t("Schließen")}</button>
        <button class="${c("btn btn-primary")}" id="bsCommentSend">${t("Senden")}</button>
      </div>
    `;
    const area = body.querySelector("#bsCommentText");
    const send = body.querySelector("#bsCommentSend");
    area.value = draft;
    send.disabled = !draft.trim();
    area.addEventListener("input", () => {
      draft = area.value;
      send.disabled = !draft.trim();
    });
    area.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        submit();
      }
    });
    const list = body.querySelector(".bs-comments");
    list.scrollTop = list.scrollHeight;
    body.querySelector("#bsCommentClose").addEventListener("click", close);
    send.addEventListener("click", submit);
    body.querySelectorAll("[data-del]").forEach((btn) =>
      btn.addEventListener("click", async () => {
        btn.disabled = true;
        try {
          await hass.callService("brainstorm", "delete_comment", { id: idea.id, comment_id: btn.dataset.del });
          await load();
        } catch (err) {
          draw(comments, (err && err.message) || t("Das hat nicht geklappt."));
        }
      })
    );
    if (!error) setTimeout(() => area.focus(), 50);
  };
  let current = [];
  const load = async () => {
    try {
      const result = await hass.callWS({ type: "brainstorm/comments", idea_id: idea.id });
      current = (result && result.comments) || [];
      draw(current);
    } catch (err) {
      draw(current, (err && err.message) || t("Das hat nicht geklappt."));
    }
  };
  const submit = async () => {
    const text = draft.trim();
    if (!text) return;
    const send = body.querySelector("#bsCommentSend");
    if (send) send.disabled = true;
    try {
      await hass.callWS({
        type: "call_service",
        domain: "brainstorm",
        service: "add_comment",
        service_data: { id: idea.id, text },
        return_response: true,
      });
      draft = "";
      await load();
    } catch (err) {
      draw(current, (err && err.message) || t("Das hat nicht geklappt."));
    }
  };
  body.innerHTML = `<div class="${c("label")}">${t("Lädt …")}</div>`;
  load();
}

/**
 * Return how far an idea is: from its subtasks if it has any, else what was
 * set by hand, or nothing.
 */
export function ideaProgress(idea) {
  const subtasks = idea && idea.subtasks;
  if (subtasks && subtasks.total) {
    return { percent: Math.max(0, Math.min(100, Number(subtasks.percent) || 0)), done: subtasks.done || 0, total: subtasks.total, auto: true };
  }
  const own = Number(idea && idea.progress) || 0;
  return own > 0 ? { percent: Math.min(100, own), auto: false } : null;
}

/** Return the next step of a progress set by hand: 0, 25, 50, 75, 100 and back to 0. */
/** Numbering styles a note can give its subtasks, as in MindManager. */
export const NUMBERING = ["decimal", "alpha", "roman"];

const toAlpha = (n) => {
  let out = "";
  for (let x = n; x > 0; x = Math.floor((x - 1) / 26)) out = String.fromCharCode(97 + ((x - 1) % 26)) + out;
  return out;
};

const toRoman = (n) => {
  const steps = [[1000, "M"], [900, "CM"], [500, "D"], [400, "CD"], [100, "C"], [90, "XC"], [50, "L"], [40, "XL"], [10, "X"], [9, "IX"], [5, "V"], [4, "IV"], [1, "I"]];
  let out = "";
  let rest = n;
  steps.forEach(([value, sign]) => {
    while (rest >= value) {
      out += sign;
      rest -= value;
    }
  });
  return out;
};

/**
 * Work out the number of every note below a numbered note, in list order.
 * The style of a note reaches all its subtasks until one sets its own;
 * decimal numbers carry the number of their parent (1, 1.1, 1.1.2).
 * Returns a Map of id to the label shown in front of the text.
 */
export function numberLabels(ideas) {
  const labels = new Map();
  const list = ideas || [];
  const ids = new Set(list.map((i) => i.id));
  const byParent = new Map();
  list.forEach((idea) => {
    const parent = idea.parent_id && ids.has(idea.parent_id) && idea.parent_id !== idea.id ? idea.parent_id : null;
    if (!byParent.has(parent)) byParent.set(parent, []);
    byParent.get(parent).push(idea);
  });
  const seen = new Set();
  const walk = (parentId, style, prefix) => {
    (byParent.get(parentId) || []).forEach((child, index) => {
      if (seen.has(child.id)) return;
      seen.add(child.id);
      let number = "";
      if (style === "decimal") {
        number = prefix ? `${prefix}.${index + 1}` : `${index + 1}`;
        labels.set(child.id, prefix ? number : `${number}.`);
      } else if (style === "alpha") {
        labels.set(child.id, `${toAlpha(index + 1)})`);
      } else if (style === "roman") {
        labels.set(child.id, `${toRoman(index + 1)}.`);
      }
      const own = NUMBERING.includes(child.numbering) ? child.numbering : null;
      const next = own || style;
      const carry = next === "decimal" && style === "decimal" ? number : "";
      walk(child.id, next, carry);
    });
  };
  walk(null, null, "");
  return labels;
}

// The notes as a tree in list order; notes whose parent is not in the list are roots
function outlineTree(ideas) {
  const list = ideas || [];
  const ids = new Set(list.map((i) => i.id));
  const byParent = new Map();
  list.forEach((idea) => {
    const parent = idea.parent_id && ids.has(idea.parent_id) && idea.parent_id !== idea.id ? idea.parent_id : null;
    if (!byParent.has(parent)) byParent.set(parent, []);
    byParent.get(parent).push(idea);
  });
  const seen = new Set();
  const build = (parentId) =>
    (byParent.get(parentId) || [])
      .filter((idea) => !seen.has(idea.id) && seen.add(idea.id))
      .map((idea) => ({ idea, children: build(idea.id) }));
  return build(null);
}

const oneLine = (text) => String(text || "").replace(/\s+/g, " ").trim();
const xmlText = (text) =>
  String(text || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/\r?\n/g, "&#10;");

/** The notes as a Markdown outline: the title as heading, the notes as a nested list. */
export function outlineMarkdown(ideas, title) {
  const lines = [`# ${oneLine(title)}`, ""];
  const walk = (nodes, depth) =>
    nodes.forEach(({ idea, children }) => {
      const pad = "  ".repeat(depth);
      lines.push(`${pad}- ${oneLine(idea.text)}`);
      if (idea.description) lines.push(`${pad}  > ${oneLine(idea.description)}`);
      walk(children, depth + 1);
    });
  walk(outlineTree(ideas), 0);
  return `${lines.join("\n")}\n`;
}

// --- PDF: a page with the picture of the map and pages with the outline ---

// Characters of the standard PDF fonts outside Latin-1, in WinAnsi order
const WIN_ANSI = { "€": 0x80, "‚": 0x82, "„": 0x84, "…": 0x85, "‘": 0x91, "’": 0x92, "“": 0x93, "”": 0x94, "•": 0x95, "–": 0x96, "—": 0x97, "™": 0x99 };

/** Remove Markdown signs and characters the PDF fonts cannot show. */
export function pdfPlain(text) {
  return oneLine(text)
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/(\*\*|__|~~|`)/g, "")
    .replace(/(^|\s)[*_](\S[^*_]*\S|\S)[*_](?=\s|$)/g, "$1$2")
    .split("")
    .filter((ch) => WIN_ANSI[ch] || (ch.charCodeAt(0) >= 32 && ch.charCodeAt(0) <= 255 && !(ch.charCodeAt(0) > 126 && ch.charCodeAt(0) < 160)))
    .join("")
    .replace(/\s+/g, " ")
    .trim();
}

// A PDF string in brackets; everything outside plain ASCII as octal escapes
function pdfString(text) {
  let out = "(";
  for (const ch of text) {
    const code = WIN_ANSI[ch] || ch.charCodeAt(0);
    if (ch === "(" || ch === ")" || ch === "\\") out += `\\${ch}`;
    else if (code < 32 || code > 126) out += `\\${code.toString(8).padStart(3, "0")}`;
    else out += ch;
  }
  return `${out})`;
}

// Rough widths of Helvetica, enough to break lines before the margin
function pdfWidth(text, size) {
  let width = 0;
  for (const ch of text) {
    if (" il.,:;'|!ijtfrI()[]".includes(ch)) width += 0.28;
    else if ("mwMW@".includes(ch)) width += 0.85;
    else if (ch >= "A" && ch <= "Z") width += 0.68;
    else width += 0.54;
  }
  return width * size;
}

function pdfWrap(text, size, maxWidth) {
  const lines = [];
  let line = "";
  for (const word of text.split(" ")) {
    const next = line ? `${line} ${word}` : word;
    if (line && pdfWidth(next, size) > maxWidth) {
      lines.push(line);
      line = word;
    } else {
      line = next;
    }
  }
  if (line) lines.push(line);
  return lines;
}

/**
 * Build a PDF file: a first page with the picture of the map (a JPEG) when
 * there is one, then the notes as an outline with their descriptions.
 */
export function outlinePdf(ideas, title, map = null, date = new Date()) {
  const A4 = [595.28, 841.89];
  const margin = 42;
  const pages = [];
  const heading = pdfPlain(title) || "Brainstorm";
  const stamp = pdfPlain(date.toLocaleDateString(dateLocale(), { day: "2-digit", month: "2-digit", year: "numeric" }));
  const text = (x, y, size, value, bold = false, gray = 0) =>
    `${gray ? `${gray} g ` : ""}BT /${bold ? "F2" : "F1"} ${size} Tf ${x.toFixed(2)} ${y.toFixed(2)} Td ${pdfString(value)} Tj ET${gray ? " 0 g" : ""}`;

  if (map && map.jpeg && map.width && map.height) {
    const landscape = map.width > map.height;
    const [w, h] = landscape ? [A4[1], A4[0]] : A4;
    const boxW = w - 2 * margin;
    const boxH = h - 2 * margin - 34;
    const scale = Math.min(boxW / map.width, boxH / map.height);
    const iw = map.width * scale;
    const ih = map.height * scale;
    const x = margin + (boxW - iw) / 2;
    const y = margin + (boxH - ih) / 2;
    pages.push({
      size: [w, h],
      image: true,
      ops: [
        text(margin, h - margin - 16, 16, heading, true),
        text(w - margin - pdfWidth(stamp, 9), h - margin - 14, 9, stamp, false, 0.45),
        `q ${iw.toFixed(2)} 0 0 ${ih.toFixed(2)} ${x.toFixed(2)} ${y.toFixed(2)} cm /Im1 Do Q`,
      ],
    });
  }

  // The outline flows over as many pages as it needs
  let ops = [];
  let y = 0;
  const newPage = () => {
    if (ops.length) pages.push({ size: A4, ops });
    ops = [];
    y = A4[1] - margin;
  };
  newPage();
  ops.push(text(margin, y - 16, 16, pages.length ? `${heading} – ${pdfPlain(t("Gliederung"))}` : heading, true));
  if (!pages.length) ops.push(text(A4[0] - margin - pdfWidth(stamp, 9), y - 14, 9, stamp, false, 0.45));
  y -= 40;
  const ensure = (needed) => {
    if (y - needed < margin) newPage();
  };
  const walk = (nodes, depth) =>
    nodes.forEach(({ idea, children }) => {
      const indent = margin + Math.min(depth, 8) * 16;
      const width = A4[0] - margin - indent - 12;
      const size = depth ? 10.5 : 12;
      const lines = pdfWrap(pdfPlain(idea.text) || "…", size, width);
      lines.forEach((line, index) => {
        ensure(size + 4);
        if (!index) ops.push(text(indent, y - size, size, depth ? "–" : "•", !depth));
        ops.push(text(indent + 12, y - size, size, line, !depth));
        y -= size + 4;
      });
      const description = pdfPlain(idea.description);
      if (description) {
        pdfWrap(description, 9, width).slice(0, 12).forEach((line) => {
          ensure(12);
          ops.push(text(indent + 12, y - 9, 9, line, false, 0.4));
          y -= 12;
        });
      }
      y -= depth ? 2 : 6;
      walk(children, depth + 1);
    });
  walk(outlineTree(ideas), 0);
  pages.push({ size: A4, ops });

  // Objects: 1 catalog, 2 pages, 3 and 4 fonts, 5 the picture, then page and content pairs
  const encoder = new TextEncoder();
  const chunks = [];
  const offsets = [];
  let length = 0;
  const add = (part) => {
    const bytes = typeof part === "string" ? encoder.encode(part) : part;
    chunks.push(bytes);
    length += bytes.length;
  };
  const object = (number, body) => {
    offsets[number] = length;
    add(`${number} 0 obj\n${body}\nendobj\n`);
  };
  const first = 6;
  add("%PDF-1.4\n%\xE2\xE3\xCF\xD3\n");
  object(1, "<< /Type /Catalog /Pages 2 0 R >>");
  object(2, `<< /Type /Pages /Kids [${pages.map((_, i) => `${first + i * 2} 0 R`).join(" ")}] /Count ${pages.length} >>`);
  object(3, "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>");
  object(4, "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>");
  if (pages.some((page) => page.image)) {
    offsets[5] = length;
    add(`5 0 obj\n<< /Type /XObject /Subtype /Image /Width ${map.pixelWidth || Math.round(map.width)} /Height ${map.pixelHeight || Math.round(map.height)} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length ${map.jpeg.length} >>\nstream\n`);
    add(map.jpeg);
    add("\nendstream\nendobj\n");
  } else {
    object(5, "null");
  }
  pages.forEach((page, i) => {
    const content = page.ops.join("\n");
    const resources = `<< /Font << /F1 3 0 R /F2 4 0 R >>${page.image ? " /XObject << /Im1 5 0 R >>" : ""} >>`;
    object(first + i * 2, `<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${page.size[0]} ${page.size[1]}] /Resources ${resources} /Contents ${first + i * 2 + 1} 0 R >>`);
    object(first + i * 2 + 1, `<< /Length ${content.length} >>\nstream\n${content}\nendstream`);
  });
  const xref = length;
  const count = first + pages.length * 2;
  let table = `xref\n0 ${count}\n0000000000 65535 f \n`;
  for (let n = 1; n < count; n += 1) table += `${String(offsets[n]).padStart(10, "0")} 00000 n \n`;
  add(`${table}trailer\n<< /Size ${count} /Root 1 0 R >>\nstartxref\n${xref}\n%%EOF\n`);
  const out = new Uint8Array(length);
  let at = 0;
  chunks.forEach((bytes) => {
    out.set(bytes, at);
    at += bytes.length;
  });
  return out;
}

/** The notes as OPML 2.0, for outliners such as Workflowy, OmniOutliner or Logseq. */
export function outlineOpml(ideas, title) {
  const walk = (nodes, depth) =>
    nodes
      .map(({ idea, children }) => {
        const pad = "  ".repeat(depth + 2);
        const note = idea.description ? ` _note="${xmlText(idea.description)}"` : "";
        const attrs = `text="${xmlText(oneLine(idea.text))}"${note}`;
        return children.length
          ? `${pad}<outline ${attrs}>\n${walk(children, depth + 1)}\n${pad}</outline>`
          : `${pad}<outline ${attrs}/>`;
      })
      .join("\n");
  const body = walk(outlineTree(ideas), 0);
  return `<?xml version="1.0" encoding="UTF-8"?>\n<opml version="2.0">\n  <head><title>${xmlText(oneLine(title))}</title></head>\n  <body>\n${body}\n  </body>\n</opml>\n`;
}

/** The notes as a FreeMind map (.mm), which Freeplane, XMind and MindManager open. */
export function outlineFreemind(ideas, title) {
  const walk = (nodes, depth) =>
    nodes
      .map(({ idea, children }) => {
        const pad = "  ".repeat(depth + 1);
        const note = idea.description
          ? `\n${pad}  <richcontent TYPE="NOTE"><html><head/><body><p>${xmlText(idea.description)}</p></body></html></richcontent>`
          : "";
        const inner = `${note}${children.length ? `\n${walk(children, depth + 1)}` : ""}`;
        return inner
          ? `${pad}<node TEXT="${xmlText(oneLine(idea.text))}">${inner}\n${pad}</node>`
          : `${pad}<node TEXT="${xmlText(oneLine(idea.text))}"/>`;
      })
      .join("\n");
  const body = walk(outlineTree(ideas), 1);
  return `<map version="1.0.1">\n  <node TEXT="${xmlText(oneLine(title))}">\n${body}\n  </node>\n</map>\n`;
}

/** Return the label of a numbering style for chips and menus. */
export function numberingLabel(style) {
  if (style === "decimal") return t("1, 1.1, 1.2");
  if (style === "alpha") return t("a, b, c");
  if (style === "roman") return t("I, II, III");
  return t("Keine");
}

export function nextProgress(percent) {
  const steps = [0, 25, 50, 75, 100];
  const index = steps.indexOf(Number(percent) || 0);
  return steps[(index + 1) % steps.length];
}

/** Return a small ring that fills up with the progress of an idea, or nothing. */
export function progressBadge(idea, { always = false } = {}) {
  const progress = ideaProgress(idea);
  if (!progress && !always) return "";
  const percent = progress ? progress.percent : 0;
  const circumference = 2 * Math.PI * 6;
  const filled = (circumference * percent) / 100;
  const label = progress && progress.auto ? `${progress.done}/${progress.total}` : `${percent} %`;
  const title = progress && progress.auto
    ? t("{done} von {total} Unteraufgaben erledigt, {percent} % geschafft", { done: progress.done, total: progress.total, percent })
    : t("Fortschritt {percent} % (antippen für den nächsten Schritt)", { percent });
  return `<span class="progress-badge${percent >= 100 ? " progress-full" : ""}${progress && progress.auto ? " progress-auto" : ""}" data-id="${escapeHtml(idea.id)}" title="${title}">`
    + `<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true"><circle cx="8" cy="8" r="6" class="progress-track"/>`
    + `<circle cx="8" cy="8" r="6" class="progress-fill" stroke-dasharray="${filled.toFixed(2)} ${circumference.toFixed(2)}" transform="rotate(-90 8 8)"/></svg>`
    + `<span>${label}</span></span>`;
}

const ATTACHMENT_URL = "/api/brainstorm/attachments";
const ATTACHMENT_ACCEPT = "image/*,.pdf,.txt,.log,.md,.csv,.json,.yaml,.yml,.zip";
const signedUrls = new Map();

/** Return a signed address, so an image tag can load a file without a token. */
/** Return the first picture among the files of a note, shown on the map. */
export function coverAttachment(idea) {
  const files = (idea && idea.attachments) || [];
  return files.find((a) => String(a.type || "").startsWith("image/") && a.type !== "image/heic") || null;
}

/** Return a short-lived address of an attachment that an image or a tab can open. */
export async function attachmentUrl(hass, ideaId, attachmentId) {
  return signedAttachmentUrl(hass, ideaId, attachmentId);
}

async function signedAttachmentUrl(hass, ideaId, attachmentId) {
  const path = `${ATTACHMENT_URL}/${encodeURIComponent(ideaId)}/${encodeURIComponent(attachmentId)}`;
  const cached = signedUrls.get(path);
  if (cached && cached.until > Date.now()) return cached.url;
  const result = await hass.callWS({ type: "auth/sign_path", path, expires: 3600 });
  signedUrls.set(path, { url: result.path, until: Date.now() + 50 * 60 * 1000 });
  return result.path;
}

async function attachmentRequest(hass, path, init) {
  const response = await hass.fetchWithAuth(path, init);
  let body = {};
  try {
    body = await response.json();
  } catch (_err) {
    body = {};
  }
  if (!response.ok) {
    throw new Error(body.message || t("Der Anhang konnte nicht gespeichert werden ({status}).", { status: response.status }));
  }
  return body;
}

function formatSize(bytes) {
  if (bytes >= 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1).replace(".", code() === "de" ? "," : ".")} MB`;
  return `${Math.max(1, Math.round(bytes / 1024))} KB`;
}

/** Return the 🔧 badge of an idea someone is working on, or nothing. */
export function inProgressBadge(idea) {
  const mark = idea && idea.in_progress;
  if (!mark) return "";
  const since = mark.since ? new Date(mark.since) : null;
  const when = since && !Number.isNaN(since.getTime())
    ? since.toLocaleString(dateLocale(), { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" })
    : "";
  const name = mark.name ? escapeHtml(mark.name) : "";
  const title = name ? t("{name} arbeitet daran seit {time}", { name, time: when }) : t("In Arbeit seit {time}", { time: when });
  return `<span class="in-progress-badge" title="${title}">🔧 ${t("In Arbeit")}${name ? ` · ${name}` : ""}</span>`;
}

/** Return the ⛔ badge of a note that waits for other open notes, or nothing. */
export function blockedBadge(idea) {
  const waits = (idea && idea.blocked_by) || [];
  if (!waits.length) return "";
  const names = waits.map((w) => escapeHtml(w.text || "")).join(", ");
  return `<span class="blocked-badge" title="${t("Wartet auf: {names}", { names })}">⛔ ${t("Wartet")}${waits.length > 1 ? ` · ${waits.length}` : ""}</span>`;
}

// Operating levels: beginners see the basics, pros see everything. Hiding
// never deletes anything, it only takes the controls out of sight.
export const LEVELS = ["beginner", "normal", "pro"];

/** Return the level of a card: its own option first, then the setting of the integration. */
export function uiLevel(config, sensor) {
  const own = config && config.level;
  if (LEVELS.includes(own)) return own;
  const shared = sensor && sensor.attributes && sensor.attributes.ui_level;
  // Installations from before the levels keep seeing everything
  return LEVELS.includes(shared) ? shared : "pro";
}

/** Return whether a level shows what needs at least the given level. */
export function levelAllows(level, needed) {
  const have = LEVELS.indexOf(level);
  return (have < 0 ? LEVELS.length - 1 : have) >= LEVELS.indexOf(needed);
}

/** Return the label of a level. */
export function levelLabel(level) {
  return { beginner: t("Einsteiger"), normal: t("Normal"), pro: t("Profi") }[level] || t("Wie in den Einstellungen");
}

/** CSS that hides what needs a higher level; the card sets data-level on itself. */
export const LEVEL_CSS = `
  .lvl { display: contents; }
  :host([data-level="beginner"]) [data-lvl="normal"],
  :host([data-level="beginner"]) [data-lvl="pro"],
  :host([data-level="normal"]) [data-lvl="pro"] { display: none !important; }
  .lvl-more { width: 100%; min-height: 44px; margin: 8px 0 4px; }
`;

/**
 * Add a "More fields" button to a dialog with hidden fields. It shows them all,
 * so values set at a higher level stay editable.
 */
export function addMoreFields(body, level, className) {
  const hidden = [...body.querySelectorAll("[data-lvl]")].filter((el) => !levelAllows(level, el.dataset.lvl));
  if (!hidden.length) return null;
  const footer = body.querySelector(".action-dialog-footer, .dialog-footer");
  const button = document.createElement("button");
  button.type = "button";
  button.className = `${className} lvl-more`;
  button.textContent = t("Mehr Felder …");
  button.addEventListener("click", () => {
    body.querySelectorAll("[data-lvl]").forEach((el) => el.removeAttribute("data-lvl"));
    button.remove();
  });
  if (footer) footer.before(button);
  else body.append(button);
  return button;
}

// Boards: Kanban by state, a timeline by due date, the Eisenhower matrix
export const BOARDS = ["kanban", "timeline", "matrix"];

function startOfDay(date, plusDays = 0) {
  const day = new Date(date);
  day.setHours(0, 0, 0, 0);
  day.setDate(day.getDate() + plusDays);
  return day;
}

function dueDate(idea) {
  const due = idea && idea.due ? new Date(idea.due) : null;
  return due && !Number.isNaN(due.getTime()) ? due : null;
}

function isImportant(idea) {
  return ["urgent", "high"].includes(String((idea && idea.priority) || "medium").toLowerCase());
}

// Urgent is the 🔥 priority or a due date within the next three days
function isUrgent(idea, now) {
  if (String((idea && idea.priority) || "").toLowerCase() === "urgent") return true;
  const due = dueDate(idea);
  return Boolean(due && due < startOfDay(now, 3));
}

function boardColumnKeys(kind) {
  if (kind === "timeline") return ["overdue", "today", "tomorrow", "week", "later", "none"];
  if (kind === "matrix") return ["do", "plan", "delegate", "drop"];
  return ["open", "doing", "waiting", "done"];
}

export function boardColumnLabel(kind, key) {
  const labels = {
    open: t("📝 Offen"),
    doing: t("🔧 In Arbeit"),
    waiting: t("⛔ Wartet"),
    done: t("✅ Erledigt"),
    overdue: t("⚠️ Überfällig"),
    today: t("Heute"),
    tomorrow: t("Morgen"),
    week: t("Diese Woche"),
    later: t("Später"),
    none: t("Ohne Datum"),
    do: t("🔥 Sofort erledigen"),
    plan: t("📅 Einplanen"),
    delegate: t("👥 Abgeben"),
    drop: t("🗑️ Später oder gar nicht"),
  };
  return labels[key] || key;
}

/** Return the column of a note on a board. */
export function boardColumnOf(kind, idea, now = new Date()) {
  if (kind === "timeline") {
    const due = dueDate(idea);
    if (!due) return "none";
    if (due < now) return "overdue";
    if (due < startOfDay(now, 1)) return "today";
    if (due < startOfDay(now, 2)) return "tomorrow";
    if (due < startOfDay(now, 7)) return "week";
    return "later";
  }
  if (kind === "matrix") {
    const important = isImportant(idea);
    const urgent = isUrgent(idea, now);
    if (important && urgent) return "do";
    if (important) return "plan";
    if (urgent) return "delegate";
    return "drop";
  }
  if (idea.status === "completed") return "done";
  if (idea.blocked_by && idea.blocked_by.length) return "waiting";
  return idea.in_progress ? "doing" : "open";
}

/** Return the columns of a board, each with the ids of its notes in their order. */
export function boardColumns(kind, ideas, now = new Date()) {
  const columns = boardColumnKeys(kind).map((key) => ({ key, label: boardColumnLabel(kind, key), ids: [] }));
  const byKey = new Map(columns.map((column) => [column.key, column]));
  ideas.forEach((idea) => {
    const column = byKey.get(boardColumnOf(kind, idea, now));
    if (column) column.ids.push(idea.id);
  });
  return columns;
}

// A due date on the given day, at the time the note had or at 09:00
function dueOn(idea, day) {
  const old = dueDate(idea);
  const due = new Date(day);
  if (old) due.setHours(old.getHours(), old.getMinutes(), 0, 0);
  else due.setHours(9, 0, 0, 0);
  return due.toISOString();
}

/**
 * Return what update_idea needs so a note dropped on a column belongs there,
 * {} when it already does, or null when that column cannot be reached by hand.
 */
export function boardDrop(kind, key, idea, now = new Date()) {
  if (boardColumnOf(kind, idea, now) === key) return {};
  if (kind === "kanban") {
    if (key === "done") return { status: "completed" };
    if (key === "doing") return { in_progress: true };
    if (key === "open") return { in_progress: false };
    return null;
  }
  if (kind === "timeline") {
    const days = { today: 0, tomorrow: 1, week: 3, later: 14 };
    if (key === "none") return { due: null };
    if (key in days) return { due: dueOn(idea, startOfDay(now, days[key])) };
    return null;
  }
  if (kind === "matrix") {
    // Importance is the priority, urgency the 🔥 priority or a near due date
    const change = {};
    const priority = String(idea.priority || "medium").toLowerCase();
    const wanted = { do: "urgent", plan: "high" }[key];
    if (wanted && priority !== wanted) change.priority = wanted;
    if (!wanted && isImportant(idea)) change.priority = "medium";
    const after = { ...idea, ...change };
    if (key === "delegate" && !isUrgent(after, now)) change.due = dueOn(idea, startOfDay(now, 1));
    // A note due within three days stays urgent, its date is not moved here
    if ((key === "plan" || key === "drop") && isUrgent(after, now)) return null;
    return change;
  }
  return null;
}

/**
 * Fit the notes and the visible part of the map into a minimap of w × h.
 * rects and view are boxes {x, y, w, h} in map coordinates. Returns the scale
 * and offset that turn a map point into a minimap point.
 */
export function minimapFrame(rects, view, w, h, pad = 6) {
  let minX = view.x;
  let minY = view.y;
  let maxX = view.x + view.w;
  let maxY = view.y + view.h;
  rects.forEach((r) => {
    minX = Math.min(minX, r.x);
    minY = Math.min(minY, r.y);
    maxX = Math.max(maxX, r.x + r.w);
    maxY = Math.max(maxY, r.y + r.h);
  });
  const spanX = Math.max(1, maxX - minX);
  const spanY = Math.max(1, maxY - minY);
  const innerW = Math.max(1, w - pad * 2);
  const innerH = Math.max(1, h - pad * 2);
  const scale = Math.min(innerW / spanX, innerH / spanY);
  return {
    scale,
    ox: pad + (innerW - spanX * scale) / 2 - minX * scale,
    oy: pad + (innerH - spanY * scale) / 2 - minY * scale,
  };
}

/** Turn a point on the minimap back into map coordinates. */
export function minimapToMap(frame, x, y) {
  return { x: (x - frame.ox) / frame.scale, y: (y - frame.oy) / frame.scale };
}

/**
 * Return the content templates: ready branches for common kinds of thinking,
 * each as a Markdown outline that import_outline understands.
 */
export function contentTemplates() {
  const outline = (title, items) => {
    const lines = [`# ${title}`];
    items.forEach((item) => {
      const [text, subs] = Array.isArray(item) ? item : [item, []];
      lines.push(`- ${text}`);
      subs.forEach((sub) => lines.push(`  - ${sub}`));
    });
    return `${lines.join("\n")}\n`;
  };
  return [
    { key: "swot", icon: "🧭", name: t("SWOT-Analyse"), outline: outline(t("SWOT-Analyse"), [t("Stärken"), t("Schwächen"), t("Chancen"), t("Risiken")]) },
    { key: "procon", icon: "⚖️", name: t("Pro und Contra"), outline: outline(t("Entscheidung"), [t("Pro"), t("Contra"), t("Offene Fragen"), t("Ergebnis")]) },
    {
      key: "project",
      icon: "🚀",
      name: t("Projektplan"),
      outline: outline(t("Projekt"), [
        t("Ziel"),
        [t("Aufgaben"), [t("Planung"), t("Umsetzung"), t("Test")]],
        t("Termine"),
        t("Budget"),
        t("Risiken"),
        t("Offene Fragen"),
      ]),
    },
    {
      key: "week",
      icon: "🗓️",
      name: t("Wochenplan"),
      outline: outline(t("Woche"), [t("Montag"), t("Dienstag"), t("Mittwoch"), t("Donnerstag"), t("Freitag"), t("Wochenende")]),
    },
    {
      key: "party",
      icon: "🎉",
      name: t("Feier planen"),
      outline: outline(t("Feier"), [t("Gäste"), t("Essen und Getränke"), t("Einkauf"), t("Deko"), t("Musik"), t("Ablauf")]),
    },
    {
      key: "trip",
      icon: "🧳",
      name: t("Reise planen"),
      outline: outline(t("Reise"), [t("Anreise"), t("Unterkunft"), [t("Packliste"), [t("Kleidung"), t("Dokumente"), t("Technik")]], t("Ausflüge"), t("Budget")]),
    },
    {
      key: "retro",
      icon: "🔁",
      name: t("Rückblick"),
      outline: outline(t("Rückblick"), [t("Was lief gut"), t("Was lief nicht gut"), t("Was wir ändern")]),
    },
    {
      key: "room",
      icon: "🏠",
      name: t("Raum renovieren"),
      outline: outline(t("Renovierung"), [t("Ausmessen"), t("Material"), t("Werkzeug"), t("Handwerker"), t("Reihenfolge"), t("Budget")]),
    },
  ];
}

/** Return the 📎 badge of an idea with files, or nothing. */
export function attachmentBadge(idea) {
  const count = (idea && idea.attachments && idea.attachments.length) || 0;
  if (!count) return "";
  return `<span class="attachment-badge" data-id="${escapeHtml(idea.id)}" title="${t("Anhänge anzeigen")}">📎 ${count}</span>`;
}

/**
 * Show the files of an idea in a container, with adding and removing for people
 * who may edit it. Images can also be pasted or dropped onto `dropTarget`.
 */
export function renderAttachments(container, { hass, idea, canEdit, dropTarget, onChange }) {
  let attachments = [...((idea && idea.attachments) || [])];
  let busy = false;

  const draw = () => {
    container.innerHTML = `
      <style>
        .bs-att { display: flex; flex-direction: column; gap: 8px; }
        .bs-att-grid { display: flex; flex-wrap: wrap; gap: 8px; }
        .bs-att-item { position: relative; width: 84px; height: 84px; border-radius: 10px; overflow: hidden;
          border: 1px solid var(--divider-color, rgba(127,127,127,0.3)); background: var(--secondary-background-color, rgba(127,127,127,0.1));
          display: flex; align-items: center; justify-content: center; cursor: pointer; }
        .bs-att-item img { width: 100%; height: 100%; object-fit: cover; }
        .bs-att-file { display: flex; flex-direction: column; align-items: center; gap: 2px; padding: 4px; text-align: center;
          font-size: 0.68rem; line-height: 1.2; color: var(--primary-text-color); word-break: break-all; }
        .bs-att-file span:first-child { font-size: 1.5rem; }
        .bs-att-del { position: absolute; top: 2px; right: 2px; width: 26px; height: 26px; border-radius: 50%; border: none;
          background: rgba(0,0,0,0.6); color: #fff; font-size: 0.8rem; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        .bs-att-actions { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
        .bs-att-add { min-height: 40px; padding: 0 14px; border-radius: 10px; cursor: pointer; font: inherit;
          border: 1px dashed var(--primary-color, #03a9f4); background: transparent; color: var(--primary-color, #03a9f4); }
        .bs-att-add:disabled { opacity: 0.5; cursor: progress; }
        .bs-att-hint { font-size: 0.75rem; color: var(--secondary-text-color); }
        .bs-att-error { font-size: 0.8rem; color: var(--error-color, #db4437); }
        .bs-att-empty { font-size: 0.8rem; color: var(--secondary-text-color); }
      </style>
      <div class="bs-att">
        ${attachments.length ? `<div class="bs-att-grid">${attachments.map((a) => `
          <div class="bs-att-item" data-att="${escapeHtml(a.id)}" title="${escapeHtml(a.name)} · ${formatSize(a.size || 0)}">
            ${String(a.type || "").startsWith("image/") && a.type !== "image/heic"
              ? `<img alt="${escapeHtml(a.name)}" data-img="${escapeHtml(a.id)}">`
              : `<div class="bs-att-file"><span>${a.type === "application/pdf" ? "📕" : a.type === "application/zip" ? "🗜️" : "📄"}</span><span>${escapeHtml(a.name.length > 24 ? `${a.name.slice(0, 21)}…` : a.name)}</span></div>`}
            ${canEdit ? `<button class="bs-att-del" data-del="${escapeHtml(a.id)}" title="${t("Anhang löschen")}" aria-label="${t("Anhang löschen")}">✕</button>` : ""}
          </div>`).join("")}</div>` : canEdit ? "" : `<div class="bs-att-empty">${t("Keine Anhänge.")}</div>`}
        ${canEdit ? `
          <div class="bs-att-actions">
            <button type="button" class="bs-att-add" ${busy ? "disabled" : ""}>${busy ? t("Wird hochgeladen …") : t("📎 Datei anhängen")}</button>
            <span class="bs-att-hint">${t("Bilder auch per Einfügen oder Ziehen. Nach dem Erledigen bleiben Anhänge 30 Tage.")}</span>
            <input type="file" multiple accept="${ATTACHMENT_ACCEPT}" style="display: none;">
          </div>` : ""}
        <div class="bs-att-error" style="display: none;"></div>
      </div>`;

    container.querySelectorAll("img[data-img]").forEach(async (img) => {
      try {
        img.src = await signedAttachmentUrl(hass, idea.id, img.dataset.img);
      } catch (err) {
        console.error("[Brainstorm] Could not load attachment", err);
      }
    });
    container.querySelectorAll(".bs-att-item").forEach((el) => {
      el.addEventListener("click", async (e) => {
        if (e.target.closest(".bs-att-del")) return;
        // Open the window first, so pop-up blockers see the tap
        const win = window.open("", "_blank");
        try {
          const url = await signedAttachmentUrl(hass, idea.id, el.dataset.att);
          if (win) win.location.href = url;
          else window.location.href = url;
        } catch (err) {
          if (win) win.close();
          showError(err.message);
        }
      });
    });
    container.querySelectorAll(".bs-att-del").forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        e.stopPropagation();
        const att = attachments.find((a) => a.id === btn.dataset.del);
        if (!att || !window.confirm(t("„{name}“ löschen?", { name: att.name }))) return;
        try {
          const body = await attachmentRequest(hass, `${ATTACHMENT_URL}/${encodeURIComponent(idea.id)}/${encodeURIComponent(att.id)}`, { method: "DELETE" });
          attachments = body.attachments || [];
          draw();
          if (onChange) onChange(attachments);
        } catch (err) {
          showError(err.message);
        }
      });
    });
    const input = container.querySelector('input[type="file"]');
    const addBtn = container.querySelector(".bs-att-add");
    if (input && addBtn) {
      addBtn.addEventListener("click", () => input.click());
      input.addEventListener("change", () => upload([...input.files]));
    }
  };

  const showError = (message) => {
    const el = container.querySelector(".bs-att-error");
    if (!el) return;
    el.textContent = `⚠️ ${message}`;
    el.style.display = "block";
  };

  const upload = async (files) => {
    if (!canEdit || busy || !files.length) return;
    const form = new FormData();
    files.forEach((file, idx) => {
      // Pasted screenshots are all called image.png
      const name = file.name && file.name !== "image.png"
        ? file.name
        : `Screenshot ${new Date().toISOString().slice(0, 19).replace("T", " ").replace(/:/g, "-")}${idx ? `-${idx + 1}` : ""}.png`;
      form.append("file", file, name);
    });
    busy = true;
    draw();
    try {
      const body = await attachmentRequest(hass, `${ATTACHMENT_URL}/${encodeURIComponent(idea.id)}`, { method: "POST", body: form });
      attachments = body.attachments || attachments;
      busy = false;
      draw();
      if (onChange) onChange(attachments);
    } catch (err) {
      busy = false;
      draw();
      showError(err.message);
    }
  };

  if (dropTarget) {
    // The dialog body is reused, so the listeners of the last idea must go
    if (dropTarget._bsAttachments) dropTarget._bsAttachments.abort();
    dropTarget._bsAttachments = null;
  }
  if (canEdit && dropTarget) {
    const controller = new AbortController();
    dropTarget._bsAttachments = controller;
    const { signal } = controller;
    dropTarget.addEventListener("paste", (e) => {
      const files = [...((e.clipboardData && e.clipboardData.files) || [])];
      if (!files.length) return;
      e.preventDefault();
      upload(files);
    }, { signal });
    dropTarget.addEventListener("dragover", (e) => {
      if (e.dataTransfer && [...e.dataTransfer.types].includes("Files")) e.preventDefault();
    }, { signal });
    dropTarget.addEventListener("drop", (e) => {
      const files = [...((e.dataTransfer && e.dataTransfer.files) || [])];
      if (!files.length) return;
      e.preventDefault();
      upload(files);
    }, { signal });
  }

  draw();
}

// How much a note shows on the map: everything, only its title, or one of
// the two depending on the zoom. Compact notes keep the map readable when
// it is zoomed out or full; a tap opens a single note.
export const NODE_DETAIL_MODES = ["auto", "compact", "normal"];
export const NODE_DETAIL_ZOOM = 0.75;

/** Return a known way of showing notes, automatic when unknown. */
export function nodeDetailMode(value) {
  return NODE_DETAIL_MODES.includes(value) ? value : "auto";
}

/** Tell whether notes are shown compact in this mode at this zoom. */
export function nodeDetailCompact(mode, scale) {
  const known = nodeDetailMode(mode);
  if (known === "compact") return true;
  if (known === "normal") return false;
  return Number(scale) < NODE_DETAIL_ZOOM;
}

/** Return the next mode of the button: automatic, compact, normal. */
export function nextNodeDetail(mode) {
  const index = NODE_DETAIL_MODES.indexOf(nodeDetailMode(mode));
  return NODE_DETAIL_MODES[(index + 1) % NODE_DETAIL_MODES.length];
}

/** Return the icon and the hint of the button for a mode. */
export function nodeDetailButton(mode) {
  const known = nodeDetailMode(mode);
  if (known === "compact") return { icon: "▭", title: t("Notizen: kompakt (nur Titel) – tippen für normal") };
  if (known === "normal") return { icon: "▤", title: t("Notizen: mit allen Angaben – tippen für automatisch") };
  return { icon: "◐", title: t("Notizen: automatisch nach Zoom – tippen für kompakt") };
}

/** Return the one status a compact note shows as a dot. */
export function nodeStatus(idea, now = Date.now()) {
  if (!idea) return { key: "normal", label: "" };
  if (idea.blocked_by && idea.blocked_by.length) return { key: "blocked", label: t("Wartet") };
  const due = idea.due ? new Date(idea.due).getTime() : NaN;
  if (!Number.isNaN(due) && due < now) return { key: "overdue", label: t("überfällig") };
  if (idea.in_progress) return { key: "working", label: t("In Arbeit") };
  const prio = String(idea.priority || "medium").toLowerCase();
  if (prio === "urgent") return { key: "urgent", label: t("🔥 Dringend") };
  if (prio === "high") return { key: "high", label: t("🔴 Hoch") };
  return { key: "normal", label: "" };
}

/** Return the status dot and the number of subtasks of a compact note. */
export function compactNodeInfo(idea, childCount, now = Date.now()) {
  const status = nodeStatus(idea, now);
  const dot = `<span class="node-dot dot-${status.key}"${status.label ? ` title="${escapeHtml(status.label)}"` : ""}></span>`;
  const kids = childCount > 0
    ? `<span class="node-kids" title="${escapeHtml(t("{count} Unteraufgaben", { count: childCount }))}">${childCount}</span>`
    : "";
  return `<span class="cloud-compact">${dot}${kids}</span>`;
}

/**
 * Return the hint for notes that waited only for the notes just done, or
 * nothing. The ideas are those from before, with their blocked_by lists.
 */
export function unblockedText(ideas, doneIds) {
  const done = new Set(doneIds || []);
  const free = (ideas || []).filter((idea) => {
    const waits = idea.blocked_by || [];
    return idea.status === "active" && !done.has(idea.id) && waits.length > 0 && waits.every((w) => done.has(w.id));
  });
  if (!free.length) return "";
  if (free.length === 1) return t("🔓 „{text}“ kann jetzt losgehen", { text: free[0].text || "" });
  return t("🔓 {count} Notizen können jetzt losgehen", { count: free.length });
}
