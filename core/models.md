# Models, advisor and review modes

Which model does which job, so strong models are spent where judgment matters
and cheaper ones where the work is already decided. Settings: `models.*` (user)
and `project.review.mode` / `modes` (project).

## 1. Tiers

Three tiers: `strong`, `standard`, `fast`. `models.tiers.<tool>` maps them to
the names a tool accepts (Claude Code: `opus`, `sonnet`, `haiku`). An empty name
means "the tool's default for that tier"; say so to the owner once.
`models.order` lists model names from strongest to weakest; in every tool a
tier never gets a stronger model than the tier above it (two tiers may share
one). A model that matches no name in the list is not checked.

## 2. Who runs on what

**Sessions** (`models.sessions`): a session cannot change its own model, so the
command that opens it carries the model. When a skill hands off to a new chat,
write the command with the tier's model and, for sessions in `models.advisor.for`,
the advisor:

| Tool | Command shape |
| --- | --- |
| Claude Code | `claude --model <name> --advisor <strong name>` then the skill command; inside a running session, `/model <name>` and `/advisor <name>` |
| Codex | `codex -m <name>` then the skill command (no advisor; use the strong tier for sessions that need it) |
| Chat apps | tell the owner which model to pick in the model menu |

If the session you are in runs on a lower tier than `models.sessions` says for
it, tell the owner once at the start.

**Advisor.** In Claude Code the advisor must be at least as strong as the main
model, and subagents inherit it. When `models.advisor.enabled`, sessions in
`models.advisor.for` run on their tier with the advisor on the advisor tier.
Consult it before committing to a plan, when stuck after two attempts, and
before declaring a sub-task done.

**Goldfish** (`models.lenses`): each lens runs on its tier, chosen when the
lens starts:

- lenses in `models.lenses.strong` on `strong`, in `models.lenses.fast` on
  `fast`, others on `models.lenses.default`;
- Claude Code: the `model` parameter of the Agent tool; Codex: the model option
  of `spawn_agent` if offered, else `codex exec -m <name>`; CLI: `claude -p
  --model <name>`; packets: the packet header names the tier and model to use.
- **Floor:** a lens in `models.lenses.strong` never runs below
  `models.floor_for_strong_lenses`. If only a weaker model is available, record
  the lens as `not run` (reason: model below floor). Small, fast models approve
  flawed work; a lens on one is worse than no lens.
- Record the model with each lens's result in the round record (`gate.md` §5).

## 3. Review modes

A task's mode sets how much review it gets. `plan` (and `fix`) propose a mode
from the task's risk, the owner confirms, and it goes on the Tasks row (`Mode`).

| Mode | Use for | Effect |
| --- | --- | --- |
| `quick` | docs, small internal changes, low-risk bugs | `project.review.modes.quick`: smaller panels, one clean round each, no cross-model |
| `standard` | most work | the project's panels and rounds |
| `critical` | money, security, auth, user or tenant data, migrations, public APIs, anything costly to reverse | `project.review.modes.critical`: two clean rounds for specs and code, cross-model, the sensitive panel on every sub-task and task review |

A mode's values replace the standard ones for that task; anything it does not
set stays standard. A mode never turns off the gate or the invariants
(`settings.md` §0). Changing a task's mode mid-way needs the owner's word and a
line in the Work log.
