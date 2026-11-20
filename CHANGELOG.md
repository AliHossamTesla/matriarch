# Changelog

Every change to `main` adds an entry here and raises the version in
`plugin.json` and `pyproject.toml` (see `CONTRIBUTING.md`). Installed copies
update when the version changes.

## 0.2.0 (2026-11-20)

- First public release.
- `doctor` command: checks tools, settings, memory and the project hub.
- Settings page (`dashboard/settings.html`): edit, check, import and export
  settings offline; one button resets everything to the defaults.
- `models.order`: model names from strongest to weakest. A tier never gets a
  stronger model than the tier above it.
- Open-source files: contributing guide, security policy, code of conduct,
  issue and pull request templates.

## 0.1.0

- First version: memory protocol (Notion and files backends), sessions,
  goldfish reviews with a deterministic gate, settings in layers, 11 commands.
