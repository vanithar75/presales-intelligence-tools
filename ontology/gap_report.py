"""Bid-desk gap report: match text/PDF and summarize mapped vs unmapped by vertical.

Usage:
  py -3.12 ontology/gap_report.py ontology/samples/demo_incident_mgmt.txt
  py -3.12 ontology/gap_report.py --pdf data/rfp/erie-trunked-radio-system-2026-018.pdf --start 21 --end 40
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ingest.matcher import match_pdf, match_text, _load_ontology  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="PSERS coverage gap report")
    ap.add_argument("path", nargs="?", help="Text fixture path")
    ap.add_argument("--pdf", type=Path)
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=40)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.pdf:
        doc = match_pdf(args.pdf, start_page=args.start, end_page=args.end, top_k=1)
        rows = doc["results"]
        counts = doc["counts"]
        source = str(args.pdf)
    elif args.path:
        text = Path(args.path).read_text(encoding="utf-8")
        rows = match_text(text, top_k=1)
        mapped = sum(1 for r in rows if not r["unmapped"])
        counts = {
            "requirements": len(rows),
            "mapped": mapped,
            "unmapped": len(rows) - mapped,
            "map_rate": round(mapped / len(rows), 3) if rows else 0.0,
        }
        source = args.path
    else:
        ap.print_help()
        return 2

    by_id, _, _, _, _ = _load_ontology()
    vert = Counter()
    unmapped_samples = []
    for r in rows:
        if r.get("unmapped"):
            unmapped_samples.append(r.get("requirement", "")[:160])
            continue
        m = (r.get("matches") or [{}])[0]
        cid = m.get("capability_id")
        c = by_id.get(cid) or {}
        vert[c.get("vertical") or c.get("domain") or "OTHER"] += 1

    report = {
        "source": source,
        "counts": counts,
        "mapped_by_vertical": dict(vert.most_common()),
        "unmapped_samples": unmapped_samples[:20],
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"source={source}")
        print(
            f"map_rate={counts.get('map_rate')} "
            f"mapped={counts.get('mapped')}/{counts.get('requirements')}"
        )
        print("mapped_by_vertical:", report["mapped_by_vertical"])
        print("unmapped_samples:")
        for s in report["unmapped_samples"]:
            print(" -", s.replace("\n", " "))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
