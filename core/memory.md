# Memory protocol

Every Matriarch skill except `exec` and `goldfish` reads this file. It defines where
memory lives, how to find it and how to write it. Skills hold method only: a
decision, rule, number, owner, ID or URL that belongs to a project goes into
memory, never into a skill or this repository.

## 0. Two memories, any backend

| Memory | Who reads it | Holds |
| --- | --- | --- |
| **Central** (one per project) | everyone on the project | the hub (Rules, People, Environment, Settings, Where we are), Decisions, Open questions, Tasks, Work log, Library |
| **Personal** (one per person) | only its owner | the person's notes and study, drafts not yet shared, personal lessons and reminders |

Each memory has its own backend, set in the user settings `memory.central` and
`memory.personal` ([`settings.md`](settings.md)). The default for both is
`notion`. A backend is an adapter that performs the operations in §7; how each
backend does them is in `backends/<name>.md` next to this file. Read the file
for every backend in use before the first memory operation.

**Never read another person's personal memory**, even if your tool can reach it.

If `memory.personal.backend` is `none`, everything personal goes to the
central memory, as in a one-person project.

## 1. Find the central memory

Every project has its own hub and its own five databases. One installation of
Matriarch serves them all; the session works out which project it is in.

0. **Which personal settings apply.** Your personal settings may hold a
   `projects:` entry per project, each with its own memory backends, models and
   language ([`settings.md`](settings.md) §1). Pick the entry first, because it
   says where the memory is: the project name the owner gave, else
   `matriarch.py which` (by folder path, then by the git remote of the
   repository the session runs in; each repository folder has its own remote).
   Several or none match and the owner named nothing: ask which project.
1. **Registry.** Find the registry named in `memory.central.registry` (§7
   `find_registry`), using the backend those settings give. One row is one
   project. Read its exact property names once.
2. **Pick the project row**, in this order:
   1. the project name or hub address the owner gave, or the `projects:` entry
      name from step 0;
   2. the row whose `Repo` matches the git remote (compare `owner/name`, ignore
      `.git` and the protocol). `Repo` may list several repositories,
      comma-separated, when a project spans a frontend and a backend;
   3. otherwise ask the owner one question: which project (list the Active
      rows). Never pick a project silently.
   No registry, or no matching row: tell the owner and offer `setup`.
3. **Read the row:** `Hub`, `Repo`, `Spec folder`, `Build command`,
   `Data sources` (one line per database: `decisions=<backend address>`), `Map`
   (only for adopted hubs: how their names map to the names below).
4. **Read the hub page.** It holds Start here, Rules, People, Environment, Settings and Where we are.
   Follow its rules for project facts and conventions. If the hub and this file
   disagree, the hub wins for project facts but never over Matriarch's
   invariants ([`settings.md`](settings.md) §0); tell the owner about the
   mismatch.

## 2. The databases

These are the standard schemas `setup` creates. An adopted hub may use other
names; use the registry `Map` and the fetched schema, and map by meaning.
Before the first write to a database in a session, fetch its data source to see
the exact property names and select options. Never add a select option on your
own; use one that exists or ask the owner.

People fields are **text**, not user accounts, because deciders and stakeholders
are often not in the workspace.

**Decisions**

| Property | Type | Values |
| --- | --- | --- |
| Decision | title | one line |
| ID | text | `<AREA>-D<NN>`, see [`ids.md`](ids.md) |
| Status | select | Decided, Proposed, Assumption, Superseded, Withdrawn |
| Area | select | the project's areas |
| Decided by | text | the person with authority |
| Date | date | |
| Statement | text | the block in §4 |
| Waiting on | text | an approval still owed |
| Source | text | link, meeting, file, or "<owner> in chat, <date>" |
| Ref | text | task ID, PR, `DEC`, `NEW` |
| Superseded by | relation | → Decisions |

**Open questions**

| Property | Type | Values |
| --- | --- | --- |
| Question | title | |
| ID | text | `<AREA>-Q<NN>` |
| Status | select | Open, Answered, Dropped |
| Owner | text | who must answer |
| Area | select | same options as Decisions |
| Blocks | text | task IDs, comma-separated |
| Needed by | date | |
| Asked on | date | |
| Answer | text | with its source |
| Decision | relation | → Decisions |

**Tasks**

