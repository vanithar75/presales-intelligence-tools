# L1 publish checklist (SME)

Use before promoting capabilities with `ontology/publish_l1.py`.

**Priority set:** [ontology/top50_bid_desk.json](../ontology/top50_bid_desk.json) (SPEC §4).

## Per-capability review

For each alias in the publish batch:

1. **Definition clarity** — One sentence a bid analyst can use without tribal knowledge; no vendor product names in the definition.
2. **ID / alias stability** — Do not rename `id` or `alias` after publish; deprecate and add a new ID if meaning changes.
3. **Stack / mission tags** — `stack_class` fits INFRA/SENS/PLAT/APP/SVC/XCUT; `mission_tags` match detect→after_action vocabulary.
4. **P25 / standards ref** — If `p25_ref` is set, it points at a real clause family; if null, that is OK for non-P25-specific caps.
5. **Not a stub** — `status` must not be `stub`. Vertical stubs (CAD/NG911/Sensors/MCX) stay stub until a later SPEC phase.
6. **Vertical** — Bid-desk top-50 are LMR (`vertical: LMR`).

## Batch steps

```bash
# Preview top-50
py -3.12 ontology/publish_l1.py --dry-run

# Publish top-50 (default)
py -3.12 ontology/publish_l1.py

# Wave 2 (Phase 3 Lite)
py -3.12 ontology/publish_l1.py --priority-file ontology/top50_wave2.json --dry-run
py -3.12 ontology/publish_l1.py --priority-file ontology/top50_wave2.json

# Validate
py -3.12 ontology/validate_l1.py
```

**Wave 2 priority set:** [ontology/top50_wave2.json](../ontology/top50_wave2.json).

## After `generate_l1.py`

`ontology/generate_l1.py` rebuilds the catalog from code and **resets status to draft**.  
If you regenerate, **re-run publish** (and re-check this checklist) before treating the catalog as published.

## Out of scope for a publish pass

- Mass rewriting of definitions
- Publishing stub verticals
- Changing the PSERS ID scheme
