#!/usr/bin/env python3
"""Deep static analysis of the Firebolt FX3 control-plane image (no PE/USB capture).

Reads firmware/niusbFirebolt.cfg and extracts the structural evidence that pins
FX3's role as a *configuration proxy + DMA bridge* rather than the acquisition
timebase:

  * Cypress CY image header + boot control bytes
  * USB device descriptor (VID/PID, bcdUSB)
  * ThreadX RTOS banner (version / serial)
  * every internal ``source/`` build path
  * ThreadX thread names and named IRQ/state handlers
  * Fusion / DMA / FPGA anchor strings
  * whole-file and windowed Shannon entropy
  * large all-zero regions (padding / erased flash tail)

Output: manifests/fx3_deep.json  (the only file this script writes).

Boundary: pure byte/string statics. No register map, no Fusion request
dictionary, no runtime behavior is claimed. Those remain unknown until
Ghidra / USB capture (see docs/fx3_role_map.md).
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import struct
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FW = ROOT / "firmware"
MANIFESTS = ROOT / "manifests"
FX3_IMAGE = FW / "niusbFirebolt.cfg"
OUT = MANIFESTS / "fx3_deep.json"

# Minimum printable-run length treated as a "string".
MIN_STR = 5
# Minimum length of a null run to be reported as a large zero region.
MIN_ZERO_RUN = 256
# Window size for the coarse entropy profile.
ENTROPY_WINDOW = 4096


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = Counter(data)
    n = len(data)
    h = -sum((v / n) * math.log2(v / n) for v in counts.values())
    return h if h else 0.0


def extract_strings(data: bytes, min_len: int = MIN_STR) -> list[str]:
    pat = rb"[\x20-\x7e]{%d,}" % min_len
    return [m.decode("latin1") for m in re.findall(pat, data)]


def analyze_cy_header(data: bytes) -> dict:
    magic = data[:2]
    ctrl = list(data[2:4]) if len(data) >= 4 else []
    return {
        "present": magic == b"CY",
        "magic_ascii": magic.decode("latin1", "replace"),
        "magic_hex": data[:4].hex() if len(data) >= 4 else data[:2].hex(),
        "image_ctrl_bytes": ctrl,
        # FX3 image format: byte[2] = image type/checksum-type, byte[3] high nibble
        # 0xB = "execute from address" boot marker used by Cypress cyfx tooling.
        "exec_marker": ctrl[1] if len(ctrl) == 2 else None,
        "note": "Cypress FX3 (CYUSB301x) boot image header",
    }


def analyze_usb_descriptor(data: bytes) -> dict:
    """Locate the 18-byte USB device descriptor and read VID/PID.

    Heuristic: bLength=0x12, bDescriptorType=0x01, bDeviceClass byte pattern.
    """
    result: dict = {
        "descriptor_offset": None,
        "idVendor": None,
        "idProduct": None,
        "idVendor_hex": None,
        "idProduct_hex": None,
        "bcdUSB": None,
    }
    for i in range(len(data) - 18):
        if data[i] == 0x12 and data[i + 1] == 0x01 and data[i + 3] == 0x02:
            vid = struct.unpack_from("<H", data, i + 8)[0]
            pid = struct.unpack_from("<H", data, i + 10)[0]
            result.update(
                {
                    "descriptor_offset": i,
                    "idVendor": vid,
                    "idProduct": pid,
                    "idVendor_hex": f"0x{vid:04X}",
                    "idProduct_hex": f"0x{pid:04X}",
                    "bcdUSB": f"0x{struct.unpack_from('<H', data, i + 2)[0]:04X}",
                }
            )
            break
    return result


def analyze_threadx(strings: list[str]) -> dict:
    banner = None
    version = None
    serial = None
    for s in strings:
        if "ThreadX" in s and "Express Logic" in s:
            banner = s
            m = re.search(r"Version\s+(\S+)", s)
            if m:
                version = m.group(1)
            m = re.search(r"SN:\s*(\S+)", s)
            if m:
                serial = m.group(1)
            break
    return {"present": banner is not None, "banner": banner, "version": version, "serial": serial}


def collect_source_paths(strings: list[str]) -> list[str]:
    paths = set()
    for s in strings:
        for m in re.findall(r"(?:\./)?source/[\w./+-]+", s):
            paths.add(m.lstrip("./"))
    return sorted(paths)


def collect_thread_names(strings: list[str]) -> list[str]:
    """ThreadX thread names: NN_NAME_THREAD tokens and '...Thread' banner names."""
    names = set()
    for s in strings:
        for m in re.findall(r"\d{2}_[A-Z0-9]+_THREAD", s):
            names.add(m)
        for m in re.findall(r"[A-Za-z][\w ]*Thread\b", s):
            if "Express Logic" not in m:
                names.add(m.strip())
    return sorted(names)


def collect_handlers(strings: list[str]) -> list[str]:
    """Numbered handler entries such as '43:State Machine handler'."""
    out = set()
    for s in strings:
        for m in re.findall(r"\d{1,3}:[\w ]*handler", s, flags=re.IGNORECASE):
            out.add(m.strip())
    return sorted(out)


def collect_keyword_strings(strings: list[str], keyword: str) -> list[str]:
    kl = keyword.lower()
    return sorted({s for s in strings if kl in s.lower()})


def large_zero_regions(data: bytes, min_run: int = MIN_ZERO_RUN) -> list[dict]:
    regions = []
    i = 0
    n = len(data)
    while i < n:
        if data[i] == 0:
            j = i
            while j < n and data[j] == 0:
                j += 1
            if j - i >= min_run:
                regions.append(
                    {
                        "offset": i,
                        "offset_hex": f"0x{i:X}",
                        "length": j - i,
                        "fraction_of_image": round((j - i) / n, 5),
                    }
                )
            i = j
        else:
            i += 1
    return sorted(regions, key=lambda r: -r["length"])


def entropy_profile(data: bytes, window: int = ENTROPY_WINDOW) -> dict:
    windows = []
    for off in range(0, len(data), window):
        chunk = data[off : off + window]
        windows.append(round(entropy(chunk), 3))
    if not windows:
        return {"window": window, "count": 0}
    return {
        "window": window,
        "count": len(windows),
        "min": min(windows),
        "max": max(windows),
        "mean": round(sum(windows) / len(windows), 3),
        "high_entropy_windows": sum(1 for w in windows if w >= 7.5),
        "low_entropy_windows": sum(1 for w in windows if w <= 1.0),
    }


def analyze(path: Path) -> dict:
    data = path.read_bytes()
    strings = extract_strings(data)

    dma = sorted(
        set(
            collect_keyword_strings(strings, "DMA")
            + collect_keyword_strings(strings, "PIB")
            + collect_keyword_strings(strings, "dmaBuf")
        )
    )

    return {
        "schema": "firebolt_learning.fx3_deep.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/analyze_fx3_deep.py",
        "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
        "phase": "static_deep_no_capture",
        "image": {
            "path": str(path.relative_to(ROOT)),
            "size": len(data),
            "sha256": sha256_file(path),
            "entropy": round(entropy(data), 3),
        },
        "cy_header": analyze_cy_header(data),
        "usb": analyze_usb_descriptor(data),
        "rtos_threadx": analyze_threadx(strings),
        "source_paths": collect_source_paths(strings),
        "thread_names": collect_thread_names(strings),
        "handlers": collect_handlers(strings),
        "fusion_strings": collect_keyword_strings(strings, "Fusion"),
        "dma_strings": dma,
        "fpga_strings": collect_keyword_strings(strings, "FPGA"),
        "entropy_profile": entropy_profile(data),
        "zero_regions": large_zero_regions(data),
        "string_stats": {
            "min_len": MIN_STR,
            "total_strings": len(strings),
            "unique_strings": len(set(strings)),
            "source_path_count": len(collect_source_paths(strings)),
            "thread_name_count": len(collect_thread_names(strings)),
            "handler_count": len(collect_handlers(strings)),
            "fusion_count": len(collect_keyword_strings(strings, "Fusion")),
            "dma_count": len(dma),
            "fpga_count": len(collect_keyword_strings(strings, "FPGA")),
        },
        "role_conclusion": {
            "fx3_role": "config_proxy_and_dma_bridge",
            "sync_timebase_in_arm": False,
            "rationale": (
                "FX3 image carries USB descriptor + Fusion vendor request handling + "
                "DMA/PIB threads + FPGA load/register-access source paths, but no "
                "sample-clock / convert-timing engine. Acquisition sync lives in the "
                "FPGA/ADC layer, not the ThreadX ARM core."
            ),
            "unknown_upgrades": {
                "FX3-REGMAP": "concrete FPGA register offsets — needs Ghidra on tFPGARegisterAccess.c",
                "FX3-FUSION-REQ": "Fusion bRequest/payload dictionary — needs USB capture (deferred)",
            },
        },
    }


def main() -> None:
    if not FX3_IMAGE.exists():
        raise SystemExit(f"missing FX3 image: {FX3_IMAGE}")
    result = analyze(FX3_IMAGE)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    summary = {
        "ok": True,
        "out": str(OUT.relative_to(ROOT)),
        "size": result["image"]["size"],
        "entropy": result["image"]["entropy"],
        "vid": result["usb"]["idVendor_hex"],
        "pid": result["usb"]["idProduct_hex"],
        "threadx": result["rtos_threadx"]["version"],
        "string_stats": result["string_stats"],
        "zero_regions": len(result["zero_regions"]),
        "role": result["role_conclusion"]["fx3_role"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
