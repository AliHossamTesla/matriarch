# Backend: files

Memory as folders of Markdown files: works offline, can live in its own git
repository, and needs no account. Works only in tools that can read and write
files on the machine that holds the folders (Claude Code, Codex, an IDE chat
with file access). Chat apps without file access cannot use it; there, the
session ends with ready-to-paste updates (`../memory.md` §5).

If the `path` for a memory that uses this backend is empty, or the folder does
not exist, stop and tell the owner. Never take an empty result as "no memory".

## Layout

Two separate trees. They must not overlap, must not be inside any product
repository that goldfish search, and must not be inside `~/.matriarch/`. The
personal tree must never be inside the central tree or any shared repository.

```
<memory.central.path>/                 shared (often its own git repository)
  registry/<project-slug>.md           one row per project
  <project-slug>/
    hub.md                             Start here, Rules, People, Environment,
                                       Settings, Where we are
    decisions/<ID>.md
    questions/<ID>.md
    tasks/<ID>.md
    worklog/<YYYY-MM-DD>-<session-slug>.md
    library/<slug>.md

<memory.personal.path>/                yours only, never shared
  personal/<YYYY-MM-DD>-<slug>.md
```

Registry row for a files project: `Hub` = `<project-slug>/hub.md`;
`Data sources` empty (the five folders above are fixed). `setup` creates
`hub.md` and the five folders.

## Row format

One file per row.

- **One-line properties** (title, ID, Status, Area, dates, people, Ref, links)
  go in front matter, one `key: value` per line, with the property names of
  `../memory.md` §2. Checkboxes are `true` or `false`. A relation holds the
  target row's ID (or IDs, comma-separated).
- **Multi-line properties** (Statement, Progress, Notes, Summary, Answer, Body)
  go in the body, each under its own `## <Property>` heading, written with the
  `section` command.
- Anything else in the body is the row's page.

```markdown
---
ID: ORD-D04
Decision: One item table for raw and prepared items
Status: Proposed
Area: ORD
Decided by: <name>
Date: 2026-11-16
Ref: ORD-DB-02
Superseded by:
---
## Statement
Decision: …
Status: …
```

**Child pages** (prompts, reports, packets, findings) live in a folder named
after their parent file without `.md`:
`tasks/ORD-API-03/Prompt · ORD-API-03.data.md`. A child's own children go in a
folder named after the child. In titles, replace `/` with `-`
(`Findings · zoom-out · claude-code-opus · 2026-11-16.md`).

## Operations

`files_tool.py` next to this file does the routine work:
`python3 ROOT/core/backends/files_tool.py <command>`. It prints JSON; an error
is `{"error": …}` with exit code 1.

| Operation | How |
| --- | --- |
| `find_registry` | `query <central>/registry` |
| `read_page` | `get <file>` (properties, `## ` sections, body) |
| `schema` | the tables in `../memory.md` §2 (files have no stored schema) |
| `query` | `query <dir> Key=Value Key=a\|b Key!=Value Key~text Date>=YYYY-MM-DD` |
| `create_row` | `new <dir> <ID or slug> Key=Value …`, then `section` for multi-line properties; fails if the file exists |
| `update_row` | `set <file> Key=Value …` for one-line properties; `section <file> <Name> <textfile>` for multi-line ones |
| `child_page` | write `<parent without .md>/<title>.md` |
| `edit_page` | `section <file> <Name> <textfile>` (for example the hub's `Where we are`) |

## Sharing the central memory between people

Put the central tree in its own git repository.

- `git pull` at the start of the session, and again right before the claim
  check and before choosing a new ID.
- Commit and push right after creating a claim row (Work log, In progress), any
  row with a new ID, and any change to a row another session may touch (Tasks,
  Decisions, Open questions, the hub). Then the next person's pull sees it.
- A push rejected because someone else pushed first: pull, check whether the
  same row or ID was changed, resolve with the owner if it was, then push.

The personal tree is never pushed to a shared remote.
