# Contributing

Thanks for helping. Matriarch is small on purpose; changes that keep it small
and plain are the easiest to accept.

## Before you start

- For anything larger than a fix, open an issue first and say what you want to
  change and why. It saves you work if the idea does not fit.
- Read [`AGENTS.md`](AGENTS.md). Its rules apply to people and agents alike:
  method only (no project facts), one source with generated adapters, plain
  English.

## Making a change

1. Fork the repository and create a branch from `main`.
2. Set up: `pip install -e ".[dev]"`.
3. Edit only the source files listed in `AGENTS.md`, then run
   `python3 scripts/build.py` to regenerate the adapters.
4. Raise the version in `plugin.json` and `pyproject.toml` and add an entry at
   the top of `CHANGELOG.md`:
   - patch (`0.2.0` → `0.2.1`): fixes and wording;
   - minor (`0.2.0` → `0.3.0`): new commands, settings or behavior;
   - major: changes that break existing settings or memory.
5. Run `python3 scripts/build.py --check` and `python3 -m pytest -q`. Both must
   pass.
6. Open a pull request against `main` and fill in the template.

Every pull request is reviewed by a maintainer listed in
[`.github/CODEOWNERS`](.github/CODEOWNERS) and needs the tests to pass before it
can merge. Commits use your own name; please do not add private project names,
URLs or IDs anywhere in the repository (the tests check common cases).

## Reporting a bug

Open an issue with the bug template. Include the output of
`python3 core/tools/matriarch.py doctor`; read it first and remove any path or
name you do not want to share.

## Security problems

Do not open a public issue. See [`SECURITY.md`](SECURITY.md).
