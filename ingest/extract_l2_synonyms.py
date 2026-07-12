"""
Sprint 2 — extract shall-like requirement phrases from allowlisted RFP PDFs
and map them to L1 capability IDs via keyword / alias matching (no LLM).

Outputs:
  ontology/l2_synonyms.json
  ontology/l2_synonyms_holdout.json
  ontology/l2_unmapped.json
"""
from __future__ import annotations

import json
import re
import hashlib
from collections import defaultdict
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
RFP_DIR = ROOT / "data" / "rfp"
L1_PATH = ROOT / "ontology" / "l1_capabilities.json"
OUT_MAIN = ROOT / "ontology" / "l2_synonyms.json"
OUT_HOLD = ROOT / "ontology" / "l2_synonyms_holdout.json"
OUT_UNMAP = ROOT / "ontology" / "l2_unmapped.json"

DOCS = [
    {
        "id": "ecso-jackson-2019",
        "file": "ecso-jackson-p25-functional-spec.pdf",
        "title": "ECSO Jackson County P25 Functional Specification",
    },
    {
        "id": "erie-trunked-2026",
        "file": "erie-trunked-radio-system-2026-018.pdf",
        "title": "Erie County Trunked Radio System RFP 2026-018",
    },
    {
        "id": "erie-subscriber-2026",
        "file": "erie-radio-subscriber-2026-019.pdf",
        "title": "Erie County Radio Subscriber RFP 2026-019",
    },
]

