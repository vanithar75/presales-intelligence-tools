# Feature specs (Spec-Driven Development)

Product authority: [`../SPEC.md`](../SPEC.md).

## How to use with Cursor

1. Open `SPEC.md` and pick the next open slice.
2. Ask the agent: *Implement `specs/04x-….md` only; Phase 6 Lite CAD+NG911; no LLM; no generate_l1; no MCX; no Sensors rework.*
3. Agent updates Status when done.

## Slice index

| ID | File | Status | Depends on |
|----|------|--------|------------|
| 001–004 | Phase 2 | Done | — |
| 010–013 | Phase 3 Lite | Done | — |
| 020–023 | Phase 4 Lite CAD | Done | — |
| 030–032 | Phase 5 Lite Sensors | Done | — |
| 040 | [040-cad-ng911-ontology.md](040-cad-ng911-ontology.md) | Done | Phase 5 |
| 041 | [041-cad-ng911-match.md](041-cad-ng911-match.md) | Done | 040 |
| 042 | [042-cad-ng911-publish.md](042-cad-ng911-publish.md) | Done | 040–041 |

**Stop here:** Phase 6 Lite CAD+NG911 complete. MCX / multi-vendor / broader corpus require a new SPEC amendment.
