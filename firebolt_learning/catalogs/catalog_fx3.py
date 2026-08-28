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
