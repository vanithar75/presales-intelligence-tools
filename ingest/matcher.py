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
    is_boilerplate_phrase,
    normalize_key,
    normalize_phrase,
    strip_page_chrome,
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
                conf = 0.92
                # Prefer vertical seeds when the phrase is clearly scoped
                if alias.startswith("CAD.") and re.search(r"\bcad\b", phrase, flags=re.I):
                    conf = 0.95
                if alias.startswith("NG911."):
                    conf = 0.96
                if alias.startswith(("VIDEO.", "IOT.", "UAS.")):
                    # Prefer more specific sensor aliases over broad ones on confidence ties
                    conf = 0.96
                    if alias in (
                        "VIDEO.PSAP_LIVESTREAM",
                        "VIDEO.LIVE_SHARE",
                        "IOT.ALPR_HOTLIST",
                        "IOT.GUNSHOT_CAD",
                        "IOT.SENSOR_ALERT_ROUTE",
                        "IOT.SENSOR_FUSION",
                        "UAS.DRONE_DOWNLINK",
                        "UAS.DRONE_GEO_FENCE",
                    ):
                        conf = 0.97
                add(cid, conf, "seed")

    # L2 synonym Jaccard (slightly looser inter for Phase-2 mid-doc recall)
    q = _tokens(phrase)
    if q:
        for tokens, cid, base in syn_index:
            inter = len(q & tokens)
            if inter < 2:
                continue
            union = len(q | tokens)
            j = inter / union if union else 0.0
            if j >= 0.28:
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
    text = strip_page_chrome(text)
    phrases = harvest_phrases(text)
    # also accept raw lines if harvest empty
    if not phrases:
        for line in text.splitlines():
            line = normalize_phrase(line)
            if len(line) >= 25 and not is_boilerplate_phrase(line):
                phrases.append(line)
    seen_exact: set[str] = set()
    seen_key: set[str] = set()
    for phrase in phrases:
        exact = phrase.lower()
        key = normalize_key(phrase)
        if exact in seen_exact:
            continue
        if key and key in seen_key:
            continue
        seen_exact.add(exact)
        if key:
            seen_key.add(key)
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


def match_pdf(
    pdf_path: Path,
    max_pages: int | None = None,
    top_k: int = 3,
    *,
    start_page: int = 1,
    end_page: int | None = None,
) -> dict:
    """Match PDF pages. Pages are 1-indexed inclusive when start/end set."""
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    total = len(reader.pages)
    start = max(1, start_page)
    if end_page is not None:
        end = min(end_page, total)
    elif max_pages is not None:
        end = min(start + max_pages - 1, total)
    else:
        end = total

    all_rows = []
    for i in range(start, end + 1):
        try:
            text = reader.pages[i - 1].extract_text() or ""
        except Exception:
            text = ""
        for row in match_text(text, top_k=top_k):
            row = {**row, "page": i}
            all_rows.append(row)

    mapped = [r for r in all_rows if not r["unmapped"]]
    unmapped = [r for r in all_rows if r["unmapped"]]
    return {
        "source_file": pdf_path.name,
        "pages_processed": max(0, end - start + 1),
        "page_range": {"start": start, "end": end},
        "counts": {
            "requirements": len(all_rows),
            "mapped": len(mapped),
            "unmapped": len(unmapped),
            "map_rate": round(len(mapped) / len(all_rows), 3) if all_rows else 0.0,
        },
        "results": all_rows,
    }
