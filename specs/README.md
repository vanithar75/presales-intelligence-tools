# Feature specs (Spec-Driven Development)

Product authority: [`../SPEC.md`](../SPEC.md).

## How to use with Cursor

1. Open `SPEC.md` and pick the next open slice (recommended order below).
2. Ask the agent: *Implement `specs/00x-….md` only; follow SPEC Phase 2.*
3. Agent updates the slice **Status** and checkboxes when done.
4. Do not start the next slice until validators for the current slice pass.

## Slice index

| ID | File | Status | Depends on |
|----|------|--------|------------|
| 001 | [001-ontology-governance.md](001-ontology-governance.md) | Planned | — |
| 002 | [002-match-quality.md](002-match-quality.md) | Planned | 001 helpful, not hard |
| 003 | [003-feedback-loop.md](003-feedback-loop.md) | Planned | — |
| 004 | [004-persistence-lite.md](004-persistence-lite.md) | Planned | — |

## Slice template (for future specs)

Each file must include: Context, Requirements, Out of scope, Acceptance tests, Implementation notes, Status.
