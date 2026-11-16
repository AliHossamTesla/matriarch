---
name: tidy
description: Keep the project memory and the docs honest - find unclosed sessions, schema drift, duplicates and stale rows, cut noise by archiving old work log rows, and check that specs, code and decisions still agree. Runs weekly on a schedule ("tidy scheduled") or when the owner asks.
license: Apache-2.0
---

# matriarch:tidy — clean memory, catch drift

## Before you start

Matriarch's shared files live in the plugin root (`ROOT`): in Claude Code
`${CLAUDE_PLUGIN_ROOT}`; in other tools two folders above this file; when this
skill was uploaded alone (claude.ai), the `matriarch/` folder next to this file.
Read `ROOT/core/session.md`, `ROOT/core/memory.md`, `ROOT/core/settings.md` and
`ROOT/core/voice.md` now.

<!-- Doc-vs-code method adapted from EGM skills/egm-drift-report/SKILL.md
@72d06f5 (Apache-2.0). Changes: decisions added as a third side; memory checks
added; results recorded in memory. -->

Two ways to run:

- **With the owner** (`matriarch:tidy`): finds, proposes, and applies what the
  owner approves (§4).
- **Scheduled** (`matriarch:tidy scheduled`): nobody is there to answer. It
  never asks a question, applies only `project.tidy.safe_fixes`, and leaves a
  report for the owner (§5).

Either way it changes rows only within `memory.md` §4.

## 1. Load

`session.md` §1–3. Name: `<Project> · tidy`, Type = Research, Ref = `TIDY`.

## 2. Memory checks

Query each database and list:

1. **Unclosed sessions:** Work log rows In progress for more than
   `project.tidy.stale_session_days` days.
2. **Schema drift:** select values not in `memory.md` §2 (or the registry Map),
   empty required fields (Ref, Date, Status, Owner, Decided by), titles that are
   not self-contained (`standards/memory-row.md`).
3. **Duplicates:** two Tasks rows with one ID; two Decisions or Open questions
   saying the same thing.
4. **Stale:** Open questions past `Needed by` or older than
   `project.tidy.stale_question_days` days; Proposed decisions waiting more than
   14 days; Tasks Blocked by something already Done or Answered;
   Assumptions older than 30 days.
5. **Broken links:** relations to deleted rows; `Superseded by` empty on a
   Superseded row.
6. **Noise:** Work log rows older than `project.tidy.archive_after_days` days,
   grouped by week.

## 3. Drift checks (when a repository is available)

For each document in the Spec folder and the Library area guides, one at a time:

1. Read it; find the code it describes (named paths first, then search).
2. Report only differences: missing (in the doc, not in the code); incomplete
   models; shortcuts (hardcoded values where logic was planned); divergent
   (another pattern or flow); undocumented important behavior.
3. Compare with Decided rows for its Area: a doc or code that contradicts one; a
   decision with no trace; a doc citing a Superseded row.

## 4. Report and act

Write the report to `~/.matriarch/<project>/tidy/<YYYY-MM-DD>.md` and to your
Work log row's page (with `project.confidentiality.store_code_in_memory: false`,
file:line references only, no code), grouped as above, each item with a proposed action. Show the
owner the counts, then go through the items one at a time, most harmful first.
For each, the owner picks: apply (you make the change and note it), make a task
(new Tasks row), or ignore (noted). `session.md` §5; tick `Hub update` if the
findings change what every session must know.

## 5. Scheduled run

Started by the scheduler with `matriarch:tidy scheduled` (one run per project in
the registry with Status Active, or the project named in the command).

1. Same load (`session.md`), same checks (§2, and §3 only when the repository is
   on this machine). Work log Type = Research, Ref = `TIDY`, Who = the person
   who scheduled it, Session = `<Project> · tidy · scheduled`.
2. Apply only the fixes in `project.tidy.safe_fixes`. If a status a fix needs
   (`Archived`, `Stopped`) is not an option in this hub's Work log, skip that fix
   and report it; never add an option or ask.
   - `archive_worklog`: for each week older than `archive_after_days`, create one
     Work log row `Week of <date> — summary` (Type = Research, Status = Done)
     whose Summary lists each session in one line (Ref, Entry, outcome, PR), then
     set those rows to Archived. First check that no `Week of <date> — summary`
     row exists for that week (another run may have made it). Never archive rows
     that are In progress, Blocked, Held or have `Hub update` ticked.
   - `mark_stale_sessions`: set Work log rows In progress for more than
     `stale_session_days` days to Stopped, adding `Closed by tidy: no activity
     since <date>` to the row's page. Never rows with Type = Task (a `plan`
     session spans days and holds the task's claim); report those instead.
3. Everything else goes in the report as a proposal; ask nothing.
4. Report on your Work log row's page, as in §4, plus what was applied. Tick
   `Hub update` so the next `status` session shows it to the owner. Never
   commit, push, merge or touch code.
5. If memory cannot be reached, stop; do not retry more than once.

## 6. Scheduling it

One scheduled run per project, not per person: before creating one, read the
hub's Environment section for a line `Tidy schedule: <who> · <when> · <where>`;
if it exists, do not create another. After creating it, add that line. `setup`
offers this, and the owner can ask any time ("schedule tidy"). Compute the time from `schedule.tidy`:

- `before_reset`: `reset` minus `hours_before` (for example reset `Mon 09:00`,
  6 hours before → `Mon 03:00`). If `reset` is empty, ask the owner for it (it
  is on their plan's usage page) and save it to their user settings.
- `weekly`: the `weekly` day and time.
- In `schedule.tidy.timezone`, else the machine's.

Then create a weekly scheduled task in the tool the owner uses, with the
prompt `matriarch:tidy scheduled`, the session model from `models.sessions.tidy`
and the memory connector enabled: a scheduled task in Claude (claude.ai or
Claude Code), an automation in Codex, or, on a machine that stays on, cron with
`claude -p "matriarch:tidy scheduled"`. Tell the owner the day, time and where it
was created. Never schedule it without the owner's word.