| Property | Type | Values |
| --- | --- | --- |
| Task | title | |
| ID | text | `<AREA>-<KIND>-<NN>`, unique ([`ids.md`](ids.md)) |
| Status | select | Backlog, Ready, In progress, Blocked, In review, Done |
| Owner | text | |
| Area | select | same options as Decisions |
| Issue | url | |
| PR | url | |
| Spec | text | repo-relative path |
| Blocked by | text | task IDs or a person |
| Next step | text | |
| Notes | text | |
| Progress | text | one line per sub-task, see below |
| Mode | select | quick, standard, critical (`models.md` §3) |

`Progress` is the structured state of the task's sub-tasks, so any session can
resume. One line per sub-task, rewritten in place as it moves:

```
<sub-task ID> · <part A|B> · round <n> · base <sha> · tests <sha or "checksum"> · code <sha or -> · <waiting exec | in check | approved | done>
```

**Work log**

| Property | Type | Values |
| --- | --- | --- |
| Entry | title | `<Ref> — <one-line goal>` |
| Date | date | |
| Type | select | Task, Review, Decision, Planning, Research, Discussion, Setup |
| Status | select | In progress, Done, Blocked, Changes requested, Held, Stopped, Archived |
| Ref | text | |
| Who | text | the owner of the session |
| Tool | select | Claude Code, claude.ai, Cowork, Codex, ChatGPT |
| Model | text | |
| Session | text | the session name |
| PR | url | |
| Summary | text | |
| Hub update | checkbox | ticked when "Where we are" must change |

A row's page body holds long output: full reports, review packets and their
findings pages.

**Library**

| Property | Type | Values |
| --- | --- | --- |
| Title | title | |
| Type | select | Design, Research, Reference, Meeting, Board, Lesson |
| Area | select | same options as Decisions |
| Link | url | |
| Summary | text | |
| Read when | text | |
| Full text inside | checkbox | |