# High-value phrase seeds → L1 alias or full id (cost-free curated map)
SEED_PHRASES: list[tuple[str, str]] = [
    (r"geo[- ]?redundant\s+core", "LMR.CORE.GEO_REDUNDANT_CORE"),
    (r"no single point of failure", "LMR.CORE.NO_SPOF"),
    (r"single point of failure", "LMR.CORE.NO_SPOF"),
    (r"fail\s*soft", "LMR.CORE.FAILSOFT"),
    (r"site trunking", "LMR.CORE.SITE_TRUNKING"),
    (r"distributed\s+(core|architecture)", "LMR.CORE.DISTRIBUTED_CORE"),
    (r"centralized\s+core", "LMR.CORE.CENTRALIZED_CORE"),
    (r"p25\s+phase\s*2", "LMR.STD.P25_PHASE2"),
    (r"p25\s+phase\s*1", "LMR.STD.P25_PHASE1"),
    (r"project\s+25\s+phase\s*2", "LMR.STD.P25_PHASE2"),
    (r"project\s+25\s+phase\s*1", "LMR.STD.P25_PHASE1"),
    (r"\btdma\b", "LMR.STD.P25_PHASE2"),
    (r"\bfdma\b", "LMR.STD.P25_PHASE1"),
    (r"simulcast", "LMR.SITE.SIMULCAST_TRUNKED"),
    (r"over[- ]the[- ]air\s+rekey", "LMR.SEC.OTAR"),
    (r"\botar\b", "LMR.SEC.OTAR"),
    (r"aes[- ]?256", "LMR.SEC.AES256"),
    (r"end[- ]to[- ]end\s+.*encrypt", "LMR.SEC.AES256"),
    (r"\bissi\b", "LMR.IOP.ISSI"),
    (r"inter[- ]?rf\s+sub[- ]?system\s+interface", "LMR.IOP.ISSI"),
    (r"\bcssi\b", "LMR.IOP.CSSI"),
    (r"daq\s*3\.?4", "LMR.COV.DAQ_3_4"),
    (r"grade of service", "LMR.COV.GOS_1PCT"),
    (r"\bgos\b", "LMR.COV.GOS_1PCT"),
    (r"95\s*%\s*(area\s*)?coverage", "LMR.COV.COV_95_AREA"),
    (r"in[- ]building\s+coverage", "LMR.COV.PORTABLE_IN_BUILDING"),
    (r"on[- ]street\s+coverage", "LMR.COV.PORTABLE_ON_STREET"),
    (r"coverage\s+(acceptance\s+)?test", "LMR.COV.COVERAGE_TESTING"),
    (r"coverage\s+guarantee", "LMR.COV.COVERAGE_GUARANTEE"),
    (r"coverage\s+map", "LMR.COV.COVERAGE_MAPS"),
    (r"emergency\s+alarm", "LMR.VOICE.EMERGENCY_ALARM"),
    (r"emergency\s+call", "LMR.VOICE.EMERGENCY_CALL"),
    (r"ptt[- ]?id", "LMR.VOICE.PTT_ID"),
    (r"talker\s+id", "LMR.VOICE.PTT_ID"),
    (r"group\s+call", "LMR.VOICE.GROUP_CALL"),
    (r"private\s+call", "LMR.VOICE.PRIVATE_CALL"),
    (r"individual\s+call", "LMR.VOICE.PRIVATE_CALL"),
    (r"dynamic\s+regroup", "LMR.CORE.DYNAMIC_REGROUP"),
    (r"network\s+management\s+system|\bnms\b", "LMR.NMS.UNIFIED_NMS"),
    (r"microwave", "LMR.BH.MICROWAVE_BH"),
    (r"fiber\s+(optic|backhaul|network)", "LMR.BH.FIBER_BH"),
    (r"backhaul", "LMR.BH.IP_TRANSPORT"),
    (r"logging\s+recorder", "LMR.DISP.LOGGING_RECORDER"),
    (r"instant\s+recall", "LMR.DISP.INSTANT_RECALL"),
    (r"dispatch\s+console", "LMR.DISP.CONSOLE_POSITIONS"),
    (r"console\s+position", "LMR.DISP.CONSOLE_POSITIONS"),
    (r"multiband", "LMR.SUB.MULTIBAND_PORTABLE"),
    (r"all[- ]band", "LMR.SUB.MULTIBAND_PORTABLE"),
    (r"portable\s+radio", "LMR.SUB.PORTABLE_GENERAL"),
    (r"mobile\s+radio", "LMR.SUB.MOBILE_GENERAL"),
    (r"control\s+station", "LMR.SUB.CONTROL_STATION"),
    (r"mil[- ]?std[- ]?810", "LMR.RUG.MILSTD_810"),
    (r"intrinsically\s+safe|hazloc", "LMR.RUG.HAZLOC"),
    (r"over[- ]the[- ]air\s+program|\botap\b", "LMR.DATA.OTAP"),
    (r"\bgps\b|\bavl\b|geo[- ]?location", "LMR.DATA.GPS_AVL"),
    (r"text\s+messag", "LMR.DATA.TEXT_MESSAGING"),
    (r"key\s+management|kmf", "LMR.SEC.KMF"),
    (r"key\s+fill|kvl", "LMR.SEC.KVL"),
    (r"fips", "LMR.SEC.FIPS"),
    (r"tower\s+top\s+amplif|\btta\b", "LMR.SITE.TTA"),
    (r"comparator", "LMR.SITE.COMPARATOR"),
    (r"voting\s+receiv", "LMR.SITE.VOTING_RECEIVER"),
    (r"base\s+station|repeater", "LMR.SITE.BASE_REPEATER"),
    (r"transparent\s+(site\s+)?roaming|automatic\s+.*roaming", "LMR.CORE.TRANSPARENT_ROAMING"),
    (r"cutover|migration\s+plan", "LMR.LIFE.CUTOVER_PLAN"),
    (r"acceptance\s+test", "LMR.LIFE.ACCEPTANCE_TEST"),
    (r"warranty", "LMR.LIFE.WARRANTY"),
    (r"spare\s+parts", "LMR.LIFE.SPARES"),
    (r"training", "LMR.LIFE.TRAINING"),
    (r"turnkey", "LMR.LIFE.TURNKEY_IMPL"),
    (r"firstnet|smartconnect|broadband\s+ptt|lte\s+.*ptt", "LMR.BB.LTE_PTT_BRIDGE"),
    (r"conventional\s+(analog|operation|system)", "LMR.STD.CONVENTIONAL_OPS"),
    (r"trunked\s+(radio|system|operation)", "LMR.STD.TRUNKED_OPS"),
    (r"interoperability\s+channel", "LMR.RF.FCC_IOP_CHANNELS"),
    (r"700\s*/?\s*800\s*mhz|7/800", "LMR.RF.BAND_800"),
    (r"\buhf\b", "LMR.RF.BAND_UHF"),
    (r"\bvhf\b", "LMR.RF.BAND_VHF"),
    (r"subscriber\s+growth|2\s*%\s*per\s+year", "LMR.COV.GROWTH_SUBSCRIBERS"),
    (r"voice\s+priorit", "LMR.VOICE.VOICE_OVER_DATA"),
    (r"call\s+alert", "LMR.VOICE.CALL_ALERT"),
    (r"radio\s+check", "LMR.VOICE.RADIO_CHECK"),
    (r"unit\s+(inhibit|stun|disable)", "LMR.VOICE.UNIT_INHIBIT"),
    (r"announcement\s+group", "LMR.VOICE.ANNOUNCEMENT_GROUP"),
    (r"system[- ]wide\s+(group\s+)?call", "LMR.CORE.SYSTEM_WIDE_CALL"),
    (r"path\s+diversity|diverse\s+(path|route)", "LMR.BH.PATH_DIVERSITY"),
    (r"remote\s+configur", "LMR.NMS.REMOTE_CONFIG"),
    (r"real[- ]?time\s+monitor", "LMR.NMS.REALTIME_MONITOR"),
    (r"firefighter|xe\b|ultra[- ]rugged", "LMR.SUB.TIER_FIRE"),
    (r"law\s+enforcement\s+(model|tier|portable|radio)", "LMR.SUB.TIER_LAW"),
    (r"public\s+service\s+(model|tier)", "LMR.SUB.TIER_PUBLIC_SERVICE"),
    (r"speaker\s+mic|accessory", "LMR.SUB.ACCESSORIES"),
    (r"programming\s+template|codeplug", "LMR.SUB.PROGRAMMING_TEMPLATES"),
    (r"vehicle\s+install", "LMR.SUB.VEHICLE_INSTALL"),
    (r"ip\s+console", "LMR.DISP.CONSOLE_IP"),
    (r"mutual\s+aid", "LMR.IOP.MUTUAL_AID_PATCH"),
    (r"conventional\s+gateway", "LMR.IOP.CONVENTIONAL_GATEWAY"),
    (r"p25\s+cap|compliance\s+assessment", "LMR.STD.P25_CAP"),
    (r"grounding|lightning\s+protect|r56", "LMR.SITE.SITE_GROUNDING"),
    (r"site\s+alarm|environmental\s+alarm", "LMR.SITE.SITE_ALARMS"),
    (r"gps\s+sync|simulcast\s+timing", "LMR.SITE.SIMULCAST_TIMING"),
]


