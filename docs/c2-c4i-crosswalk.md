# C2 / C3 / C4I → PSERS L1 crosswalk

**Status:** Phase 7 Lite (terminology only)  
**Rule:** Map sector jargon onto public-safety PSERS capabilities. Do **not** create military/defence peer L1 trees in this phase.

| Term (RFP / buyer language) | Meaning (short) | Primary PSERS L1 alias(es) | Notes |
|----------------------------|-----------------|----------------------------|-------|
| Command and Control (C2) | Coordinate + situational awareness | `CAD.COMMAND_VIEW`, `EOC.SIT_AWARENESS` | Public-safety = PSAP/EOC supervisor view |
| C3 (Command, Control, Communications) | C2 + mission-critical voice/data | `CAD.COMMAND_VIEW`, LMR aliases, `CAD.RADIO_INTEGRATION`, **`MCX.MCPTT`** (Phase 8 Lite) | MCX Lite shipped; deep 3GPP tree still deferred |
| C4I (… Computers, Intelligence) | C3 + platforms + intel/sensor feeds | `EOC.SIT_AWARENESS`, `EOC.COMMON_OP_PICTURE`, CAD/RMS/VMS, `IOT.SENSOR_FUSION` | Computers ≈ PLAT/APP; intel ≈ sensors + fusion |
| C4ISR | C4I + reconnaissance/ISR collection | Above + `UAS.*`, `VIDEO.*`, `IOT.*` | ISR collection already partially in Sensors |
| Common operating picture (COP) | Shared multi-source SA display | `EOC.COMMON_OP_PICTURE`, `EOC.SIT_AWARENESS` | Also “TOC COP” in defence RFPs → same L1 |
| Mobile / field incident capture | Respond apps | `FIELD.INCIDENT_CAPTURE`, `CAD.MOBILE_CLIENT`, `FIELD.MDT` | |
| Digital evidence / BWC | Capture + custody | `FIELD.EVIDENCE_CAPTURE`, `VIDEO.BODYWORN`, `VIDEO.BODYWORN_EVIDENCE`, `RMS.EVIDENCE_PROPERTY` | |
| Records / case close-out | After-action | `RMS.INCIDENT_REPORT`, `RMS.CASE_PACKAGE`, `RMS.SUPPLEMENTAL_REPORT` | |

## Sector differences (deferred as L1 forks)

| Dimension | Public safety (this ontology) | Military / defence (deferred) |
|-----------|------------------------------|-------------------------------|
| Trigger | 911 / NG911 / alarm / tip | Order, ISR cue, ROE event |
| “Incident” | Call / incident / case | Event, TIC, contact, mission package |
| Command | PSAP, ICS/NIMS, EOC | TOC/COC, battle management |
| Close-out | RMS + evidence vault | AAR / intel product / mission log |

Military peer L1 verticals require a later SPEC amendment and budget.
