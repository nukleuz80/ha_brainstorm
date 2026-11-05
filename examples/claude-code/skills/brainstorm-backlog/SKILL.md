---
name: brainstorm-backlog
description: Work through a Brainstorm Hub category as the task backlog of a coding project, over the Home Assistant MCP server. Use when the user says "next task", "work on the backlog", "what is open in Brainstorm", or asks to tick off or note a task in Brainstorm.
---

# Brainstorm Hub as a backlog for coding agents

Brainstorm Hub (Home Assistant integration `brainstorm`) keeps ideas in
categories. One category, shared with your Home Assistant user, is the backlog
of the project you are working on. You read it, implement entries, and tick
them off with a short result note. The person decides what goes in; you never
delete anything.

## Setup the person has done

- A Home Assistant MCP server is connected, for example
  [ha-mcp](https://github.com/homeassistant-ai/ha-mcp). Its token belongs to a
  user of its own for the AI (for example "Claude"), not to the person.
  With the HA-MCP custom component (server inside Home Assistant) that user
  is an administrator; standalone ha-mcp also works with a user without
  admin rights, but then its admin-only tools fail. Brainstorm's actions work
  either way.
- Brainstorm privacy is on, and the person shared the backlog category with
  that user, with *Edit* if you may tick entries off.
- The category name is in the project instructions (CLAUDE.md, AGENTS.md).
  If it is missing, ask once and suggest writing it there.

## Reading the backlog

Call the action `brainstorm.get_ideas` with a response, over the MCP server's
service tool (in ha-mcp: `ha_call_service`, `return_response: true`):

```json
{"domain": "brainstorm", "service": "get_ideas", "return_response": true,
 "data": {"category": "<backlog category>"}}
```

Each idea has `id`, `text`, `priority` (`urgent`, `high`, `medium`, `low`),
`parent_id`, `order`, `due` and, once ticked off, `result`. Entries with a
`parent_id` are steps of a larger entry: work on the steps in their `order`,
and on the parent only when its steps are done.

The action only returns what your user may see. Never read
`.storage/brainstorm.storage` instead: it holds the private ideas of everyone
in the house, and Home Assistant overwrites changes to it.

## Choosing the next entry

1. Take what the person names. Otherwise suggest the entry with the highest
   priority whose earlier steps are done, and say in one line why.
2. Read conditions in the text, such as "only after step 1 runs in daily
   use" or "check X first". Do the check first and report it; do not skip it.
3. An entry that is too vague to implement gets one clarifying question,
   not a guess.

## Marking the entry you work on

When you start on an entry, mark it so the person sees it in the cards
(🔧 In progress, with your user's name):

```json
{"domain": "brainstorm", "service": "update_idea",
 "data": {"id": "<id>", "in_progress": true}}
```

Ticking the entry off removes the mark by itself. If you stop without
finishing, remove it with `"in_progress": false` and say what is missing.
Mark only the entry you are actually working on. It needs Brainstorm 1.7.10
or later; leave it out on older versions.

## Ticking off

Only tick off what is implemented, tested and committed (and pushed or
released, if the project does that). Then call:

```json
{"domain": "brainstorm", "service": "update_idea",
 "data": {"id": "<id>", "status": "completed",
          "result": "v1.6.18: field result in update_idea, both cards show it, 693 tests pass"}}
```

- `result` says in one or two sentences what came of it: version or commit,
  what changed, how it was tested, what is left open. At most 1000
  characters. It needs Brainstorm 1.6.18 or later; leave it out on older
  versions.
- Name every entry you ticked off in your reply to the person.
- Partly done: leave the entry open and tell the person what is missing.
  Add new entries only when the person asks for it.

## What you never do

- Delete entries or categories, change shares or settings. Deleting stays
  with the person, and the actions refuse it for shared entries anyway.
- Tick off something that is not finished or not tested.
- Work around a refused action (`no_access_idea`, `admin_only`). Tell the
  person which share is missing instead.