def load_l1() -> tuple[dict[str, dict], dict[str, str]]:
    doc = json.loads(L1_PATH.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in doc["capabilities"]}
    alias_to_id: dict[str, str] = {}
    for c in doc["capabilities"]:
        if c.get("alias"):
            alias_to_id[c["alias"]] = c["id"]
        alias_to_id[c["id"]] = c["id"]
    return by_id, alias_to_id


def resolve_alias(token: str, alias_to_id: dict[str, str]) -> str | None:
    return alias_to_id.get(token)


def extract_pages(pdf_path: Path) -> list[tuple[int, str]]:
    reader = PdfReader(str(pdf_path))
    pages: list[tuple[int, str]] = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        pages.append((i, text))
    return pages


SHALL_RE = re.compile(
    r"(?i)((?:the\s+)?(?:contractor|proposer|vendor|system|selected\s+vendor|respondent|offeror|"
    r"radio\s+system|subscriber|equipment|network|nms|console|contractor'?s?\s+proposed\s+system)"
    r"[^.]{0,200}?\b(?:shall|must|will)\b[^.!?\n]{10,240}[.!?])"
)

BULLET_SHALL_RE = re.compile(
    r"(?im)^\s*(?:\(?[a-z0-9]+\)?\.?|[A-Z]\.|[-•*])\s+((?:[^.\n]{0,40}\b(?:shall|must)\b[^.\n]{10,200}))"
)

SIMPLE_SHALL_RE = re.compile(
    r"(?i)\b((?:shall|must)\s+(?:provide|support|include|be|have|allow|enable|meet|comply|"
    r"operate|offer|maintain|perform|deliver)[^.\n]{8,180}[.!]?)"
)


