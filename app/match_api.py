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
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
STATIC = Path(__file__).resolve().parent / "static"
FEEDBACK = ROOT / "ontology" / "l2_feedback.jsonl"
SAMPLES = ROOT / "ontology" / "samples"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ingest.matcher import match_pdf, match_text, _load_ontology  # noqa: E402

app = FastAPI(title="PSERS Presales Intelligence", version="0.4.0")


class TextMatchRequest(BaseModel):
    text: str = Field(..., min_length=10)
    top_k: int = 3


class SynonymFeedback(BaseModel):
    phrase: str = Field(..., min_length=3)
    capability_id: str = Field(..., min_length=3)
    note: str = ""
    action: str = Field(default="accept", pattern="^(accept|correct|reject)$")


@app.get("/health")
def health():
    return {"status": "ok", "sprint": "S4", "ui": True}


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
    return {"ok": True, "saved": record}


@app.get("/api/demo/fixture")
def demo_fixture():
    path = SAMPLES / "demo_requirements.txt"
    if not path.exists():
        raise HTTPException(status_code=404, detail="demo fixture missing")
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
