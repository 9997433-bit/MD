#!/usr/bin/env python3
"""L4 prep: FT600 D3XX minimal scaffold (no hardware required to import-check)."""
from __future__ import annotations

import argparse
import sys


def main() -> int:
    ap = argparse.ArgumentParser(description="FT600 enum/read scaffold (needs FTD3XX)")
    ap.add_argument("--list", action="store_true", help="list devices")
    ap.add_argument("--read", type=int, default=0, help="read N bytes from pipe 0x82")
    args = ap.parse_args()

    try:
        import FTD3XX  # type: ignore
    except Exception:
        print("FTD3XX not installed. Install FTDI D3XX / PyD3XX first.", file=sys.stderr)
        print("Prep checklist: udev 0403:601e, SuperSpeed port, external power first.", file=sys.stderr)
        return 2

    # Placeholder API surface — adjust to installed binding (FTD3XX vs PyD3XX).
    print("FTD3XX import OK — implement enum/read against local binding.")
    if args.list:
        print("(list devices here)")
    if args.read:
        print(f"(read {args.read} bytes from 0x82 here)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
