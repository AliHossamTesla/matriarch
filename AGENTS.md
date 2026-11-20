# Working on Matriarch

Rules for anyone (human or agent) changing this repository.

1. **Method only.** Skills, personas, standards and core files describe how to
   work. They never contain a project's facts: no Notion URLs or collection IDs,
   no repository names other than this one, no people's names, no business
   rules. Those live in each project's Notion hub. `tests/` enforces this.
2. **One source, generated adapters.** Edit `plugin.json`, `personas/`,
   `skills/`, `core/`, `standards/`, `settings/` and `dashboard/template.html`
   only. Run `python3 scripts/build.py`; never hand-edit `.claude-plugin/`,
   `.codex-plugin/`, `.agents/` or `dashboard/settings.html`. A new invariant goes
   into both `core/tools/matriarch.py` and the dashboard template, with the same
   text (a test checks it).
3. **Every skill starts with the "Before you start" block** that resolves `ROOT`
   the same way, so the claude.ai zips work.
4. **Personas are goldfish.** A persona never gets Notion access or chat history
   and never writes files (the synthesizer writes its report only).
5. **Upstream material** keeps its attribution comment with the EGM commit. When
   pulling a newer upstream version, update the commit and `NOTICE`.
6. **Plain English** in every file: short sentences, no promotional adjectives.
7. Before committing: `python3 scripts/build.py --check` and `python3 -m pytest`.
   Design changes go to `docs/design.md` first.
8. **Every change is a new commit with a new version.** Never amend or force-push
   `main`. Raise the version in `plugin.json` and `pyproject.toml` (patch for
   fixes, minor for new behavior, major for breaking changes) and add a
   `CHANGELOG.md` entry; installed copies update only when the version changes.
   Changes reach `main` through a reviewed pull request (`CONTRIBUTING.md`).
