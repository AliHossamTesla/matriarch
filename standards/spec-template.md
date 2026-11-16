# Task spec template

<!-- New in Matriarch. Combines two earlier projects' task spec and design file with
EGM's feature-spec / implementation-readiness split. The line
"## Implementation plan" is the split point reviews use between the feature
part and the plan part. -->

The review log does not go in the spec, because goldfish read the spec and must
not see earlier findings. It lives on the task's Work log page.

Copy this to `<Spec folder>/<ID>.md` (the Spec folder comes from the registry
row; default `docs/specs/`). Fill every section; write "none" rather than
deleting one.

```markdown
# <ID>: <title>

- Status: Draft | In review | Approved | As built
- Owner: <name> · Task: <Tasks row link> · Issue: <link>
- Decisions relied on: <Decision title — Status — link>, one per line

## Problem
<what is wrong or missing today, with one concrete example from the domain>

## Goals and non-goals

## Decision
<what we will build, consistent with the decisions above. Anything new is
marked Proposed (<who decides>)>

## Alternatives considered
<each option and the concrete reason it lost>

## Contract
<exact names and types: tables and columns, endpoints, request and response,
events, method signatures, config keys, error codes>

## Risks and mitigations

## Out of scope

## Open questions
<question — owner — what it blocks>

## Implementation plan

### Files
| Path | Create / Modify / Delete | Why |

### Sub-tasks
- [ ] <ID>.1 <goal: what works after it> — files · depends on · Done when
  (tests) · How to check it yourself (command and what to look at)
- [ ] <ID>.2 …

### Steps
<per sub-task: ordered 2–5 minute steps. Each: write the failing test → run,
see it fail → implement → run, see it pass. Commits follow the project's
commit settings, never the implementer.>

### Done when
<each as a test: given … when … then …, including unhappy paths>

### Locked tests
<test files that become read-only once the owner approves them>

## As built
<differences between this spec and the merged code, and why>
```
