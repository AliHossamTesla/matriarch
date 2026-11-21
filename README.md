# Matriarch

[![tests](https://github.com/AliHossamTesla/Matriarch/actions/workflows/tests.yml/badge.svg)](https://github.com/AliHossamTesla/Matriarch/actions/workflows/tests.yml)

**Design with an elephant. Review with a goldfish. Remember with the matriarch.**

Matriarch is a plugin for AI coding and chat assistants. It builds on Google's
[Elephant-Goldfish Model](https://github.com/google/elephant-goldfish-model)
(EGM), where a context-rich session designs and fresh reviewers with no history
check the result. Matriarch adds what EGM does not have: **a project memory that
outlives every chat**, and **review gates that code can check**.

> **Status: v0.2, pre-beta.** The method ran by hand on real projects before
> this plugin existed; the plugin itself has not yet been run end to end on a
> real project. See [Guarantees and limits](#guarantees-and-limits).

## The idea

| Role | What it is |
| --- | --- |
| **Matriarch** | The memory: decisions, open questions, tasks, a work log and a library, per project, plus a personal memory per person. It outlives every session. |
| **Elephant** | Any session that loads the memory before it works and writes back what it learned before it ends. |
| **Goldfish** | A fresh reviewer that sees only the artifact, the code and the decisions it is handed. It never reads the memory, so it catches what the elephant stopped noticing. |
| **You** | You decide. Decisions that belong to someone else stay Proposed. |

Works in **Claude Code, Codex, claude.ai and ChatGPT**. A goldfish can run in a
different tool or model from the elephant, through a self-contained review
packet.

## How a task runs

```
plan  (one chat: thinks, never writes code)
  ├─ shapes the idea, closes every open point with you, writes the spec
  ├─ goldfish panel on the spec ──► gate
  ├─ splits it into sub-tasks, one implementer prompt each
  │
  │   for each sub-task:
  │     exec  (another chat, in the repo)   Part A: tests ──► check ──► lock tests
  │                                         Part B: code  ──► check ──► commit
  │
  └─ check on the whole task ──► pull request ──► review
```

`check` runs inside the plan chat, because plan knows why every choice was made.
Each review point has its own goldfish panel (business, code quality, security,
spec compliance and more), and a deterministic **gate** decides whether work may
continue: `PASS`, `PASS_WITH_ACTIONS`, `PASS_WITH_WAIVERS`, `FAIL` or
`INCOMPLETE`.

## Commands

| Command | Use it to |
| --- | --- |
| `matriarch:doctor` | check that tools, settings and memory are ready here, and how to fix what is not |
| `matriarch:setup` | give a project its memory, or adopt an existing handoff page; choose the settings |
| `matriarch:status` | see where things stand, order the work, keep "Where we are" current |
| `matriarch:plan <ID or idea>` | the brain of one task: from idea to spec, sub-tasks, prompts and reviews |
| `matriarch:exec <sub-task ID>` | the hands: in another chat, build one sub-task exactly as its prompt says |
| `matriarch:check <ID>` | inside `plan`: review a sub-task or the whole task with a goldfish panel |
| `matriarch:fix <bug>` | reproduce, find the root cause, fix through exec and check |
| `matriarch:docs <area>` | learn an unfamiliar area together and write a guide every session reuses |
| `matriarch:discuss <topic>` | think something through; switch to a structured decision when needed |
| `matriarch:review <PR or doc>` | review a teammate's work; post and merge only on your word |
| `matriarch:tidy` | clean the memory and check that docs, code and decisions agree; `tidy scheduled` runs weekly |
| `matriarch:goldfish <packet>` | in a fresh chat: be the goldfish for one review packet |

In claude.ai, where skills have no namespace, they are named `matriarch-plan`,
`matriarch-exec` and so on.

## Quick start

1. Check the [requirements](#requirements).
2. [Install](#install) the plugin in your tool and connect Notion.
3. In the repository you want to work on, run `matriarch:doctor`. Fix what it
   reports.
4. Run `matriarch:setup` once for the project. It creates the project's memory
   in Notion (or adopts a page you already have), then shows the main settings
   in one short table with what it proposes and why, and adjusts them to your
   answer.
5. Run `matriarch:status` to see where things stand, then `matriarch:plan` with
   a small first task.

If something goes wrong, open an issue with the output of
`python3 core/tools/matriarch.py doctor` (it holds no secrets, but check it for
paths you do not want to share).

## Requirements

- **Python 3.10 or later** with PyYAML (`pip install pyyaml`). The gate,
  settings checks and `doctor` run with it.
- **git**, and the **GitHub CLI** signed in (`gh auth login`) for reviews,
  pull requests and merges.
- **A Notion account** with the Notion connector (or MCP server) in your tool.
  Matriarch creates its pages there. To work offline, choose the `files`
  backend in your settings instead.

## Install

Every tool needs access to your memory backend (Notion by default).

**Claude Code** (2.1.271 or later, for read-only goldfish agents):

```sh
claude plugin marketplace add AliHossamTesla/Matriarch
claude plugin install matriarch@matriarch
```

The plugin declares the Notion MCP server; run `/mcp` once and log in.

**Codex CLI**:

```sh
codex plugin marketplace add AliHossamTesla/Matriarch
codex plugin add matriarch@matriarch
```

Add Notion to `~/.codex/config.toml` (`[mcp_servers.notion]` with
`url = "https://mcp.notion.com/mcp"`), then `codex mcp login notion`.

**claude.ai**: clone the repository, run `python3 scripts/build.py`, then upload the zips from
`dist/claude-ai/` under Settings → Capabilities → Skills. Each zip carries the
shared files it needs. Connect the Notion connector.

**ChatGPT**: the plugin needs a local executor, so it runs in the Codex and
ChatGPT desktop apps (install from the marketplace above), not in ChatGPT web
chats. A web chat can still act as a goldfish: paste a review packet into a
temporary chat; no plugin needed.

## First run

Start with `matriarch:doctor`. From a clone of this repository you can also run
`python3 core/tools/matriarch.py doctor --cwd <your project folder>`. It checks
the tools, the settings and the memory, and says how to fix each problem; checks
marked `info` (Notion) are done by the `doctor` command through the connector.

Where to start depends on the project. [`core/start.md`](core/start.md) gives
the first steps for each case and the daily loop:

| Stage | Start with |
| --- | --- |
| New project | `setup`, then `discuss` the vision and the big choices, then a first `plan` task for the repository skeleton and its `AGENTS.md` |
| Existing, small codebase | `setup`, one `docs` pass over the code, then confirm the decisions the code already made |
| Large enterprise codebase | `setup` with confidential settings, `docs environment`, then `docs <area>` just before the first task in each area |

After that, every project runs the same loop: `status` in the morning, `plan` and
`exec` for work, `review` for teammates, `tidy` weekly.

## Memory

- **Central memory**, one per project, shared by the team: the hub (rules,
  people, environment, settings, where we are) and five databases: Decisions,
  Open questions, Tasks, Work log, Library.
- **Personal memory**, one per person: notes, study, drafts not yet shared.
  Nobody else reads it; a draft reaches the team only when you share it.
- **Backends:** Notion (default for both) or plain Markdown `files` (offline,
  can live in its own git repository). A registry lets one setup serve all your
  projects.
- **Many projects, one install:** every project has its own hub and databases.
  A session finds its project from the repository it runs in (each repository
  folder has its own git remote) or from the name you give. Personal settings
  can differ per project (`projects:` in your user settings), so a work project
  can keep its memory on your machine while a side project uses Notion.
- **IDs that say what things are:** tasks `ORD-API-03`, sub-tasks
  `ORD-API-03.data`, bugs `PAY-FIX-07`, decisions `AUTH-D04`.

## Settings

Everything that differs between people or projects is a setting.
[`settings/defaults.yaml`](settings/defaults.yaml) lists every key with
comments, in three layers:

| Layer | Where | Examples |
| --- | --- | --- |
| Defaults | ships with the plugin | all keys |
| Personal | `~/.matriarch/config.yaml` | reply language, memory backends, model per session and lens, weekly tidy time |
| Project | the "Settings" section of the project hub | review panels and rounds, review mode, test locking, commit and merge rules, confidentiality, IDs |

**Settings dashboard:** open [`dashboard/settings.html`](dashboard/settings.html)
in a browser (offline, nothing leaves the page). It shows every setting with its
explanation, checks the schema and the invariants as you type, previews which
goldfish run on which model, estimates the goldfish runs for a task in each
mode, and exports your `config.yaml` and the hub's Settings block. Your work is
kept in the browser between visits. To load the settings you already have, if you have a
`~/.matriarch/config.yaml`, run
`python3 core/tools/matriarch.py config --user ~/.matriarch/config.yaml` (add
`--project <hub settings file>`) and paste its whole output into Import.

`python3 core/tools/matriarch.py config` validates them and rejects settings that
would weaken a review. Model tiers (strong, standard, fast), the advisor, and the
quick / standard / critical review modes are described in
[`core/models.md`](core/models.md).

## Guarantees and limits

Enforced with code where code runs (Claude Code, Codex):

- the review gate ([`core/gate.md`](core/gate.md), `matriarch.py gate`): the
  panel comes from the settings, not from the agent; a missing lens or an open
  Blocker never passes; work moves on only after enough clean rounds on the same
  version, and waivers need an owner, a reason, a review date and a decision;
- settings validation and its invariants (`matriarch.py config`), including
  personal and central memory folders kept apart;
- confidentiality before anything leaves the machine or goes into memory
  (`matriarch.py export`, with a secret and personal-data scan);
- read-only reviewer agents in Claude Code: no write tools, no MCP, no
  `CLAUDE.md`;
- merges bound to the reviewed commit (GitHub's merge `sha` guard).

Instructions the model follows, not guarantees:

- **One writer per task.** Notion and plain files have no locks. The claim check
  lowers the chance that two sessions work on one task at once; it cannot rule
  it out. Run one session per task at a time.
- Goldfish isolation outside Claude Code: Codex still loads `AGENTS.md`, and a
  chat app may inject your memory unless you use an incognito or temporary chat.
- Everything in chat apps without code execution, where the model applies the
  gate and the settings itself.

Larger items, such as atomic task claims and an offline event journal, are
parked in [`docs/roadmap.md`](docs/roadmap.md) with the reason for each.

## Layout

```
core/          protocols: memory, sessions, goldfish, review loop, gate, settings,
               models, IDs, starting guides
core/backends/ notion and files backends, files_tool.py
core/tools/    matriarch.py: gate, config, which, doctor, scan, export, sha256
personas/      goldfish reviewer prompts
standards/     rubrics, the spec template, the implementer prompt
settings/      defaults.yaml and its JSON schema
dashboard/     settings.html (generated) and its template
skills/        one folder per command
scripts/       build.py: Claude Code agents, plugin manifests, claude.ai zips
docs/          design.md (why it works this way), roadmap.md
```

## Development

```sh
pip install -e ".[dev]"
python3 scripts/build.py --check   # generated files are current
python3 -m pytest -q               # structure, gate, settings and backend tests
python3 scripts/build.py           # regenerate adapters and the claude.ai zips
```

Rules for contributors are in [`AGENTS.md`](AGENTS.md); the design and the
alternatives considered are in [`docs/design.md`](docs/design.md).

## License

Apache-2.0. Includes material adapted from the Elephant-Goldfish Model,
Copyright 2026 Google LLC; see [`NOTICE`](NOTICE). Not affiliated with Google.

## Contributing

Issues and pull requests are welcome. Read [`CONTRIBUTING.md`](CONTRIBUTING.md)
first; every change raises the version and is listed in
[`CHANGELOG.md`](CHANGELOG.md). Report security problems privately
([`SECURITY.md`](SECURITY.md)).
