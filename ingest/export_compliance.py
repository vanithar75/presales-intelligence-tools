"""CLI: RFP PDF/text → compliance workbook (.xlsx) for Google Sheets import."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ingest.compliance_matrix import (  # noqa: E402
    build_compliance_rows,
    write_compliance_xlsx,
)
from ingest.matcher import match_pdf, match_text  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Export RFP match results as a compliance .xlsx workbook"
    )
    ap.add_argument("path", type=Path, help="PDF or .txt file")
    ap.add_argument(
        "-o",
        "--out",
        type=Path,
        default=None,
        help="Output .xlsx path (default: out/<stem>-compliance.xlsx)",
    )
    ap.add_argument("--max-pages", type=int, default=40)
    ap.add_argument(
        "--start-page",
        type=int,
        default=1,
        help="PDF 1-indexed start page (inclusive)",
    )
    ap.add_argument(
        "--end-page",
        type=int,
        default=None,
        help="PDF 1-indexed end page (inclusive); overrides --max-pages when set",
    )
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument(
        "--json-summary",
        action="store_true",
        help="Print summary JSON to stdout",
    )
    args = ap.parse_args()

    path: Path = args.path
    if not path.exists():
        print(f"missing file: {path}", file=sys.stderr)
        return 1

    if path.suffix.lower() == ".pdf":
        doc = match_pdf(
            path,
            max_pages=args.max_pages,
            top_k=args.top_k,
            start_page=args.start_page,
            end_page=args.end_page,
        )
        results = doc.get("results") or []
        source_file = doc.get("source_file") or path.name
        page_range = doc.get("page_range") or {}
    else:
        text = path.read_text(encoding="utf-8", errors="ignore")
        results = match_text(text, top_k=args.top_k)
        source_file = path.name
        page_range = {}

    out = args.out or (ROOT / "out" / f"{path.stem}-compliance.xlsx")
    rows = build_compliance_rows(results, source_file=source_file)
    summary = write_compliance_xlsx(out, rows, source_file=source_file)
    if page_range:
        summary["page_range"] = page_range
        summary["pages_processed"] = doc.get("pages_processed")

    if args.json_summary:
        print(json.dumps(summary, indent=2))
    else:
        range_note = ""
        if page_range:
            range_note = f" pages {page_range.get('start')}-{page_range.get('end')},"
        print(
            f"wrote {out} —{range_note} {summary['requirements']} rows, "
            f"map_rate={summary['map_rate']}, "
            f"suggested_c={summary['suggested_c']}, "
            f"blank_for_review={summary['blank_for_review']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
