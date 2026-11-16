# Review gate

The single rule for what a review round means. Every skill, persona and
setting defers to this file; nothing else defines when work may continue.

## 1. Severity → action

| Severity | Meaning | Action |
| --- | --- | --- |
| Blocker | breaks a stated goal, limit, rule or decision; loses or corrupts data; opens a security hole; cannot be built or run | **stops** the work until fixed, contested with evidence, or waived by the owner |
| Major | likely bugs, rework or confusion | work **continues**; the finding becomes a tracked action (owner, where it will be fixed) |
| Nit | wording, small gaps | recorded only |

## 2. Resolutions

Each finding ends a round with exactly one resolution (`resolve.md`):

| Resolution | Meaning |
| --- | --- |
| `fixed` | the target was changed; the next round checks it |
| `contested` | wrong, with evidence the reviewer could read; the owner agreed |
| `action` | a Major tracked for later: owner and where (sub-task, task row) |
| `waived` | the owner accepts a known problem: owner, reason, review date |
| `declined` | a Nit not worth changing (Nits only) |
| `open` | not settled yet |

## 3. Gate result for one round

Compute in this order; the first that applies wins.

| Result | When |
| --- | --- |
| `INCOMPLETE` | a lens in the panel did not complete (`not run`), or a Major or Nit is still `open`, or the target changed while the lenses were reviewing it |
| `FAIL` | a Blocker is not `fixed`, `contested` or `waived` (an open Blocker is a `FAIL`) |
| `PASS_WITH_WAIVERS` | a Blocker or Major is `waived` |
| `PASS_WITH_ACTIONS` | a Major is `action` |
| `PASS` | everything else |

A lens may be skipped only when the owner records the reason; a skipped lens is
a waiver, so the round can be at best `PASS_WITH_WAIVERS`.

The round record describes the target **as the lenses reviewed it**; fixes you
apply afterwards belong to the next round.

## 4. Counting rounds

- A **clean round** is `PASS` or `PASS_WITH_ACTIONS` **with no Blocker or Major
  resolved `fixed`**. A round that needed fixes is not clean.
- **The panel is not the agent's choice.** A round must contain every lens of the
  panel for its review point, from the effective settings and the task's mode,
  plus the sensitive panel when it applies. A lens left out is `INCOMPLETE`.
- Work moves on when the clean rounds **in a row on the same target version**
  (same SHA-256) reach `project.review.clean_rounds_needed` for its kind (or the
  mode's value). Each round uses fresh goldfish, so two clean rounds on the same
  version are two independent reviews. **Any change to the target, even a Nit
  fix, starts the count again.**
- `PASS_WITH_WAIVERS` is never counted as clean. It moves on only when the owner
  says so. Every waiver needs the owner, the reason, a review date and the ID of
  the Decisions row that records it; a skipped lens needs the owner and the
  reason.
- `FAIL` and `INCOMPLETE` never move on. After `project.review.max_rounds`
  rounds, the owner chooses: one more round, waive (then `PASS_WITH_WAIVERS`),
  or back to the design.
- Nothing approves, commits, locks or merges unless work may move on.

## 5. Computing it

Where code runs (Claude Code, Codex), write a round record per round and run the
tool with the earlier rounds of the same review point; use its result, not your
own reading:

```
python3 ROOT/core/tools/matriarch.py gate <round.json> \
    --previous <round-1.json> --previous <round-2.json> \
    --user ~/.matriarch/config.yaml --project <hub settings saved as YAML>
```

```json
{
  "point": "subtask",
  "mode": "standard",
  "sensitive": false,
  "target_sha256": "<matriarch.py sha256 of the target or diff.patch>",
  "lenses": [{"name": "spec-compliance", "status": "completed", "model": "…"},
             {"name": "business", "status": "not_run", "reason": "timeout"}],
  "findings": [{"id": "F1", "lens": "code-quality", "severity": "Major",
                "resolution": "action", "owner": "<name>", "where": "ORD-API-03.edge"},
               {"id": "F2", "lens": "security", "severity": "Blocker",
                "resolution": "waived", "owner": "<name>", "reason": "…",
                "decision": "ORD-D07", "review_by": "2026-12-01"}]
}
```

It returns the panel the round needed, the gate result, the clean streak and
`move_on`; it exits 0 only when work may move on.

In a chat app without code execution, apply §3 and §4 by hand and keep the
records the same way, so the next session with code can check them.
