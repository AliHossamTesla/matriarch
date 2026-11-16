---
name: fix
description: Fix one bug the disciplined way - reproduce it, find the root cause, write a failing test, then a small fix through exec and check. A light plan for bugs. Use when the owner reports a bug, a failing test or a production error.
license: Apache-2.0
---

# matriarch:fix — one bug, root cause first

## Before you start

Matriarch's shared files live in the plugin root (`ROOT`): in Claude Code
`${CLAUDE_PLUGIN_ROOT}`; in other tools two folders above this file; when this
skill was uploaded alone (claude.ai), the `matriarch/` folder next to this file.
Read `ROOT/core/session.md`, `ROOT/core/memory.md`, `ROOT/core/settings.md`,
`ROOT/core/voice.md`, `ROOT/core/goldfish.md` and `ROOT/core/review.md` now.

Like `plan`, this session thinks and does not write production code; the fix
goes through `matriarch:exec` and `matriarch:check`. A bug that needs a design
change becomes a `plan` task instead.

## 1. Load

`session.md` §1–3. Name: `<ID> · fix · <topic>`, Type = Task (so the claim
check sees it). Find or create the Tasks row
(ID `<AREA>-FIX-<NN>` per `ROOT/core/ids.md`, Area, Notes = the bug report as
given). Search
Work log and Tasks for the same symptom: it may be known. Propose the review mode
(`ROOT/core/models.md` §3; most bugs are `quick` or `standard`, security and data
bugs `critical`).

## 2. Understand (read-only)

1. **Read the whole error**: message, stack trace, logs the owner shares, the
   request and data that trigger it. No guessing from the first line.
2. **Reproduce** it: the exact steps or a test that shows it. Cannot reproduce →
   ask the owner one question for what is missing; do not fix blind.
3. **Compare** with a path that works (another input, another module, the last
   good commit: `git log -p`, `git bisect` when useful).
4. **One hypothesis at a time**: state it, test it, keep or drop it. Write each on
   the Work log page.
5. **Root cause** in one sentence, with file:line. Explain it to the owner, with
   why the fix belongs there and not where the symptom shows.

## 3. Fix

1. A short spec section in the Tasks row page: cause, fix, what else could be hit
   (search for the same pattern), test that proves it.
2. One sub-task `<ID>.fix` (`<ID>.fix-<slug>` when there are several) with an implementer prompt (`implementer-prompt.md`):
   Part A is the failing test that reproduces the bug; Part B is the fix. Review
   point `prompt` until `ROOT/core/gate.md` §4 allows moving on.
3. Loop as in `plan` §7: `exec`, then `check`, lock, commit.
4. Same pattern elsewhere? Each other place is its own sub-task or a new Tasks
   row, as the owner chooses.

**After `project.review.max_fix_attempts` failed fixes** of the same failure:
stop. The model of the system is wrong; go back to step 2 with the owner, or
turn it into a `plan` task.

## 4. End

Report: cause, fix, test, other places checked, PR. Work log and Tasks rows per
`session.md` §5. If the cause teaches something general, offer a Lesson row.
