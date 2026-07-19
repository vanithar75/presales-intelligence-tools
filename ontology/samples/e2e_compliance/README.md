# E2E compliance workbook samples

Generated from allowlisted RFP PDFs (gitignored binaries). Re-run:

```bash
python3 ingest/download_rfps.py   # once
python3 ingest/e2e_compliance_pdf.py
# Erie trunked pages 21–25 → *-compliance.xlsx + preview.csv/md
```

Or any page window:

```bash
python3 ingest/export_compliance.py data/rfp/erie-trunked-radio-system-2026-018.pdf \
  --start-page 21 --end-page 25 -o out/erie-pp21-25.xlsx
```
