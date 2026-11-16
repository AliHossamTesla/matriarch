# Resolve findings

<!-- Categories adapted from EGM skills/egm-resolve/SKILL.md @72d06f5
(Apache-2.0). Changes: ESCALATE routes to memory Open questions and Decisions;
memory-only evidence rule. -->

Best run in the session that wrote the artifact: it remembers why it chose
what it chose. Inputs: the target, its line range, and the findings (a report
file, packet findings pages, or a PR review's list).

**Resuming in a new session** (the original chat is gone, or findings came back
hours later): follow [`session.md`](session.md) §1–3 first, then read the Work log row for the Ref (its page has the stage reached and
`Waiting on packet` lines), the target, every `Findings · …` page under its
packets, the Decisions for its Area and the review log on that page. Your evidence for
contests must come from those, not from memory of a chat you never saw.

## 1. Classify every finding (exactly one category)

- **FIX** — the finding is right. Write the precise change (location and new
  text or code).
- **CONTEST** — the finding is wrong, and you can prove it with something the
  reviewer **could have read**: a file and symbol, a line of the artifact. Cite
  it.
- **ESCALATE** — the finding is wrong or unanswerable from the artifact, but the
  evidence lives only in project memory or in someone's head (a Decisions row
  the goldfish did not get, a verbal agreement), **or** the fix needs a decision
  outside the owner's authority. Do not fix it yourself.
- **ACTION** — a valid Major you will not fix in this artifact now: name the
  owner and where it will be fixed (a later sub-task, a Tasks row). Work
  continues (`gate.md` §1).
- **WAIVE** — only the owner can waive: a known Blocker or Major accepted as it
  is, with the owner's name, reason and a review date. Recorded as a Decisions
  row.
- **DECLINE** — a Nit not worth changing. Recorded, not fixed.

Each category maps to a gate resolution: FIX → `fixed`, CONTEST (owner agrees) →
`contested`, ACTION → `action`, WAIVE → `waived`, DECLINE → `declined`, ESCALATE
→ `open` until the owner or the right person answers.

Rules:

- "This was intentional" is not evidence. No checkable evidence → ESCALATE or
  FIX.
- **A comprehension gap is never contested.** If a fresh reader could not follow
  it, the document is missing context.
- **Memory is not a hiding place.** If your evidence is a Decisions row, the
  usual right answer is FIX: quote or link the row in the artifact so the next
  reader sees it. ESCALATE only when quoting it would not settle the point.
- Never change a severity. Disagree through CONTEST, with the reason.
- You wrote the artifact. Wanting to contest is not evidence the reviewer is
  wrong.

**A Blocker must say which reason makes it one** (`personas/_mandates.md`). A
Blocker with none of those reasons is reclassified only by contesting it with
the reason; the owner decides.

## 2. Show the owner

Write `<point>-r<n>-resolution.md` in the Elephant folder (`goldfish.md` §1) and on the Work log page with each
finding: id, lens, severity, category, justification, proposed change.

In chat, in the owner's language: ESCALATE items first (they need the owner's
knowledge, not just approval), one at a time; then a one-line count of the
rest. Ask one question: apply all FIX items, go through them one by one, or
stop.

## 3. Apply and record

1. Apply approved FIX edits to the artifact. If the artifact is code written
   by an `exec` chat, do not edit it: write the fixes into the paste-ready reply
   for that chat instead. Re-read the artifact after editing.
2. ESCALATE outcomes:
   - the owner decides within authority → Decisions row (Decided), and quote it
     in the artifact;
   - someone else must decide → Decisions row (Proposed, `Decided by` = them)
     and an Open questions row (Owner = them, Blocks = the task);
   - a fact only a person knows → Open questions row.
3. Add each finding to the review log on the Work log page (finding · lens ·
   category · change made). Never write it into the artifact: goldfish read the
   artifact on re-runs.
4. Write the round record and compute the gate ([`gate.md`](gate.md)); give the
   result to the calling procedure.
