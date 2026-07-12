"""Generate Sprint-1 L1 capability catalog (LMR deep + PSERS stubs)."""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).with_name("l1_capabilities.json")


def cap(
    stack: str,
    domain: str,
    code: str,
    name: str,
    definition: str,
    missions: list[str],
    *,
    alias: str | None = None,
    status: str = "draft",
    vertical: str = "LMR",
    p25_ref: str | None = None,
) -> dict:
    full_id = f"PSERS.{stack}.{domain}.{code}"
    row = {
        "id": full_id,
        "alias": alias or (f"LMR.{domain}.{code}" if vertical == "LMR" and stack == "INFRA" and domain not in ("MCX",) else None),
        "name": name,
        "definition": definition,
        "stack_class": stack,
        "domain": domain,
        "mission_tags": missions,
        "status": status,
        "vertical": vertical,
        "p25_ref": p25_ref,
    }
    return row


def lmr_caps() -> list[dict]:
    c: list[dict] = []

    # STD — Standards & access modes (~12)
    std = [
        ("P25_PHASE1", "P25 Phase 1 FDMA", "Support Project 25 Phase 1 FDMA common air interface operation.", ["respond", "coordinate"], "2.1.1.1"),
        ("P25_PHASE2", "P25 Phase 2 TDMA", "Support Project 25 Phase 2 TDMA common air interface operation.", ["respond", "coordinate"], "2.1.1.2"),
        ("DUAL_MODE_FDMA_TDMA", "Dual-mode FDMA/TDMA", "Operate in both P25 Phase 1 and Phase 2 modes as required.", ["respond"], None),
        ("CONVENTIONAL_OPS", "Conventional operation", "Support conventional (non-trunked) P25/analog operation.", ["respond"], None),
        ("TRUNKED_OPS", "Trunked operation", "Support trunked system control and voice/data services.", ["respond", "dispatch"], None),
        ("ANALOG_INTEROP", "Analog FM interoperability", "Support analog FM on designated interoperability channels.", ["coordinate"], None),
        ("DMR_TIER2", "DMR Tier II conventional", "Support DMR Tier II where specified for campus/utility use.", ["respond"], None),
        ("DMR_TIER3", "DMR Tier III trunked", "Support DMR Tier III trunking where specified.", ["respond"], None),
        ("P25_CAP", "P25 CAP compliance", "Equipment tested under P25 CAP where required in the RFP.", ["after_action"], None),
        ("TIA102_SUITE", "TIA-102 standards suite", "Conform to applicable TIA-102 documents for claimed features.", ["respond"], None),
        ("COMMON_CHANNEL_OPS", "Common channel operation", "Support P25 common/interoperability channel operation.", ["coordinate"], "2.1.1.3"),
        ("MIXED_FLEET", "Mixed Phase 1/2 fleet", "Infrastructure supports mixed Phase 1 and Phase 2 subscribers.", ["respond"], None),
    ]
    for code, name, defn, miss, pref in std:
        c.append(cap("INFRA", "STD", code, name, defn, miss, p25_ref=pref))

    # RF — Spectrum & bands (~10)
    for code, name, defn, miss in [
        ("BAND_VHF", "VHF operation", "Operate in VHF public-safety band allocations as licensed.", ["respond"]),
        ("BAND_UHF", "UHF operation", "Operate in UHF public-safety band allocations as licensed.", ["respond"]),
        ("BAND_700", "700 MHz operation", "Operate in 700 MHz public-safety allocations.", ["respond"]),
        ("BAND_800", "800 MHz operation", "Operate in 800 MHz public-safety allocations.", ["respond"]),
        ("BAND_900", "900 MHz operation", "Operate in 900 MHz allocations where licensed.", ["respond"]),
        ("MULTIBAND_SU", "Multiband subscriber", "Subscriber unit operates across multiple LMR bands (e.g. VHF/UHF/7/800).", ["respond", "coordinate"]),
        ("CHANNEL_CAPACITY", "Channel capacity planning", "Provide channel counts meeting stated GoS and growth assumptions.", ["dispatch"]),
        ("FCC_IOP_CHANNELS", "FCC interoperability channels", "Support designated FCC interoperability channels.", ["coordinate"]),
        ("NARROWBAND", "Narrowband compliance", "Meet applicable narrowband channel spacing requirements.", ["respond"]),
        ("FREQUENCY_REUSE", "Frequency reuse design", "Support frequency reuse / simulcast planning assumptions in design.", ["respond"]),
    ]:
        c.append(cap("INFRA", "RF", code, name, defn, miss))

    # CORE (~12)
    for code, name, defn, miss in [
        ("CENTRALIZED_CORE", "Centralized core", "System uses geographically redundant centralized core controllers.", ["dispatch", "coordinate"]),
        ("DISTRIBUTED_CORE", "Distributed core", "System uses distributed architecture where sites can assume core functions.", ["dispatch", "coordinate"]),
        ("GEO_REDUNDANT_CORE", "Geo-redundant core", "Primary and secondary cores at geographically separate locations.", ["coordinate"]),
        ("NO_SPOF", "No single point of failure", "No single failure of control-plane equipment disables system-wide voice.", ["respond", "coordinate"]),
        ("FAILSOFT", "Failsoft / site trunking", "Graceful degradation to site trunking or conventional failsoft on core loss.", ["respond"]),
        ("SITE_TRUNKING", "Site trunking mode", "Continue local trunked operation when wide-area links fail.", ["respond"]),
        ("SYSTEM_WIDE_CALL", "System-wide group call", "Support system-wide group call to all SUs in a trunked system.", ["coordinate"]),
        ("BACKUP_RESTORE", "Backup and restore", "Backup/restore of critical system configuration and databases.", ["after_action"]),
        ("OWNERSHIP_CORE", "Agency-owned core", "Agency owns/operates primary and redundant core equipment where required.", ["after_action"]),
        ("TRANSPARENT_ROAMING", "Transparent site roaming", "Automatic intra-system roaming across sites.", ["respond"]),
        ("FAULT_TOLERANT_CONTROL", "Fault-tolerant system control", "Redundant controllers with no SPOF in control network.", ["coordinate"]),
        ("DYNAMIC_REGROUP", "Dynamic regrouping", "Merge/unmerge talkgroups dynamically for incidents.", ["coordinate", "dispatch"]),
    ]:
        c.append(cap("INFRA", "CORE", code, name, defn, miss))

    # SITE (~14)
    for code, name, defn, miss in [
        ("BASE_REPEATER", "Base station / repeater", "P25-capable base station or repeater at RF sites.", ["respond"]),
        ("COMPARATOR", "Simulcast comparator", "Audio/data comparator for simulcast voting.", ["respond"]),
        ("VOTING_RECEIVER", "Receiver voting", "Voted receive for improved talk-in performance.", ["respond"]),
        ("SIMULCAST_TRUNKED", "Trunked simulcast", "Simulcast transmission across multiple sites for wide-area coverage.", ["respond", "coordinate"]),
        ("MULTICAST", "Multicast / multi-cast sites", "Support multicast site configurations where specified.", ["respond"]),
        ("TTA", "Tower top amplifier", "Tower-top amplifiers to improve uplink sensitivity.", ["respond"]),
        ("ANTENNA_SYSTEM", "Antenna system", "Site antenna systems meeting design gain and pattern assumptions.", ["respond"]),
        ("SITE_ALARMS", "Site environmental alarms", "Monitor site power, HVAC, intrusion, and RF alarms.", ["after_action"]),
        ("RFSS", "RF subsystem (RFSS)", "P25 RF Subsystem as defined in TIA-102.", ["respond"]),
        ("EXPRESS_SINGLE_SITE", "Single-site trunked package", "Factory-packaged single-site trunked system option.", ["respond"]),
        ("SITE_GROUNDING", "Site grounding & lightning", "Grounding/bonding per public-safety site standards (e.g. R56-class).", ["after_action"]),
        ("CHANNEL_BANK", "Site channel equipment", "Sufficient channel equipment for design traffic load.", ["dispatch"]),
        ("RECEIVER_SITE", "Receive-only sites", "Optional receive-only sites for talk-in improvement.", ["respond"]),
        ("SIMULCAST_TIMING", "Simulcast timing/GPS sync", "GPS or equivalent sync for simulcast timing integrity.", ["respond"]),
    ]:
        c.append(cap("INFRA", "SITE", code, name, defn, miss))

    # COV (~12)
    for code, name, defn, miss in [
        ("DAQ_3_4", "DAQ 3.4 delivered audio", "Coverage designed/tested to DAQ 3.4 (or equivalent) where specified.", ["respond"]),
        ("COV_95_AREA", "95% area coverage", "Meet stated percent geographic area coverage objective.", ["respond"]),
        ("COV_95_POP", "Population coverage", "Meet stated population coverage objective.", ["respond"]),
        ("COV_ROADS", "Major road coverage", "Coverage statistics for major roads as specified.", ["respond"]),
        ("MOBILE_ON_STREET", "Mobile on-street coverage", "Mobile radio on-street coverage in service area.", ["respond"]),
        ("PORTABLE_ON_STREET", "Portable on-street coverage", "Portable on-street coverage in defined service area.", ["respond"]),
        ("PORTABLE_IN_BUILDING", "Portable in-building coverage", "In-building portable coverage in designated zones.", ["respond"]),
        ("GOS_1PCT", "Grade of Service ≤1%", "Traffic design for GoS less than or equal to 1% (or RFP value).", ["dispatch"]),
        ("GROWTH_SUBSCRIBERS", "Subscriber growth allowance", "Capacity includes stated annual subscriber growth.", ["dispatch"]),
        ("COVERAGE_GUARANTEE", "Coverage guarantee", "Contractual coverage guarantee with remediation.", ["after_action"]),
        ("COVERAGE_TESTING", "Coverage acceptance testing", "Formal coverage testing with agency witnesses.", ["after_action"]),
        ("COVERAGE_MAPS", "Predictive coverage maps", "Provide design coverage maps with stated assumptions.", ["after_action"]),
    ]:
        c.append(cap("INFRA", "COV", code, name, defn, miss))

    # VOICE (~20)
    voice = [
        ("GROUP_CALL", "Group call", "Talkgroup / group voice call service.", ["respond", "dispatch"]),
        ("PRIVATE_CALL", "Private / individual call", "Unit-to-unit private call.", ["respond"]),
        ("EMERGENCY_ALARM", "Emergency alarm", "Emergency alarm from SU to console/system.", ["respond", "dispatch"]),
        ("EMERGENCY_CALL", "Emergency call", "Emergency voice call with priority handling.", ["respond", "dispatch"]),
        ("PTT_ID", "PTT-ID / talker ID", "Transport talker ID to receiving units/consoles.", ["dispatch", "respond"]),
        ("CALL_ALERT", "Call alert / paging", "Call alert or paging function to a unit.", ["dispatch"]),
        ("PRIORITY_LEVELS", "User/talkgroup priority", "Priority levels for users and talkgroups.", ["dispatch"]),
        ("VOICE_OVER_DATA", "Voice priority over data", "Voice traffic prioritized over data on shared resources.", ["respond"]),
        ("ANNOUNCEMENT_GROUP", "Announcement group call", "Call addressed to an announcement group of talkgroups.", ["coordinate"]),
        ("BROADCAST_CALL", "Broadcast call", "One-way broadcast group call without hang time.", ["coordinate"]),
        ("ALL_CALL", "All call", "All-call to units on channel/system as defined.", ["coordinate"]),
        ("BUSY_LOCKOUT", "Busy channel lockout", "Polite/busy lockout behavior on conventional channels.", ["respond"]),
        ("RADIO_CHECK", "Radio check", "Determine if a specific SU is available on the system.", ["dispatch"]),
        ("UNIT_INHIBIT", "Unit inhibit / de-authorize", "Inhibit or de-authorize a subscriber unit.", ["dispatch"]),
        ("SITE_RESTRICTION", "Site/talkgroup restriction", "Restrict SUs/talkgroups to particular sites or resources.", ["dispatch"]),
        ("SURVEILLANCE_MODE", "Surveillance mode", "Surveillance / silent mode of operation for SUs.", ["respond"]),
        ("HANGTIME", "Repeater hangtime control", "Configurable conventional repeater hangtime.", ["respond"]),
        ("PSTN_INTERCONNECT", "PSTN interconnect", "Telephone interconnect calls (full-duplex where required).", ["dispatch"]),
        ("DTMF_OVERDIAL", "DTMF overdial", "Digital DTMF overdial support for interconnect.", ["dispatch"]),
        ("STATUS_PRIORITY", "Status and message priority", "Prioritized status/predefined messages relative to voice.", ["respond"]),
    ]
    for code, name, defn, miss in voice:
        c.append(cap("INFRA", "VOICE", code, name, defn, miss))

    # DATA (~10)
    for code, name, defn, miss in [
        ("TEXT_MESSAGING", "Text messaging", "Text messages between units/consoles.", ["respond", "dispatch"]),
        ("STATUS_MESSAGING", "Status / predefined messages", "Preprogrammed status or data messages.", ["respond"]),
        ("GPS_AVL", "GPS / AVL location", "Geo-location reporting from subscriber units.", ["locate", "dispatch"]),
        ("MDT_DATA", "Mobile data terminal data", "MDT/host data communications over LMR data services.", ["respond"]),
        ("HOST_DATA_IF", "Fixed host data interface", "Fixed host data interface (Ed/A-class) as applicable.", ["dispatch"]),
        ("DATA_SPEED_MIN", "Minimum data throughput", "Meet minimum data speed requirements where specified.", ["respond"]),
        ("OTAP", "Over-the-air programming", "Remote programming/configuration of subscriber units.", ["after_action"]),
        ("LOCATION_ON_PTT", "Location with PTT", "Location update correlated with PTT/voice activity.", ["locate"]),
        ("DATA_ROAMING", "Data roaming tracking", "Track units for data/OTAR resource management across sites.", ["respond"]),
        ("PACKET_DATA", "Packet data service", "IP/packet data service on the radio system where offered.", ["respond"]),
    ]:
        c.append(cap("INFRA", "DATA", code, name, defn, miss))

    # SEC (~12)
    for code, name, defn, miss in [
        ("AES256", "AES-256 voice encryption", "AES-256 end-to-end voice encryption for talkgroups/units.", ["respond", "coordinate"]),
        ("MULTI_KEY", "Multi-key encryption", "Store and select multiple encryption keys in SU/infrastructure.", ["respond"]),
        ("OTAR", "Over-the-air rekeying", "OTAR key management to fielded subscriber units.", ["respond", "after_action"]),
        ("KMF", "Key management facility", "KMF/KNL infrastructure for key lifecycle.", ["after_action"]),
        ("KVL", "Key fill device / KVL", "Key fill device interface for manual/local keyload.", ["after_action"]),
        ("FIPS", "FIPS cryptographic modules", "FIPS-validated crypto modules where required.", ["after_action"]),
        ("CONTROL_CH_ENC", "Control channel encryption", "Encrypted control channel / link protection as offered.", ["respond"]),
        ("DES_LEGACY", "Legacy DES support", "DES or Encryption Lite only if explicitly required for migration.", ["respond"]),
        ("END_TO_END_CONSOLE", "Console end-to-end encrypt", "Encrypted path including consoles and logging recorders.", ["dispatch"]),
        ("AUTH_SU", "Subscriber authentication", "Authenticate SUs before granting system services.", ["respond"]),
        ("SECURE_NMS", "Secure NMS access", "Authenticated/authorized access to network management.", ["after_action"]),
        ("KEY_COUNT", "Large key capacity", "SU key storage capacity meeting agency policy.", ["respond"]),
    ]:
        c.append(cap("INFRA", "SEC", code, name, defn, miss))

    # IOP (~10)
    for code, name, defn, miss in [
        ("ISSI", "ISSI inter-RFSS interface", "P25 Inter-RF Subsystem Interface for multi-system interconnect.", ["coordinate"]),
        ("CSSI", "CSSI console subsystem interface", "P25 Console Subsystem Interface.", ["dispatch", "coordinate"]),
        ("CONVENTIONAL_GATEWAY", "Conventional gateway", "Interop with conventional systems via gateway/patch.", ["coordinate"]),
        ("MUTUAL_AID_PATCH", "Mutual-aid console patch", "Console-initiated patches across systems/talkgroups.", ["coordinate"]),
        ("AGENCY_ROAMING", "Inter-agency roaming", "Roaming of authorized users across partner systems.", ["coordinate"]),
        ("FIXED_STATION_IF", "Fixed station interface", "Standard fixed station interfaces as applicable.", ["respond"]),
        ("CAI_INTEROP", "CAI interoperability", "Common Air Interface interoperability across compliant vendors.", ["coordinate"]),
        ("VHF_PAGING_IOP", "VHF paging/interop channel", "VHF analog interoperability and/or paging channel support.", ["inform", "coordinate"]),
        ("CAD_INTERFACE", "CAD interface touchpoint", "Interface from radio/console subsystem to CAD (deep CAD is PLAT stub).", ["dispatch"]),
        ("LMR_MCX_IWF_TOUCH", "LMR–MCX interworking touchpoint", "Capability to interwork with MCX via IWF-class bridging (see XCUT stub).", ["coordinate"]),
    ]:
        c.append(cap("INFRA", "IOP", code, name, defn, miss))

    # DISP (~14) — console/recording on radio side
    for code, name, defn, miss in [
        ("CONSOLE_POSITIONS", "Dispatch console positions", "Operator positions for dispatch on the radio system.", ["dispatch"]),
        ("CONSOLE_PATCH", "Console patching", "Patch talkgroups/channels from console.", ["dispatch", "coordinate"]),
        ("INSTANT_RECALL", "Instant recall recorder", "Short-term instant recall of dispatch audio.", ["dispatch"]),
        ("LOGGING_RECORDER", "Logging recorder", "Long-term logging of radio/console audio.", ["after_action"]),
        ("END_TO_END_LOGGING", "Encrypted logging path", "Logging of encrypted calls per agency policy.", ["after_action"]),
        ("CONSOLE_MULTI_SELECT", "Multi-select / simo select", "Monitor/select multiple talkgroups simultaneously.", ["dispatch"]),
        ("CONSOLE_EMERG_DISPLAY", "Emergency display", "Prominent emergency alarm/call display at console.", ["dispatch"]),
        ("CONSOLE_ALIAS", "Unit alias display", "Display unit aliases/IDs at console.", ["dispatch"]),
        ("MDC_OR_CAD_LINK", "MDC/CAD screen pop", "Screen pop or CAD notification on radio events.", ["dispatch"]),
        ("BACKUP_DISPATCH", "Backup dispatch location", "Capability to operate dispatch from alternate site.", ["dispatch", "coordinate"]),
        ("CONSOLE_IP", "IP console architecture", "IP-based console subsystem.", ["dispatch"]),
        ("SUPERVISOR_POSITION", "Supervisor console features", "Supervisor monitoring and control features.", ["dispatch"]),
        ("TONE_SIGNALING", "Tone signaling / alerts", "Generate/receive tone sequences as required.", ["dispatch"]),
        ("RADIO_DISPATCH_WORKFLOW", "Radio-centric dispatch workflow", "Workflow support for radio dispatch independent of full CAD.", ["dispatch"]),
    ]:
        c.append(cap("INFRA", "DISP", code, name, defn, miss))

    # BH (~10)
    for code, name, defn, miss in [
        ("MICROWAVE_BH", "Microwave backhaul", "Microwave links between sites/dispatch.", ["respond"]),
        ("FIBER_BH", "Fiber backhaul", "Fiber connectivity for RF sites and cores.", ["respond"]),
        ("IP_TRANSPORT", "IP transport network", "IP backhaul transporting P25 site/core traffic.", ["respond"]),
        ("PATH_DIVERSITY", "Path diversity", "Diverse routes to avoid single backhaul cut.", ["coordinate"]),
        ("RING_TOPOLOGY", "Ring / protected topology", "Protected ring or equivalent backhaul resilience.", ["coordinate"]),
        ("BH_CAPACITY", "Backhaul capacity sizing", "Bandwidth sized for voice, data, NMS, and growth.", ["respond"]),
        ("BH_NMS_INTEGRATION", "Backhaul in unified NMS", "Backhaul alarms visible in system NMS.", ["after_action"]),
        ("SITE_CONNECTIVITY_SLA", "Site link availability", "Meet stated site connectivity availability targets.", ["respond"]),
        ("LEASED_VS_OWNED", "Owned or leased transport", "Support agency-owned or leased transport models.", ["after_action"]),
        ("SYNC_DISTRIBUTION", "Timing distribution over BH", "Distribute sync/timing as required for simulcast.", ["respond"]),
    ]:
        c.append(cap("INFRA", "BH", code, name, defn, miss))

    # NMS (~10)
    for code, name, defn, miss in [
        ("UNIFIED_NMS", "Unified network management", "Single NMS spanning radio, backhaul, and site alarms.", ["after_action"]),
        ("REALTIME_MONITOR", "Real-time monitoring", "Real-time status of sites, channels, and cores.", ["dispatch", "after_action"]),
        ("REMOTE_CONFIG", "Remote configuration", "Remote configuration of network elements.", ["after_action"]),
        ("SNMP_ALARMS", "SNMP / alarm forwarding", "Standard alarm interfaces to NOC tools.", ["after_action"]),
        ("CONFIG_BACKUP", "Configuration backup", "Automated backup of element configurations.", ["after_action"]),
        ("AUDIT_LOGS", "Management audit logs", "Audit trail of administrative actions.", ["after_action"]),
        ("PERFORMANCE_REPORTS", "Performance reporting", "Traffic/usage/performance reports.", ["after_action"]),
        ("HIERARCHICAL_NMS", "Hierarchical NMS", "Hierarchical managers rolling into enterprise view.", ["after_action"]),
        ("USER_ADMIN", "User & role administration", "Role-based admin of system users/talkgroups.", ["after_action"]),
        ("SOFTWARE_PATCHING", "OS/application patching", "Vendor-supported patching of supplied servers/OS.", ["after_action"]),
    ]:
        c.append(cap("INFRA", "NMS", code, name, defn, miss))

    # SUB (~16)
    for code, name, defn, miss in [
        ("PORTABLE_GENERAL", "Portable subscriber", "Handheld portable radio meeting baseline P25 requirements.", ["respond"]),
        ("MOBILE_GENERAL", "Mobile subscriber", "Vehicle mobile radio meeting baseline requirements.", ["respond"]),
        ("CONTROL_STATION", "Control station", "Desktop/control station radio option.", ["dispatch"]),
        ("TIER_LAW", "Law enforcement tier radio", "Higher-tier portable/mobile for law enforcement feature set.", ["respond"]),
        ("TIER_FIRE", "Fire / XE tier radio", "Firefighter ultra-rugged portable tier.", ["respond"]),
        ("TIER_PUBLIC_SERVICE", "Public service tier radio", "Public works/service tier radio.", ["respond"]),
        ("MULTIBAND_PORTABLE", "Multiband portable", "All-band or multi-band portable option.", ["respond", "coordinate"]),
        ("MULTIBAND_MOBILE", "Multiband mobile", "All-band or multi-band mobile option.", ["respond", "coordinate"]),
        ("ACCESSORIES", "Audio accessories", "Speaker mics, headsets, remote speaker options.", ["respond"]),
        ("VEHICLE_INSTALL", "Vehicle installation kit", "Mounts, cabling, antennas for mobiles.", ["respond"]),
        ("BATTERY_OPTIONS", "Battery options", "Duty-cycle appropriate battery options.", ["respond"]),
        ("PROGRAMMING_TEMPLATES", "Programming templates", "Agency programming templates and codeplugs.", ["after_action"]),
        ("FLEET_MIX", "Mixed fleet tiers", "Support concurrent tiers in one fleet.", ["respond"]),
        ("WIFI_SU", "Wi-Fi capable subscriber", "SU Wi-Fi for OTAP/data where offered.", ["respond"]),
        ("BT_SU", "Bluetooth accessories", "Bluetooth audio accessory support.", ["respond"]),
        ("SENSOR_PORTS", "External sensor/data ports", "Interfaces for peripherals as specified.", ["respond"]),
    ]:
        c.append(cap("INFRA", "SUB", code, name, defn, miss))

    # RUG (~10)
    for code, name, defn, miss in [
        ("MILSTD_810", "MIL-STD-810 ruggedization", "Meet stated MIL-STD-810 methods (shock, vibe, rain, etc.).", ["respond"]),
        ("IP_RATING", "IP dust/water rating", "Meet stated IP rating for portables.", ["respond"]),
        ("XE_FIREFIGHTER", "Firefighter ultra-rugged", "XE/ultra-rugged firefighter form factor and glove UI.", ["respond"]),
        ("LOUD_AUDIO", "High-power / loud audio", "High audio output for noisy environments.", ["respond"]),
        ("GLOVE_UI", "Glove-friendly UI", "Controls operable with gloved hands.", ["respond"]),
        ("DISPLAY_NIGHT", "Day/night display", "Readable display in bright/low light.", ["respond"]),
        ("TOP_DISPLAY", "Top/secondary display", "Secondary display for channel/status.", ["respond"]),
        ("EMERG_BUTTON", "Dedicated emergency control", "Dedicated emergency button meeting ergonomic reqs.", ["respond"]),
        ("TEMP_RANGE", "Operating temperature range", "Meet environmental temperature specifications.", ["respond"]),
        ("HAZLOC", "Hazardous location rating", "Intrinsically safe / hazloc options where required.", ["respond"]),
    ]:
        c.append(cap("INFRA", "RUG", code, name, defn, miss))

    # BB (~8)
    for code, name, defn, miss in [
        ("LTE_PTT_BRIDGE", "LMR–LTE PTT bridge", "Broadband PTT bridging to LMR talkgroups (SmartConnect-class).", ["respond", "coordinate"]),
        ("FIRSTNET_READY", "FirstNet / public safety LTE ready", "Operate with public-safety LTE services where offered.", ["respond"]),
        ("WIFI_CONNECTIVITY", "Wi-Fi connectivity on SU", "SU connects to Wi-Fi for apps/OTAP.", ["respond"]),
        ("MODEM_TETHER", "Data modem tethering", "Tether to approved routers/modems for data.", ["respond"]),
        ("SMART_LOCATE", "Broadband-enhanced location", "Enhanced location via broadband path when available.", ["locate"]),
        ("SMART_PROGRAMMING", "Broadband OTAP/programming", "Programming via broadband path.", ["after_action"]),
        ("CONVERGED_DEVICE", "Converged LMR+broadband device", "Single device hosting LMR and broadband applications.", ["respond"]),
        ("PTT_APP_INTEROP", "Broadband PTT app interop", "Interop with approved broadband PTT clients.", ["coordinate"]),
    ]:
        c.append(cap("INFRA", "BB", code, name, defn, miss))

    # LIFE (~12)
    for code, name, defn, miss in [
        ("TURNKEY_IMPL", "Turnkey implementation", "Design, furnish, install, test, and commission as turnkey.", ["after_action"]),
        ("CUTOVER_PLAN", "Cutover / migration plan", "Phased cutover preserving operations on legacy systems.", ["coordinate"]),
        ("ACCEPTANCE_TEST", "Acceptance testing", "Formal ATP with agency sign-off.", ["after_action"]),
        ("TRAINING", "User & tech training", "Training for end users, dispatchers, and technicians.", ["after_action"]),
        ("WARRANTY", "Warranty terms", "Meet stated warranty duration and scope.", ["after_action"]),
        ("SPARES", "Spare parts kit", "Recommended spares provisioning.", ["after_action"]),
        ("MAINT_SLA", "Maintenance SLA", "Ongoing maintenance service levels.", ["after_action"]),
        ("DOCUMENTATION", "As-built documentation", "As-built drawings, configs, and manuals.", ["after_action"]),
        ("PROJECT_MGMT", "Project management", "Dedicated PM and schedule reporting.", ["after_action"]),
        ("FCC_LICENSING_SUPPORT", "Licensing support", "Support for frequency coordination/licensing tasks.", ["after_action"]),
        ("COVERAGE_REMEDIATION", "Coverage remediation", "Remediate coverage shortfalls at no added cost if guaranteed.", ["after_action"]),
        ("LIFECYCLE_OBSOLESCENCE", "Obsolescence / roadmap notice", "Vendor notice of product obsolescence and migration path.", ["after_action"]),
    ]:
        c.append(cap("INFRA", "LIFE", code, name, defn, miss))

    return c