def normalize_phrase(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip(" \t\r\n-•*")
    s = re.sub(r"\s+([,.;:])", r"\1", s)
    return s[:300]


def normalize_key(s: str) -> str:
    """Aggressive key for near-duplicate collapse."""
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(
        r"\b(the|a|an|contractor|proposer|vendor|selected|system|shall|must|will|provide|support|include|be|have)\b",
        " ",
        s,
    )
    s = re.sub(r"\s+", " ", s).strip()
    return s[:180]


def harvest_phrases(page_text: str) -> list[str]:
    found: list[str] = []
    for rx in (SHALL_RE, BULLET_SHALL_RE, SIMPLE_SHALL_RE):
        for m in rx.finditer(page_text):
            phrase = normalize_phrase(m.group(1) if m.lastindex else m.group(0))
            if len(phrase) < 20:
                continue
            if phrase.lower().startswith("table of contents"):
                continue
            if phrase.count(".") >= 5 and "...." in phrase.replace(" ", ""):
                continue  # TOC leader dots
            if re.search(r"\.{4,}", phrase):
                continue
            found.append(phrase)
    # Also keep short capability-like noun phrases containing seed keywords
    for line in page_text.splitlines():
        line_n = normalize_phrase(line)
        if 25 <= len(line_n) <= 160 and re.search(r"(?i)shall|must|provide|support|encrypt|simulcast|otar|issi|coverage|console|trunk", line_n):
            if re.search(r"(?i)\b(shall|must|support|provide)\b", line_n):
                found.append(line_n)
    # dedupe preserve order
    seen = set()
    out = []
    for p in found:
        key = p.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out


def build_token_index(by_id: dict[str, dict]) -> list[tuple[str, str, re.Pattern[str]]]:
    """Map capability name tokens to ids for secondary matching."""
    index: list[tuple[str, str, re.Pattern[str]]] = []
    for cid, c in by_id.items():
        if c.get("status") == "stub":
            continue
        name = c["name"]
        # skip very generic short names
        if len(name) < 8:
            continue
        pat = re.compile(rf"(?i)\b{re.escape(name)}\b")
        index.append((cid, name, pat))
        # also match notable multi-word fragments from definition first 6 words — skip
    return index


def match_phrase(
    phrase: str,
    alias_to_id: dict[str, str],
    name_index: list[tuple[str, str, re.Pattern[str]]],
) -> list[tuple[str, float, str]]:
    """Return list of (capability_id, confidence, method)."""
    hits: list[tuple[str, float, str]] = []
    low = phrase.lower()

    for pat, alias in SEED_PHRASES:
        if re.search(pat, phrase, flags=re.I):
            cid = resolve_alias(alias, alias_to_id)
            if cid:
                hits.append((cid, 0.92, "seed"))

    for cid, name, pat in name_index:
        if pat.search(phrase):
            hits.append((cid, 0.75, "name"))

    # Alias code fragments e.g. ISSI already handled; also match LMR-ish acronyms in phrase
    for alias, cid in alias_to_id.items():
        if not alias.startswith("LMR."):
            continue
        code = alias.split(".")[-1].replace("_", " ")
        if len(code) < 6:
            continue
        if code.lower() in low:
            hits.append((cid, 0.65, "alias_code"))

    # dedupe keep highest confidence
    best: dict[str, tuple[float, str]] = {}
    for cid, conf, method in hits:
        if cid not in best or conf > best[cid][0]:
            best[cid] = (conf, method)
    return [(cid, conf, method) for cid, (conf, method) in best.items()]


def phrase_hash(doc_id: str, phrase: str) -> str:
    return hashlib.sha1(f"{doc_id}|{phrase.lower()}".encode()).hexdigest()[:12]


def main() -> None:
    by_id, alias_to_id = load_l1()
    name_index = build_token_index(by_id)

    mapped_rows: list[dict] = []
    unmapped: list[dict] = []
    per_cap: dict[str, int] = defaultdict(int)

    for doc in DOCS:
        path = RFP_DIR / doc["file"]
        if not path.exists():
            raise SystemExit(f"missing PDF: {path}")
        print(f"extract {doc['id']} ...")
        pages = extract_pages(path)
        doc_phrases = 0
        for page_no, text in pages:
            phrases = harvest_phrases(text)
            for phrase in phrases:
                matches = match_phrase(phrase, alias_to_id, name_index)
                row_base = {
                    "phrase": phrase,
                    "source_doc_id": doc["id"],
                    "source_file": doc["file"],
                    "page": page_no,
                    "phrase_id": phrase_hash(doc["id"], phrase),
                }
                if not matches:
                    unmapped.append(row_base)
                    continue
                # keep top 2 matches max to avoid explosion
                matches = sorted(matches, key=lambda x: -x[1])[:2]
                for cid, conf, method in matches:
                    mapped_rows.append(
                        {
                            **row_base,
                            "capability_id": cid,
                            "capability_alias": by_id[cid].get("alias"),
                            "confidence": round(conf, 2),
                            "match_method": method,
                            "status": "auto_accepted",
                        }
                    )
                    per_cap[cid] += 1
                    doc_phrases += 1
        print(f"  pages={len(pages)} mapped_links~={doc_phrases}")

    # Dedupe identical phrase+capability and near-duplicates
    uniq: dict[tuple[str, str], dict] = {}
    for r in mapped_rows:
        key = (normalize_key(r["phrase"]), r["capability_id"])
        if not key[0]:
            continue
        if key not in uniq or r["confidence"] > uniq[key]["confidence"]:
            # prefer longer, cleaner phrase when confidence equal
            if key in uniq and r["confidence"] == uniq[key]["confidence"]:
                if len(r["phrase"]) <= len(uniq[key]["phrase"]):
                    continue
            uniq[key] = r
    mapped_rows = list(uniq.values())

    # Within each capability, drop near-duplicate phrases (substring / high token overlap)
    by_c_tmp: dict[str, list[dict]] = defaultdict(list)
    for r in mapped_rows:
        by_c_tmp[r["capability_id"]].append(r)
    cleaned: list[dict] = []
    for cid, rows in by_c_tmp.items():
        rows = sorted(rows, key=lambda r: (-r["confidence"], -len(r["phrase"])))
        kept_keys: list[str] = []
        for r in rows:
            k = normalize_key(r["phrase"])
            tokens = set(k.split())
            dup = False
            for prev in kept_keys:
                if k in prev or prev in k:
                    dup = True
                    break
                prev_t = set(prev.split())
                if tokens and prev_t:
                    overlap = len(tokens & prev_t) / max(1, min(len(tokens), len(prev_t)))
                    if overlap >= 0.85:
                        dup = True
                        break
            if dup:
                continue
            kept_keys.append(k)
            cleaned.append(r)
    mapped_rows = cleaned

    # Prefer denser coverage: if over 900, keep highest confidence + ensure top caps covered
    mapped_rows.sort(key=lambda r: (-r["confidence"], r["capability_id"], r["phrase"]))

    # Hold out ~10% by phrase_id hash
    main_rows: list[dict] = []
    hold_rows: list[dict] = []
    for r in mapped_rows:
        if int(r["phrase_id"][:2], 16) % 10 == 0:
            hold_rows.append(r)
        else:
            main_rows.append(r)

    # Cap main set to ~800 if huge, keeping diversity across capabilities
    if len(main_rows) > 800:
        by_c: dict[str, list[dict]] = defaultdict(list)
        for r in main_rows:
            by_c[r["capability_id"]].append(r)
        capped: list[dict] = []
        # round-robin up to 10 per capability then fill
        for cid, rows in by_c.items():
            capped.extend(rows[:10])
        if len(capped) < 400:
            rest = [r for rows in by_c.values() for r in rows[10:]]
            capped.extend(rest[: 800 - len(capped)])
        main_rows = capped[:800]

    # Ensure minimum density on high-value caps if present in mapped set
    top_aliases = [
        "LMR.CORE.GEO_REDUNDANT_CORE",
        "LMR.CORE.NO_SPOF",
        "LMR.SITE.SIMULCAST_TRUNKED",
        "LMR.SEC.OTAR",
        "LMR.SEC.AES256",
        "LMR.IOP.ISSI",
        "LMR.COV.DAQ_3_4",
        "LMR.COV.GOS_1PCT",
        "LMR.STD.P25_PHASE2",
        "LMR.VOICE.EMERGENCY_ALARM",
        "LMR.DISP.CONSOLE_POSITIONS",
        "LMR.NMS.UNIFIED_NMS",
        "LMR.DATA.GPS_AVL",
        "LMR.SUB.MULTIBAND_PORTABLE",
        "LMR.BB.LTE_PTT_BRIDGE",
    ]
    covered = {r["capability_alias"] for r in main_rows}
    print("top alias coverage:", sum(1 for a in top_aliases if a in covered), "/", len(top_aliases))

    caps_with_syn = len({r["capability_id"] for r in main_rows})
    payload = {
        "schema_version": "1.0",
        "sprint": "S2",
        "method": "deterministic_seed_and_name_match",
        "counts": {
            "synonyms": len(main_rows),
            "holdout": len(hold_rows),
            "unmapped_phrases": len(unmapped),
            "capabilities_with_synonyms": caps_with_syn,
            "documents": len(DOCS),
        },
        "documents": DOCS,
        "synonyms": main_rows,
    }
    hold_payload = {
        "schema_version": "1.0",
        "sprint": "S2",
        "purpose": "held_out_eval_set_do_not_tune_on",
        "counts": {"synonyms": len(hold_rows)},
        "synonyms": hold_rows,
    }
    # trim unmapped to 500 samples for inspection
    unmapped_payload = {
        "schema_version": "1.0",
        "sprint": "S2",
        "counts": {"unmapped_phrases": len(unmapped), "sample_size": min(500, len(unmapped))},
        "phrases": unmapped[:500],
    }

    OUT_MAIN.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_HOLD.write_text(json.dumps(hold_payload, indent=2), encoding="utf-8")
    OUT_UNMAP.write_text(json.dumps(unmapped_payload, indent=2), encoding="utf-8")
    print(
        f"wrote {OUT_MAIN.name}: synonyms={len(main_rows)} holdout={len(hold_rows)} "
        f"unmapped={len(unmapped)} caps_covered={caps_with_syn}"
    )


if __name__ == "__main__":
    main()
