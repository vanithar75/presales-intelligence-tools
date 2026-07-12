# 003 — Feedback loop

**Status:** Planned  
**SPEC refs:** FR-3  
**Owner:** engineering  

---

## Context

Sprint 4 appends analyst feedback to `ontology/l2_feedback.jsonl` only. Phase 2 must turn accepted/corrected feedback into L2 synonyms via a review queue and publish step.

## Requirements

1. Keep JSONL audit append on every feedback action (`accept` / `correct` / `reject`).
2. On `accept` or `correct`, upsert into `ontology/l2_review_queue.json`:
   - `phrase`, `capability_id`, `action`, `ts`, `note`, `source: analyst_ui`
3. Provide CLI `ingest/publish_l2_feedback.py` (name flexible) that:
   - Reads review queue
   - Dedupes against existing `l2_synonyms.json` (normalized phrase + capability_id)
   - Appends new synonyms with `status: analyst_accepted`, `match_method: feedback`
   - Updates L2 counts metadata
   - Clears or marks queue items as `published`
4. Rejected items stay in JSONL / queue with `action=reject` and are never merged.
5. UI may show a short confirmation that item was queued (already has save status).

## Out of scope

- Full multi-user review workflow / auth
- Automatic re-train of seeds from feedback
- Editing L1 from the feedback form

## Acceptance tests

- [ ] POST `/api/feedback/synonym` with `accept` writes JSONL **and** review queue entry
- [ ] Publish CLI increases `l2_synonyms.json` synonym count when given a novel phrase
- [ ] Re-running publish on same phrase does not duplicate
- [ ] `validate_l2.py` OK after publish
- [ ] Reject path does not appear in published L2

## Implementation notes (files)

- [app/match_api.py](../app/match_api.py)
- [app/static/app.js](../app/static/app.js) (minor status copy if needed)
- [ontology/l2_synonyms.json](../ontology/l2_synonyms.json)
- New: `ontology/l2_review_queue.json`, `ingest/publish_l2_feedback.py`
- Ensure `l2_feedback.jsonl` remains gitignored; consider committing empty `l2_review_queue.json` skeleton `{ "items": [] }`

## Status

Planned — not started.
