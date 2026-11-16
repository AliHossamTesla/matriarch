# IDs

Every task, sub-task, decision and open question gets an ID that says what it
is and where it belongs, so a person can read `ORD-API-03.data` and know it is
the data step of an orders API task without opening anything.

## 1. Shapes

| Item | Shape | Example |
| --- | --- | --- |
| Task | `<AREA>-<KIND>-<NN>` | `ORD-API-03` |
| Bug | `<AREA>-FIX-<NN>` | `PAY-FIX-07` |
| Sub-task | `<task ID>.<step>` or `<task ID>.<step>-<slug>` | `ORD-API-03.data`, `ORD-API-03.logic-pricing` |
| Decision | `<AREA>-D<NN>` | `AUTH-D04` |
| Open question | `<AREA>-Q<NN>` | `AUTH-Q12` |

- `<AREA>`: one of `project.ids.areas` (2–4 capital letters, one per module or
  part of the product, chosen at setup).
- `<KIND>`: one of `project.ids.kinds`: what the work mostly changes.
- `<NN>`: two digits or more, the next free number **for that AREA and KIND**
  (tasks) or **for that AREA** (decisions, questions). Numbers are never reused,
  even after a row is deleted or Withdrawn.
- `<step>`: one of `project.ids.steps`, in build order. When a task has two
  sub-tasks of the same step, both get a slug: 1–2 lowercase words that name
  what differs (`logic-pricing`, `logic-refunds`). Never `logic-2`.

## 2. Making one

1. Pick AREA and KIND by what the work changes. Unsure between two: ask the
   owner one question.
2. Query the database for IDs that start with `<AREA>-<KIND>-` (or `<AREA>-D`,
   `<AREA>-Q`) and take the highest number plus one.
3. Write the row, then query the ID again. If two rows share it, keep the older
   one, give yours the next free number, and tell the owner (`memory.md` §4).
4. An ID never changes after creation, even if the work turns out to be another
   kind. Note the real kind in the row instead.

Adopted hubs with an older ID pattern keep their existing IDs; new rows use this
pattern unless the hub's Settings say otherwise (`project.ids.pattern: legacy`
plus a line in the hub Rules describing it).

## 3. Where IDs appear

Tasks `ID`, Decisions `ID`, Open questions `ID`, spec file names
(`<Spec folder>/<task ID>.md`), prompt pages (`Prompt · <sub-task ID>`),
reports, `Progress` lines, branch names when the hub's rules ask for them, and
session names. Commit messages follow `project.commits.team_readable`: with it
on, IDs stay out of commit messages.
