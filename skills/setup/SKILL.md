---
name: setup
description: Give a project its Matriarch memory - create or adopt the hub and its databases, register it, and on first use review the main settings with the owner in one short pass and write them. Use once per project, or to connect an existing handoff page.
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
in the settings review (§2e), and end with its first steps.

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

Then run the settings review (§2e) for the project part.

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
instructions) does not exist yet, this is the owner's first setup: run the
settings review (§2e) for the personal part, then create the file in tools that
can reach it, or give the block to paste. Personal settings never go on the
hub: each team member has their own.

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

### 2e. Settings review (first setup)

One short pass over the settings that matter, so the owner starts with values
that fit, not with defaults they never saw. Run it once:

- **personal part** when the owner has no user settings yet (§2c);
- **project part** when the hub is new (§2a), or adopted (§2b) after its Settings
  were derived from the existing rules.

Both parts at once when both apply. When setup runs again on a project that is
already set up, skip this; settings change through `status` or the dashboard
(`dashboard/settings.html`).

1. **Detect before asking.** Fill what you can see, and mark each as detected:
   - `user.language`: the language the owner writes in.
   - `schedule.tidy.timezone`: the machine's time zone, where code runs.
   - `models.tiers`: the tool you are in; keep its defaults unless the tool
     names its models differently.
   - `tests.lock`: `commit` if test files are tracked in git, `checksum` if
     the repository ignores them.
   - `merge`: `self-after-review` if the hub's People lists only the owner,
     else `reviewer`. `merge_method`: what the repository allows, where `gh`
     works.
   - Everything else: the value the stage proposes (`ROOT/core/start.md`), else
     the default.
2. **Show one table** of about ten rows, only these keys (the part that
   applies):

   | Part | Keys |
   | --- | --- |
   | personal | `user.language`, `user.explain`, `memory.central.backend`, `memory.personal.backend`, `schedule.tidy.when` (with `reset` when `before_reset`) |
   | project | `confidentiality.level`, `review.mode`, `tests.first` and `tests.lock`, `commits.by` and `commits.attribution`, `merge` and `merge_method` |

   Columns: `Setting | Proposed | Why` (the why in a few words: "default",
   "detected: tests ignored by git", "large codebase"). Say once that every
   other key keeps its default and can be changed later.
3. **Ask one question:** keep all, or say what to change, in plain words. If
   `schedule.tidy.when` is `before_reset` and `reset` is empty, ask for the
   reset time in the same question (or propose `weekly`).
4. **Apply the answer.** Turn each change into its key; ask only when a change
   is unclear. Validate with
   `python3 ROOT/core/tools/matriarch.py config --user <file> --project <file>`
   where code runs (by hand against `ROOT/settings/schema.json` otherwise). If a
   change breaks an invariant, say which and propose the nearest valid value;
   never loosen an invariant (`ROOT/core/settings.md` §0).
5. **Write only the differences from the defaults:** personal keys to the user
   settings (§2c), project keys to the hub's Settings block with a Decisions row
   `Setting <key> = <value>` for each, in the Area the setting is about, or the
   first Area when it applies to the whole project. End with one line: the
   settings that now differ from the defaults.

## 3. Check and finish

1. Read back the registry row; fetch each data source to prove access and check
   the schema (`files`: `query` each folder); validate the settings with
   `python3 ROOT/core/tools/matriarch.py config --user <file> --project <file>`
   where code runs (by hand against `ROOT/settings/schema.json` otherwise), and fix
   every error and broken invariant with the owner before finishing.
2. Add a Work log row: `Setup — Matriarch memory`, Type = Setup, Status = Done,
   Summary = what was created, mapped and set, and the settings that differ from
   the defaults.
3. Tell the owner in 3 lines: where the hub is, what was created or mapped, and
   the next command from the stage's first steps (`ROOT/core/start.md`).
   For a team, remind the owner to share the `Matriarch` page (registry and
   hub) with the team; each teammate then runs `setup` for §2c only.
