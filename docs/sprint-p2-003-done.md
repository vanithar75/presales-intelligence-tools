# Phase 2 / 003 — Feedback loop (done)

**Date:** 2026-07-12  
**Spec:** [specs/003-feedback-loop.md](../specs/003-feedback-loop.md)

## Flow

```text
UI accept/correct/reject
  → append ontology/l2_feedback.jsonl (audit, gitignored)
  → upsert ontology/l2_review_queue.json
publish CLI (accept/correct only)
  → dedupe → ontology/l2_synonyms.json (status: analyst_accepted)
```

## Commands

```bash
# After UI feedback:
py -3.12 ingest/publish_l2_feedback.py --dry-run
py -3.12 ingest/publish_l2_feedback.py
py -3.12 ontology/validate_l2.py
```

## Verified

- POST `/api/feedback/synonym` accept → JSONL + queue `pending`
- Reject → queue `rejected`, never merged
- First publish: 492 → **493** synonyms
- Second publish: no duplicate
- `validate_l2.py` OK
