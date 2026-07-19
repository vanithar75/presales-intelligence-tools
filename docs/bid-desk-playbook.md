# PSERS bid-desk playbook

**Audience:** sales, bid desk, solution architects, and technical stakeholders  
**Product:** Presales Intelligence — RFP language → L1 capabilities → MSI coverage  
**Authority:** [SPEC.md](../SPEC.md) · Explainer: [ontology-stakeholder-guide.md](ontology-stakeholder-guide.md) · C2 terms: [c2-c4i-crosswalk.md](c2-c4i-crosswalk.md) · Phase 9: [sprint-p9-done.md](sprint-p9-done.md)

**One sentence:** We never map RFP text straight to SKUs—everything routes through stable PSERS capabilities (L1).

---

## 1. Run the platform & live demo

### Start the API (PowerShell)

From the repo root:

```powershell
cd C:\Vanitha\work\Agents\presales-intelligence-platform
py -3.12 -m pip install -r requirements.txt
py -3.12 -m uvicorn app.match_api:app --host 127.0.0.1 --port 8000
```

Leave the terminal open. Confirm the server is up:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Expected: `status: ok`, `ui: true`.

### Browser URL

**http://127.0.0.1:8000/**

The header should show `API ok · P9-080` (or later sprint). If it says **API offline — start uvicorn**, the server is not running.

### 10-minute demo path

| Time | Step | Action |
|------|------|--------|
| **2 min** | **Explainer** | Scroll to **Ontology explainer**. Walk the incident swimlane (`detect` → `call_take` → `dispatch` → `respond` → `after_action` → `coordinate`). Say the one-liner above. Point at live counts and the **Vertical maturity** table. |
| **5 min** | **Load demos → Match** | **Open paste tab**. Load **full-stack** → **Run match**. Repeat with **incident-mgmt** and **MCX**. Highlight one mapped row: requirement → L1 alias → MSI coverage. |
| **2 min** | **Gaps first** | Click **Gaps first**. Unmapped rows float to the top—triage for bid follow-up. |
| **1 min** | **Export** | **Download coverage CSV** or **JSON**. Hand off to bid desk. |

**Optional C2 callout:** Paste *“Command and control supervisory views shall show active incidents”* → maps via C2 crosswalk seeds, not a new vertical.

**Do not:** dump full L1 JSON, force-directed graphs, or promise multi-vendor L3 without a SPEC amendment.

### Optional CLI (pre-demo sanity check)

```powershell
py -3.12 ontology/eval_match.py --soft
py -3.12 ontology/gap_report.py ontology/samples/demo_fullstack.txt
```

**API export (no UI):**

```powershell
$body = @{ text = (Get-Content ontology/samples/demo_fullstack.txt -Raw) } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/match/export?format=csv" -Body $body -ContentType "application/json" -OutFile psers-coverage.csv
```

Key routes: `GET /health` · `GET /api/ontology/summary` · `GET /api/demo/fixture?name=fullstack|incident|mcx` · `POST /api/match/text` · `POST /api/match/export?format=csv|json`

### Troubleshooting

| Symptom | Fix |
|---------|-----|
| **API offline** | Start uvicorn (above). Check port 8000. |
| **`mid_doc` fails in eval** | RFP PDFs are gitignored. Run `py -3.12 ingest/download_rfps.py` → `data/rfp/`. |
| **Fixture load 404** | Confirm `ontology/samples/demo_*.txt` exists; restart uvicorn after pull. |
| **PDF upload empty / slow** | Prefer paste-tab fixtures for demos. Default max pages: 20. |

---

## 2. Bid-desk match & coverage workflow

Paste buyer **shall-statements** (or upload an RFP PDF) into the analyst UI and run match. Each line of RFP language is **L2** (buyer phrasing). The matcher resolves L2 to a stable **L1 capability** (`PSERS.<STACK>.<DOMAIN>.<CAPABILITY>`) via synonym seeds and crosswalk terms—not by jumping straight to SKUs. Each mapped L1 then carries **L3 MSI coverage** (product family and support level: native, option, etc.). This three-layer bridge keeps compliance matrices stable when RFP wording changes but the underlying mission need does not.

### Demo fixtures — when to use which

Load from the Paste tab (UI buttons) or `GET /api/demo/fixture?name=<key>`.

