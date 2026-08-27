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
from catalogs.catalog_exp import ENTRIES as EXP
from catalogs.catalog_hw import ENTRIES as HW
from catalogs.catalog_learn import ENTRIES as LEARN
from catalogs.catalog_ref import ENTRIES as REF
from catalogs.catalog_signal import ENTRIES as SIG
from catalogs.catalog_usb import ENTRIES as USB

ALL = HW + BIT + SIG + USB + REF + ARCH + LEARN + EXP


def main() -> None:
    by_layer: dict[str, list[str]] = {}
    for e in ALL:
        layer = e["layer"].lower() if e["layer"] not in ("FW", "PROTO", "DRV") else "usb"
        by_layer.setdefault(layer, []).append(e["identifier"])

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "layer_counts": {k: len(v) for k, v in by_layer.items()},
        "total_identifiers": len(ALL),
        "themes": {
            "usb_path": ["HW-003-USB-CONTROLLER", "REF-USB-SLAVE-FIFO-SLRD", "ARCH-002-DATA-PATH"],
            "adc_path": ["HW-005-ADC-PRIMARY", "REF-ADC-SPI-DOUT", "SIG-003-PATH-ADC"],
            "fpga_config": ["BIT-IDCODE", "BIT-CMD-SEQUENCE", "ARCH-015-BIT-LOAD"],
            "eeprom_boot": ["FW-EEPROM-IMAGE", "FW-EEPROM-LAYOUT-REF", "EXP-001-EEPROM-DUMP"],
        },
    }
    out = ROOT / "manifests" / "crossref_index.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result["layer_counts"], indent=2))


if __name__ == "__main__":
    main()
