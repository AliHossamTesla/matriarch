# Memory Row Standard

<!-- New in Matriarch. -->

This standard defines when a memory row is good enough to be someone's only
source.

## Core principle

A row passes if a session that never saw the conversation that wrote it can
act on it correctly: it knows what was decided or asked, by whom, when, why,
what it depends on, and whether it is settled.

## Rules

*   **Self-contained.** No "as discussed", "the above", "same as last time",
    "this". Name the thing.
*   **Status is honest.** Decided only if the person with authority said so.
    Otherwise Proposed (with the decider) or Assumption.
*   **Who and when.** `Decided by` / `Owner` / `Who` and a date on every row.
*   **Source.** A link, a meeting, a file path or "<owner> in chat, <date>". A number
    or market fact without a dated source is an Assumption.
*   **One thing per row.** Two decisions are two rows. A question that has two
    parts is two questions if different people answer them.
*   **Links, not copies.** Point to the spec, PR, issue or Library row instead
    of pasting it, except when a goldfish will need the text (then quote).
*   **History kept.** A change is a new row plus Superseded on the old one,
    never an edit of the old Statement.
*   **Short title, full body.** The title fits on one line; the Statement,
    Answer or Summary carries the detail.

## Examples

Bad: `Decision: use the new approach` · Status: Decided.

Good: `Decision: one item table for raw and prepared items` · Status:
Proposed · Decided by: <CTO> · Waiting on: <CTO>'s review · Statement: (block
from core/memory.md) · Ref: <AREA>-S03 · Source: <AREA>-S03 spec §Alternatives.
