"""End-to-end: one allowlisted RFP PDF (5 pages) → compliance .xlsx + preview.

Default: Erie trunked RFP pages 21–25 (requirement-dense mid-doc window).
Requires PDF present (run ingest/download_rfps.py first).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ingest.compliance_matrix import (  # noqa: E402
    COMPLIANCE_FIELDS,
    build_compliance_rows,
    write_compliance_xlsx,
)
from ingest.matcher import match_pdf  # noqa: E402

DEFAULT_PDF = ROOT / "data" / "rfp" / "erie-trunked-radio-system-2026-018.pdf"
DEFAULT_START = 21
DEFAULT_END = 25


def write_preview_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COMPLIANCE_FIELDS, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow(row)


def write_preview_md(path: Path, summary: dict, rows: list[dict], limit: int = 12) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# E2E compliance matrix preview",
        "",
        f"- **Source:** `{summary.get('source_file')}`",
        f"- **Pages:** {summary.get('page_range', {}).get('start')}-{summary.get('page_range', {}).get('end')}",
        f"- **Requirements:** {summary.get('requirements')}",
        f"- **Mapped:** {summary.get('mapped')} (map_rate={summary.get('map_rate')})",
        f"- **Suggested C:** {summary.get('suggested_c')} · **A:** {summary.get('suggested_a')} · **blank:** {summary.get('blank_for_review')}",
        "",
        "## Sample rows (first {})".format(min(limit, len(rows))),
        "",
        "| req_id | page | code | L1 alias | requirement (truncated) |",
        "|--------|------|------|----------|------------------------|",
    ]
    for r in rows[:limit]:
        req = (r.get("requirement") or "").replace("|", "/").replace("\n", " ")
        if len(req) > 90:
            req = req[:87] + "..."
        lines.append(
            f"| `{r.get('req_id') or '—'}` | {r.get('page')} | "
            f"{r.get('compliance_code') or '—'} | "
            f"`{r.get('capability_alias') or '—'}` | {req} |"
        )
    gaps = [r for r in rows if not r.get("mapped") or not r.get("compliance_code")]
    lines.extend(["", f"## Gaps / blank codes ({len(gaps)} total)", ""])
    for r in gaps[:8]:
        req = (r.get("requirement") or "").replace("|", "/")[:100]
        lines.append(f"- p{r.get('page')}: {req}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="E2E PDF → compliance workbook (5-page slice)")
    ap.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    ap.add_argument("--start-page", type=int, default=DEFAULT_START)
    ap.add_argument("--end-page", type=int, default=DEFAULT_END)
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "samples" / "compliance",
    )
    args = ap.parse_args()

    pdf: Path = args.pdf
    if not pdf.exists():
        print(
            f"RFP PDF missing: {pdf}\nRun: python3 ingest/download_rfps.py",
            file=sys.stderr,
        )
        return 2

    doc = match_pdf(
        pdf,
        start_page=args.start_page,
        end_page=args.end_page,
        top_k=3,
    )
    results = doc.get("results") or []
    source_file = doc.get("source_file") or pdf.name
    rows = build_compliance_rows(results, source_file=source_file)

    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{pdf.stem}_pp{args.start_page}-{args.end_page}"
    xlsx = out_dir / f"{stem}-compliance.xlsx"
    csv_path = out_dir / f"{stem}-preview.csv"
    md_path = out_dir / f"{stem}-preview.md"
    summary_path = out_dir / f"{stem}-summary.json"

    summary = write_compliance_xlsx(xlsx, rows, source_file=source_file)
    summary["page_range"] = doc.get("page_range")
    summary["pages_processed"] = doc.get("pages_processed")
    summary["xlsx"] = str(xlsx.relative_to(ROOT))

    write_preview_csv(csv_path, rows)
    write_preview_md(md_path, summary, rows)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    print(f"\nwrote {xlsx}")
    print(f"wrote {csv_path}")
    print(f"wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