| Fixture | File | Use when |
|---------|------|----------|
| **LMR** (`demo`) | `demo_requirements.txt` | Trunked P25, encryption/OTAR, ISSI, coverage/DAQ, NMS—classic **radio / infrastructure** bids |
| **CAD** (`cad`) | `demo_cad_requirements.txt` | Dispatch-centric RFPs: incident lifecycle, unit status, AVL, mobile CAD |
| **NG911** (`ng911`) | `demo_ng911_requirements.txt` | PSAP / i3 call-taking |
| **Incident** (`incident`) | `demo_incident_mgmt.txt` | End-to-end incident journey + C2 language |
| **MCX** (`mcx`) | `demo_mcx_requirements.txt` | MCPTT / MCVideo / MCData / LMR–MCX IWF |
| **Full-stack** (`fullstack`) | `demo_fullstack.txt` | Integrated stack maturity / gap baseline |
| **PSAP loop** (`psap`) | `demo_psap_loop.txt` | Tight call-take → CAD dispatch slice |

### Mapped vs unmapped · Gaps first

- **Mapped** — L2 → L1 with confidence and MSI coverage. Bid-desk safe when the capability is `published`.
- **Unmapped** — no L1 hit. Treat as a **coverage gap** (missing synonym, new phrasing, deferred, or out-of-scope).

Filters: **All** · **Mapped** · **Unmapped** · **Gaps first** (unmapped on top for triage).

### Coverage CSV/JSON in bid response

Columns: `requirement` · `page` · `mapped` · `capability_id` · `capability_alias` · `capability_name` · `confidence` · `method` · `msi_coverage`

1. **Compliance matrix** — filter `mapped=true`; group by L1 or MSI family.  
2. **Executive summary** — use map rate as first-pass addressability.  
3. **Gap table** — filter `mapped=false`; classify (synonym fix, roadmap, partner, defer).  
4. **Low-confidence review** — re-check weak matches before claiming full compliance.

### `POST /api/match/export`

```bash
curl -s -X POST "http://127.0.0.1:8000/api/match/export?format=csv" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"The CAD system shall create and update incidents.\nNG911 call data shall hand off into CAD.\"}" \
  -o psers-coverage.csv
```

### Feedback → review queue → publish L2

UI **accept/correct** → pending review queue. **Reject** is audit-only. SME **Dry-run publish** then **Publish pending** (or `ingest/publish_l2_feedback.py`) merges into L2 synonyms for the next match run—without editing L1/L3 in the field.

---

## 3. Ontology map for conversations

PSERS is a **capability ontology**, not a product catalog. Buyer RFP language (L2) maps to stable capabilities (L1), then to MSI products (L3). Never skip L1.

**Catalog snapshot (Phase 10):** 351 L1 capabilities — **351 published**, 0 draft, 0 stubs · 493 L2 synonyms · **358** L3 mappings (20 MSI products).

### Mission swimlane — where verticals sit

```text
detect → call_take → locate → dispatch → respond → coordinate → inform → after_action
```

| Mission tag | Stage | Primary verticals / aliases |
|-------------|-------|----------------------------|
| `detect` | Sense / trigger | **Sensors** — `VIDEO.*`, `IOT.*`, `UAS.*` |
| `call_take` | PSAP intake | **NG911** — `NG911.*` |
| `locate` | Find / geolocate | **GIS** — `GIS.*` |
| `dispatch` | Assign / route | **CAD** — `CAD.*` |
| `respond` | Field action | **FIELD** — `FIELD.*`, `CAD.MOBILE_CLIENT`; **LMR** / **MCX** |
| `coordinate` | Command view | **EOC** — `EOC.*`; `CAD.COMMAND_VIEW` |
| `inform` | Public notify | **ALERT** — `ALERT.*` |
| `after_action` | Close-out | **RMS** — `RMS.*`; BWC evidence |

**Comms spine:** LMR + MCX under INFRA; bridge via `MCX.LMR_IWF` / `PSERS.XCUT.IOP.LMR_MCX_IWF`.

### Vertical maturity

| Vertical | Bid-desk status |
|----------|-----------------|
| **LMR** | Published — primary (**192**/192; Phase 10 cleared drafts) |
| **CAD / NG911** | Published |
| **Sensors** | Published |
| **FIELD / RMS / EOC** | Published — incident process |
| **MCX** | Published Lite — deep 3GPP deferred |
| **GIS / ALERT** | Published (thin waves) |

Live counts: UI maturity table or `GET /api/ontology/summary`.

### C2 / C3 / C4I talking points

Map defence jargon to existing aliases—do **not** invent a military peer tree. See [c2-c4i-crosswalk.md](c2-c4i-crosswalk.md).