**Personal** (one database, in the person's personal memory)

| Property | Type | Values |
| --- | --- | --- |
| Title | title | |
| Type | select | Note, Study, Lesson, Draft decision, Draft question, Reminder |
| Project | text | the project name, or empty for general |
| Area | text | |
| Date | date | |
| Status | select | Open, Shared, Done, Dropped |
| Shared as | text | the ID of the central row it became |
| Body | text | short text; long text goes in the row's page |

## 3. Read rules

- **Archived rows** (Work log rows rolled into a weekly summary by `tidy`) are
  left out of every query unless you are looking for history.
- **Query, do not read everything.** Filter by Area, Status, Owner, ID or Ref,
  and open only the rows you need. Decisions you rely on: Status not Superseded
  or Withdrawn.
- **One database per query.** A skill that needs several databases (`status`,
  `tidy`) runs one query for each and joins the results itself. Some backends
  refuse a query across databases (`backends/notion.md`).
- **Status words carry meaning.** Decided: settled. Proposed: the person in
  `Decided by` still has to decide; do not build on it as settled. Assumption: a
  guess someone must confirm. Never hide `Waiting on` behind a status.
- **Repo vs memory.** The repository wins for what the code does; memory wins
  for what was decided. When they disagree, record the mismatch (an Open
  question, or a note on your Work log row) and tell the owner.
- **Recency is context, not proof.** If two rows conflict, say so; do not pick
  one silently.

## 4. Write rules

- **Write it in the same turn.** A decision that is not written down did not
  happen. Do not batch writes to the end of a session.
- **Own rows only, with a short list of exceptions.** Sessions run in parallel.
  Create new rows freely; edit only rows your session created, except:
  - Tasks: `Status`, `Next step`, `PR`, `Blocked by` of the task your session
    works on (`plan`, `fix`, and `review` for its PR's task); `plan`, `fix` and
    `check` also write `Progress` and the `Locked tests:` line in `Notes` of the
    task they work on; `status` may set
    `Next step`, `Blocked by`, `Spec` and `Status` on any task when planning;
  - Decisions: `Status` and `Superseded by` when the owner supersedes,
    withdraws, or accepts a Proposed row (`Status` → Decided);
  - Open questions: `Status`, `Answer` and `Decision` when an answer arrives.
  - Work log: `status` clears `Hub update` after it updates the hub;
  - other databases the hub lists for market or customer facts: `discuss`
    may update a row's facts and its date, with the source;
  - Library area guides: `docs` may update a guide another session wrote; it
    keeps the old text in a `## History` section with the date, session and what
    changed;
  - Work log rows: a scheduled `tidy` run may apply the fixes listed in
    `project.tidy.safe_fixes` and nothing else;
  - any row: `tidy` may apply a correction the owner approved in that session,
    and notes it in the row's page (`Tidy <date>: <what changed>`).
  Never edit another session's Work log row otherwise, and never rewrite any
  Statement.
- **Claim before you work.** Before setting a task In progress, query Work log
  for `Ref` = the task ID, `Type` = Task and Status = In progress. If one exists, stop and ask
  the owner whether to continue that session's work or wait.
- **Unique IDs.** Make IDs per [`ids.md`](ids.md): after creating a row with an
  ID, query by it again; if two rows share it, give yours the next free number
  and tell the owner.
- **History stays.** Never rewrite a decision. Set the old row to Superseded
  (fill `Superseded by`) and add a new row.
- **Decide only within your owner's authority.** The hub's People section says
  who decides what. A decision outside the owner's call is written as Proposed
  with the real decider in `Decided by`, plus an Open question for that person.
- **Mark guesses.** Anything not confirmed by a person or a source is
  Assumption.
- **Self-contained rows.** A row must make sense to a session that never saw
  this chat. See [`../standards/memory-row.md`](../standards/memory-row.md).
- **Decision Statement block** (use it in `Statement`):

  ```
  Decision: <one line>
  Status: Decided (<who>, <date>) | Proposed (<who decides>) | Assumption
  Context: <why now, what breaks if wrong>
  Options: A … / B … / wait … (one line each)
  Chosen: <option> because <one line>
  Would change it: <fact>
  Sources: <docs, meetings, links with dates>
  ```

## 4b. What goes where

- **Central:** anything another person or session needs: decisions (Decided,
  Proposed, Assumption), open questions, tasks and their progress, every session's
  Work log row, area guides, settings, rules.
- **Personal:** the owner's study notes, half-formed ideas, drafts the owner does
  not want to show yet, personal lessons and reminders.
- When unsure, ask the owner one question: "keep this to yourself, or share it
  with the team?" Default to central for anything that changes how others work.
- **Sharing** moves a personal row into the central memory when the owner says
  so (`status`, action "share"): create the central row (with its ID), then set
  the personal row to Status = Shared and `Shared as` = that ID. Never share
  without the owner's word.
- Reading: sessions read the central memory and the current person's personal
  memory for the project. A personal row is context for this person, never a
  fact for the team: do not quote or copy it into central rows, specs, prompts,
  packets, goldfish inputs, commit messages or pull requests without sharing it
  first.

## 5. No memory tool in this session

Say so in one line, keep working, and end your final message with every update
you would have made as a ready-to-paste block, one entry per row:

```
[Decisions] new row
Decision: …
Status: …
[Work log] update row "<Entry>"
Status: …
Summary: …
```

## 6. Connecting a backend

See `backends/<name>.md` for setup. For Notion:

- **claude.ai:** connect the Notion connector.
- **Claude Code:** the plugin declares the Notion MCP server; run `/mcp` once
  and log in. Without the plugin:
  `claude mcp add --scope user --transport http notion https://mcp.notion.com/mcp`.
- **Codex:** in `~/.codex/config.toml` add `[mcp_servers.notion]` with
  `url = "https://mcp.notion.com/mcp"`, then `codex mcp login notion`. Goldfish
  runs switch it off (`core/goldfish.md` §2).
- **ChatGPT:** enable the Notion connector for the chat, where your plan allows
  it. If it is read-only, use the ready-to-paste block in §5.
Never put memory credentials or setup in a project repository.

## 7. Operations every backend provides

| Operation | Does |
| --- | --- |
| `find_registry` | locate the registry of projects |
| `read_page(address)` | read a page (the hub, a row's page) |
| `schema(database)` | the exact property names, types and options |
| `query(database, filter)` | rows matching property filters, newest first |
| `create_row(database, properties, body)` | add a row; returns its address |
| `update_row(address, properties)` | change properties of an existing row |
| `child_page(address, title, body)` | add a page under a row (reports, prompts, packets, findings) |
| `edit_page(address, section, text)` | replace one section of a page (the hub's Where we are, Settings) |

Skills name these operations by meaning ("query Decisions for the Area"); the
backend file says how.
