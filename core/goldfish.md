# Goldfish protocol

A goldfish is a reviewer with **no shared history**. Its value is that it does
not know what the Elephant knows, so it notices what the document leaves out.
Anything that leaks the Elephant's context into a goldfish turns it into a
second, weaker elephant.

## 1. What a goldfish gets

Every lens gets `personas/_mandates.md`, its own persona file, the target (a
file, or text in a packet) and the inputs in this table, and nothing more.
Decisions quoted inside the target itself (a spec or prompt quotes the rows it
relies on) are part of the target and are fine.

| Lens | Standard | Extra inputs |
| --- | --- | --- |
| comprehension | none | none: the target only |
| zoom-out | `zoom-out` | `decisions.md`, `AGENTS.md`, the repository |
| business | none | `decisions.md`, area guides for the area |
| decision-fit | none | `decisions.md` |
| design-critic | `feature-spec` | `AGENTS.md` |
| implementation-readiness | `implementation-readiness` | the spec when the target is a prompt |
| codebase-fit | `implementation-readiness` | `AGENTS.md`, the repository |
| code-quality | none | the changed files in full, golden files named in the prompt, `AGENTS.md`, the repository |
| spec-compliance | none | the spec (or prompt), `diff.patch`, the locked tests list |
| test-evidence | none | the spec's Done when, the test files |
| correctness | none | `AGENTS.md`, the changed files, the repository |
| security | none | `AGENTS.md`, the changed files, the repository |
| premortem | none | the decision brief and its stance |

`decisions.md` holds the relevant Decisions rows copied as text (Decision,
Status, Decided by, Date, Statement). Pass `AGENTS.md`, never `CLAUDE.md`: the
Claude Code agents skip `CLAUDE.md` on purpose.

Never pass: this conversation, your reasoning, your preferred answer, your
earlier findings, other lenses' findings, a summary of the chat, or memory
access (central or personal). A goldfish must not search or read memory; if it needs a fact, it
reports the gap as a finding.

**Keep review files out of the goldfish's reach.** For each lens, copy its
inputs into its own folder `~/.matriarch/<project>/<ref>/<point>-r<n>/in/<lens>/`
and pass only that folder's absolute paths. Reports, resolutions and earlier
rounds go to `~/.matriarch/<project>/_elephant/<ref>/`, which is never passed to
a lens. Nothing goes inside the repository, because lenses search it.

**Targets must be files.** A memory page or Google Doc under review is first
exported to a Markdown file in the review folder; the goldfish reads the file.

Tell every goldfish, in the prompt: "Judge, do not oppose: say what is wrong
and say plainly what is sound. Only a broken stated goal, limit, rule or
decision, data loss, a security hole or something that cannot be built is a
Blocker. Quote the line you mean. If you could not read a file you were
given, say so and stop: you have not reviewed."

## 2. How to start one (in order of preference)

Pick each lens's model first ([`models.md`](models.md) §2).

1. **A plugin subagent in this tool.**
   - Claude Code (2.1.271 or later): the `Agent` tool with the plugin agent
     `matriarch:<lens>`. These agents have read-only tools, no MCP and no
     `CLAUDE.md`. If the named agent is missing, use path 2 or 3; a
     general-purpose agent has memory tools, skills and write tools and is not a
     goldfish.
   - Codex: `spawn_agent` with `fork_context: false` (or `fork_turns: "none"`,
     whichever the tool schema offers), telling it to read the persona file
     first. Codex may still load `AGENTS.md` files; that is a known limit.
   - Claude Cowork: subagents cannot start subagents; dispatch every lens from
     the main context.
2. **A separate CLI run** in the repository, for another model or when no
   subagent tool exists:
   - `claude -p "<prompt>" --strict-mcp-config --mcp-config <empty.json>
     --allowedTools "Read,Grep,Glob"` where `<empty.json>` is
     `{"mcpServers": {}}` in the review folder. It still loads `CLAUDE.md`.
   - `codex exec -s read-only -c 'mcp_servers={}' "<prompt>"`, or run it with a
     separate `CODEX_HOME` whose config has no MCP servers. Check first that
     `codex mcp list` in that setup shows no memory server (such as Notion). It still loads
     `AGENTS.md`.
   Give it a generous timeout.
