"""FX3-* : Marengo/Firebolt MCU 固件控制面角色（阶段 D，不抓包）。"""
from __future__ import annotations

from typing import Any

FX3_ENTRIES: list[tuple[str, str, str, str, str]] = [
    (
        "FX3-IMG-CY-MAGIC",
        "Image starts with Cypress CY header + 0xB0 exec marker",
        "confirmed",
        "firmware_bytes",
        "niusbFirebolt.cfg offset 0: 43 59 1c b0",
    ),
    (
        "FX3-USB-VIDPID",
        "USB VID 0x3923 PID 0x7B44",
        "confirmed",
        "firmware_device_descriptor",
        "Matches Firebolt / USB-6453 community reports",
    ),
    (
        "FX3-RTOS-THREADX",
        "ThreadX ARM9 G5.1.5.1",
        "confirmed",
        "firmware_string",
        "Express Logic copyright string",
    ),
    (
        "FX3-SRC-NIMARENGO",
        "Internal tree nimarengoCore / nimarengoSrc",
        "confirmed",
        "firmware_string",
        "Marengo platform naming",
    ),
    (
        "FX3-FPGA-LOAD",
        "startup/tFPGA.c loads/configures FPGA",
        "confirmed",
        "firmware_string",
        "Role: configuration agent",
    ),
    (
        "FX3-FPGA-REGACC",
        "tFPGARegisterAccess.c pokes FPGA registers",
        "confirmed",
        "firmware_string",
        "Register map body unknown without RE/capture",
    ),
    (
        "FX3-FUSION",
        "Fusion vendor device request path present",
        "confirmed",
        "firmware_string",
        "tFusionManager / tFusionVendorDeviceRequest.h",
    ),
    (
        "FX3-DMA",
        "DMA manager + DMA/PIB threads",
        "confirmed",
        "firmware_string",
        "01_DMA_THREAD / 03_PIB_THREAD / tDMAManager.c",
    ),
    (
        "FX3-STATE-MACHINE",
        "State Machine handler thread name",
        "hypothesis",
        "firmware_string",
        "May be device/USB state, not AI sample FSM",
    ),
    (
        "FX3-COUNTER-MON",
        "Counter Data Monitor handler",
        "candidate",
        "firmware_string",
        "Likely ties to 4 counters; not proven as AI clock",
    ),
    (
        "FX3-REGMAP",
        "Concrete FPGA register offsets",
        "unknown",
        "needs_ghidra_or_capture",
        "OMISSIONS",
    ),
    (
        "FX3-FUSION-REQ",
        "Fusion bRequest / payload dictionary",
        "unknown",
        "needs_usb_capture",
        "Explicitly deferred this phase",
    ),
    (
        "FX3-ROLE-SUMMARY",
        "FX3 = config proxy + DMA bridge; not sync timebase",
        "confirmed",
        "arch_synthesis",
        "Synthesized from strings + SPEC sync layer",
    ),
    (
        "FX3-USB-IF-VENDOR",
        "Single interface class 255 (vendor-specific)",
        "confirmed",
        "firmware_config_descriptor",
        "fx3_static_re.json; aligns with Fusion control plane",
    ),
    (
        "FX3-USB-EP-TOPOLOGY",
        "16 endpoints: 15 bulk + 1 interrupt IN (0x82)",
        "confirmed",
        "firmware_config_descriptor",
        "Many bulk EPs consistent with multi-stream DMA / Signal Stream hypothesis",
    ),
    (
        "FX3-USB-DESC-USB2-VIEW",
        "Embedded descriptors are USB2-coded (bcdUSB 0x0210, maxpkt 64)",
        "confirmed",
        "firmware_config_descriptor",
        "Do not deny product USB-C/SS; only asserts what this .cfg embeds",
    ),
    (
        "FX3-LOAD-BASE-SYSMEM",
        "String VA addend 0x3FFD6000 maps into FX3 SYSMEM",
        "candidate",
        "pointer_heuristic",
        "tFPGARegisterAccess.c file 0x4624C -> VA 0x4001C24C; aids future Ghidra load",
    ),
    (
        "FX3-UIB-BASE",
        "USB UIB MMIO literals at 0xE0030000 / 0xE0033000",
        "confirmed",
        "firmware_mmio_literals",
        "Highest-frequency E00* immediates; USB engine",
    ),
    (
        "FX3-GCTL-BASE",
        "GCTL MMIO literals at 0xE0050000 / 0xE0051000",
        "confirmed",
        "firmware_mmio_literals",
        "Clock/power/id controller region",
    ),
    (
        "FX3-PIB-BASE",
        "PIB/GPIF MMIO base 0xE0010000 present",
        "confirmed",
        "firmware_mmio_literals",
        "On-chip bridge toward FPGA GPIF-II",
    ),
    (
        "FX3-PIB-SOCKET-STRIDE",
        "PIB socket register stride = 16 bytes (index<<4)",
        "confirmed",
        "arm_disassembly",
        "VA 0x400115F8: r3=0xE0010000+(index<<4); see fx3_mmio_map.json",
    ),
    (
        "FX3-GPIF-FPGA-BRIDGE",
        "FPGA reached via PIB/GPIF sockets, not via ARM sample-clock engine",
        "confirmed",
        "arch_synthesis",
        "Reinforces FX3-ROLE-SUMMARY; fabric regmap still unknown",
    ),
    (
        "FX3-PIB-CFG-BASE",
        "Writes observed at 0xE0011000 (public SDK reserved gap)",
        "candidate",
        "arm_disassembly_sdk_gap",
        "Demoted: not a named pib_regs.h block; see FX3-PIB-E0011000-GAP",
    ),
    (
        "FX3-PIB-CFG-STORES",
        "Init func stores many offsets relative to 0xE0011000 base",
        "candidate",
        "arm_disassembly_sdk_gap",
        "Stores confirmed; field names unknown (reserved region)",
    ),
    (
        "FX3-SUBSYSTEM-TAGS",
        "Tags Op/Fpga/Fusion/Trace near Main Thread strings",
        "candidate",
        "firmware_string_table",
        "Possible log/state enums; not proven AI sample FSM",
    ),
    (
        "FX3-GPIF-CFG-OBJECT",
        "Config object field layout +0x00..+0x18 at VA 0x400113D0",
        "candidate",
        "arm_disassembly",
        "Descriptor/walker — not channel sample table",
    ),
    (
        "FX3-ACCESS-PATH-SHAPE",
        "Host/Fusion→FX3→PIB→GPIF→FPGA path shape recovered",
        "confirmed",
        "arch_synthesis",
        "Does not include fabric regmap or Fusion field dictionary",
    ),
    (
        "FX3-PIB-SDK-CROSSREF",
        "Firmware literals match Cypress PIB/GPIF/socket map",
        "confirmed",
        "sdk_crossref",
        "0xE0010000/4000/8000 present; see fx3_pib_crossref.json",
    ),
    (
        "FX3-GPIF-CONFIG-LIT",
        "GPIF_CONFIG literal 0xE0014000 present",
        "confirmed",
        "firmware_mmio_literals",
        "Public CY_U3P_PIB_GPIF_CONFIG_ADDRESS",
    ),
    (
        "FX3-SOCK-BASE-LIT",
        "PIB socket array base 0xE0018000 present",
        "confirmed",
        "firmware_mmio_literals",
        "Official stride n*0x80; 32 sockets",
    ),
    (
        "FX3-SOCK-STRIDE-OFFICIAL",
        "Official DMA socket stride is 128 bytes at 0xE0018000",
        "confirmed",
        "sdk_crossref",
        "Distinct from observed <<4 pattern at 0xE0010000",
    ),
    (
        "FX3-PIB-E0011000-GAP",
        "0xE0011000 is in public rsrvd0 gap — unnamed",
        "candidate",
        "sdk_crossref",
        "Prior 'PIB cfg base' naming demoted; writes exist but no SDK field names",
    ),
    (
        "FX3-PP-MMIO-WINDOW",
        "PP_MMIO_ADDR/DATA (0xE0017E3C/40) not absolute in image",
        "unknown",
        "sdk_crossref_absent_literal",
        "Likely fabric window; access path unresolved",
    ),
]


def build_entries() -> list[dict[str, Any]]:
    return [
        {
            "identifier": i,
            "module": "fx3",
            "source_identifier": t,
            "status": s,
            "boundary": b,
            "note": n,
        }
        for i, t, s, b, n in FX3_ENTRIES
    ]


def entry_ids() -> list[str]:
    return [e[0] for e in FX3_ENTRIES]
