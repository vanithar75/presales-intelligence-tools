# PSERS root & facets

**Status:** Frozen for MVP (Sprint 0)  
**Root ID:** `PSERS`  
**Full name:** Public Safety Emergency Response System (of Systems)

## Definition

The coordinated set of people, processes, and technical capabilities that detect, receive, dispatch, respond to, coordinate, and document emergency incidents for public safety agencies.

## Three complementary models

1. **Operational CDM** — NENA EIDO/IDX, NIEM/EIDD, EDXL (runtime incident exchange). Align later; not required for MVP matching.
2. **Capability Ontology (L1)** — Stable buyer requirements for RFP matching. **This repo's focus.**
3. **Product Catalog (L3)** — Vendor SKUs/families (MSI in MVP).

## ID scheme

```text
PSERS.<STACK>.<DOMAIN>.<CAPABILITY>
```

MVP aliases: short codes like `LMR.RF.SIMULCAST_TRUNKED` map to full IDs via `alias` field.

## Stack facet (required on every L1)

| Code | Name | Examples |
|------|------|----------|
| `INFRA` | Infrastructure | LMR, MCX, backhaul, sites |
| `SENS` | Sensors | Cameras, drones, ALPR, gunshot, IoT |
| `PLAT` | Platforms | NG911, CAD, RMS, GIS, VMS |
| `APP` | Applications | Field mobile, consoles, mass notify |
| `SVC` | Services | Integration, managed, training |
| `XCUT` | CrossCutting | IAM, encryption, interop, resilience |

## Mission facet (tags, multi-valued)

`detect` | `call_take` | `locate` | `dispatch` | `respond` | `coordinate` | `inform` | `after_action`

## LMR vs MCX

Peers under Mission-Critical Communications (`INFRA`). Bridge via `PSERS.XCUT.IOP.LMR_MCX_IWF`. Do not nest one under the other.

## Governance

- Root `PSERS` immutable
- Published L1 IDs immutable (add/deprecate only)
- New verticals add domains under existing stack facets — no new root
