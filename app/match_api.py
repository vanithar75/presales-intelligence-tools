"""
PSERS Presales Match API + Analyst UI (Sprint 4).

Run:
  py -3.12 -m uvicorn app.match_api:app --host 127.0.0.1 --port 8000
  Open http://127.0.0.1:8000/
"""
from __future__ import annotations

import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
STATIC = Path(__file__).resolve().parent / "static"
FEEDBACK = ROOT / "ontology" / "l2_feedback.jsonl"
REVIEW_QUEUE = ROOT / "ontology" / "l2_review_queue.json"
SAMPLES = ROOT / "ontology" / "samples"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ingest.extract_l2_synonyms import normalize_key  # noqa: E402
from ingest.matcher import match_pdf, match_text, _load_ontology  # noqa: E402
from ingest.publish_l2_feedback import load_review_queue, publish_review_queue  # noqa: E402

app = FastAPI(title="PSERS Presales Intelligence", version="0.5.0")


class TextMatchRequest(BaseModel):
    text: str = Field(..., min_length=10)
    top_k: int = 3


class SynonymFeedback(BaseModel):
    phrase: str = Field(..., min_length=3)
    capability_id: str = Field(..., min_length=3)
    note: str = ""
    action: str = Field(default="accept", pattern="^(accept|correct|reject)$")


def _upsert_review_queue(record: dict) -> dict:
    """Upsert accept/correct into review queue; reject stored but never publishable."""
    REVIEW_QUEUE.parent.mkdir(parents=True, exist_ok=True)
    if REVIEW_QUEUE.exists():
        doc = json.loads(REVIEW_QUEUE.read_text(encoding="utf-8"))
    else:
        doc = {"schema_version": "1.0", "items": []}
    items: list[dict] = list(doc.get("items") or [])
    phrase = record["phrase"]
    cid = record["capability_id"]
    action = record["action"]
    key = (normalize_key(phrase), cid, action)

    queue_item = {
        "phrase": phrase,
        "capability_id": cid,
        "capability_alias": record.get("capability_alias"),
        "action": action,
        "ts": record["ts"],
        "note": record.get("note") or "",
        "source": "analyst_ui",
        "status": "pending" if action in ("accept", "correct") else "rejected",
    }

    replaced = False
    for i, existing in enumerate(items):
        ek = (
            normalize_key(existing.get("phrase", "")),
            existing.get("capability_id"),
            existing.get("action"),
        )
        if ek == key:
            # Keep published status if already merged; otherwise refresh
            if existing.get("status") == "published" and action in ("accept", "correct"):
                queue_item["status"] = "published"
                queue_item["published_at"] = existing.get("published_at")
                queue_item["publish_note"] = existing.get("publish_note", "already_published")
            items[i] = queue_item
            replaced = True
            break
    if not replaced:
        items.append(queue_item)

    doc["schema_version"] = doc.get("schema_version") or "1.0"
    doc["items"] = items
    doc["updated_at"] = record["ts"]
    REVIEW_QUEUE.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return queue_item


@app.get("/health")
def health():
    return {"status": "ok", "sprint": "P8-072", "ui": True}


