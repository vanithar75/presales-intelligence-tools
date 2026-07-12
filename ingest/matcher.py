"""Deterministic RFP phrase → L1 capability matcher (Sprint 3)."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Reuse seed patterns from L2 extractor
from ingest.extract_l2_synonyms import (  # noqa: E402
    SEED_PHRASES,
    harvest_phrases,
    normalize_phrase,
)


@dataclass
class MatchHit:
    capability_id: str
    capability_alias: str | None
    capability_name: str
    confidence: float
    method: str


@lru_cache(maxsize=1)
def _load_ontology():
    l1 = json.loads((ROOT / "ontology" / "l1_capabilities.json").read_text(encoding="utf-8"))
    l2 = json.loads((ROOT / "ontology" / "l2_synonyms.json").read_text(encoding="utf-8"))
    l3p = json.loads((ROOT / "ontology" / "l3_msi_products.json").read_text(encoding="utf-8"))
    l3m = json.loads((ROOT / "ontology" / "l3_product_capabilities.json").read_text(encoding="utf-8"))

    by_id = {c["id"]: c for c in l1["capabilities"]}
    alias_to_id = {}
    for c in l1["capabilities"]:
        if c.get("alias"):
            alias_to_id[c["alias"]] = c["id"]
        alias_to_id[c["id"]] = c["id"]

    # synonym lookup: normalized token fingerprint → capability ids
    syn_index: list[tuple[set[str], str, float]] = []
    for s in l2["synonyms"]:
        tokens = _tokens(s["phrase"])
        if len(tokens) >= 3:
            syn_index.append((tokens, s["capability_id"], float(s.get("confidence", 0.8))))

    products = {p["id"]: p for p in l3p["products"]}
    cover: dict[str, list[dict]] = {}
    for m in l3m["mappings"]:
        cover.setdefault(m["capability_id"], []).append(m)

    return by_id, alias_to_id, syn_index, products, cover


def _tokens(text: str) -> set[str]:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    stop = {
        "the", "a", "an", "and", "or", "of", "to", "for", "in", "on", "by", "with",
        "shall", "must", "will", "be", "is", "are", "provide", "support", "include",
        "system", "contractor", "vendor", "selected", "proposer",
    }
    return {t for t in text.split() if len(t) > 2 and t not in stop}


def match_phrase(phrase: str, top_k: int = 3) -> list[MatchHit]:
    by_id, alias_to_id, syn_index, _, _ = _load_ontology()
    hits: dict[str, MatchHit] = {}

    def add(cid: str, conf: float, method: str) -> None:
        c = by_id.get(cid)
        if not c:
            return
        prev = hits.get(cid)
        if prev and prev.confidence >= conf:
            return
        hits[cid] = MatchHit(
            capability_id=cid,
            capability_alias=c.get("alias"),
            capability_name=c["name"],
            confidence=round(conf, 3),
            method=method,
        )

    for pat, alias in SEED_PHRASES:
        if re.search(pat, phrase, flags=re.I):
            cid = alias_to_id.get(alias)
            if cid:
                add(cid, 0.92, "seed")

    # L2 synonym Jaccard
    q = _tokens(phrase)
    if q:
        for tokens, cid, base in syn_index:
            inter = len(q & tokens)
            if inter < 3:
                continue
            union = len(q | tokens)
            j = inter / union if union else 0.0
            if j >= 0.35:
                add(cid, min(0.9, 0.55 + j * 0.4) * (0.9 + 0.1 * base), "l2_overlap")

    # capability name contains
    low = phrase.lower()
    for cid, c in by_id.items():
        if c.get("status") == "stub":
            continue
        name = c["name"].lower()
        if len(name) >= 8 and name in low:
            add(cid, 0.72, "name")

    ranked = sorted(hits.values(), key=lambda h: (-h.confidence, h.capability_id))
    return ranked[:top_k]


def msi_coverage(capability_ids: list[str]) -> list[dict]:
    _, _, _, products, cover = _load_ontology()
    rows = []
    for cid in capability_ids:
        for m in cover.get(cid, []):
            p = products.get(m["product_id"], {})
            rows.append(
                {
                    "capability_id": cid,
                    "product_id": m["product_id"],
                    "product_name": p.get("sku_or_name"),
                    "family": p.get("family"),
                    "support_level": m["support_level"],
                    "notes": m.get("notes") or "",
                }
            )
    return rows


def match_text(text: str, top_k: int = 3) -> list[dict]:
    results = []
    phrases = harvest_phrases(text)
    # also accept raw lines if harvest empty
    if not phrases:
        for line in text.splitlines():
            line = normalize_phrase(line)
            if len(line) >= 25:
                phrases.append(line)
    seen = set()
    for phrase in phrases:
        key = phrase.lower()
        if key in seen:
            continue
        seen.add(key)
        hits = match_phrase(phrase, top_k=top_k)
        if not hits:
            results.append(
                {
                    "requirement": phrase,
                    "matches": [],
                    "unmapped": True,
                }
            )
            continue
        cap_ids = [h.capability_id for h in hits]
        results.append(
            {
                "requirement": phrase,
                "unmapped": False,
                "matches": [
                    {
                        "capability_id": h.capability_id,
                        "capability_alias": h.capability_alias,
                        "capability_name": h.capability_name,
                        "confidence": h.confidence,
                        "method": h.method,
                    }
                    for h in hits
                ],
                "msi_coverage": msi_coverage(cap_ids),
            }
        )
    return results


def match_pdf(pdf_path: Path, max_pages: int | None = None, top_k: int = 3) -> dict:
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    pages = reader.pages[: max_pages or len(reader.pages)]
    all_rows = []
    for i, page in enumerate(pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        for row in match_text(text, top_k=top_k):
            row = {**row, "page": i}
            all_rows.append(row)

    mapped = [r for r in all_rows if not r["unmapped"]]
    unmapped = [r for r in all_rows if r["unmapped"]]
    return {
        "source_file": pdf_path.name,
        "pages_processed": len(pages),
        "counts": {
            "requirements": len(all_rows),
            "mapped": len(mapped),
            "unmapped": len(unmapped),
            "map_rate": round(len(mapped) / len(all_rows), 3) if all_rows else 0.0,
        },
        "results": all_rows,
    }
