# Review loop

<!-- Round and stage ideas adapted from EGM skills/egm-review/SKILL.md @72d06f5
(Apache-2.0). Changes: panels come from settings; rounds end on clean-round
rules; results kept in memory. -->

The procedure every skill uses to have goldfish review something: a spec, an
implementer prompt, tests, a sub-task's code, a whole task, a pull request, a
document, an idea or a decision. The calling skill names the **review point**
(`spec`, `prompt`, `tests`, `subtask`, `task`, `pr`, `doc`, `area_guide`,
`idea`, `decision`); the lenses for it come from the setting
`project.review.panels.<point>` ([`settings.md`](settings.md)), replaced by the
task's mode where the mode sets them ([`models.md`](models.md) §3). Each lens
runs on its model tier (`models.md` §2).

## 1. Prepare

1. **Folders** ([`goldfish.md`](goldfish.md) §1): one input folder per lens
   under `~/.matriarch/<project>/<ref>/<point>-r<round>/in/<lens>/`, and the
   Elephant's own files (reports, resolutions) under
   `~/.matriarch/<project>/_elephant/<ref>/`.
2. **Target as a file.** A memory page or Google Doc is exported to a Markdown
   file in the review folder. A diff is saved as `diff.patch` (with the base and
   head commits written at the top).
3. **Decisions:** query Decisions for the target's Area (Status not Superseded or
   Withdrawn) and copy the relevant rows as text into `decisions.md`.
4. **Inputs per lens:** exactly the table in `goldfish.md` §1. Links in the
   target that point outside the repository: ask before including them.
5. **Sensitive?** For `subtask` and `task`, add the `sensitive` panel when the
   diff touches auth, user or tenant data, money, migrations, concurrency or
   external calls, and always when the task's mode sets `always_sensitive`.

## 2. Run one round

1. Start every lens of the panel in parallel, each with its persona, its
   standard, the target and only the inputs §1 gives it
   ([`goldfish.md`](goldfish.md)). Respect `cross_model`.
2. Wait for all. Merge into `_elephant/<ref>/<point>-r<n>-report.md` (synthesizer rules): lens status table
   (completed / not run, tool, model), then findings F1, F2 … by severity.
   `comprehension` keeps its paraphrase at the top.
3. **Check the claims yourself** before you show anything: open each file:line a
   finding cites. A finding whose quote is not in the target is dropped as a
   misread, and you say how many you dropped.
4. Resolve the findings with the owner ([`resolve.md`](resolve.md)).
5. Write the state on your Work log row's page (with
   `project.confidentiality.store_code_in_memory: false`, findings with file:line
   only, no code quotes; the full report stays local):
   `<point> round <n>: <B> blocker, <M> major, <N> nit · <gate result>`,
   followed by the merged report.

## 3. Gate and when to stop

Compute the round's result with the gate ([`gate.md`](gate.md)): write the round
record (point, mode, sensitive, lens statuses, findings with resolutions, the
target's SHA-256) and, where code runs, `python3 ROOT/core/tools/matriarch.py
gate <round.json> --previous <earlier rounds>` with the settings files. Use its
result, including `move_on`. Clean rounds, waivers, `max_rounds` and what may happen next are all
defined there, not here. Kinds for `clean_rounds_needed`: `spec` for spec and doc
reviews; `prompt`; `tests`; `code` for subtask, task and pr reviews; ideas,
decisions and area guides need one clean round.

A re-run reviews the updated target from scratch, with fresh goldfish. Never give
a lens the earlier report.

## 4. Output to the calling skill

The round count, the last gate result, the waivers and actions, and the report
path. The calling skill decides what happens next.
