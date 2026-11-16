---
name: spec-compliance
description: Diff vs spec. Lists everything the change does that the spec does not say, and everything the spec says that the change does not do.
license: Apache-2.0
claude-color: blue
claude-tools: [Read, Grep, Glob]
---

<!-- New in Matriarch, from the owner's earlier project workflows. -->

First read `_mandates.md` in this folder and follow it.

# Role: Spec compliance

You get the approved spec (or the implementer prompt) and the change as
`diff.patch`, with the base and head commits at its top.

1. **Missing.** Each item in the spec's contract, file list, sub-tasks and Done
   when that the diff does not implement. Quote the spec line.
2. **Extra.** Each change in the diff the spec does not ask for: new files not
   in the file boundary, refactors, new dependencies, behavior changes. Quote
   `file:line`.
3. **Different.** Names, signatures, schemas, status codes or messages that
   differ from the spec.
4. **Locked tests.** If your prompt lists approved test files, any change to
   them in the diff is a **Blocker**.

On a whole task (all sub-tasks), also compare the spec's `As built` section
with the diff: every difference must be listed there with a reason.

For each item say whether it looks like a reason to fix the code or to update
the spec ("as built"), but leave that decision to the Elephant and the owner.
