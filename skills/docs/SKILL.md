---
name: docs
description: Learn an unfamiliar area of the system together - read the code, ask the owner and the right people, and write an area guide that every later session reuses. Use before working on a feature or module nobody has explained yet, especially in a large existing codebase.
license: Apache-2.0
---

# matriarch:docs — learn an area, once, for every session

## Before you start

Matriarch's shared files live in the plugin root (`ROOT`): in Claude Code
`${CLAUDE_PLUGIN_ROOT}`; in other tools two folders above this file; when this
skill was uploaded alone (claude.ai), the `matriarch/` folder next to this file.
Read `ROOT/core/session.md`, `ROOT/core/memory.md`, `ROOT/core/settings.md`,
`ROOT/core/voice.md`, `ROOT/core/goldfish.md` and `ROOT/core/review.md` now.

Read-only for the repository. The output is an **area guide**: a Library row
(Type = Reference, Area, `Read when` = "before planning or fixing anything in
<area>", `Full text inside` = checked) whose page is the guide.

## 1. Load and scope

`session.md` §1–3. Name: `<Area> · docs`, Type = Research, Ref = `DOCS-<area>`.
Query Library for an existing guide on the area: update it rather than start a
new one. Agree the scope with the owner in one question: which feature or
module, which entry points (screen, API, job, message), and what the owner needs
to do there next.

## 2. Read the code (before asking)

1. Find the entry points and trace one real flow end to end: request → layers →
   data → side effects → response. Note each file:line.
2. List the data: tables or collections, key fields, who writes them.
3. List the rules the code enforces (validations, states and transitions,
   limits, permissions), each with file:line.
4. Note the conventions and pick 1–3 **golden files**: clean, typical examples
   that new code in this area should copy.
5. Mark everything you could not explain from the code.

## 3. Ask (one question per message)

Go through what you could not explain, most important first: why a rule exists,
what a state means for the business, which cases happen in practice, who uses
it. Classify every answer as a decision, a conditional preference, a teaching
example or an open point. A question only someone else can answer becomes an
Open questions row with its owner. A rule that is a business decision becomes a
Decisions row (with its source). Never turn a guess into a rule; mark it
Assumption.

## 4. Write the guide

```markdown
# <Area>: area guide
As of <date> · commit <SHA> · sources: code, <people and dates>

## What it is for
## Who uses it and when
## Business process          (steps in plain words, with the decisions quoted)
## Flows in the code         (per entry point: file:line chain)
## Data                      (tables, key fields, who writes)
## Rules                     (rule — enforced where — source)
## States                    (if any: states and transitions)
## Conventions and golden files
## Glossary                  (project terms in this area)
## Unknowns                  (open questions with owners)
## Traps                     (things that look wrong but are intended, and why)
```

Review point `area_guide` (`review.md`): the comprehension goldfish reads the
guide alone. Its paraphrase must match what the owner understands; its guesses
are gaps to fill.

## 5. End

Show the owner the guide link and the unknowns. `session.md` §5; tick
`Hub update` when the guide changes how others should work in this area.
