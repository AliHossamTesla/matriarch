# Implementer prompt

<!-- New in Matriarch, from the owner's earlier project workflows. -->

`plan` writes one prompt per sub-task. `exec <ID>` follows it in another chat.
The prompt is the implementer's whole world: it must work for a session that
has never seen the project, the spec discussion or the memory.

## Where it lives

A child page of the task's Tasks row titled `Prompt · <sub-task ID>`, and a copy
in the review folder for goldfish review. `plan` hands the owner the page link
with the command; in an implementer chat without a memory tool, the owner pastes
the page text instead. A changed prompt keeps its page, with a `Version: <n>`
line at the top and a short change note.

## Template

```markdown
# Prompt · <sub-task ID> · <one-line goal>

Base: branch <branch> at <commit SHA, filled by plan at hand-off>. Run
`git status` first; stop if the tree is not clean (the task's spec file at
<spec path> does not count).
Reply language for the owner: <user.language>.

## Goal
<what works after this sub-task that did not work before>

## Context
<only what is needed: the flow, the classes involved with paths, the business
rule in plain words with the decision quoted>

## Rules
- Do only what this prompt says. If anything is unclear or the code does not
  match this prompt, stop and report NEEDS_CONTEXT; do not decide.
- Follow the repository rules in <AGENTS.md / CLAUDE.md path>.
- New classes copy the structure of the golden file: <path>.
- Do not commit, push, switch branches or edit files outside the list below.
- <project rules: language level, libraries allowed, logging limits, test data>

## Files
| Path | Create / Modify | What changes |

## Part A · Tests
<the tests to write: file, test name, given / when / then, including unhappy
paths. Run them; they must fail for the stated reason. Then stop and report.>

## Part B · Implementation   (only after the owner sends "go Part B · locked <sha or checksums> <files>")
<ordered steps per file: signatures, logic, errors, logging. Make the Part A
tests pass without changing them. Run the build command: <command>.>

## Report
Reply in chat with:
STATUS: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED
BASE: <commit you started from> · HEAD: <commit now>
TESTS: <command> → <passed>/<total>, <failed list or "none">
CONCERNS: <or "none">
Then write the full report (what you changed per file and why, commands run with
output, anything you could not do) as a child page of this prompt page titled
`Report · <sub-task ID> · <A|B> · r<n> · <date>`, or paste it if you have no
memory tool.
```

## Rules for plan when writing it

- **Zero decisions left** (`standards/implementation-readiness.md`): names,
  signatures, error codes, log lines and test data are spelled out.
- **One sub-task, one prompt, one goal.** About an hour of work and about 80
  changed lines.
- **Quote, do not refer.** A decision the code depends on is quoted in Context,
  not linked to memory: the implementer cannot read memory.
- **Golden file named** for every new class.
- **Part A only when** `project.tests.first` is true; otherwise merge the tests
  into Part B.
