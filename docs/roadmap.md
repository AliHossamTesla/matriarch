# Roadmap

## Done in v0.1

- Persistent central and personal memory, Notion and files backends.
- Skills `setup`, `status`, `plan`, `exec`, `check`, `fix`, `docs`, `discuss`,
  `review`, `tidy`, `goldfish`.
- Deterministic review gate and settings validation (`core/tools/matriarch.py`).
- Merges bound to the reviewed commit; trust order; confidentiality settings.
- Model tiers, advisor, quick / standard / critical modes.
- Weekly tidy before the usage reset; three starting guides.

## Parked

Each item is sound but larger than v0.1 needs. They are parked, not dropped.

| Item | Why it matters | Why parked |
| --- | --- | --- |
| **Atomic task claims** (a coordination store with compare-and-swap, leases, fencing tokens) | Two sessions can still claim one task at the same instant; Notion and files have no locks | Serves teams with many parallel writers; v0.1 promises one writer per task |
| **Local pending-event journal** (idempotent replay to memory after an outage) | A memory outage mid-session can leave code ahead of memory | The ready-to-paste fallback covers a single user; a journal needs a sync command and conflict rules |
| **Immutable review records** (hashes of spec, prompt, diff, decisions and policy bound to each approval) | Full audit trail: any change invalidates approval | The gate already records the target hash per round; full binding needs the journal first |
| **Policy kernel as a state machine** (every transition checked by code) | Takes trust off model instructions | Code runs only in Claude Code and Codex; start from the existing gate and config checks |
| **Integration test harness** (live runs in Claude Code, Codex, Notion: timeouts, injected documents, moved PR heads, outages) | Proves the guarantees, not only the structure | Needs accounts and fixtures; next after the first real project |
| **Reviewer evaluation loop** (cases with answer keys, judge model, held-out set) | Tune personas by measurement, as the egm-chat study did | Needs a case set from real projects |
| **Reproducible release zips** (fixed timestamps, manifest with hashes) | Byte-identical builds | Cosmetic until there are public releases |
| **More backends** (Google Sheets, SQLite) | Teams without Notion | `files` covers offline use for now |
| **Name and trademark check** for "Matriarch" | Other software uses the name | Before any public branding |
