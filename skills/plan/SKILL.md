---
name: plan
description: The thinking session for one task, from idea to merged PR - shape the idea, question the owner until every point is closed, write the spec, split it into sub-tasks with implementer prompts, have goldfish review each, then check every sub-task that exec delivers and the whole task. Use when the owner names a task ID, a feature or an idea to build.
license: Apache-2.0
---

# matriarch:plan — the brain of one task

## Before you start

Matriarch's shared files live in the plugin root (`ROOT`): in Claude Code
`${CLAUDE_PLUGIN_ROOT}`; in other tools two folders above this file; when this
skill was uploaded alone (claude.ai), the `matriarch/` folder next to this file.
Read `ROOT/core/session.md`, `ROOT/core/memory.md`, `ROOT/core/settings.md`,
`ROOT/core/voice.md`, `ROOT/core/goldfish.md` and `ROOT/core/review.md` now.
Formats: `ROOT/standards/spec-template.md`, `ROOT/standards/implementer-prompt.md`.

**Roles.** This session thinks, writes specs and prompts, reviews and records.
It never writes production code. Code is written by `matriarch:exec` in another
chat. This session also runs `matriarch:check` on what exec delivers, because it
knows why each choice was made. Large tasks stay in one plan session for all
their sub-tasks (the mentor).

## 0. Load

1. `session.md` §1–3. Name: `<ID> · plan · <topic>` (or `NEW · plan · <topic>`
   until the task has an ID). Type = Task, Ref = the task ID. Run the claim
   check. Set the Tasks row to In progress.
2. Query: the Tasks row; Decisions for its Area; Open questions that block it;
   the last 3 Work log rows with this Ref (resume if an earlier plan session
   stopped); Library rows for the area (area guides from `matriarch:docs` first).
3. Repository: the registry `Repo`. Local: use the checkout, clean tree,
   updated base branch. Read `AGENTS.md` / `CLAUDE.md` fresh.
4. **Blocked?** A dependency not met, or a decision owned by someone else still
   Proposed: stop, say who owes what, set the task to Blocked.

## 1. Shape (only when the task is still an idea)

One question per message, until the owner says "enough":
the problem in one sentence with one real example; who it is for and how they
do it today; 2–4 observable outcomes; out of scope; constraints and the
decisions it must respect.

Then a fast goldfish challenge: review point `idea` (`review.md`) on a short
brief. Bring back only points that change scope, risk or order. Create the Tasks
row with its ID (`ROOT/core/ids.md`) and continue.

## 1b. Mode

Propose the task's review mode from its risk (`ROOT/core/models.md` §3): one line
with the reason. The owner confirms; write it on the Tasks row (`Mode`).

## 2. Investigate (read-only)

Trace one real request or job through the code the task touches. Explain the
flow to the owner in a few lines with file paths. The owner corrects your model
before you design on it. Note the golden files new code should copy.

## 3. Close every open point

Before writing the spec, list every open point you see (behavior, data, errors,
limits, permissions, migration, rollout, what the UI or caller expects). Go
through them **one question per message**: give up to 3 options with how each
works, its cost and when it fails; ask the owner's answer first when
`user.explain` is `teach`; recommend one; the owner chooses. Record each answer
at once: a Decisions row with its ID (Decided, or Proposed for another decider),
an Open questions row with its ID for anything only someone else can answer, and rejected options
with their reason. Do not start the spec while a point that changes the design
is open.

## 4. Spec

Write `<Spec folder>/<ID>.md` from the template, section by section, with the
owner's approval after Problem + Decision, after Contract, and after the
Implementation plan. Quote every Decisions row it relies on; mark anything new
Proposed with its decider; every guess is an Assumption.

**Review point `spec`** (`review.md`): loop until the needed clean rounds.

## 5. Sub-tasks and prompts

1. Split into 2–6 sub-tasks (about an hour and 80 changed lines each; each
   builds and passes its tests alone; order: contract → data → logic → wiring →
   edge cases). Give each its ID `<task ID>.<step>` (`ROOT/core/ids.md`), and add
   them to the spec checklist.
2. Write one implementer prompt per sub-task (`implementer-prompt.md`), saved as
   `Prompt · <sub-task ID>` under the Tasks row. Leave its Base line for the
   hand-off: the commit is not known yet.