@app.get("/api/ontology/summary")
def ontology_summary():
    """Lightweight L1 status counts for the stakeholder explainer UI."""
    l1_path = ROOT / "ontology" / "l1_capabilities.json"
    if not l1_path.exists():
        raise HTTPException(status_code=404, detail="l1_capabilities.json missing")
    doc = json.loads(l1_path.read_text(encoding="utf-8"))
    caps = list(doc.get("capabilities") or [])
    status_counts = {"published": 0, "draft": 0, "stub": 0, "deprecated": 0, "other": 0}
    by_vertical: dict[str, dict[str, int]] = {}
    by_stack: dict[str, int] = {}

    def vertical_of(c: dict) -> str:
        if c.get("vertical"):
            return str(c["vertical"])
        alias = c.get("alias") or ""
        if alias.startswith("CAD.") or alias == "CAD.MOBILE_CLIENT":
            return "CAD"
        if alias.startswith("FIELD.") or c["id"].startswith("PSERS.APP.FIELD."):
            return "FIELD"
        if alias.startswith("LMR."):
            return "LMR"
        return str(c.get("domain") or "OTHER")

    for c in caps:
        st = c.get("status") or "other"
        if st in status_counts:
            status_counts[st] += 1
        else:
            status_counts["other"] += 1
        stack = str(c.get("stack_class") or "OTHER")
        by_stack[stack] = by_stack.get(stack, 0) + 1
        vert = vertical_of(c)
        bucket = by_vertical.setdefault(
            vert, {"published": 0, "draft": 0, "stub": 0, "deprecated": 0, "total": 0}
        )
        bucket["total"] += 1
        if st in ("published", "draft", "stub", "deprecated"):
            bucket[st] += 1

    return {
        "schema_version": doc.get("schema_version"),
        "sprint": doc.get("sprint"),
        "total": len(caps),
        "status": status_counts,
        "by_vertical": dict(sorted(by_vertical.items())),
        "by_stack": dict(sorted(by_stack.items())),
        "guide": "docs/ontology-stakeholder-guide.md",
    }


@app.get("/api/review-queue")
def get_review_queue():
    doc = load_review_queue(REVIEW_QUEUE)
    items = list(doc.get("items") or [])
    counts = {"pending": 0, "published": 0, "rejected": 0, "other": 0}
    for it in items:
        st = it.get("status") or "pending"
        if st in counts:
            counts[st] += 1
        else:
            counts["other"] += 1
    return {
        "schema_version": doc.get("schema_version", "1.0"),
        "updated_at": doc.get("updated_at"),
        "counts": counts,
        "items": items,
        "queue_path": "ontology/l2_review_queue.json",
    }


@app.post("/api/review-queue/publish")
def publish_review_queue_endpoint(dry_run: bool = False):
    try:
        summary = publish_review_queue(dry_run=dry_run, queue_path=REVIEW_QUEUE)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return {"ok": True, "summary": summary}


@app.get("/api/capabilities")
def list_capabilities(q: str = "", limit: int = 50):
    by_id, _, _, _, _ = _load_ontology()
    rows = []
    ql = q.lower().strip()
    for c in by_id.values():
        if c.get("status") == "stub" and not ql:
            continue
        blob = f"{c['id']} {c.get('alias') or ''} {c['name']}".lower()
        if ql and ql not in blob:
            continue
        rows.append(
            {
                "id": c["id"],
                "alias": c.get("alias"),
                "name": c["name"],
                "domain": c.get("domain"),
                "stack_class": c.get("stack_class"),
            }
        )
        if len(rows) >= limit:
            break
    return {"capabilities": rows}


@app.post("/api/match/text")
def match_text_endpoint(body: TextMatchRequest):
    rows = match_text(body.text, top_k=body.top_k)
    mapped = sum(1 for r in rows if not r["unmapped"])
    return {
        "counts": {
            "requirements": len(rows),
            "mapped": mapped,
            "unmapped": len(rows) - mapped,
            "map_rate": round(mapped / len(rows), 3) if rows else 0.0,
        },
        "results": rows,
    }


def _coverage_rows(results: list[dict]) -> list[dict]:
    """Flatten match results into bid-desk coverage rows."""
    out = []
    for r in results:
        m = (r.get("matches") or [None])[0]
        msi = r.get("msi_coverage") or (m.get("msi_coverage") if m else None) or []
        if isinstance(msi, list) and msi:
            msi_str = "; ".join(
                f"{x.get('family') or x.get('product_id') or ''}:"
                f"{x.get('support_level') or ''}"
                for x in msi
            )
        else:
            msi_str = ""
        out.append(
            {
                "requirement": r.get("requirement") or "",
                "page": r.get("page"),
                "mapped": not r.get("unmapped"),
                "capability_id": (m or {}).get("capability_id") or "",
                "capability_alias": (m or {}).get("capability_alias") or "",
                "capability_name": (m or {}).get("capability_name") or "",
                "confidence": (m or {}).get("confidence"),
                "method": (m or {}).get("method") or "",
                "msi_coverage": msi_str,
            }
        )
    return out


