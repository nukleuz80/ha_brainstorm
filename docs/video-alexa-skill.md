# 🎬 Video: Eigenen Alexa-Skill für Brainstorm einrichten

⬅️ [Zurück zur Anleitung](anleitung.md#12-alexa-mit-eigenem-skill) · 📄 [Schriftliche Anleitung in der README](../README_de.md#variante-c-eigener-alexa-skill-optional-ein-satz-eine-antwort)

[![Video starten](video/poster.jpg)](video/brainstorm-alexa-skill.mp4)

**[▶️ Video ansehen (MP4, 6 Minuten, deutsch mit Untertiteln im Bild)](video/brainstorm-alexa-skill.mp4)**

Das Video führt in 18 Kapiteln durch die Alexa-Entwicklerkonsole, ein Kapitel pro Einstellung. Die markierten Felder zeigen, was du einstellen musst. Die Konsole ist schematisch nachgezeichnet, Amazon ändert ihre Oberfläche gelegentlich, die Bezeichnungen bleiben aber gleich. Die MP4-Datei enthält Kapitelmarken, die die meisten Player (VLC, QuickTime, Plex) anzeigen.

## Kapitel

| Zeit | Kapitel | Einstellung |
| :--- | :--- | :--- |
| 0:00 | Einleitung | Was der Skill bringt: ein Satz, eine Antwort |
| 0:25 | 1. Voraussetzungen | Gleiches Amazon-Konto wie die Echos, Home Assistant per HTTPS erreichbar |
| 0:55 | 2. Home Assistant: Spracheingabe | **Konfigurieren ➔ Alexa-Spracheingabe & Skill** auf **Skill** oder **Beide** |
| 1:24 | 3. Skill-Name | `Brainstorm` |
| 1:39 | 4. Sprache (Primary locale) | **German (DE)**, passend zur Sprache des Echos |
| 1:53 | 5. Erfahrung & Modell | Modell **Custom** |
| 2:04 | 6. Hosting | **Alexa-hosted (Python)**, Region z. B. **EU (Ireland)** |
| 2:23 | 7. Vorlage | **Start from Scratch**, dann **Create Skill** |
| 2:38 | 8. Interfaces | **Alexa Presentation Language** mit den Hub-Profilen (nur Echo Show) |
| 2:56 | 9. Permissions | **Reminders** (nur für echte Alexa-Erinnerungen) |
| 3:11 | 10. Sprachmodell | **JSON Editor**: Feld *Sprachmodell* einfügen, **Save**, **Build Skill** |
| 3:42 | 11. Aufrufname | **Skill Invocation Name** `brainstorm` nicht ändern |
| 3:56 | 12. Skill-Code | `lambda_function.py` durch Feld *Skill-Code* ersetzen, **Deploy** |
| 4:20 | 13. Test | **Development** einstellen und Satz im Simulator testen |
| 4:43 | 14. Kopplung | In Home Assistant **Absenden**, erster Satz koppelt den Skill |
| 5:06 | 15. Alexa-App | Skill unter den Entwickler-Skills, Berechtigung *Erinnerungen* |
| 5:20 | 16. Alte Routinen aufräumen | Routinen für *„öffne Brainstorm“* im Modus **Skill** löschen |
| 5:34 | 17. Fehlerbehebung | *„Ich weiß nicht, wie ich dabei helfen soll“* und *„nicht gespeichert“* |
| 5:50 | 18. Zusammenfassung | Alle Einstellungen auf einen Blick |

## Intro für weitere Videos

Das animierte Intro mit dem Brainstorm-Logo liegt einzeln unter [`video/brainstorm-intro.mp4`](video/brainstorm-intro.mp4) (5 Sekunden, 1280×720, 25 fps, AAC mono). Mit anderem Titel erzeugst du es neu, siehe [`tools/video`](../tools/video/README.md).
