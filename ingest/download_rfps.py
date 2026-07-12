"""Download the 3 allowlisted MVP RFP PDFs into data/rfp/."""
from __future__ import annotations

import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "rfp"

FILES = [
    (
        "ecso-jackson-p25-functional-spec.pdf",
        "https://ecso911.com/wp-content/uploads/2019/11/ECSO-P25-Ph2-Functional-Specification-FINAL-20191118.pdf",
    ),
    (
        "erie-trunked-radio-system-2026-018.pdf",
        "https://www3.erie.gov/purchasing/sites/www3.erie.gov.purchasing/files/2026-02/erie-county-trunked-radio-system-rfp-2026-018vf.pdf",
    ),
    (
        "erie-radio-subscriber-2026-019.pdf",
        "https://www3.erie.gov/purchasing/sites/www3.erie.gov.purchasing/files/2026-02/erie-county-radio-subscriber-rfp-2026-019vf.pdf",
    ),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, url in FILES:
        dest = OUT / name
        if dest.exists() and dest.stat().st_size > 10_000:
            print(f"skip {name} (exists)")
            continue
        print(f"fetch {name} ...")
        req = urllib.request.Request(url, headers={"User-Agent": "PSERS-MVP/0.1"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            dest.write_bytes(resp.read())
        print(f"  wrote {dest.stat().st_size} bytes")


if __name__ == "__main__":
    main()