def _coverage_csv(rows: list[dict]) -> str:
    import csv
    import io

    buf = io.StringIO()
    fields = [
        "requirement",
        "page",
        "mapped",
        "capability_id",
        "capability_alias",
        "capability_name",
        "confidence",
        "method",
        "msi_coverage",
    ]
    w = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore")
    w.writeheader()
    for row in rows:
        w.writerow(row)
    return buf.getvalue()


@app.post("/api/match/export")
def match_export(body: TextMatchRequest, format: str = "json"):
    """Bid-desk coverage report: requirement → L1 → MSI (json or csv)."""
    rows = match_text(body.text, top_k=body.top_k)
    mapped = sum(1 for r in rows if not r["unmapped"])
    coverage = _coverage_rows(rows)
    summary = {
        "requirements": len(rows),
        "mapped": mapped,
        "unmapped": len(rows) - mapped,
        "map_rate": round(mapped / len(rows), 3) if rows else 0.0,
    }
    fmt = (format or "json").lower().strip()
    if fmt == "csv":
        return Response(
            content=_coverage_csv(coverage),
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="psers-coverage.csv"'
            },
        )
    return {"counts": summary, "rows": coverage}


@app.post("/api/match/pdf")
async def match_pdf_endpoint(
    file: UploadFile = File(...),
    max_pages: int = 20,
    top_k: int = 3,
):
    suffix = Path(file.filename or "upload.pdf").suffix or ".pdf"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)
    try:
        return match_pdf(tmp_path, max_pages=max_pages, top_k=top_k)
    finally:
        tmp_path.unlink(missing_ok=True)


@app.post("/api/feedback/synonym")
def synonym_feedback(body: SynonymFeedback):
    by_id, _, _, _, _ = _load_ontology()
    if body.capability_id not in by_id:
        raise HTTPException(status_code=400, detail="Unknown capability_id")
    FEEDBACK.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "phrase": body.phrase.strip(),
        "capability_id": body.capability_id,
        "capability_alias": by_id[body.capability_id].get("alias"),
        "action": body.action,
        "note": body.note,
        "status": "analyst_feedback",
    }
    with FEEDBACK.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    queued = None
    # Accept/correct → review queue; reject also recorded in queue (never published)
    queued = _upsert_review_queue(record)

    return {
        "ok": True,
        "saved": record,
        "queued": queued,
        "queue_path": "ontology/l2_review_queue.json",
    }


@app.get("/api/demo/fixture")
def demo_fixture(name: str = "demo"):
    """Load a sample requirements fixture for the Paste tab.

    name: demo | incident | cad | ng911 | sensors | psap
    """
    mapping = {
        "demo": "demo_requirements.txt",
        "incident": "demo_incident_mgmt.txt",
        "cad": "demo_cad_requirements.txt",
        "ng911": "demo_ng911_requirements.txt",
        "sensors": "demo_sensors_requirements.txt",
    "mcx": "demo_mcx_requirements.txt",
        "psap": "demo_psap_loop.txt",
    }
    filename = mapping.get(name.strip().lower(), "demo_requirements.txt")
    path = SAMPLES / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"fixture missing: {filename}")
    return {"filename": path.name, "text": path.read_text(encoding="utf-8")}


@app.post("/match/text")
def match_text_legacy(body: TextMatchRequest):
    return match_text_endpoint(body)


@app.post("/match/pdf")
async def match_pdf_legacy(
    file: UploadFile = File(...),
    max_pages: int = 20,
    top_k: int = 3,
):
    return await match_pdf_endpoint(file=file, max_pages=max_pages, top_k=top_k)


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")
