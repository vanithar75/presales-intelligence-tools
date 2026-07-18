# NG911 emergency call handling (foundation)

**Date:** 2026-07-18

## What changed

- New `ontology/expand_ng911_l1.py` — promote 5 NG911 stubs → draft + append **20** call-handling caps (ESRP, ECRF/LVF, text-to-911, multimedia, abandoned calls, TTY/RTT, ACD, recording, Phase II, ADR, failover, EIDO, telematics, CAD handoff, etc.).
- Published **20** via `ontology/top20_ng911.json` (sprint **P4-NG911**).
- Deterministic NG911 seeds; `demo_ng911_requirements.txt`; `ng911_demo` eval suite.
- Matcher prefers `NG911.*` seeds (0.96) over generic LMR “emergency call” hits.
- **+15** CommandCentral → NG911 L3 mappings.

## Results

| Metric | Value |
|--------|-------|
| NG911 caps | **25** |
| NG911 published | **20** |
| Catalog schema | **1.8** |
| ng911_demo | **1.00** (18/18) |
| Stubs remaining | **21** (≥20 validator) |
| LMR mid-doc | **0.702** (unchanged) |

```bash
py -3.12 ontology/expand_ng911_l1.py --dry-run
py -3.12 ontology/eval_match.py
```
