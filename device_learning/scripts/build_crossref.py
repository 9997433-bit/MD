#!/usr/bin/env python3
"""Build cross-layer identifier cross-reference index."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from catalogs.catalog_arch import ENTRIES as ARCH
from catalogs.catalog_bit import ENTRIES as BIT
from catalogs.catalog_hw import ENTRIES as HW
from catalogs.catalog_ref import ENTRIES as REF
from catalogs.catalog_signal import ENTRIES as SIG
from catalogs.catalog_usb import ENTRIES as USB


def main() -> None:
    all_e = HW + BIT + SIG + USB + REF + ARCH
    by_layer: dict[str, list[str]] = {}
    for e in all_e:
        layer = e["layer"].lower() if e["layer"] not in ("FW", "PROTO", "DRV") else "usb"
        by_layer.setdefault(layer, []).append(e["identifier"])

    themes = {
        "usb_path": ["HW-003-USB-CONTROLLER", "REF-USB-SLAVE-FIFO-SLRD", "ARCH-002-DATA-PATH", "PROTO-EP-BULK-IN"],
        "adc_path": ["HW-005-ADC-PRIMARY", "REF-ADC-SPI-DOUT", "SIG-003-PATH-ADC", "NODE-ADC"],
        "fpga_config": ["BIT-IDCODE", "BIT-CMD-SEQUENCE", "ARCH-003-CONFIG-CHAIN", "ARCH-015-BIT-LOAD"],
        "relay_path": ["HW-008-RELAY-ARRAY", "SIG-002-RELAY-MATRIX", "BRG-013", "ARCH-013-RELAY-CTRL"],
        "eeprom_boot": ["FW-EEPROM-IMAGE", "FW-EEPROM-LAYOUT-REF", "ARCH-004-USB-BOOT", "REF-EEPROM-I2C-SCL"],
    }
    pins = json.loads((ROOT / "manifests" / "pin_hypothesis.json").read_text(encoding="utf-8"))
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "layer_counts": {k: len(v) for k, v in by_layer.items()},
        "themes": themes,
        "pin_bridges": [b["id"] for b in pins.get("bridges", [])],
        "total_identifiers": len(all_e),
    }
    out = ROOT / "manifests" / "crossref_index.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result["layer_counts"], indent=2))


if __name__ == "__main__":
    main()