def stubs() -> list[dict]:
    """Non-LMR stubs for extensibility (~30)."""
    items = [
        ("PLAT", "NG911", "CALL_HANDLING", "NG911 call handling", "Receive and process emergency calls in NG911/i3 environment.", ["call_take"], "NG911"),
        ("PLAT", "NG911", "EIDO_EXCHANGE", "EIDO incident exchange", "Exchange Emergency Incident Data Objects with authorized FEs.", ["call_take", "dispatch", "coordinate"], "NG911"),
        ("PLAT", "NG911", "TEXT_TO_911", "Text-to-911", "Support SMS/text emergency contacts where deployed.", ["call_take"], "NG911"),
        ("PLAT", "NG911", "MULTIMEDIA", "Multimedia to PSAP", "Accept multimedia (e.g. images/video) per NG911 capabilities.", ["call_take"], "NG911"),
        ("PLAT", "NG911", "ALI_AML", "Location for callers", "Acquire caller location (ALI/AML/civic/geodetic).", ["locate", "call_take"], "NG911"),
        ("PLAT", "CAD", "INCIDENT_CREATE", "CAD incident creation", "Create and update incidents in Computer-Aided Dispatch.", ["dispatch"], "CAD"),
        ("PLAT", "CAD", "UNIT_STATUS", "CAD unit status", "Track unit status and assignments in CAD.", ["dispatch", "respond"], "CAD"),
        ("PLAT", "CAD", "RECOMMENDATION", "CAD unit recommendation", "Recommend units based on location/type/priority.", ["dispatch"], "CAD"),
        ("PLAT", "CAD", "CAD_TO_CAD", "CAD-to-CAD exchange", "Exchange incident/unit data with partner CAD systems.", ["coordinate"], "CAD"),
        ("PLAT", "CAD", "AVL_DISPLAY", "CAD AVL map display", "Display unit AVL on CAD maps.", ["locate", "dispatch"], "CAD"),
        ("PLAT", "RMS", "INCIDENT_REPORT", "RMS incident reporting", "Records management for incident reports and evidence metadata.", ["after_action"], "RMS"),
        ("PLAT", "GIS", "COMMON_MAP", "Common operational map", "Shared GIS/map layers for dispatch and field.", ["locate", "coordinate"], "GIS"),
        ("PLAT", "VMS", "VIDEO_MANAGEMENT", "Video management system", "Manage and retrieve agency video streams/recordings.", ["detect", "coordinate"], "VIDEO"),
        ("APP", "FIELD", "MOBILE_CAD", "Field mobile CAD client", "Mobile application for field CAD workflow.", ["respond", "dispatch"], "FIELD"),
        ("APP", "FIELD", "MDT", "Mobile data terminal app", "In-vehicle MDT application suite.", ["respond"], "FIELD"),
        ("APP", "ALERT", "MASS_NOTIFY", "Mass notification", "Outbound public/employee mass notification.", ["inform"], "ALERT"),
        ("APP", "ALERT", "IPAWS", "IPAWS alerting", "Originate/relay IPAWS/CAP alerts.", ["inform"], "ALERT"),
        ("APP", "EOC", "SIT_AWARENESS", "EOC situational awareness", "EOC common operating picture / sitrep tools.", ["coordinate"], "EOC"),
        ("SENS", "VIDEO", "FIXED_CCTV", "Fixed CCTV camera", "Fixed camera sensor contributing video observations.", ["detect"], "VIDEO"),
        ("SENS", "VIDEO", "LIVE_SHARE", "Live video share to ops", "Share live video into CAD/EOC/console workflows.", ["coordinate", "detect"], "VIDEO"),
        ("SENS", "VIDEO", "BODYWORN", "Body-worn camera", "Body-worn camera capture and evidence workflow.", ["respond", "after_action"], "VIDEO"),
        ("SENS", "UAS", "DISPATCHABLE_AIRCRAFT", "Dispatchable UAS/drone", "Drone as a dispatchable aerial sensor/unit.", ["detect", "respond"], "UAS"),
        ("SENS", "IOT", "GUNSHOT", "Gunshot detection", "Acoustic gunshot detection feeding incidents.", ["detect"], "IOT"),
        ("SENS", "IOT", "ALPR", "Automated license plate reader", "ALPR reads as observations linked to incidents.", ["detect", "locate"], "IOT"),
        ("SENS", "IOT", "ENVIRONMENTAL", "Environmental smart-city sensor", "Environmental/IoT sensors enriching situational awareness.", ["detect"], "IOT"),
        ("INFRA", "MCX", "MCPTT", "MCPTT group voice", "3GPP Mission-Critical Push-to-Talk group voice.", ["respond", "coordinate"], "MCX"),
        ("INFRA", "MCX", "MCVIDEO", "MCVideo", "3GPP Mission-Critical Video service.", ["respond", "coordinate"], "MCX"),
        ("INFRA", "MCX", "MCDATA", "MCData", "3GPP Mission-Critical Data service.", ["respond"], "MCX"),
        ("INFRA", "MCX", "MCPTT_EMERG", "MCPTT emergency calling", "MCX emergency calling / priority preemption behaviors.", ["respond"], "MCX"),
        ("XCUT", "IOP", "LMR_MCX_IWF", "LMR–MCX Interworking Function", "Interworking function bridging LMR and MCX domains.", ["coordinate"], "IOP"),
        ("XCUT", "SEC", "ENTERPRISE_IAM", "Enterprise identity for PS apps", "SSO/IAM across CAD/mobile/command applications.", ["after_action"], "SEC"),
        ("XCUT", "LOC", "INDOOR_LOCATION", "Indoor location services", "Indoor caller/unit location beyond outdoor GNSS.", ["locate"], "LOC"),
    ]
    out = []
    for stack, domain, code, name, defn, miss, vertical in items:
        out.append(
            cap(
                stack,
                domain,
                code,
                name,
                defn,
                miss,
                alias=None,
                status="stub",
                vertical=vertical,
            )
        )
    return out


def main() -> None:
    capabilities = lmr_caps() + stubs()
    # dedupe by id
    seen: set[str] = set()
    uniq = []
    for row in capabilities:
        if row["id"] in seen:
            continue
        seen.add(row["id"])
        uniq.append(row)

    lmr = [x for x in uniq if x["status"] != "stub"]
    stub = [x for x in uniq if x["status"] == "stub"]
    doc = {
        "schema_version": "1.0",
        "root": "PSERS",
        "sprint": "S1",
        "generated_by": "ontology/generate_l1.py",
        "counts": {"total": len(uniq), "lmr_draft": len(lmr), "stubs": len(stub)},
        "capabilities": uniq,
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"wrote {OUT} total={len(uniq)} lmr={len(lmr)} stubs={len(stub)}")


if __name__ == "__main__":
    main()
