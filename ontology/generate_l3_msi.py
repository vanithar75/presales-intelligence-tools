"""Generate MSI (Motorola Solutions) L3 product catalog and L1 mappings."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1_PATH = ROOT / "ontology" / "l1_capabilities.json"
OUT_PRODUCTS = ROOT / "ontology" / "l3_msi_products.json"
OUT_MAP = ROOT / "ontology" / "l3_product_capabilities.json"

MSI_URL = "https://www.motorolasolutions.com"

PRODUCTS = [
    {"id": "MSI.ASTRO25.SYSTEM", "family": "ASTRO 25", "sku_or_name": "ASTRO 25 P25 System", "form_factor": "infrastructure", "notes": "P25 trunked/conventional core and RFSS ecosystem"},
    {"id": "MSI.ASTRO25.SIMULCAST", "family": "ASTRO 25", "sku_or_name": "ASTRO 25 Simulcast", "form_factor": "infrastructure", "notes": "Wide-area simulcast configuration"},
    {"id": "MSI.ASTRO25.ISSI", "family": "ASTRO 25", "sku_or_name": "ASTRO 25 ISSI Gateway", "form_factor": "infrastructure", "notes": "Inter-RF Subsystem Interface"},
    {"id": "MSI.ASTRO25.KMF", "family": "ASTRO 25", "sku_or_name": "ASTRO Key Management Facility", "form_factor": "infrastructure", "notes": "OTAR / key management"},
    {"id": "MSI.GTR8000", "family": "G-Series RF", "sku_or_name": "GTR 8000 Base Station / Repeater", "form_factor": "site_rf", "notes": "Site base/repeater"},
    {"id": "MSI.APX.PORTABLE", "family": "APX", "sku_or_name": "APX P25 Portable Family", "form_factor": "portable", "notes": "Mission-critical P25 portables"},
    {"id": "MSI.APX.MOBILE", "family": "APX", "sku_or_name": "APX P25 Mobile Family", "form_factor": "mobile", "notes": "Mission-critical P25 mobiles"},
    {"id": "MSI.APX.8000", "family": "APX", "sku_or_name": "APX 8000 All-Band Portable", "form_factor": "portable", "notes": "Multiband portable"},
    {"id": "MSI.APX.NEXT", "family": "APX NEXT", "sku_or_name": "APX NEXT Smart Radio", "form_factor": "portable", "notes": "Broadband-converged P25 smart radio"},
    {"id": "MSI.APX.N_SERIES", "family": "APX N-Series", "sku_or_name": "APX N30/N50/N70 Family", "form_factor": "portable", "notes": "N-series portables"},
    {"id": "MSI.APX.XE", "family": "APX", "sku_or_name": "APX XE Firefighter Portable", "form_factor": "portable", "notes": "Ultra-rugged firefighter form factor"},
    {"id": "MSI.MOTOTRBO.RADIO", "family": "MOTOTRBO", "sku_or_name": "MOTOTRBO Digital Radio Family", "form_factor": "subscriber", "notes": "DMR professional radio"},
    {"id": "MSI.MOTOTRBO.INFRA", "family": "MOTOTRBO", "sku_or_name": "MOTOTRBO Infrastructure", "form_factor": "infrastructure", "notes": "DMR capacity/trunking infra"},
    {"id": "MSI.MCC.CONSOLE", "family": "MCC Consoles", "sku_or_name": "MCC Console Family", "form_factor": "console", "notes": "Dispatch console positions"},
    {"id": "MSI.CC.COMMAND", "family": "CommandCentral", "sku_or_name": "CommandCentral Suite", "form_factor": "platform", "notes": "Command/applications suite (map by module)"},
    {"id": "MSI.SMARTCONNECT", "family": "SmartConnect", "sku_or_name": "SmartConnect LMR-Broadband", "form_factor": "broadband", "notes": "LMR–LTE/broadband PTT bridge features"},
    {"id": "MSI.KVL", "family": "Key Management", "sku_or_name": "KVL Key Variable Loader", "form_factor": "accessory", "notes": "Manual key fill device family"},
    {"id": "MSI.NMS.ASTRO", "family": "ASTRO 25", "sku_or_name": "ASTRO Network Management", "form_factor": "nms", "notes": "Radio system NMS"},
    {"id": "MSI.LOGGING", "family": "Logging", "sku_or_name": "Radio Logging / Recording Solutions", "form_factor": "recording", "notes": "Logging recorder integrations"},
    {"id": "MSI.SERVICES.IMPL", "family": "Services", "sku_or_name": "Implementation & Integration Services", "form_factor": "service", "notes": "Turnkey deploy, cutover, training"},
]

# alias → list of (product_id, support_level, notes)
# Focus on top bid-desk capabilities + broad family coverage
MAPPINGS: list[tuple[str, str, str, str]] = [
    # Standards / core / sites
    ("LMR.STD.P25_PHASE1", "MSI.ASTRO25.SYSTEM", "native", "ASTRO 25 Phase 1"),
    ("LMR.STD.P25_PHASE2", "MSI.ASTRO25.SYSTEM", "native", "ASTRO 25 Phase 2"),
    ("LMR.STD.DUAL_MODE_FDMA_TDMA", "MSI.ASTRO25.SYSTEM", "native", ""),
    ("LMR.STD.TRUNKED_OPS", "MSI.ASTRO25.SYSTEM", "native", ""),
    ("LMR.STD.CONVENTIONAL_OPS", "MSI.ASTRO25.SYSTEM", "native", ""),
    ("LMR.STD.P25_CAP", "MSI.ASTRO25.SYSTEM", "native", "CAP-tested configurations"),
    ("LMR.STD.DMR_TIER2", "MSI.MOTOTRBO.RADIO", "native", "MOTOTRBO DMR"),
    ("LMR.STD.DMR_TIER3", "MSI.MOTOTRBO.INFRA", "native", ""),
    ("LMR.CORE.GEO_REDUNDANT_CORE", "MSI.ASTRO25.SYSTEM", "native", "Geo-redundant ASTRO cores"),
    ("LMR.CORE.NO_SPOF", "MSI.ASTRO25.SYSTEM", "native", ""),
    ("LMR.CORE.CENTRALIZED_CORE", "MSI.ASTRO25.SYSTEM", "native", ""),
    ("LMR.CORE.DISTRIBUTED_CORE", "MSI.ASTRO25.SYSTEM", "option", "Architecture-dependent"),
    ("LMR.CORE.FAILSOFT", "MSI.ASTRO25.SYSTEM", "native", ""),
    ("LMR.CORE.SITE_TRUNKING", "MSI.ASTRO25.SYSTEM", "native", ""),
    ("LMR.CORE.TRANSPARENT_ROAMING", "MSI.ASTRO25.SYSTEM", "native", ""),
    ("LMR.CORE.DYNAMIC_REGROUP", "MSI.ASTRO25.SYSTEM", "native", ""),
    ("LMR.CORE.SYSTEM_WIDE_CALL", "MSI.ASTRO25.SYSTEM", "native", ""),
    ("LMR.CORE.FAULT_TOLERANT_CONTROL", "MSI.ASTRO25.SYSTEM", "native", ""),
    ("LMR.CORE.BACKUP_RESTORE", "MSI.NMS.ASTRO", "native", ""),
    ("LMR.SITE.SIMULCAST_TRUNKED", "MSI.ASTRO25.SIMULCAST", "native", ""),
    ("LMR.SITE.BASE_REPEATER", "MSI.GTR8000", "native", ""),
    ("LMR.SITE.COMPARATOR", "MSI.ASTRO25.SIMULCAST", "native", ""),
    ("LMR.SITE.VOTING_RECEIVER", "MSI.ASTRO25.SIMULCAST", "native", ""),
    ("LMR.SITE.SIMULCAST_TIMING", "MSI.ASTRO25.SIMULCAST", "native", ""),
    ("LMR.SITE.TTA", "MSI.GTR8000", "option", "Site RF optioning"),
    ("LMR.SITE.SITE_ALARMS", "MSI.NMS.ASTRO", "native", ""),
    ("LMR.SITE.SITE_GROUNDING", "MSI.SERVICES.IMPL", "partner", "R56-class practices via services/install"),
    # Coverage
    ("LMR.COV.DAQ_3_4", "MSI.ASTRO25.SYSTEM", "native", "Design/test to DAQ targets"),
    ("LMR.COV.COV_95_AREA", "MSI.ASTRO25.SYSTEM", "native", ""),
    ("LMR.COV.GOS_1PCT", "MSI.ASTRO25.SYSTEM", "native", ""),
    ("LMR.COV.PORTABLE_IN_BUILDING", "MSI.ASTRO25.SYSTEM", "native", "Design-dependent"),
    ("LMR.COV.COVERAGE_TESTING", "MSI.SERVICES.IMPL", "native", ""),
    ("LMR.COV.COVERAGE_GUARANTEE", "MSI.SERVICES.IMPL", "option", "Contractual"),
    ("LMR.COV.COVERAGE_MAPS", "MSI.SERVICES.IMPL", "native", ""),
    ("LMR.COV.GROWTH_SUBSCRIBERS", "MSI.ASTRO25.SYSTEM", "native", ""),
    # Voice / data / security
    ("LMR.VOICE.GROUP_CALL", "MSI.ASTRO25.SYSTEM", "native", ""),
    ("LMR.VOICE.PRIVATE_CALL", "MSI.ASTRO25.SYSTEM", "native", ""),
    ("LMR.VOICE.EMERGENCY_ALARM", "MSI.ASTRO25.SYSTEM", "native", ""),
    ("LMR.VOICE.EMERGENCY_CALL", "MSI.ASTRO25.SYSTEM", "native", ""),
    ("LMR.VOICE.PTT_ID", "MSI.ASTRO25.SYSTEM", "native", ""),
    ("LMR.VOICE.CALL_ALERT", "MSI.ASTRO25.SYSTEM", "native", ""),
    ("LMR.VOICE.VOICE_OVER_DATA", "MSI.ASTRO25.SYSTEM", "native", ""),
    ("LMR.VOICE.RADIO_CHECK", "MSI.ASTRO25.SYSTEM", "native", ""),
    ("LMR.VOICE.UNIT_INHIBIT", "MSI.ASTRO25.SYSTEM", "native", ""),
    ("LMR.DATA.GPS_AVL", "MSI.APX.PORTABLE", "native", "APX location features"),
    ("LMR.DATA.GPS_AVL", "MSI.APX.NEXT", "native", ""),
    ("LMR.DATA.TEXT_MESSAGING", "MSI.ASTRO25.SYSTEM", "native", ""),
    ("LMR.DATA.OTAP", "MSI.APX.PORTABLE", "native", ""),
    ("LMR.DATA.OTAP", "MSI.SMARTCONNECT", "option", "Broadband programming path"),
    ("LMR.SEC.AES256", "MSI.ASTRO25.SYSTEM", "native", ""),
    ("LMR.SEC.AES256", "MSI.APX.PORTABLE", "native", ""),
    ("LMR.SEC.OTAR", "MSI.ASTRO25.KMF", "native", ""),
    ("LMR.SEC.OTAR", "MSI.APX.PORTABLE", "native", "OTAR-capable APX"),
    ("LMR.SEC.KMF", "MSI.ASTRO25.KMF", "native", ""),
    ("LMR.SEC.KVL", "MSI.KVL", "native", ""),
    ("LMR.SEC.MULTI_KEY", "MSI.APX.PORTABLE", "native", ""),
    ("LMR.SEC.FIPS", "MSI.APX.PORTABLE", "option", "Model/config dependent"),
    ("LMR.SEC.END_TO_END_CONSOLE", "MSI.MCC.CONSOLE", "native", ""),
    # Interop / dispatch / backhaul / NMS
    ("LMR.IOP.ISSI", "MSI.ASTRO25.ISSI", "native", ""),
    ("LMR.IOP.CSSI", "MSI.MCC.CONSOLE", "native", ""),
    ("LMR.IOP.MUTUAL_AID_PATCH", "MSI.MCC.CONSOLE", "native", ""),
    ("LMR.IOP.CONVENTIONAL_GATEWAY", "MSI.ASTRO25.SYSTEM", "option", ""),
    ("LMR.IOP.CAD_INTERFACE", "MSI.CC.COMMAND", "option", "CAD integrations via suite/partners"),
    ("LMR.IOP.LMR_MCX_IWF_TOUCH", "MSI.SMARTCONNECT", "option", "Broadband bridge class; full 3GPP IWF varies"),
    ("LMR.DISP.CONSOLE_POSITIONS", "MSI.MCC.CONSOLE", "native", ""),
    ("LMR.DISP.CONSOLE_IP", "MSI.MCC.CONSOLE", "native", ""),
    ("LMR.DISP.CONSOLE_PATCH", "MSI.MCC.CONSOLE", "native", ""),
    ("LMR.DISP.LOGGING_RECORDER", "MSI.LOGGING", "native", ""),
    ("LMR.DISP.INSTANT_RECALL", "MSI.MCC.CONSOLE", "native", ""),
    ("LMR.DISP.CONSOLE_EMERG_DISPLAY", "MSI.MCC.CONSOLE", "native", ""),
    ("LMR.DISP.BACKUP_DISPATCH", "MSI.MCC.CONSOLE", "option", ""),
    ("LMR.BH.MICROWAVE_BH", "MSI.SERVICES.IMPL", "partner", "Often partner microwave; MSI integrates"),
    ("LMR.BH.FIBER_BH", "MSI.SERVICES.IMPL", "partner", ""),
    ("LMR.BH.IP_TRANSPORT", "MSI.ASTRO25.SYSTEM", "native", "IP transport for ASTRO sites"),
    ("LMR.BH.PATH_DIVERSITY", "MSI.SERVICES.IMPL", "option", "Design-dependent"),
    ("LMR.BH.BH_NMS_INTEGRATION", "MSI.NMS.ASTRO", "option", ""),
    ("LMR.NMS.UNIFIED_NMS", "MSI.NMS.ASTRO", "native", ""),
    ("LMR.NMS.REALTIME_MONITOR", "MSI.NMS.ASTRO", "native", ""),
    ("LMR.NMS.REMOTE_CONFIG", "MSI.NMS.ASTRO", "native", ""),
    ("LMR.NMS.PERFORMANCE_REPORTS", "MSI.NMS.ASTRO", "native", ""),
    ("LMR.NMS.SOFTWARE_PATCHING", "MSI.SERVICES.IMPL", "native", ""),
    # Subscribers / rugged / broadband / lifecycle
    ("LMR.SUB.PORTABLE_GENERAL", "MSI.APX.PORTABLE", "native", ""),
    ("LMR.SUB.MOBILE_GENERAL", "MSI.APX.MOBILE", "native", ""),
    ("LMR.SUB.CONTROL_STATION", "MSI.APX.MOBILE", "native", "Control station configs"),
    ("LMR.SUB.MULTIBAND_PORTABLE", "MSI.APX.8000", "native", ""),
    ("LMR.SUB.MULTIBAND_PORTABLE", "MSI.APX.NEXT", "native", ""),
    ("LMR.SUB.MULTIBAND_MOBILE", "MSI.APX.MOBILE", "native", "All-band mobile options"),
    ("LMR.SUB.TIER_LAW", "MSI.APX.PORTABLE", "native", ""),
    ("LMR.SUB.TIER_FIRE", "MSI.APX.XE", "native", ""),
    ("LMR.SUB.TIER_PUBLIC_SERVICE", "MSI.APX.PORTABLE", "native", ""),
    ("LMR.SUB.TIER_PUBLIC_SERVICE", "MSI.MOTOTRBO.RADIO", "native", "Non-mission-critical tier option"),
    ("LMR.SUB.ACCESSORIES", "MSI.APX.PORTABLE", "native", ""),
    ("LMR.SUB.VEHICLE_INSTALL", "MSI.APX.MOBILE", "native", ""),
    ("LMR.SUB.PROGRAMMING_TEMPLATES", "MSI.SERVICES.IMPL", "native", ""),
    ("LMR.SUB.WIFI_SU", "MSI.APX.NEXT", "native", ""),
    ("LMR.SUB.BT_SU", "MSI.APX.NEXT", "native", ""),
    ("LMR.RUG.MILSTD_810", "MSI.APX.PORTABLE", "native", ""),
    ("LMR.RUG.XE_FIREFIGHTER", "MSI.APX.XE", "native", ""),
    ("LMR.RUG.IP_RATING", "MSI.APX.PORTABLE", "native", ""),
    ("LMR.RUG.LOUD_AUDIO", "MSI.APX.PORTABLE", "native", ""),
    ("LMR.RUG.GLOVE_UI", "MSI.APX.XE", "native", ""),
    ("LMR.RUG.HAZLOC", "MSI.APX.PORTABLE", "option", "IS models"),
    ("LMR.BB.LTE_PTT_BRIDGE", "MSI.SMARTCONNECT", "native", ""),
    ("LMR.BB.LTE_PTT_BRIDGE", "MSI.APX.NEXT", "native", ""),
    ("LMR.BB.FIRSTNET_READY", "MSI.APX.NEXT", "native", ""),
    ("LMR.BB.SMART_LOCATE", "MSI.APX.NEXT", "native", ""),
    ("LMR.BB.SMART_PROGRAMMING", "MSI.APX.NEXT", "native", ""),
    ("LMR.BB.CONVERGED_DEVICE", "MSI.APX.NEXT", "native", ""),
    ("LMR.BB.WIFI_CONNECTIVITY", "MSI.APX.NEXT", "native", ""),
    ("LMR.LIFE.TURNKEY_IMPL", "MSI.SERVICES.IMPL", "native", ""),
    ("LMR.LIFE.CUTOVER_PLAN", "MSI.SERVICES.IMPL", "native", ""),
    ("LMR.LIFE.ACCEPTANCE_TEST", "MSI.SERVICES.IMPL", "native", ""),
    ("LMR.LIFE.TRAINING", "MSI.SERVICES.IMPL", "native", ""),
    ("LMR.LIFE.WARRANTY", "MSI.SERVICES.IMPL", "native", ""),
    ("LMR.LIFE.SPARES", "MSI.SERVICES.IMPL", "native", ""),
    ("LMR.LIFE.MAINT_SLA", "MSI.SERVICES.IMPL", "option", ""),
    ("LMR.LIFE.DOCUMENTATION", "MSI.SERVICES.IMPL", "native", ""),
    ("LMR.LIFE.PROJECT_MGMT", "MSI.SERVICES.IMPL", "native", ""),
    ("LMR.RF.MULTIBAND_SU", "MSI.APX.8000", "native", ""),
    ("LMR.RF.BAND_700", "MSI.ASTRO25.SYSTEM", "native", ""),
    ("LMR.RF.BAND_800", "MSI.ASTRO25.SYSTEM", "native", ""),
    ("LMR.RF.BAND_UHF", "MSI.ASTRO25.SYSTEM", "native", ""),
    ("LMR.RF.BAND_VHF", "MSI.ASTRO25.SYSTEM", "native", ""),
]


def main() -> None:
    l1 = json.loads(L1_PATH.read_text(encoding="utf-8"))
    alias_to_id = {}
    for c in l1["capabilities"]:
        if c.get("alias"):
            alias_to_id[c["alias"]] = c["id"]
        alias_to_id[c["id"]] = c["id"]

    products = [{**p, "vendor_id": "MSI", "source_url": MSI_URL} for p in PRODUCTS]
    product_ids = {p["id"] for p in products}

    mappings = []
    missing_alias = []
    for alias, product_id, level, notes in MAPPINGS:
        if product_id not in product_ids:
            raise SystemExit(f"unknown product {product_id}")
        cid = alias_to_id.get(alias)
        if not cid:
            missing_alias.append(alias)
            continue
        mappings.append(
            {
                "product_id": product_id,
                "capability_id": cid,
                "capability_alias": alias if alias.startswith("LMR.") else None,
                "support_level": level,
                "notes": notes,
                "source_url": MSI_URL,
                "status": "draft",
            }
        )

    # dedupe
    uniq = {}
    for m in mappings:
        key = (m["product_id"], m["capability_id"])
        uniq[key] = m
    mappings = list(uniq.values())

    prod_doc = {
        "schema_version": "1.0",
        "sprint": "S3",
        "vendor_id": "MSI",
        "vendor_name": "Motorola Solutions",
        "counts": {"products": len(products)},
        "products": products,
    }
    map_doc = {
        "schema_version": "1.0",
        "sprint": "S3",
        "vendor_id": "MSI",
        "counts": {
            "mappings": len(mappings),
            "capabilities_mapped": len({m["capability_id"] for m in mappings}),
            "products_used": len({m["product_id"] for m in mappings}),
            "missing_aliases": missing_alias,
        },
        "mappings": mappings,
    }
    OUT_PRODUCTS.write_text(json.dumps(prod_doc, indent=2), encoding="utf-8")
    OUT_MAP.write_text(json.dumps(map_doc, indent=2), encoding="utf-8")
    print(
        f"products={len(products)} mappings={len(mappings)} "
        f"caps={map_doc['counts']['capabilities_mapped']} missing={missing_alias}"
    )


if __name__ == "__main__":
    main()
