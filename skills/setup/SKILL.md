---
name: setup
description: Give a project its Matriarch memory - create or adopt the hub and its databases, register it, and write the project settings. Use once per project, or to connect an existing handoff page.
license: Apache-2.0
disable-model-invocation: true
---

# matriarch:setup — give a project a memory

## Before you start

Matriarch's shared files live in the plugin root (`ROOT`): in Claude Code
`${CLAUDE_PLUGIN_ROOT}`; in other tools two folders above this file; when this
skill was uploaded alone (claude.ai), the `matriarch/` folder next to this file.
Read `ROOT/core/memory.md`, `ROOT/core/settings.md`, `ROOT/core/session.md` and
`ROOT/core/voice.md` now, and `ROOT/core/backends/<name>.md` for each backend in
`memory.central` and `memory.personal`. This skill needs the tool for those
backends; without it, stop and say how to connect it (`memory.md` §6).

Session name: `<Project> · setup`.

## 1. The registry

1. Find the registry (`memory.md` §1; for `files`, the `registry/` folder under
   `memory.central.path`).
2. **Joining a project someone else set up?** If the registry has a row for this
   project, go straight to §2c. If you cannot see a registry but the project
   has a team, ask the owner to share the `Matriarch` page with you; do not
   create a second registry.
3. Missing: ask the owner one question: where to create it (Notion default: a
   new top-level page `Matriarch`, private until shared with the team; files:
   `memory.central.path`, which must be outside any product repository). Inside
   it, create a database titled exactly as `memory.central.registry` (default
   `Matriarch · Projects`); every session finds it by that title. Give it:
   `Name` (title),
   `Hub` (URL), `Repo` (text, `owner/name`; several comma-separated when the project spans repositories), `Spec folder` (text, default
   `docs/specs/`), `Build command` (text), `Data sources` (text), `Map` (text),
   `Status` (select: Active, Paused, Archived), `Notes` (text).

## 2. New or existing project?

First ask one question: which stage the project is in, new, existing and small,
or existing and large (`ROOT/core/start.md`). Once the hub exists, write it in
the hub's Environment section (`Stage: …`). Use that stage's proposed settings
when you go through the project settings, and end with its first steps.

Then ask one question: create a new hub, or adopt an existing page (give its
link)?

### 2a. New hub

Gather, one question at a time (skip what the owner already said): project
name; repository (`owner/name`) if any; the owner's name;
who decides what; the spec folder; the build and test command; the Areas
(5–8, each with a 2–4 letter code for IDs, such as ORD Orders, PAY Payments,
AUTH Accounts; they become `project.ids.areas` and the Area select options).

Create a page `<Project>'s Handoff` under the registry's parent with:

````markdown
> Start here. This page is the project memory for <Project>. Every session reads
> it first, then queries only the database rows its job needs. Method lives in
> the Matriarch skills; facts live here.

# Rules
- Memory lives in these databases, not in chat. A decision that is not written
  down did not happen.
- Query, do not read everything. Change only your own rows, except as
  Matriarch's memory protocol lists.
- Decided / Proposed / Assumption / Superseded mean what they say.
- <project rules the owner gave, each with its date and source>

# People
- <Owner> — <role>; decides <areas>.
- <others> — <role>; decides <areas>. Who reviews whom: <rule>.

# Environment
- <how to build and run locally, modules, where working files live>

# Settings
```yaml
project:
  <only the keys that differ from ROOT/settings/defaults.yaml>
```

# Where we are (<date>)
- <filled by status>
````

Under the hub create the five databases (`files`: the five folders and
`hub.md`, `ROOT/core/backends/files.md`) with exactly the properties, types and
options in `ROOT/core/memory.md` §2 (Area options from the owner's list; create
the two relations after both databases exist). Fill the registry row: Name,
Hub, Repo, Spec folder, Build command, Status = Active, and `Data sources` as
five lines `decisions=…`, `questions=…`, `tasks=…`, `log=…`, `library=…`.

Then go through the project settings with the owner, one question per group,
showing the default and asking only where it may differ: IDs (areas),
confidentiality, the default review mode, tests (first, lock), commits (by, attribution, messages), merge, review panels and
rounds. Write only the differences into the Settings block, and a Decisions row
`Setting <key> = <value>` for each, in the Area that the setting is about, or
the first Area when it applies to the whole project.

### 2b. Adopt an existing hub

1. Fetch the page and its child databases; fetch each data source's schema.
2. Map them by meaning to the five standard databases. List each standard
   property with no match.
3. Show the mapping as a short table and ask one question: add the missing
   properties (recommended when few), or keep the schema as is. Never rename or
   delete their properties.
4. Write the registry row with `Data sources` and a `Map` text such as
   `log=Session log; log.Entry=Name`. Add the `Hub update` checkbox to their work
   log if it is missing.
5. Add the missing hub sections (Rules, People, Environment, Settings, Where we
   are) without rewriting existing text. Derive Settings from the hub's existing
   rules (for example, tests kept out of git → `tests.lock: checksum`) and
   confirm each with the owner.
6. If the project used older per-project skills, list the project facts in them
   that are not on the hub yet, and offer to move them. Do not edit those skills.

### 2c. Personal memory and settings

Personal memory is per person, so every team member runs this part once for
themselves, also on a project someone else set up.

1. Unless `memory.personal.backend` is `none`, find the personal memory
   (Notion: `memory.personal.url`; files: `memory.personal.path`). Missing:
   create it with the `Personal` database (`memory.md` §2). In Notion, keep the
   page private to its owner and write its URL to `memory.personal.url`.
   For `files`, refuse a personal path that is inside or contains the central
   path, is inside a git repository with a shared remote or a product
   repository, or is inside `~/.matriarch/`; ask for another.
2. Settings: see below.


If `~/.matriarch/config.yaml` (or a `# Matriarch settings` block in chat-app
instructions) does not exist yet, ask the owner for `user.language`,
`user.explain` and, only if they do not want the Notion defaults, `memory.*`;
then create the file in tools that can reach it, or give the
block to paste. Personal settings never go on the hub: each team member has
their own.

### 2c-bis. This project's personal settings

If this project needs personal settings that differ from the owner's others
(memory on this machine for client code, other models, another language), add a
`projects:` entry for it to the user settings with a `match` rule: the folder of
its repository (`path`) or its git remote (`repo`). Run `matriarch.py which
--user <file>` from the repository folder to confirm it matches, and
`matriarch.py config` to validate.

### 2d. Weekly tidy

Offer once to schedule the weekly tidy (the `tidy` skill, section "Scheduling
it"): it keeps memory short and reports what needs the
owner. Only with the owner's yes.

## 3. Check and finish

1. Read back the registry row; fetch each data source to prove access and check
   the schema (`files`: `query` each folder); validate the settings with
   `python3 ROOT/core/tools/matriarch.py config --user <file> --project <file>`
   where code runs (by hand against `ROOT/settings/schema.json` otherwise), and fix
   every error and broken invariant with the owner before finishing.
2. Add a Work log row: `Setup — Matriarch memory`, Type = Setup, Status = Done,
   Summary = what was created, mapped and set.
3. Tell the owner in 3 lines: where the hub is, what was created or mapped, and
   the next command from the stage's first steps (`ROOT/core/start.md`).
   For a team, remind the owner to share the `Matriarch` page (registry and
   hub) with the team; each teammate then runs `setup` for §2c only.