| Term | Map to |
|------|--------|
| C2 | `CAD.COMMAND_VIEW`, `EOC.SIT_AWARENESS` |
| C3 | + `LMR.*`, `CAD.RADIO_INTEGRATION`, `MCX.MCPTT` |
| C4I / COP | `EOC.COMMON_OP_PICTURE`, CAD/RMS/VMS, sensor fusion |

### Explicitly out of scope (need SPEC amendment)

Military peer L1 · multi-vendor L3 · proposal/pricing gen · broad RFP crawl · deep MCX beyond Lite · EIDO/IDX runtime · graph DB explorer.

### Where truth lives

| What | Path |
|------|------|
| L1 catalog | `ontology/l1_capabilities.json` |
| Publish | `ontology/publish_l1.py` + `top_*.json` |
| Expanders | `ontology/expand_*.py` |
| Authority | `SPEC.md`, `docs/psers-root.md` |
| L2 / L3 | `l2_synonyms.json`, `l3_*.json` |
| Quality | `eval_match.py`, `gap_report.py`, `validate_l*.py` |

Never run `generate_l1.py` casually—it resets publish state.

---

## 4. Stakeholder meeting scripts

Lead with process, not the graph.

### A) Exec / sales — 5 minutes (journey only)

**Goal:** Align on how PSERS frames deals—incident lifecycle first, products second.

**Agenda**
- Mission swimlane: detect → call take → dispatch → field → evidence → records → command view  
- Example systems per stage (not SKUs)  
- C2/C3/C4I = same capabilities, not a military vertical  
- Close with the one sentence at the top of this playbook  

**Killer sentence:** *“Every RFP requirement sits on the same incident journey—sense it, take the call, dispatch, respond, prove it, close the record, and command the picture.”*

| Do | Don't |
|----|-------|
| Stay on the swimlane | Open with JSON or a 300-node graph |
| One concrete stage (field evidence) | Demo CSV/export in a 5-min exec slot |
| Tie to buyer outcomes | Debate EIDO/IDX or multi-vendor |

### B) Bid desk / solution architect — 15 minutes (live match + CSV)

**Goal:** Prove L2→L1→L3 and leave with an exportable coverage artifact.

**Agenda**
- (2 min) One sentence + swimlane  
- (8 min) Paste → load incident or fullstack → Run match → walk one row  
- (3 min) C2 callout phrase  
- (2 min) Download coverage CSV  

**Killer sentence:** *“Paste buyer language, get stable capability IDs and MSI coverage in one pass—then hand sales a CSV they can defend in the bid room.”*

| Do | Don't |
|----|-------|
| Worked example → `FIELD.EVIDENCE_CAPTURE` → CommandCentral | Dump full L1 JSON |
| Be honest about gaps / Gaps first | Promise draft caps or multi-vendor |
| CSV as the takeaway | Turn into governance debate |

### C) Technical / ontology — 10 minutes (stacks, publish, governance)

**Goal:** Where truth lives; what `published` means; change control.

**Agenda**
- ID scheme + stacks (INFRA/SENS/PLAT/APP/SVC/XCUT)  
- Status: published vs draft vs stub; live `GET /api/ontology/summary`  
- Authority: L1 JSON, SPEC, expand/publish scripts, eval gates  
- Boundaries: military peer L1 / deep MCX / multi-vendor deferred  

**Killer sentence:** *“Published L1 is the contract with bid desk—everything else is expansion backlog until it passes eval and lands in a publish batch.”*

| Do | Don't |
|----|-------|
| Point to artifact paths + eval | Re-demo paste unless asked |
| MCX/GIS as stub→published examples | Ad-hoc L3 outside SPEC |
| `fullstack_demo` as regression anchor | Treat draft as bid-desk safe |

---

## 5. Quick reference

| Need | Where |
|------|--------|
| Start UI | `py -3.12 -m uvicorn app.match_api:app --host 127.0.0.1 --port 8000` → http://127.0.0.1:8000/ |
| Eval suites | `py -3.12 ontology/eval_match.py --soft` |
| Gap report | `py -3.12 ontology/gap_report.py ontology/samples/demo_fullstack.txt` |
| Coverage API | `POST /api/match/export?format=csv` |
| Ontology counts | `GET /api/ontology/summary` |

## 6. Do not promise (without SPEC amendment)

- Military / defence peer L1 trees  
- Multi-vendor L3 matrix  
- Proposal narrative / pricing BOM  
- Broad RFP web crawl  
- Full interactive ontology graph database  
