# 010 — L1 publish wave 2

**Status:** Done  
**SPEC refs:** Phase 3 Lite FR-P3.1  
**Owner:** engineering  

---

## Context

Phase 2 published the top-50 bid-desk set. ~100+ LMR capabilities remain `draft`. Bid-desk trust improves by promoting a second curated wave without expanding verticals or stubs.

## Requirements

1. Machine-readable priority list `ontology/top50_wave2.json` (≥25 aliases, not overlapping top-50, LMR only).
2. Extend `ontology/publish_l1.py` with `--priority-file` (default remains `top50_bid_desk.json`).
3. Publish wave2 → `status: published`; refuse stubs; bump catalog metadata; decision-log entry.
4. `validate_l1.py` stays green. Target: ≥75 published total (50 + ≥25).

## Out of scope

- Definition rewrites, ID renames, stub publish, `generate_l1.py` regenerate

## Acceptance tests

- [x] `publish_l1.py --priority-file ontology/top50_wave2.json --dry-run` resolves ≥25
- [x] After publish: ≥75 L1 rows with `status=published`
- [x] Stub refusal still works
- [x] Decision-log entry for wave2
- [x] `validate_l1.py` OK

## Implementation notes (files)

- `ontology/top50_wave2.json`, `ontology/publish_l1.py`, `ontology/l1_capabilities.json`
- `docs/decision-log.md`, `docs/l1-publish-checklist.md` (reuse)

## Status

Done — 2026-07-18. Catalog `schema_version` **1.2**, sprint **P3-010**, **75** published (+25 wave2).
