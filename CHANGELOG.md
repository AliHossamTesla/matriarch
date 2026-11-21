# Changelog

Every change to `main` adds an entry here and raises the version in
`plugin.json` and `pyproject.toml` (see `CONTRIBUTING.md`). Installed copies
update when the version changes.

## 0.3.0 (2026-11-21)

- `setup`: new §2e, a settings review on first use. It detects what it can
  (language, time zone, tests in git, solo owner, merge methods), shows about
  ten main settings in one table with the proposed value and why, asks one
  question, validates the answer and writes only the differences. It replaces
  the question-per-group walk through the project settings. A second `setup`
  on a project skips it; settings then change through `status` or the dashboard.
- `start.md`, README and design doc describe the review.

## 0.2.2 (2026-11-21)

- Notion backend: query one data source at a time. Filter queries are the
  default; SQL only for single-source questions; never SQL across databases,
  which needs the Business plan. A failed `entitlement_required` query is
  re-run as one filter query per data source (#5).
- `memory.md` §3: new read rule "One database per query"; `status` and `tidy`
  follow it.
- `doctor`: new check "Queries" tries one filter query and, on Notion, one
  two-database SQL query, and reports `info` when the plan does not allow it.

## 0.2.1 (2026-11-20)

- `models.order`: a model now matches the longest name it contains, so
  `gpt-5-mini` is no longer read as `gpt-5` and an inverted pair is caught.
- Settings page: every field's label names its control for screen readers;
  focus stays on the reset buttons; clearer note on the personal page.
- Status lines in the README and design doc say v0.2.

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
