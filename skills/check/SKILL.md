---
name: check
description: Review what exec delivered - one sub-task's tests or code, or a whole task - with a goldfish panel, verify the claims, resolve findings and produce a paste-ready reply for the exec chat. Runs inside the plan session; use "check" with a sub-task ID (ORD-API-03.data) or a task ID (ORD-API-03).
license: Apache-2.0
---

# matriarch:check — review the hands' work

## Before you start

Matriarch's shared files live in the plugin root (`ROOT`): in Claude Code
`${CLAUDE_PLUGIN_ROOT}`; in other tools two folders above this file; when this
skill was uploaded alone (claude.ai), the `matriarch/` folder next to this file.
Read `ROOT/core/review.md`, `ROOT/core/resolve.md` and `ROOT/core/goldfish.md`
if this session has not read them yet.

**Where it runs.** Inside the `plan` session of the task: it knows why each
choice was made, so it judges findings best. If that chat is gone, run it in a
new session: follow `ROOT/core/session.md` §1–3 (name `<ID> · check`, its own
Work log row with a link to the plan session's row), then read the Tasks row
(`Progress`, Notes), the spec, the prompt, exec's reports and the plan session's
Work log page before anything else. Record on your own row, never on plan's.

## 1. One sub-task: `check <sub-task ID>`

1. **Read** exec's latest report (`Report · <ID> · <A|B> · r<n> · …` or pasted),
   the prompt, the spec section and the diff from the report's BASE (check that
   it matches the prompt's Base): `git diff <base>` plus untracked files from
   `git status --porcelain`, saved as `diff.patch` with base and head at the top.
2. **Verify the claims yourself** before any goldfish:
   - rerun the test command and quote the result;
   - `git status`: only files in the prompt's Files table changed (the spec file
     does not count);
   - for Part B, check the locked tests (`commit`: `git diff --exit-code <lock>
     -- <files>`; `checksum`: write the checksums from Notes to a file in the
     Elephant folder, then `sha256sum -c` it);
   - a report that says DONE but fails any of these is not done; say so plainly.
3. **Review:** Part A → review point `tests`; Part B → review point `subtask`
   (plus `sensitive` when it applies). Give lenses the prompt, the spec section,
   the diff and the changed files in full. Run `review.md` §2 for one round.
4. **Resolve** with the owner (`resolve.md`). Code fixes are never made here;
   they go into the reply.
5. **Reply for the exec chat**, in a code block, in English:
   - fixes needed: numbered, each with file:line, what is wrong, what to do, and
     "rerun <command> and report";
   - or, when `ROOT/core/gate.md` §4 allows moving on (enough clean rounds in a
     row for this kind, or the owner moved on from `PASS_WITH_WAIVERS`):
     `Approved.` (Part A: then the plan session locks
     the tests and sends `go Part B`; Part B: the plan session commits). Never on
     `FAIL` or `INCOMPLETE`.
6. Update `Progress` and record on the Work log page (plan's when running inside
   plan, your own otherwise): `<sub-task ID> <A|B> round <n>: <counts> ·
   <gate result>`, the report, and what was sent back. Stop rules: `review.md` §3
   (`tests` or `code`).

## 2. A whole task: `check <task ID>`

1. Read the spec (with its As built section), the Tasks row, every sub-task's
   final report and the full diff from the task's base to the branch head.
2. Verify: full build and test command; locked tests unchanged; no file outside
   the union of the prompts' file lists.
3. Review point `task` (plus `sensitive` when it applies), with the spec,
   `decisions.md` and the whole diff. The lenses look at how the parts fit
   together and at the end-to-end business flow, not at each sub-task again.
4. Resolve. Fixes become a new sub-task (`<task ID>.<step>-<slug>`), planned and executed
   like the others; documentation-only differences go into As built with the
   owner's approval.
5. Tell the plan session the task is ready for its pull request, or what remains.

## Never

Edit production code or tests here; approve without rerunning the tests; give a
lens the plan session's history or an earlier round's report.
