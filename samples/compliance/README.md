# Compliance workbook samples

Bid-desk compliance matrix artifacts (not ontology). Ontology JSON stays under `ontology/`.

Re-run from an allowlisted RFP PDF:

```bash
python3 ingest/download_rfps.py   # once
python3 ingest/e2e_compliance_pdf.py
# Erie trunked pages 21–25 → samples/compliance/*-compliance.xlsx
```

Any page window:

```bash
python3 ingest/export_compliance.py data/rfp/erie-trunked-radio-system-2026-018.pdf \
  --start-page 21 --end-page 25 -o samples/compliance/erie-pp21-25.xlsx
```