3. **Review point `prompt`** on each prompt, with the spec as context.

## 6. Owner's gate

Show: what the spec decides (3–5 lines), the review findings that mattered,
open questions with owners, and the sub-task table (ID · goal · files · how to
check by hand · who does it). Ask one question: which sub-tasks the owner does
himself, and whether to stop after each one (default). No code is written before
the owner says start.

When the owner approves, **commit the spec alone** (a docs commit; or give the
owner the command when `project.commits.by` is `owner`). Later spec edits (ticks,
As built) go into the next sub-task's commit. exec and check ignore the spec file
in their clean-tree and file checks.

## 7. The sub-task loop (one at a time, in order)

1. Before each, tell the owner in 2–3 lines what it does and why now.
2. Fill the prompt's Base line with the current branch head, then give the owner
   the command for a **fresh** implementer chat in the repository, with the
   exec model and advisor (`ROOT/core/models.md` §2), for example
   `claude --model sonnet --advisor opus` then
   `matriarch:exec <sub-task ID> A <prompt page address>` (part B when tests are not
   first). For a sub-task the owner does himself, give a brief instead (goal,
   files, the failing test, where to look) and hints only, no code, unless he
   asks. Update `Progress`.
3. **Tests first** (when `project.tests.first`): exec runs Part A and reports.
   Run `matriarch:check <sub-task ID>` here (review point `tests`). When the gate
   allows it (`ROOT/core/gate.md` §4) and the owner approves the tests, lock them per `project.tests.lock`:
   - `commit`: commit the test files alone (or, when `commits.by` is `owner`,
     give the owner the exact `git add <paths> && git commit -m "…"` and ask for
     the SHA);
   - `checksum`: `sha256sum` of each test file.
   Write `Locked tests: <SHA or checksums> · <all locked files so far>` in the
   Tasks row's Notes and update `Progress`. Then give the owner the paste-ready
   reply for the exec chat: `go Part B · locked <SHA or checksums> <files>`.
4. exec runs Part B and reports. Run `matriarch:check <sub-task ID>` here (review
   point `subtask`). Its output is a paste-ready reply for the exec chat: fixes,
   or approval.
5. On approval (gate allows it, never on `FAIL` or `INCOMPLETE`): if
   `project.commits.by` is `plan`, commit only the files the
   prompt allowed, staged by explicit path, with a message per
   `project.commits` (shown to the owner first when `owner_approves_message`).
   Write the SHA into `Progress`. Tick the sub-task in the spec (it rides along in
   this commit). When `per_subtask` is false, commit nothing now; commit once
   before the pull request.
6. **When exec does not report DONE:**

   | Status | What plan does |
   | --- | --- |
   | `NEEDS_CONTEXT` | answer it: record any decision; update the prompt (new Version, change note); review point `prompt` on the changed part; reply with the new prompt link |
   | `BLOCKED` | fix the ground (branch, environment, a missing earlier sub-task) with the owner, then reply "retry" |
   | `DONE_WITH_CONCERNS` | run check as usual; check must answer each concern |

   A lost exec chat is replaced by a fresh one with `matriarch:exec <sub-task ID>
   <A|B> <prompt link>`; `Progress` says which part.
7. **After `max_fix_attempts`** failed fixes of the same failure, stop and go
   back to the design with the owner. If a sub-task turns out bigger or
   different than planned, re-split it with the owner and update the spec.

## 8. The whole task

1. Run `matriarch:check <task ID>` (review point `task`): whole diff, As built,
   drift against the spec and decisions.
2. Open the pull request per the hub's rules and `project.merge_method`: title, body (issue, spec link, how
   to test, locked tests line). Request the reviewer per `project.merge`; a solo
   owner runs `matriarch:review <PR>` in a fresh session.
3. Report to the owner:

   ```
   Task: <ID> — <PR link>
   Done: <what works now> · sub-tasks <done>/<total> (who did each)
   Differs from the spec: <what and why, or "nothing">
   Open questions: <or "none">
   Next: <what can start now>
   ```
4. Memory: Work log row (Status, Summary, PR), Tasks row (In review, PR, Next
   step), decisions and questions as rows. Offer one optional Lesson for the
   Library.

## Never

Write production code; change a decision on your own; pass this session's
history to a goldfish; let exec decide something the prompt left open; put
project facts in a skill.
