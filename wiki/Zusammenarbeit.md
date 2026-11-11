🏠 [Start](Home) · 🇬🇧 [English version](Collaboration)

## 👥 Privatsphäre & Freigaben

Standardmäßig sehen alle Benutzer deines Home Assistant alle Einträge. Unter **Brainstorm Hub ➔ Konfigurieren ➔ Privatsphäre & Benutzer** kannst du das ändern. Wähle dabei einen **Hauptbenutzer**, dem alle vorhandenen Einträge gehören.

- **Eingeschaltet:** Jeder Eintrag gehört der Person, die ihn angelegt hat, und nur sie sowie Personen mit Freigabe sehen ihn.
- **Einzelne Einträge:** Eintrag lange drücken ➔ **👥 Freigeben**, pro Person *Ansehen* oder *Bearbeiten*, oder für *Alle Benutzer*.
- **Kategorien:** Kategorie auswählen ➔ **👥 … freigeben**. Das gilt für deine eigenen Einträge darin, auch für spätere.
- **Mehrere Einträge:** **☑️ Auswählen**, dann auf einmal erledigen, verschieben, freigeben oder löschen. Das geht auch ohne Privatsphäre.
- **Rechte:** *Bearbeiten* erlaubt Ändern und Abhaken. Löschen und Weitergeben bleiben beim Besitzer.
- **In fremde Listen schreiben:** Gibt dir jemand eine Kategorie persönlich mit *Bearbeiten* frei, landen deine neuen Einträge darin in seiner Liste und gehören ihm. Das gilt auch für Unteraufgaben zu seinen Einträgen. Eine Freigabe für *Alle Benutzer* zählt dafür nicht, und haben dir mehrere Personen dieselbe Kategorie freigegeben, bleibt der Eintrag deiner.
- **Wer hat es eingetragen:** Stammt ein Eintrag in deiner Liste von jemand anderem, zeigen beide Karten ein Abzeichen mit seinem Namen, etwa *✍️ Claude*. Hat seine Person in Home Assistant ein Bild, erscheint in der Listenkarte das Bild statt ✍️. So erkennst du auf einen Blick, was eine KI über ihren eigenen Benutzer angelegt hat.
- **Echos und Alexa-Apps:** Unter **Echos & Apps Personen zuordnen** gehört jedes Gerät einer Person. Was dort gesagt wird, gehört ihr, und nur ihre Einträge werden vorgelesen. Home Assistant erkennt keine Stimmen, und im Raum hören alle mit.

> [!IMPORTANT]
> Administratoren und alle mit Zugriff auf die Dateien können weiterhin alles lesen. Die To-do-Listen von Home Assistant zeigen nur, was für alle freigegeben ist, weil sie alle Benutzer lesen können. Bestehende Markdown-Exporte bleiben beim Einschalten liegen; neue entstehen nur, wenn du das erlaubst.

## 🗳️ Gemeinsam auf der Map

- **Abstimmen und Reaktionen (v1.10.7):** 🗳️ unten rechts oder **V** startet eine Abstimmung in einer Kategorie: Jede Person bekommt z. B. 5 Stimmen und verteilt sie mit − / + an den Notizen, in der Mindmap wie in der Liste. Verdeckt sieht jeder bis zum Ende nur die eigenen Stimmen. Beim Beenden erscheint die Rangliste mit 🥇🥈🥉, ein Tipp sortiert die Kategorie danach. Dazu Reaktionen 👍 ❤️ 😂 ❗ an jeder Notiz (Kontextmenü bzw. ⋯ in der Mindmap); wer eine geteilte Notiz nur sehen darf, darf trotzdem reagieren und abstimmen.
- **Kommentare (v1.11.2):** 💬 im Kontextmenü der Liste oder unter ⋯ in der Mindmap öffnet den Verlauf einer Notiz: wer, wann, was, mit Formatierung. Eine Notiz mit Kommentaren zeigt 💬 und die Anzahl, ein Tipp darauf öffnet ihn. **@Name** benachrichtigt die Person über ihre Kanäle unter *Erinnerungen ➔ Personen*. Eigene Kommentare lassen sich löschen; wer die Notiz ändern darf, kann alle löschen. Wer eine geteilte Notiz nur sehen darf, darf trotzdem kommentieren.
- **Live-Präsenz (v1.11.8):** Oben links in der Mindmap stehen die Personen, die dieselbe Liste gerade offen haben, als Kreis mit ihren Initialen, eine Person auch mit zwei Geräten nur einmal. Bearbeitet jemand eine Notiz, hat der Kreis einen Ring und an der Notiz hängt ✏️ mit dem Namen; der Tooltip nennt die Notiz. Läuft über die WebSocket-Verbindung von Home Assistant, nichts davon wird gespeichert.
- **Verdeckte Brainstorm-Runde (v1.11.5):** Im ⚡ Brainstorm-Dialog *🙈 Verdeckt* ankreuzen: Bis zum Aufdecken sieht jede Person nur die eigenen neuen Ideen in dieser Kategorie, so beeinflusst niemand die anderen. Über der Map erscheint ein Hinweis mit *Mitmachen* und *Aufdecken*; mit Timer deckt die Runde nach Ablauf von selbst auf. Wer eine verdeckte Idee nicht sieht, kann sie auch nicht ändern; Alexa-Notizen ohne Person bleiben sichtbar.
