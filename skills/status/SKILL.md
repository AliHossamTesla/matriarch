---
name: status
description: Where are we - load the project memory, report what moved, what is blocked and on whom, what waits on the owner, keep "Where we are" current, order the backlog and hand off to the right session. Use when the owner asks for status, wants to plan the week, or starts the day.
license: Apache-2.0
---

# matriarch:status — where are we

## Before you start

Matriarch's shared files live in the plugin root (`ROOT`): in Claude Code
`${CLAUDE_PLUGIN_ROOT}`; in other tools two folders above this file; when this
skill was uploaded alone (claude.ai), the `matriarch/` folder next to this file.
Read `ROOT/core/session.md`, `ROOT/core/memory.md`, `ROOT/core/settings.md` and
`ROOT/core/voice.md` now.

This session holds the big picture. It writes no production code and no specs.
It is the only session that edits the hub's **Where we are**, **Rules** and
**Settings**.

## 1. Load

`session.md` §1–3. Name: `<Project> · status · <topic>`, Type = Planning,
Ref = `STATUS`. Then query, one database per query (`memory.md` §3):

- **Tasks** with Status in (In progress, Blocked, In review, Ready);
- **Open questions** with Status = Open, sorted by Needed by;
- **Decisions** with Status in (Proposed, Assumption) and a `Waiting on`;
- **Work log** rows dated on or after the "Where we are (<date>)" heading, and
  every row with `Hub update` ticked;
- **Work log** rows with Status = In progress older than 2 days (likely left
  open).

Tell the owner in 4–6 lines: what moved, what is blocked and on whom, what waits
on the owner, sessions left open, open personal drafts for this project, and one
suggestion for what to do next. Ask
one question.

## 2. What the owner may ask here

- **Order the work.** Re-rank Ready and Backlog tasks by what unblocks the most;
  set `Next step` and `Blocked by`. New work that is only an idea goes to
  `matriarch:plan` (it shapes ideas first).
- **Accept or reject proposals** that other sessions left (Proposed decisions,
  answered questions): set Status per `memory.md` §4.
- **Record an answer** someone gave to an Open question: Status = Answered,
  Answer with its source, and the Decisions row it produces.
- **Prepare a meeting** with a person: their Open questions, the Proposed
  decisions waiting on them, and what each blocks.
- **Change a project setting** (`settings.md` §3).
- **Share** a personal row with the team (`memory.md` §4b): show it, ask which
  central row it becomes (decision, question, task or Library), create it with
  its ID, and mark the personal row Shared. Only on the owner's word.
- **Close a stale session row** only when the owner confirms what happened; write
  `Stopped` and the reason.

## 3. Hand off

Give the exact command for a fresh chat, the tool that suits it, and the model
for that session (`ROOT/core/models.md` §2):

| Need | Command |
| --- | --- |
| Plan a task or shape an idea | `matriarch:plan <ID or idea>` |
| Build one sub-task (another chat, in the repo) | `matriarch:exec <sub-task ID>` |
| Fix a bug | `matriarch:fix <bug>` |
| Learn an area of the system | `matriarch:docs <area>` |
| Think something through, no task | `matriarch:discuss <topic>` |
| Review someone's PR or document | `matriarch:review <PR or link>` |
| Clean memory and check drift | `matriarch:tidy` |

## 4. Keep the hub current

1. Re-fetch the hub just before writing. Rewrite **Where we are (<date>)**: one
   line per active stream, then **Blocked**, **Waiting on <person>**, **Next for
   <owner>**. Under 15 lines, facts with row links.
2. Clear `Hub update` on the Work log rows you covered.
3. A new project-wide rule the owner approved goes into **Rules** with its date
   and source.
4. Check that Rules, Settings and People do not contradict Decisions; if they
   do, tell the owner and fix the side the owner says is wrong.

## 5. End

`session.md` §5. The Summary lists what changed in memory.
