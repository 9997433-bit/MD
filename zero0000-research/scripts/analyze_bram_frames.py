#!/usr/bin/env python3
"""
7 系列 FDRI 逐帧非零分析 + BRAM 内容区候选边界（无 Vivado）。

依据 UG470：全器件 FDRI 先写 block type 0（CLB/IO/CLK），再写 block type 1（BRAM 内容）。
本板为单次 FDRI 自增，无法从包头直接读出 blk 切换点；因此用「后半段密度塌陷」
估计 BRAM 内容起点，并统计该区内非零字节——用于加强「无大规模 BRAM ROM 初值」
（P2.5 / 软核）的可复现证据。

精确列级映射仍需器件 frame map（Vivado；公开 **prjxray-db 无 xc7k160t**，见 `prjxray_K160T帧图可得性.md`）→ 边界保持 🔶。

用法：
  python3 analyze_bram_frames.py [/path/to/s2056.bin]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_BIN = HERE.parent / "assets" / "firmware" / "20230825_s2056.bin"
DEFAULT_MCS = HERE.parent / "assets" / "firmware" / "20230825_s2056.mcs"
WORDS_PER_FRAME = 101
UG470_K160T_BITS = 53_540_576  # UG470 device table


def load_bin(path: Path) -> bytes:
    if path.suffix.lower() == ".mcs":
        from parse_mcs import parse_mcs

        return bytes(parse_mcs(path))
    return path.read_bytes()


def find_fdri_payload(data: bytes) -> tuple[int, int]:
    sync = data.find(bytes.fromhex("aa995566"))
    if sync < 0:
        raise SystemExit("SYNC not found")
    pos = sync + 4
    last_reg = None
    end = len(data)

    def u32(o: int) -> int:
        return int.from_bytes(data[o : o + 4], "big")

    while pos + 4 <= end:
        w = u32(pos)
        pos += 4
        ptype = w >> 29
        if ptype == 1:
            opc = (w >> 27) & 3
            reg = (w >> 13) & 0x3FFF
            wc = w & 0x7FF
            if opc == 2:
                last_reg = reg
                pos += wc * 4
            continue
        if ptype == 2:
            opc = (w >> 27) & 3
            wc = w & 0x07FFFFFF
            if opc == 2 and last_reg == 2:
                return pos, wc
            pos += wc * 4
            continue
        break
    raise SystemExit("FDRI payload not found")


def analyze(data: bytes) -> dict:
    off0, wc = find_fdri_payload(data)
    nframes = wc // WORDS_PER_FRAME
    frame_bytes = WORDS_PER_FRAME * 4
    zero = b"\x00" * frame_bytes
    nz = [
        0
        if data[off0 + i * frame_bytes : off0 + (i + 1) * frame_bytes] == zero
        else 1
        for i in range(nframes)
    ]

    # 候选 BRAM 起点：其后尾密度 <5%，且前 200 帧密度 >40%
    bram_start = None
    for L in range(200, nframes - 100):
        tail = sum(nz[L:]) / (nframes - L)
        head = sum(nz[L - 200 : L]) / 200
        if tail < 0.05 and head > 0.40:
            bram_start = L
            break

    # 固定 10 段密度（与历史文档对齐）
    segs = []
    for s in range(10):
        lo = s * nframes // 10
        hi = (s + 1) * nframes // 10
        segs.append(
            {
                "seg": s,
                "lo": lo,
                "hi": hi,
                "nz": sum(nz[lo:hi]),
                "span": hi - lo,
                "rate": sum(nz[lo:hi]) / (hi - lo) if hi > lo else 0.0,
            }
        )

    trailing_zeros = 0
    for i in range(nframes - 1, -1, -1):
        if nz[i] == 0:
            trailing_zeros += 1
        else:
            break

    out: dict = {
        "nframes": nframes,
        "fdri_bits": nframes * WORDS_PER_FRAME * 32,
        "ug470_k160t_bits": UG470_K160T_BITS,
        "ug470_minus_fdri_bits": UG470_K160T_BITS - nframes * WORDS_PER_FRAME * 32,
        "nonzero_frames": sum(nz),
        "nonzero_frame_rate": sum(nz) / nframes,
        "segments10": segs,
        "trailing_zero_frames": trailing_zeros,
        "bram_start_candidate": bram_start,
        "method": (
            "UG470 write order blk0→blk1; boundary by density cliff "
            "(tail<5% & prev200>40%); not a Vivado frame map"
        ),
    }

    if bram_start is not None:
        zone = nz[bram_start:]
        nz_idx = [bram_start + i for i, v in enumerate(zone) if v]
        nz_bytes = 0
        for i in nz_idx:
            fb = data[off0 + i * frame_bytes : off0 + (i + 1) * frame_bytes]
            nz_bytes += sum(1 for b in fb if b)
        out["bram_zone"] = {
            "lo": bram_start,
            "hi": nframes,
            "frames": nframes - bram_start,
            "nonzero_frames": len(nz_idx),
            "nonzero_frame_rate": len(nz_idx) / (nframes - bram_start),
            "nonzero_bytes": nz_bytes,
            "last_nonzero_frame": nz_idx[-1] if nz_idx else None,
        }
        # 对照「尾部 20%」固定窗（历史粗估）
        lo20 = int(nframes * 0.80)
        out["tail20_pct"] = {
            "lo": lo20,
            "nonzero_frames": sum(nz[lo20:]),
            "frames": nframes - lo20,
            "rate": sum(nz[lo20:]) / (nframes - lo20),
        }
    return out


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_BIN
    if not path.is_file():
        if DEFAULT_MCS.is_file():
            print(f"# rebuild bin from {DEFAULT_MCS}", flush=True)
            from parse_mcs import parse_mcs

            DEFAULT_BIN.write_bytes(bytes(parse_mcs(DEFAULT_MCS)))
            path = DEFAULT_BIN
        else:
            print("missing firmware", file=sys.stderr)
            return 1
    data = load_bin(path)
    report = analyze(data)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    bz = report.get("bram_zone")
    if bz:
        print(
            f"\n# summary: BRAM-candidate frames[{bz['lo']},{bz['hi']}) "
            f"nz_frames={bz['nonzero_frames']}/{bz['frames']} "
            f"({bz['nonzero_frame_rate']*100:.2f}%), "
            f"nonzero_bytes={bz['nonzero_bytes']}",
            flush=True,
        )
        print(
            "# interpretation: initialized BRAM ROM content is scarce → "
            "weakens PicoBlaze / BRAM-resident MicroBlaze; does not rule out "
            "SPI/DDR-boot tiny cores (P2.5 stays 🔶 until JTAG/ILA).",
            flush=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
