---
name: doctor
description: Check that Matriarch is ready to use here - tools, settings, which project applies, the memory connector, the registry, the hub and its databases - and say how to fix each problem. Read-only. Use before the first session in a tool or project, or when something does not work.
license: Apache-2.0
---

# matriarch:doctor — is everything ready?

## Before you start

Matriarch's shared files live in the plugin root (`ROOT`): in Claude Code
`${CLAUDE_PLUGIN_ROOT}`; in other tools two folders above this file; when this
skill was uploaded alone (claude.ai), the `matriarch/` folder next to this file.
Read `ROOT/core/memory.md`, `ROOT/core/settings.md` and `ROOT/core/voice.md`
now, and `ROOT/core/backends/<name>.md` for each backend in use.

**Read-only.** Doctor writes no memory rows, no settings and no Work log row.
The only file it writes is one temporary copy of the hub settings (§2.7),
outside the repository, deleted after. It reports and says how to fix.

Session name: `<Project or tool> · doctor`.

## 1. Local checks (where code runs)

From the repository folder the owner will work in:

```
python3 ROOT/core/tools/matriarch.py doctor
```

(add `--user <file>` or `--project <file>` if the settings live elsewhere). It
checks Python, PyYAML, git, the GitHub CLI, the Claude Code version, the
settings and their invariants, which `projects:` entry applies here, `files`
memory folders and the repository state. Status `info` means "not checked
here": Notion memory is checked in §2. Keep its results for the report.

In a chat app without code execution, skip to §2 and check the settings block
in the instructions by hand against `ROOT/settings/schema.json`.

## 2. Memory checks (through the connector)

Run each, stop the section at the first `fail` that makes the rest impossible:

1. **Connector:** the tool for each memory backend in use is present and
   answers (one search or one read).
2. **Registry:** found under `memory.central.registry` (or the `files` folder);
   exactly one.
3. **Project row:** the project from the local checks, the owner's words, or the
   repository's remote matches exactly one row; `Status` is Active.
4. **Hub:** `Hub` opens; it has the sections Rules, People, Environment,
   Settings and Where we are. List the missing ones.
5. **Databases:** each address in `Data sources` opens. Compare each schema with
   `memory.md` §2 (through the registry `Map` for adopted hubs): list missing
   properties, wrong types and missing select options (for example the Work log
   Status option `Archived`, the Tasks properties `Mode` and `Progress`). Missing ones are `warn`
   for adopted hubs and `fail` for hubs made by `setup`.
6. **Queries:** run one filter query on the Work log that returns at most one
   row. It must work (`fail` if not). Then, for the Notion backend only, try one
   small SQL query that names two of the databases (read-only, at most one
   row). If it fails with `entitlement_required`, report `info: cross-database
   SQL not available on this plan; sessions query one database at a time`. Any
   other error is `warn`.
7. **Hub settings:** save the Settings block to a temporary file outside the
   repository (the only file doctor writes; delete it after), then run
   `matriarch.py config --user <your user settings> --project <that file>`.
   It must pass.
8. **Personal memory** (unless `none`): opens by `memory.personal.url` (Notion)
   or path (`files`); has the `Personal` database. Never search for it by
   title.
9. **Weekly tidy:** the hub's Environment has a `Tidy schedule:` line, or
   `schedule.tidy.when` is `off`.

## 3. Report

One table, `fail` first, then `warn`, then `info`, then `ok`:

```
| Status | Check | What I found | Fix |
```

Then one line: ready, or the first thing to fix. For each fix, name the command
or the setting (`setup`, `matriarch.py config`, a key in the user settings, a
property to add). Offer to run `setup` when the registry, the hub or the
personal memory is missing. Change nothing yourself.
