/**
 * Brainstorm Hub - texts of the cards.
 *
 * The German text is the key, so the cards read naturally and German needs no
 * dictionary. To add a language, add a dictionary below; a missing text shows the
 * English one.
 */
const DICTIONARIES = {
  en: {
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
  return { query: "", prios: new Set(), overdue: false, soon: false, working: false, tags: new Set(), markers: new Set() };
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
  for (const tag of filter.tags) {
    if (!tags.includes(tag)) return false;
  }
  const markers = ideaMarkers(idea);
  for (const marker of filter.markers || []) {
    if (!markers.includes(marker)) return false;
  }
  return true;
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
