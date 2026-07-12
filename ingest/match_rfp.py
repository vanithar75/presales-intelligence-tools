"""CLI: match an RFP PDF (or text file) to L1 + MSI coverage."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ingest.matcher import match_pdf, match_text  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Match RFP requirements to PSERS L1 + MSI coverage")
    ap.add_argument("path", type=Path, help="PDF or .txt file")
    ap.add_argument("--max-pages", type=int, default=15, help="Max PDF pages (default 15 for cost/speed)")
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--out", type=Path, default=None, help="Write JSON output path")
    ap.add_argument("--summary-only", action="store_true")
    args = ap.parse_args()

    path: Path = args.path
    if not path.exists():
        print(f"missing file: {path}", file=sys.stderr)
        return 1

    if path.suffix.lower() == ".pdf":
        doc = match_pdf(path, max_pages=args.max_pages, top_k=args.top_k)
    else:
        text = path.read_text(encoding="utf-8", errors="ignore")
        rows = match_text(text, top_k=args.top_k)
        mapped = sum(1 for r in rows if not r["unmapped"])
        doc = {
            "source_file": path.name,
            "pages_processed": 1,
            "counts": {
                "requirements": len(rows),
                "mapped": mapped,
                "unmapped": len(rows) - mapped,
                "map_rate": round(mapped / len(rows), 3) if rows else 0.0,
            },
            "results": rows,
        }

    print(json.dumps(doc["counts"], indent=2))
    if not args.summary_only:
        # print a few mapped examples
        shown = 0
        for r in doc["results"]:
            if r["unmapped"]:
                continue
            m0 = r["matches"][0]
            print(f"p{r.get('page', '?')}: {m0['capability_alias']} ({m0['confidence']}) <- {r['requirement'][:100]}")
            shown += 1
            if shown >= 8:
                break

    out = args.out
    if out is None:
        out = ROOT / "ontology" / "samples" / f"match_{path.stem}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    # store compact sample: cap results length for repo size
    slim = {
        **doc,
        "results": doc["results"][:200],
        "note": "Truncated to first 200 requirement rows for sample artifact",
    }
    out.write_text(json.dumps(slim, indent=2), encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
