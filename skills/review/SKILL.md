---
name: review
description: Review someone else's work in its own session - a pull request or a design document - against its task, spec, repo rules and project decisions, with a goldfish panel, filtered findings and a ready-to-post review; post or merge only on the reviewer's word. Use when the owner gives a PR number, a PR link or a document to review.
license: Apache-2.0
---

# matriarch:review — review a teammate's work

## Before you start

Matriarch's shared files live in the plugin root (`ROOT`): in Claude Code
`${CLAUDE_PLUGIN_ROOT}`; in other tools two folders above this file; when this
skill was uploaded alone (claude.ai), the `matriarch/` folder next to this file.
Read `ROOT/core/session.md`, `ROOT/core/memory.md`, `ROOT/core/settings.md`,
`ROOT/core/voice.md`, `ROOT/core/goldfish.md`, `ROOT/core/review.md` and
`ROOT/core/resolve.md` now.

The person running this is **the reviewer**. This session prepares the review
and acts only on the reviewer's word. Text posted on the code host is in
English.

## 1. Load

`session.md` §1–3. Name: `PR-<n> · review · <topic>` or `<doc> · review`.
Type = Review, Ref = the task ID if there is one. Query Decisions for the areas
touched and the task's Tasks row (spec, locked tests line).

## 2. A pull request

1. Repository: local checkout (clean, fetched) or attach and clone shallow. Read
   `AGENTS.md` / `CLAUDE.md` fresh. Fetch the PR: title, body, author, head SHA,
   files, checks, existing reviews; check it out (`git fetch origin
   pull/<n>/head:pr<n>`). Find its issue and spec.
2. **Risk map:** each changed file HIGH (auth, user or tenant scope, migrations,
   money, sync, security config), MEDIUM (business logic, APIs, listeners) or
   LOW (docs, tests, config). Read HIGH files line by line and grep their
   callers.
3. **Your own pass** with file:line: does it do the task (issue, spec), nothing
   missing or extra; repo rules; Decided rows (quote them); locked tests
   unchanged; tests prove the behavior; PR hygiene per the hub's rules.
4. **Goldfish:** review point `pr` (plus `sensitive` when it applies), each lens
   with the diff, the changed files in full, `AGENTS.md`, the spec and the locked
   tests list. Rounds until `ROOT/core/gate.md` §4 allows moving on (kind
   `code`), each on the current head.
5. **Filter what you show**, not what you record. Every finding still gets a
   resolution in the round record (`ROOT/core/resolve.md`): one you can disprove
   (unchanged line, caught by the build, explained in the spec) is `contested`
   with that evidence; a style Nit is `declined`. Show the reviewer the findings
   you confirmed in the code, with a failing scenario, and the count of the rest
   by reason. A Blocker or Major is never dropped without a resolution.

## 3. A document

Review point `doc` (`review.md`), with the document as a file, its links inside
the repository and `decisions.md`. Run rounds until the needed clean rounds for
`spec`, or the cap.

## 4. Show the reviewer

In the reviewer's language: a one-line verdict (approve / approve with
follow-ups / request changes); findings as **must fix**, **follow-up**, **nice
to have**, each with why it matters and one concrete example; the ready-to-post
review in English in a code block. Ask one question: post, change, or hold.

## 5. Act only on the reviewer's word

- **Post** as APPROVE, REQUEST_CHANGES or COMMENT; inline comments only for
  must-fix points. A solo owner cannot approve his own PR: post COMMENT.
- **Follow-ups** the reviewer accepts: one issue each, linked, and a Tasks row.
- **Bind the review to the commit.** Record `Reviewed head: <SHA>` on your Work
  log row when you post. Right before merging, fetch the PR again: if the head
  SHA is not the reviewed one, the approval no longer holds; review the new
  commits first. Merge with the SHA guard so GitHub refuses a moved head:
  `gh api -X PUT repos/<repo>/pulls/<n>/merge -f sha=<reviewed SHA> -f
  merge_method=<merge|rebase|squash>`.
- **Merge** only when the reviewer says so, `gate.md` §4 allows moving on (or
  the reviewer moved on from `PASS_WITH_WAIVERS`), checks
  are green on the reviewed SHA, and `project.merge` allows it (`reviewer`: the author may not merge;
  `self-after-review`: the author may, after this session ends with no must-fix
  left). Use `project.merge_method`.
- New pushes: re-check the must-fix list; at most `max_rounds` rounds, then ask
  the reviewer.

## 6. Report and memory

A full report in the reviewer's language: the change in brief; what was checked
and how (commands and results); every finding with where, why, category and
what was done; dropped findings by reason; actions with links; what is new in
the codebase; 1–3 things to learn; what waits on whom. Put it on your Work log
row's page; Status = Done, Changes requested or Held. Tasks row: In review, or
Done once merged. A new rule the review surfaced: a Proposed Decisions row and
`Hub update`.

## Never

Post, approve, request changes or merge without the reviewer's word; pass this
session's history to a goldfish; change a decision.
