"""
Minimal Match API (Sprint 3).

Run:
  py -3.12 -m pip install fastapi uvicorn
  py -3.12 -m uvicorn app.match_api:app --host 127.0.0.1 --port 8000

Endpoints:
  GET  /health
  POST /match/text   JSON { "text": "..." }
  POST /match/pdf    multipart file upload
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ingest.matcher import match_pdf, match_text  # noqa: E402

app = FastAPI(title="PSERS Match API", version="0.3.0")


class TextMatchRequest(BaseModel):
    text: str = Field(..., min_length=10)
    top_k: int = 3


@app.get("/health")
def health():
    return {"status": "ok", "sprint": "S3"}


@app.post("/match/text")
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


@app.post("/match/pdf")
async def match_pdf_endpoint(file: UploadFile = File(...), max_pages: int = 15, top_k: int = 3):
    suffix = Path(file.filename or "upload.pdf").suffix or ".pdf"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)
    try:
        return match_pdf(tmp_path, max_pages=max_pages, top_k=top_k)
    finally:
        tmp_path.unlink(missing_ok=True)
