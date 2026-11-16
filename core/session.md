# Session protocol

Every Matriarch skill (all except `exec` and `goldfish`) runs as one session with one job: one task, one review,
one decision, one idea, one packet. This file is the frame around that job.

## 1. Name the session (first message)

Give the session one English name so it can be found again:

| Skill | Name |
| --- | --- |
| `setup` | `<Project> · setup` |
| `status` | `<Project> · status · <topic>` |
| `plan` | `<ID> · plan · <topic>` |
| `check` (alone) | `<ID> · check` |
| `fix` | `<ID> · fix · <topic>` |
| `docs` | `<Area> · docs` |
| `discuss` | `DISC · <topic>` or `DEC · <topic>` |
| `review` | `PR-<n> · review · <topic>` or `<doc> · review` |
| `tidy` | `<Project> · tidy` |
| `doctor` | `<Project or tool> · doctor` |

`<topic>` is 2–5 lowercase English words. No dates, no emojis. You cannot rename
the session yourself: open your first reply with the name in a code block and
the step for the tool in use:
- Claude Code or Codex: `/rename <name>`; find it later with `/resume <name>`
  (Codex: the `codex resume` picker).
- claude.ai or ChatGPT: chat title → Rename.

## 2. Load (silently)

1. Find the project and fetch the hub ([`memory.md`](memory.md) §1).
2. Read the settings ([`settings.md`](settings.md)), then the hub's **Rules**,
   **People**, **Environment** and **Where we are**. People says who decides
   what. Follow them.
3. Query only what the job needs (each skill lists it), plus the current
   person's Personal rows for this project with Status = Open (unless
   `memory.personal.backend` is `none`). Typical: the Tasks row
   by ID; Decisions for the Area with Status not Superseded/Withdrawn; Open
   questions with Status = Open that block the job; the last 3 Work log rows for
   the same Ref.
4. **Already done or decided?** If memory shows the job is finished or the
   question decided, say so (with date and owner) and stop, unless the owner is
   challenging it. Reopening needs "what changed since".
5. If the session runs in a repository: `git branch --show-current` and
   `git status --short`. A dirty tree you did not make: tell the owner before
   touching anything.

## 3. Log the start

A task session (`plan`, `fix`) runs the claim check first
([`memory.md`](memory.md) §4). Reviews, resolves and PR sessions do not claim.


Add a **Work log** row: `Entry` = `<Ref> — <one-line goal>`, `Date`, `Type`,
`Status` = In progress, `Ref`, `Who` (the owner), `Tool`, `Model`, `Session`.
Then tell the owner in 2–3 lines, in their language, what state you found and
what you will do next.

## 4. During the work

- Write each decision, question and task change to memory when it happens
  ([`memory.md`](memory.md) §4).
- One question at a time. When `user.explain` is `teach`, ask the owner's own
  answer before yours on anything important.
- Mark every guess **Assumption**.
- Never decide for someone else; write it as Proposed for them.
- Follow the voice rules in [`voice.md`](voice.md).

## 5. Log the end (every session, also when stopping early)

1. Update your **Work log** row: `Status`, `Summary` (what changed, files,
   decisions, PR, next step), `PR`. Put long output (the full report) in the
   row's page body. If you stopped early, say why.
2. Update the **Tasks** row you own: `Status`, `Next step`, `PR`, `Blocked by`.
3. If the session changed something every session must know (a new rule, a new
   blocker, a changed plan), tick `Hub update` on your Work log row and say what
   in the Summary. The `status` session picks it up. Only `status` edits
   the hub page.
4. Before ending any turn that changed something, check: is everything
   important in memory? If it is only in this chat, the next session will not
   know it.
