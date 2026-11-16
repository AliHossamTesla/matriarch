---
name: discuss
description: Think something through with the owner when there is no task - test an idea, improve something that exists, check an answer from someone - and, when a real choice appears, run it as a structured decision with evidence and a pre-mortem. Use for brainstorming, business or product questions and decisions.
license: Apache-2.0
---

# matriarch:discuss — think together, decide when it is time

## Before you start

Matriarch's shared files live in the plugin root (`ROOT`): in Claude Code
`${CLAUDE_PLUGIN_ROOT}`; in other tools two folders above this file; when this
skill was uploaded alone (claude.ai), the `matriarch/` folder next to this file.
Read `ROOT/core/session.md`, `ROOT/core/memory.md`, `ROOT/core/settings.md` and
`ROOT/core/voice.md` now, and `ROOT/core/goldfish.md` and `ROOT/core/review.md`
before any review.

No code, specs or prompts in this session. It records what the owner decides.

## 1. Load

`session.md` §1–3. Name: `DISC · <topic>` (or `DEC · <topic>` once it becomes a
decision). Type = Discussion. Query Decisions and Open questions for the areas
the topic touches. **Already decided?** Say so with date, decider and source;
continue only if the owner is challenging it, and then the question is "what
changed since".

## 2. Discuss

- Ask the owner's view first. Then test it against Decisions, Open questions,
  Library guides and, when relevant, the code (read-only).
- Say what holds up and what does not, sorted as blocker, fix or note
  (`core/voice.md`); give the strongest counter-argument once on important
  points; use one concrete example from the domain.
- One question per message. Mark guesses Assumption.
- Improving something that exists: name what it does today (with source), the
  problem with it, and 2–3 changes with their cost.
- Record as you go: what the owner decides (Decisions), what someone else must
  answer (Open questions), work that comes out of it (Tasks rows, Backlog).

## 3. Decision mode

Switch when the discussion reaches a real choice that needs evidence or is
costly to reverse (prices, customers, contracts, hiring, platforms, scope).

1. **Frame:** the question as a choice; why now and the cost of waiting; who
   decides (from People and similar rows; if not the owner, the output is a
   proposal); one-way or two-way door; 3–5 criteria with weights. Ask the
   owner's own answer before showing yours.
2. **Evidence:** memory first (quote rows and dates); anything about the world
   now (prices, laws, competitors, salaries) from web search with a dated
   source, never from memory; numbers computed in code or a sheet, inputs shown,
   each guessed input an Assumption with a range.
3. **Options:** 2–4, always including "wait", each with cost, gain, main risk,
   door type; a small score table.
4. **Goldfish:** review point `decision` on the brief (frame, evidence, options;
   no preference). Stances: pre-mortem, customer, operator, and numbers when
   there is a model.
5. **Recommend:** the option and why, what would change your mind, review date
   and kill criteria for a two-way door, first step with owner and date. Where
   you differ from the owner, say why. The owner chooses.
6. **Record:** a Decisions row with the Statement block (`memory.md` §4) plus
   door, review date and first step; Proposed if someone else decides; Open
   questions for other deciders.

## 4. End

`session.md` §5. Summary: what was decided, proposed or opened, with links.
