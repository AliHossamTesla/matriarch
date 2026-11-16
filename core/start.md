# Starting a project, and the daily loop

Before anything else, run `doctor` in the tool and folder you will work in: it
checks the tools, the settings and the memory, and says how to fix each problem.
To choose settings, the dashboard (`dashboard/settings.html`) shows each one,
checks them and exports the files.

Three starting points need different first steps. `setup` asks which one
applies, proposes the settings below, and then follows the matching section.
After that, every project runs the same daily loop (§4).

| Stage | Signs |
| --- | --- |
| **New** | no code yet, or only a skeleton |
| **Existing, small** | one person can read the main flows in a day or two; few modules |
| **Existing, large** | an enterprise or legacy system; many modules, teams and years of history; nobody reads all of it |

## 1. New project

Settings to propose: defaults (`standard` mode, tests first, lock by `commit`,
commits by plan).

1. **`setup`**: new hub. Areas = the modules you plan, even if empty.
2. **`discuss`: vision and scope.** Who it is for, the problem, what version 1
   does and does not do. Each answer becomes a Decisions row.
3. **`discuss`: the big choices** in decision mode: stack, data store, hosting,
   how modules talk. These are one-way doors; give them evidence and a
   pre-mortem.
4. **First task: the repository skeleton** (`<AREA>-DOC-01` or `-OPS-01`) with
   `plan`: folder layout, build and test commands, an `AGENTS.md` with the repo
   rules, the spec folder, CI. The first classes written here become the golden
   files later tasks copy.
5. Then the daily loop. No `docs` sessions are needed until the code grows.

## 2. Existing, small codebase

Settings to propose: defaults. If the code has no tests yet, the first task adds
the test setup, so `tests.first` can work.

1. **`setup`**: new hub, or adopt the existing notes. Areas = the top-level
   modules.
2. **`docs` once over the codebase**, as one guide or one per main area: flows,
   data, rules, golden files, glossary, unknowns.
3. **Recover the decisions the code already made.** For each rule or convention
   `docs` found, add a Decisions row with Status Assumption and the code file as
   Source. In a `status` session the owner confirms each (Decided), corrects it,
   or drops it. From then on, reviews check new work against them.
4. If the repository has no `AGENTS.md`, the first `plan` task writes one from
   the guides.
5. Then the daily loop.

## 3. Existing, large codebase (enterprise)

The rule here: **never map everything; learn each area just before you work in
it.** Mapping a large system up front costs more than it saves and goes stale.

Settings to propose, each confirmed with the owner:

- `confidentiality.level: confidential` for client or company code
  (`external_review: ask` or `deny`, `store_code_in_memory: false`).
- `tests.lock: checksum` if tests are kept out of git.
- `commits.attribution: false` if the company forbids AI attribution.
- `merge` and `merge_method` as the team does it.
- Areas = only the modules the owner touches.
- Prompts pasted into the IDE chat when the IDE has no memory connector.

First steps:

1. **`setup`** as above.
2. **`docs environment`**: the Environment section of the hub. How to build and
   run locally (versions, flags, local database, mocks), branch rules, where
   working files live (outside the repository), who to ask for what. This is the
   page that lets a cold session start in minutes.
3. **Team conventions and rules** the owner already knows go in as Decisions rows
   with date and source. Statements from meetings are classified (decision,
   conditional preference, teaching example, open point) before they are used.
4. **Before the first task in an area: `docs <area>`.** Only that area: the flow
   the task touches, its data, its rules and, above all, its **golden files**. In
   legacy code, copying the structure of a named existing class matters more
   than any style guide.
5. **First task with `plan`**, usually in `standard` mode (`critical` for money,
   security or data). The investigation step traces one real request before
   anything is designed.
6. Then the daily loop. When a task enters a new area, `docs <area>` comes first.
   Personal memory is the place for study notes about the system.

## 4. The daily loop

| When | Session | Does |
| --- | --- | --- |
| Start of the day | `status` | what moved, what is blocked and on whom, what waits on you |
| New work | `plan <ID or idea>` | shape it, close open points, spec, sub-tasks, prompts |
| Each sub-task | `exec <sub-task ID>` in the implementer chat | tests, then code, from the prompt only |
| After each exec report | `check` inside plan | goldfish panel, gate, reply for exec, commit |
| End of the task | `check <task ID>`, then the pull request | whole-task review, PR |
| A teammate's work | `review <PR>` | panel, filtered findings, post only on your word |
| A bug | `fix <bug>` | reproduce, root cause, failing test, fix |
| A new area | `docs <area>` | learn it before planning in it |
| A question with no task | `discuss <topic>` | think together; decision mode when needed |
| Weekly, before your usage reset | `tidy scheduled` | archive noise, report stale and drifting items |

Pick the review mode per task (`models.md` §3): `quick` for small, low-risk
work keeps the loop light; `critical` where mistakes are expensive.
