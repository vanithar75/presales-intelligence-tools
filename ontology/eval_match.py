"""Match quality eval (LMR + CAD + NG911 + Sensors + PSAP loop + incident mgmt).

Suites:
  - demo / mid_doc / cad_demo / ng911_demo / sensors_demo / psap_loop / incident_mgmt / holdout

Usage:
  py -3.12 ontology/eval_match.py
  py -3.12 ontology/eval_match.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ingest.matcher import match_pdf, match_phrase, match_text  # noqa: E402

DEMO_PATH = ROOT / "ontology" / "samples" / "demo_requirements.txt"
CAD_DEMO_PATH = ROOT / "ontology" / "samples" / "demo_cad_requirements.txt"
NG911_DEMO_PATH = ROOT / "ontology" / "samples" / "demo_ng911_requirements.txt"
SENSORS_DEMO_PATH = ROOT / "ontology" / "samples" / "demo_sensors_requirements.txt"
PSAP_LOOP_PATH = ROOT / "ontology" / "samples" / "demo_psap_loop.txt"
INCIDENT_MGMT_PATH = ROOT / "ontology" / "samples" / "demo_incident_mgmt.txt"
MCX_DEMO_PATH = ROOT / "ontology" / "samples" / "demo_mcx_requirements.txt"
HOLDOUT_PATH = ROOT / "ontology" / "l2_synonyms_holdout.json"
ERIE_PDF = ROOT / "data" / "rfp" / "erie-trunked-radio-system-2026-018.pdf"
ECSO_PDF = ROOT / "data" / "rfp" / "ecso-jackson-p25-functional-spec.pdf"

DEMO_TARGET = 0.80
MID_DOC_TARGET = 0.60
CAD_DEMO_TARGET = 0.80
NG911_DEMO_TARGET = 0.80
SENSORS_DEMO_TARGET = 0.80
PSAP_LOOP_TARGET = 0.80
INCIDENT_MGMT_TARGET = 0.80
MCX_DEMO_TARGET = 0.80


def _eval_line_fixture(path: Path, suite: str, target: float) -> dict:
    if not path.exists():
        return {
            "suite": suite,
            "error": f"missing {path.name}",
            "map_rate": 0.0,
            "target": target,
            "pass": False,
        }
    text = path.read_text(encoding="utf-8")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    mapped = 0
    rows = []
    for line in lines:
        hits = match_phrase(line, top_k=1)
        ok = bool(hits)
        if ok:
            mapped += 1
        rows.append(
            {
                "requirement": line,
                "mapped": ok,
                "top": (
                    {
                        "capability_id": hits[0].capability_id,
                        "alias": hits[0].capability_alias,
                        "confidence": hits[0].confidence,
                        "method": hits[0].method,
                    }
                    if hits
                    else None
                ),
            }
        )
    rate = mapped / len(lines) if lines else 0.0
    out: dict = {
        "suite": suite,
        "source": str(path.relative_to(ROOT)),
        "requirements": len(lines),
        "mapped": mapped,
        "map_rate": round(rate, 3),
        "target": target,
        "pass": rate >= target,
        "sample": rows[:3],
    }
    if suite == "demo":
        harvest_rows = match_text(text, top_k=1)
        harvest_mapped = sum(1 for r in harvest_rows if not r["unmapped"])
        out["harvest_requirements"] = len(harvest_rows)
        out["harvest_mapped"] = harvest_mapped
        out["harvest_map_rate"] = (
            round(harvest_mapped / len(harvest_rows), 3) if harvest_rows else 0.0
        )
    return out


def eval_demo() -> dict:
    return _eval_line_fixture(DEMO_PATH, "demo", DEMO_TARGET)


def eval_cad_demo() -> dict:
    return _eval_line_fixture(CAD_DEMO_PATH, "cad_demo", CAD_DEMO_TARGET)


def eval_ng911_demo() -> dict:
    return _eval_line_fixture(NG911_DEMO_PATH, "ng911_demo", NG911_DEMO_TARGET)


def eval_sensors_demo() -> dict:
    return _eval_line_fixture(SENSORS_DEMO_PATH, "sensors_demo", SENSORS_DEMO_TARGET)


def eval_psap_loop() -> dict:
    return _eval_line_fixture(PSAP_LOOP_PATH, "psap_loop", PSAP_LOOP_TARGET)


def eval_incident_mgmt() -> dict:
    return _eval_line_fixture(INCIDENT_MGMT_PATH, "incident_mgmt", INCIDENT_MGMT_TARGET)


def eval_mcx_demo() -> dict:
    return _eval_line_fixture(MCX_DEMO_PATH, "mcx_demo", MCX_DEMO_TARGET)


def eval_mid_doc() -> dict:
    if ERIE_PDF.exists():
        pdf = ERIE_PDF
        label = "erie-trunked pages 21-40"
    elif ECSO_PDF.exists():
        pdf = ECSO_PDF
        label = "ecso-jackson pages 21-40 (fallback)"
    else:
        return {
            "suite": "mid_doc",
            "error": "RFP PDF missing — download via ingest/download_rfps.py",
            "map_rate": 0.0,
            "target": MID_DOC_TARGET,
            "pass": False,
        }

    doc = match_pdf(pdf, start_page=21, end_page=40, top_k=3)
    counts = doc["counts"]
    with_msi = 0
    for r in doc["results"]:
        if not r["unmapped"] and r.get("msi_coverage"):
            with_msi += 1
    return {
        "suite": "mid_doc",
        "source": pdf.name,
        "label": label,
        "page_range": doc.get("page_range"),
        "requirements": counts["requirements"],
        "mapped": counts["mapped"],
        "unmapped": counts["unmapped"],
        "map_rate": counts["map_rate"],
        "target": MID_DOC_TARGET,
        "pass": counts["map_rate"] >= MID_DOC_TARGET,
        "mapped_with_msi_coverage": with_msi,
    }


def eval_holdout() -> dict:
    if not HOLDOUT_PATH.exists():
        return {"suite": "holdout", "error": "missing holdout file", "recall": 0.0}
    doc = json.loads(HOLDOUT_PATH.read_text(encoding="utf-8"))
    syns = doc.get("synonyms", [])
    hit = 0
    for s in syns:
        phrase = s["phrase"]
        expected = s["capability_id"]
        matches = match_phrase(phrase, top_k=3)
        ids = {m.capability_id for m in matches}
        if expected in ids:
            hit += 1
    total = len(syns)
    recall = hit / total if total else 0.0
    return {
        "suite": "holdout",
        "source": str(HOLDOUT_PATH.relative_to(ROOT)),
        "phrases": total,
        "correct_top3": hit,
        "recall": round(recall, 3),
        "note": "informational — do not tune solely on holdout",
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="PSERS match quality eval (LMR + CAD + NG911 + Sensors + PSAP + incident + MCX)"
    )
    ap.add_argument("--soft", action="store_true", help="Always exit 0; report only")
    ap.add_argument("--json", action="store_true", help="Print JSON summary only")
    args = ap.parse_args()

    report = {
        "demo": eval_demo(),
        "mid_doc": eval_mid_doc(),
        "cad_demo": eval_cad_demo(),
        "ng911_demo": eval_ng911_demo(),
        "sensors_demo": eval_sensors_demo(),
        "psap_loop": eval_psap_loop(),
        "incident_mgmt": eval_incident_mgmt(),
        "mcx_demo": eval_mcx_demo(),
        "holdout": eval_holdout(),
    }
    hard_pass = (
        bool(report["demo"].get("pass"))
        and bool(report["mid_doc"].get("pass"))
        and bool(report["cad_demo"].get("pass"))
        and bool(report["ng911_demo"].get("pass"))
        and bool(report["sensors_demo"].get("pass"))
        and bool(report["psap_loop"].get("pass"))
        and bool(report["incident_mgmt"].get("pass"))
        and bool(report["mcx_demo"].get("pass"))
    )
    report["overall_pass"] = hard_pass
    report["targets"] = {
        "demo": DEMO_TARGET,
        "mid_doc": MID_DOC_TARGET,
        "cad_demo": CAD_DEMO_TARGET,
        "ng911_demo": NG911_DEMO_TARGET,
        "sensors_demo": SENSORS_DEMO_TARGET,
        "psap_loop": PSAP_LOOP_TARGET,
        "incident_mgmt": INCIDENT_MGMT_TARGET,
        "mcx_demo": MCX_DEMO_TARGET,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(
            "=== Match quality eval (LMR + CAD + NG911 + Sensors + PSAP + incident + MCX) ==="
        )
        for key in (
            "demo",
            "mid_doc",
            "cad_demo",
            "ng911_demo",
            "sensors_demo",
            "psap_loop",
            "incident_mgmt",
            "mcx_demo",
            "holdout",
        ):
            s = report[key]
            if key == "holdout":
                print(
                    f"[{key}] recall={s.get('recall')} "
                    f"({s.get('correct_top3')}/{s.get('phrases')}) — informational"
                )
                continue
            status = "PASS" if s.get("pass") else "FAIL"
            print(
                f"[{key}] {status} map_rate={s.get('map_rate')} "
                f"target>={s.get('target')} "
                f"mapped={s.get('mapped')}/{s.get('requirements')} "
                f"({s.get('label') or s.get('source')})"
            )
        print(f"overall_pass={hard_pass}")

    if args.soft:
        return 0
    return 0 if hard_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
