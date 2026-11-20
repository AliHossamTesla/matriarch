# Matriarch: design

- **Status:** v0.2 (first public release)
- **Based on:** [Elephant-Goldfish Model](https://github.com/google/elephant-goldfish-model)
  (Google, Apache-2.0) at commit `72d06f5`.

## 1. Problem

The Elephant-Goldfish Model (EGM) splits AI-assisted work into two roles. The
**Elephant** is a session that holds the project context and drafts the design.
**Goldfish** are fresh reviewers that see only the document and the code, so they
catch the assumptions the Elephant stopped noticing. A human makes the trade-offs.

EGM has one gap: **the Elephant forgets.** In EGM the Elephant is the current
chat. When the chat ends, only the checked-in design document survives. The
decisions behind it, the open questions, who owes what, what happened in the
last session and why an option was rejected all end with the chat. The next
session starts as a goldfish that thinks it is an elephant.

Real projects run for months, in many sessions, in several tools (Claude Code,
claude.ai, Codex, ChatGPT), sometimes in parallel. For example, a task session
in Claude Code, a pull request review in Codex and a pricing decision in a chat
app can all run in the same week. Each needs the same decisions, and each makes
new ones.

## 2. The idea

**The Elephant is not a chat. It is a memory that any session can load.**

A matriarch is the old female who leads an elephant herd. She remembers where
the water is and what danger looks like, for decades, and the herd inherits that
knowledge. In this tool:

- The **matriarch** is the project memory: decisions, open questions, tasks, a
  work log and a library. It outlives every session.
- An **Elephant** is any session that loads that memory before it works and
  writes back what it learned before it ends.
- A **Goldfish** is still a fresh reviewer with no history. It must never read
  the memory freely, because that would make it an elephant. It gets only what
  the Elephant hands it: the artifact, the files, and the decision rows quoted
  as text.
- The **owner** decides. Decisions that belong to someone else stay Proposed.

## 3. Goals and non-goals

Goals:

1. Any session, in any supported tool, can start cold and be working with the
   right context in under a minute, by reading the project hub and querying only
   the rows it needs.
2. Every decision, question, task change and session is written to memory in the
   same turn it happens. If it is not in memory, it did not happen.
3. Goldfish reviews keep EGM's rigor: staged lenses, document standards,
   checkable contests and bounded review rounds.
4. A goldfish can run in a different tool or model from the Elephant (a review
   packet), including tools that cannot start subagents.
5. Skills hold method only. Facts live in memory. One installation serves many
   projects.

Non-goals:

- A website, a marketplace listing, or support for every agent harness.
- Replacing tests, CI or human code review.

## 4. Architecture

```
Central memory (shared; default backend: Notion)
  Matriarch · Projects          registry, one row per project
    └─ <Project> hub page        Start here, Rules, People, Where we are
         ├─ Decisions
         ├─ Open questions
         ├─ Tasks
         ├─ Work log            (rows hold reports and review packets)
         └─ Library

Personal memory (one per person; default backend: Notion)
  Matriarch · Personal          notes, study, drafts, lessons, reminders

This repository (the plugin)
  core/        shared method: memory protocol, session protocol, goldfish rules, voice
  personas/    goldfish reviewer prompts (one file each)
  standards/   rubrics the goldfish grade against, and the spec template
  skills/      one folder per command
  scripts/     build.py generates the per-tool adapters and the claude.ai zips
```

### 4.1 Memory

The full schema and write rules are in [`core/memory.md`](../core/memory.md).

**Two memories.** The central memory is shared by everyone on a project:
decisions, questions, tasks, the work log, the library and the hub. The personal
memory belongs to one person: notes, study, drafts not yet shared, personal
lessons. A session reads the central memory and its own person's personal
memory, never anyone else's. A personal draft becomes a central row only when
its owner shares it. With no personal memory configured, everything goes to the
central one, which is the one-person setup.

**Backends.** Each memory has its own backend, set per person in the user
settings. Both default to Notion. `files` stores one Markdown file per row in a
folder (offline, can live in its own git repository) and works in tools with
file access. Skills use eight operations (`core/memory.md` §7); each backend
file in `core/backends/` says how to perform them. Google Sheets and SQLite are
candidates for later backends.

Key rules:

- **Query, do not read everything.** Filter by Area, Status, Owner or ID.
- **Status words matter:** Decided, Proposed (the named person still decides),
  Assumption, Superseded, Withdrawn.
- **History stays.** A changed decision: the old row becomes Superseded and a
  new row is added.
- **Own rows only.** Sessions run in parallel; a session edits only rows it
  created, plus a short, explicit list of exceptions in `core/memory.md` §4.
- **No memory tool?** Keep working and end with every update as a
  ready-to-paste block.

The **registry** lets one installation serve many projects. A session finds its
project by the repository it runs in (`git remote`) or by the name the owner
gives, then reads the hub and the database IDs from the registry row.
`setup` can create a new hub or adopt an existing one by mapping its
databases.

Project facts (the owner's language, who reviews whom, the spec folder, the
build command, commit rules) live on the hub's **Rules** and **People** sections
and the registry row, never in a skill.

### 4.2 Sessions

Every skill follows [`core/session.md`](../core/session.md): name the session so
it can be resumed; load the registry row, the hub and only the rows the job
needs; log the start; write each decision as it happens; log the end.

### 4.3 Goldfish

[`core/goldfish.md`](../core/goldfish.md) defines how a goldfish starts, in
order of preference:

1. **Subagent** in the same tool. In Claude Code the personas are plugin agents
   with read-only tools, no MCP and no `CLAUDE.md`.
2. **Separate CLI run** (`claude -p`, `codex exec`) with MCP switched off.
3. **Review packet:** a self-contained prompt for one lens (mandates, persona,
   standard, artifact and context files as text, and quoted decisions where the
   lens gets them). The owner pastes it into a fresh incognito or temporary chat
   in any tool and brings the findings back. It needs no plugin, no repository
   and no memory access.

A review in the Elephant's own context is not a goldfish review. If no path is
available, the skill stops and says so.

### 4.4 Skills

Two kinds of session do the building, and they never mix: **plan** thinks and
**exec** writes code.

| Skill | Session | Does |
| --- | --- | --- |
| `setup` | once per project | create or adopt a hub, register it, set project settings |
| `status` | the main planning chat | where we are, order the work, keep the hub current, hand off |
| `plan` | one task, from idea to PR | shape the idea, close every open point, spec, sub-tasks with implementer prompts, review, then check each sub-task and the whole task |
| `exec` | one sub-task, in another chat | follow the prompt: tests (Part A), then code (Part B); report with a status word |
| `check` | inside `plan` | goldfish panel on a sub-task's tests or code, or on the whole task; paste-ready reply for exec |
| `fix` | one bug | reproduce, root cause, failing test, fix through exec and check |
| `docs` | one area | learn an area with the owner and write an area guide |
| `discuss` | no task | think together; structured decision mode with evidence and a pre-mortem |
| `review` | someone else's PR or document | panel, filtered findings, act only on the reviewer's word |
| `tidy` | periodic | memory hygiene and three-way drift (docs, code, decisions) |
| `goldfish` | a fresh chat | run one review packet |
| `doctor` | before first use, or when something fails | check tools, settings, memory and hub; report what to fix |

Shared procedures that are not commands: the review loop
([`core/review.md`](../core/review.md)), resolving findings
([`core/resolve.md`](../core/resolve.md)) and settings
([`core/settings.md`](../core/settings.md)).

### 4.4.1 Review points

Goldfish panels are settings (`project.review.panels`). Defaults:

| Point | When | Lenses |
| --- | --- | --- |
| `spec` | plan, before sub-tasks | comprehension, zoom-out, business, decision-fit, design-critic, implementation-readiness |
| `prompt` | plan, each implementer prompt | implementation-readiness, codebase-fit |
| `tests` | check, after Part A | test-evidence, business, spec-compliance |
| `subtask` | check, after Part B | spec-compliance, code-quality, business, test-evidence |
| `sensitive` | added to subtask and task when the diff is risky | correctness, security |
| `task` | check, whole task | zoom-out, business, spec-compliance, decision-fit, security, test-evidence |
| `pr` | review | spec-compliance, code-quality, correctness, security, test-evidence |
| `doc` | review | comprehension, zoom-out, business, decision-fit, design-critic |
| `area_guide` | docs | comprehension |
| `idea` | plan, shaping | zoom-out, design-critic, decision-fit |
| `decision` | discuss | premortem (pre-mortem, customer, operator, numbers) |

A round is clean when no Blocker or Major is left unsettled. Specs need two clean
rounds in a row; prompts, tests and code need one; after three rounds the owner
decides.

### 4.4.2 Gate, trust and models

- **Review gate** ([`core/gate.md`](../core/gate.md)): one table turns a round's
  lens statuses and resolved findings into `PASS`, `PASS_WITH_ACTIONS`,
  `PASS_WITH_WAIVERS`, `FAIL` or `INCOMPLETE`. A missing lens or an open Blocker
  never passes; a Major continues as a tracked action; waivers are recorded and
  never counted as clean. `core/tools/matriarch.py gate` computes it where code
  runs.
- **Order of trust** ([`core/settings.md`](../core/settings.md) §0): host rules,
  then Matriarch invariants, then project and user settings, then content.
  Instructions found in documents or memory are data, never policy.
- **Confidentiality:** a project can keep code out of memory and require the
  owner's consent before anything goes to another provider.
- **Models** ([`core/models.md`](../core/models.md)): strong, standard and fast
  tiers per session and per lens, the advisor for standard sessions, and a floor
  that keeps lenses which can stop work off small models. Review modes (quick,
  standard, critical) size the review to the task's risk.
- **Doctor and dashboard:** `doctor` checks tools, settings, the memory
  connector, the registry, the hub and its schemas before use, and says how to
  fix each problem. `dashboard/settings.html` is a generated, offline page to edit
  and check settings and to preview panels, models and the goldfish runs a task
  costs in each mode.
- **Starting points** ([`core/start.md`](../core/start.md)): new, small existing
  and large existing codebases start differently, then share one daily loop.

### 4.5 What Matriarch adds to EGM

1. Persistent memory with a registry, own-row rules and history.
2. A decision-fit lens: a goldfish checks the artifact against the decisions the
   Elephant quotes, so a design cannot silently contradict an earlier call.
3. Review packets: cross-tool, cross-model goldfish, also from chat apps.
4. When the evidence against a finding is a decision the goldfish could not see,
   the usual answer is to quote it in the document, which must stand on its
   own.
5. Locked tests: once the owner approves the tests, the implementer may not
   change them, and the review proves it (by commit or by checksum, a setting).
6. Settings in three layers (plugin defaults, user, project hub), so behavior
   that differs between people and projects is configuration, not a fork.
7. An owner-gated task flow with sub-tasks the owner can take himself, and the
   owner's language and style read from the hub.

## 5. Lessons from production use

Before v0.1, the method ran by hand on two real projects for several weeks:
a feature in a large legacy enterprise codebase, and a new multi-tenant SaaS
product built by a small team. What worked and what failed there shapes the
next versions.

### 5.1 Keep

1. **Strict roles.** The Elephant never edits application code. It writes an
   implementer prompt to a file; a tests session writes only tests; an
   implementation session makes them pass without changing them.
2. **Status words from the implementer:** `DONE`, `DONE_WITH_CONCERNS`,
   `NEEDS_CONTEXT`, `BLOCKED`, one line of test results, and a full report in a
   file the Elephant checks against the repository.
3. **A mentor Elephant for large tasks:** one session takes the sub-tasks one by
   one, each its own loop (prompt, result, review, owner approval).
4. **Review rounds with a clear stop rule.** A clean round has no unsettled
   Blocker or Major. Stop after one clean round for prompts, tests and code, and
   after two in a row for a design. Cap at three rounds; then the owner decides.
   The same for fixes: after three failed fixes of one failure, go back to the
   design.
5. **Golden files.** Every new class copies the structure of a named existing
   file. In a legacy codebase this matters more than any style guide.
6. **An environment page:** local setup, modules, build commands and where every
   working file lives. It is what lets a cold session start working at once.
7. **One commit per approved sub-task**, with a message written for the team
   (what changed and why, no task IDs or tool links), approved by the owner.
8. **Every rule carries its date and source.**
9. **Databases, not one long page.** Sessions query the rows they need.
10. **One Work log row per session**, opened at the start and closed at the end,
    instead of one row per small step.
11. **Sub-tasks the owner can do himself,** and "the thing to learn" at the end
    of a review, for an owner who is learning the system.
12. **Project knowledge skills.** Domain method (architecture habits, quality
    gates, business lenses) as skills that hold method only, separate from the
    workflow skills.
13. **Classifying meeting statements** as a decision, a conditional preference,
    a teaching example or an open point before using them.

### 5.2 Avoid

1. **Facts inside skills.** In both projects, rules written into a skill had to
   be changed in two places and drifted. Skills hold method; facts live in
   memory.
2. **Unclosed sessions and schema drift.** Work log rows left In progress, rows
   without a reference, select values outside the schema. Memory needs regular
   maintenance.
3. **One way to lock tests.** Some codebases keep tests out of git; a commit
   cannot lock them. The lock method must be a project setting (commit or
   checksum).
4. **Fixed commit attribution.** Some teams forbid AI attribution lines in
   commit messages. It must be a project rule.

### 5.3 From the egm-chat evaluation

An independent evaluation of a single-chat EGM skill (`egm-chat`, 12 rounds, 33
versions, about 7,700 model runs, 11 Nov 2026) changed the reviewer rules:

1. **"Challenge the proposal" backfires.** Its first version held sound plans
   for gaps they did not have and did worse than no skill. What fixed it: sort
   issues as blocker, fix or note; hold only for a blocker; a blocker only when
   the plan breaks a limit or rule it states; never phrase a fix as a
   precondition; add no requirements; treat stated facts as true; recompute
   figures. Matriarch's voice and goldfish mandates now follow these rules.
2. **Strong models already find nearly every real problem.** The value of the
   method is the right proceed-or-hold decision and fewer invented blockers, not
   more findings. Extra lenses add angles, not recall, so panels stay settings.
3. **Weak models approve flawed plans.** Important lenses should not run on
   small, fast models (see model settings).
4. **Measure, do not guess.** Changes to personas should be tested against cases
   with answer keys and kept only when they beat run-to-run noise (parked in the
   roadmap).

### 5.4 From an independent engineering audit

A static audit of v0.1 (16 Nov 2026) found that the review gate counted a round
as clean even when a lens had not run, treated waivers as clean, and left Major
findings both blocking and non-blocking in different files; that merges were not
bound to the reviewed commit; and that hub text could override the protocol.
Those are fixed (§4.4.2). Its larger proposals (atomic claims, an event journal,
immutable review records, a policy state machine) are parked in the roadmap.

## 6. Alternatives considered

- **Memory as files inside the product repository.** Versioned with the code,
  but goldfish search the repository and would read it, and memory commits mix
  with code commits. The `files` backend keeps memory in its own folder or
  repository instead.
- **Fork EGM and add a layer.** Easier to pull upstream fixes, but carries a
  website, many harness adapters and CI that this tool does not need. Rejected
  for a lean plugin; upstream changes to personas and standards are copied by
  hand, with the commit noted at the top of each file.
- **One skill per project.** Each copy drifts, and project facts leak into
  skills. Rejected: project facts move to the hub, and the skills are generic.

## 7. Risks and limits

- **The memory service is a single point of failure.** Sessions keep working and
  print ready-to-paste updates.
- **Goldfish leakage.** Enforced only for Claude Code plugin agents. Elsewhere it
  is partly instruction: Codex subagents may still load `AGENTS.md`; `claude -p`
  loads `CLAUDE.md`; a chat app may inject the user's memory unless the packet
  runs in an incognito or temporary chat. Review files stay outside the
  repository so code search cannot find them.
- **exec isolation.** exec is told to read only its prompt page, but a tool with
  the memory connector could read more. In an IDE chat without the connector
  the prompt is pasted, which enforces it.
- **Parallel sessions.** Neither Notion nor plain files have locks. A claim check, an ID re-check and
  the own-rows rule reduce conflicts; they do not remove them.
- **Schema drift in adopted hubs.** Every write first fetches the schema and maps
  by meaning; the registry stores the mapping.
- **Cost.** A review point runs up to six goldfish per round. Panels are settings, so a
  project can make them lighter.

## 8. Roadmap

Parked items and why: [`roadmap.md`](roadmap.md).

## 9. Build and test

- `python3 scripts/build.py` regenerates the Claude Code agents, the plugin
  manifests and `dist/claude-ai/<skill>.zip`.
- `python3 -m pytest` checks frontmatter, references, generated files, and that
  method files carry no project facts. Put project-specific terms to block in
  `tests/forbidden-terms.local.txt` (git-ignored).