3. **A review packet** (claude.ai, ChatGPT, or a deliberate cross-tool review):
   see §4.

**Cross-model rule.** When another model is reachable (the other CLI, or a
packet the owner runs in another tool), run at least one lens on it. Record the
tool and model with each lens's result.

If none of the three is possible, stop and tell the owner. A review in your own
context is not a goldfish review; do not run one and call it that.

## 3. Collecting results

- Run the lenses of one stage in parallel; wait for all before the next stage.
- A lens that fails, times out or returns nothing **did not review**. Retry once;
  if it fails again, its status is `not run`. Never count it as zero findings.
- Keep a finding only if it has a location and a concrete reason. Merge
  duplicates; keep the higher severity.
- Severity is the goldfish's call. The Elephant may contest it in the resolve step (`resolve.md`)
  but never silently lowers it.
- The synthesizer (`personas/synthesizer.md`) can merge when your tool allows
  nested subagents; otherwise merge in the main context.

## 3b. Confidential content

`project.confidentiality` decides what may leave the machine:

- **Before any packet, CLI run on another provider, or memory page holding code**,
  where code runs: `python3 ROOT/core/tools/matriarch.py export --to external|memory
  [--approved-by <owner>] <files>`. It scans for secrets and personal data and
  applies the settings below; go on only if it exits 0. Any hit: show the owner
  the lines and remove or mask them. In a chat app, do the same checks by hand:
  keys, tokens, passwords, connection strings, private keys, `.env` values, real
  names, phone numbers, emails, national IDs.
- `external_review: deny`: no packets and no goldfish on another provider; use
  path 1 or a local CLI of the same provider only.
- `external_review: ask`: each packet or other-provider run needs the owner's
  yes, given after you say which tool and model will see which files.
- `store_code_in_memory: false`: packets stay local files (not memory pages);
  memory gets findings with file:line references, no code quotes or diffs.

## 4. Review packets

A packet is a **self-contained prompt for one lens**. It holds everything the
goldfish needs as text, so it runs in any fresh chat in any tool, with or
without the plugin, without the repository and without memory access.

**The Elephant writes one packet per lens** (a decision brief may put all its
stances in one packet) as a Markdown file in the review folder, and, unless
`store_code_in_memory` is false, also as a child page of its own Work log row,
titled `Packet · <target> · <lens>`. Confidential rules first (§3b):

```
# Matriarch review packet — <target> — <lens>
Run in a NEW chat with no project, no memory and no connectors you do not need
(claude.ai: incognito chat, outside any Project; ChatGPT: temporary chat).
Do not look anything up beyond this text. Reply only with your findings.

## Instructions
<full text of personas/_mandates.md>
<full text of personas/<lens>.md>
## Standard
<full text of the standard, or "none">
## Artifact: <path>@<commit or "draft">
<full text, with line numbers>
## Context file: <path>            (one section per file)
<full text>
## Decisions                         (only lenses that get decisions.md, §1)
<quoted rows>
```

Lenses that must search the codebase need the repository: `codebase-fit`, and
`correctness` or `security` on a diff. Run them through path 1 or 2, not as a
packet. A `zoom-out` packet skips its reuse search and must say so in its
findings.

The Elephant then tells the owner: open a fresh chat as the packet says, paste
the packet (or, where the plugin and a memory tool are installed, run
`matriarch:goldfish <packet page address>`), and bring the findings back by pasting them
into the Elephant session. Then the Elephant records on its Work log row:
`Waiting on packet: <lens> · <page address>` so any later session can resume.

When findings come back, the findings page for that run must exist exactly
once, as a child of the packet page titled `Findings · <lens> · <tool>/<model> ·
<date>`. `goldfish` creates it when it has a memory tool; otherwise the Elephant
creates it from the pasted text after checking none exists for that run. Never
edit a previous run's page.
