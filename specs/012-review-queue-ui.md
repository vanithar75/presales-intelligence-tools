# 012 — Review queue UI

**Status:** Done  
**SPEC refs:** Phase 3 Lite FR-P3.3  
**Owner:** engineering  

---

## Context

Accept/correct feedback already stages into `ontology/l2_review_queue.json` and CLI publish merges to L2. Analysts need a light UI to see the queue and publish without the CLI.

## Requirements

1. `GET /api/review-queue` — return queue items (pending / published / rejected).
2. `POST /api/review-queue/publish?dry_run=true|false` — wrap `ingest/publish_l2_feedback.py` logic.
3. UI panel: list items by status; “Publish pending” button; show last publish summary.
4. Reuse existing static styles; no auth.

## Out of scope

- Multi-user SME workflow, conflict UI, DB-backed queue, redesign

## Acceptance tests

- [x] GET returns current queue JSON shape
- [x] POST dry_run does not mutate files; real publish merges pending accepts/corrects
- [x] Rejects never merge
- [x] Panel visible on analyst UI

## Implementation notes (files)

- `ingest/publish_l2_feedback.py` — `publish_review_queue()` / `load_review_queue()`
- `app/match_api.py` — GET/POST endpoints
- `app/static/index.html`, `app/static/app.js`, `app/static/styles.css`

## Status

Done — 2026-07-18.
