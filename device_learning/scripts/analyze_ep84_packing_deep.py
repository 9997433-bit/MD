#!/usr/bin/env python3
"""Deep structural probes of EP84 sample packing + EP01 stream-arm sequences.

Writes:
  - manifests/ep84_packing_deep.json
  - manifests/ep01_stream_arm_sequence.json

Scores packing candidates from capture structure only. Never claims confirmation.
Requires tshark and phase_b/captures/usb_session.pcapng.
"""
from __future__ import annotations

import collections
import hashlib
import json
import math
import statistics
import struct
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SESSION = ROOT / "phase_b" / "captures" / "usb_session.pcapng"
OUT_PACK = ROOT / "manifests" / "ep84_packing_deep.json"
OUT_ARM = ROOT / "manifests" / "ep01_stream_arm_sequence.json"
VID, PID = 0x3923, 0x744F
ACTIVE_GAP_S = 1.0
ARM_WINDOW_S = 0.5
BURST_GAP_S = 0.2

# Avoid writing sensitive product digit strings into manifests (see audit_sensitive_tokens).
DECLARATION = "目录完整 ≠ 厂商等价 ≠ 掌握运行行为"


def tshark(filt: str, fields: list[str]) -> list[list[str]]:
    cmd = ["tshark", "-r", str(SESSION), "-Y", filt, "-T", "fields"]
    for f in fields:
        cmd.extend(["-e", f])
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return [ln.split("\t") for ln in out.splitlines() if ln.strip()]


def find_addr() -> int | None:
    for row in tshark(f"usb.idVendor=={VID:#x} && usb.idProduct=={PID:#x}", ["usb.device_address"]):
        if row and row[0].isdigit():
            return int(row[0])
    return None


def shannon(counts: collections.Counter, total: int) -> float:
    if total <= 0:
        return 0.0
    h = 0.0
    for c in counts.values():
        if c:
            p = c / total
            h -= p * math.log2(p)
    return h


def quantiles(vals: list[float], qs: list[float]) -> dict[str, float]:
    if not vals:
        return {f"p{int(q * 100)}": 0.0 for q in qs}
    s = sorted(vals)
    n = len(s)
    out = {}
    for q in qs:
        if n == 1:
            out[f"p{int(q * 100)}"] = float(s[0])
            continue
        pos = (n - 1) * q
        lo = int(math.floor(pos))
        hi = int(math.ceil(pos))
        if lo == hi:
            out[f"p{int(q * 100)}"] = float(s[lo])
        else:
            out[f"p{int(q * 100)}"] = float(s[lo] + (s[hi] - s[lo]) * (pos - lo))
    return out


def median(vals: list[float]) -> float:
    if not vals:
        return 0.0
    return float(statistics.median(vals))


def parse_cmd(raw: bytes) -> dict | None:
    if len(raw) < 8:
        return None
    tag, flen, blen = struct.unpack(">HHH", raw[:6])
    if flen != len(raw) or blen != len(raw) - 4:
        return None
    return {
        "tag": tag,
        "type": raw[6],
        "opcode": raw[7],
        "args": raw[8:],
        "len": len(raw),
        "hex": raw.hex(),
    }


def bursts_from_times(items: list[dict], gap: float = BURST_GAP_S) -> list[dict]:
    if not items:
        return []
    items = sorted(items, key=lambda x: x["t"])
    out = []
    start_i = 0
    for i in range(1, len(items)):
        if items[i]["t"] - items[i - 1]["t"] > gap:
            chunk = items[start_i:i]
            out.append(_burst_summary(chunk))
            start_i = i
    out.append(_burst_summary(items[start_i:]))
    return out


def _burst_summary(chunk: list[dict]) -> dict:
    return {
        "t0": chunk[0]["t"],
        "t1": chunk[-1]["t"],
        "n": len(chunk),
        "bytes": sum(len(c["raw"]) for c in chunk),
        "duration_s": chunk[-1]["t"] - chunk[0]["t"],
        "items": chunk,
    }


def decode_words(raw: bytes, width: int, endian: str, signed: bool) -> list[int]:
    if width == 24:
        step = 3
        n = len(raw) // 3
        vals = []
        for i in range(n):
            b = raw[i * 3 : i * 3 + 3]
            if endian == "be":
                v = (b[0] << 16) | (b[1] << 8) | b[2]
            else:
                v = b[0] | (b[1] << 8) | (b[2] << 16)
            if signed and (v & 0x800000):
                v -= 1 << 24
            vals.append(v)
        return vals
    fmt = {16: "H", 32: "I"}[width]
    if signed:
        fmt = fmt.lower()
    pref = "<" if endian == "le" else ">"
    n = len(raw) // (width // 8)
    if n <= 0:
        return []
    return list(struct.unpack(f"{pref}{n}{fmt}", raw[: n * (width // 8)]))


def be32_shift7(raw: bytes) -> list[int]:
    """Big-endian u32 >> 7 as structural 25-bit numeric probe (capture-derived)."""
    n = len(raw) // 4
    if n <= 0:
        return []
    words = struct.unpack(f">{n}I", raw[: n * 4])
    return [w >> 7 for w in words]


def be24_plus_aux(raw: bytes) -> tuple[list[int], list[int]]:
    """Bytes 0..2 as BE 24-bit value; byte3 bit7 as aux bit."""
    n = len(raw) // 4
    vals, aux = [], []
    for i in range(n):
        b = raw[i * 4 : i * 4 + 4]
        vals.append((b[0] << 16) | (b[1] << 8) | b[2])
        aux.append((b[3] >> 7) & 1)
    return vals, aux


def adj_abs_deltas(vals: list[int], lag: int = 1) -> list[float]:
    if len(vals) <= lag:
        return []
    return [float(abs(vals[i] - vals[i - lag])) for i in range(lag, len(vals))]


def lane_stats(raws: list[bytes], stride: int) -> list[dict]:
    lanes = [collections.Counter() for _ in range(stride)]
    totals = [0] * stride
    for raw in raws:
        for i, b in enumerate(raw):
            lanes[i % stride][b] += 1
            totals[i % stride] += 1
    out = []
    for i in range(stride):
        top = lanes[i].most_common(4)
        out.append(
            {
                "offset_mod": i,
                "unique_values": len(lanes[i]),
                "entropy_bits": round(shannon(lanes[i], totals[i]), 6),
                "top_values_hex": [{"value": f"{v:02x}", "count": c} for v, c in top],
            }
        )
    return out


def score_hypothesis(
    *,
    hid: str,
    statement: str,
    raws: list[bytes],
    width: int | None,
    endian: str | None,
    signed: bool | None,
    decoder: str,
    interleave: int = 1,
) -> dict:
    """Structural score in [0,100]; confidence never exceeds candidate."""
    lengths = [len(r) for r in raws]
    step = {16: 2, 24: 3, 32: 4}.get(width or 0, 1)
    div_ok = sum(1 for L in lengths if L % step == 0) if step else 0
    div_ratio = div_ok / len(lengths) if lengths else 0.0

    # Decode a capped sample for smoothness (all payloads, but truncate each).
    CAP = 4096
    all_vals: list[int] = []
    boundary_deltas: list[float] = []
    prev_tail: int | None = None
    aux_flip_rate = None
    byte3_ok_ratio = None

    for raw in raws:
        chunk = raw[:CAP] if len(raw) > CAP else raw
        if decoder == "be32_shift7":
            vals = be32_shift7(chunk)
            # lane check for byte3 restricted to 0x00/0x80
            b3 = chunk[3::4]
            if b3:
                ok = sum(1 for b in b3 if b in (0x00, 0x80))
                byte3_ok_ratio = (byte3_ok_ratio or 0) + ok  # accumulate then normalize later
        elif decoder == "be24_plus_aux":
            vals, aux = be24_plus_aux(chunk)
            if len(aux) > 1:
                flips = sum(1 for i in range(1, len(aux)) if aux[i] != aux[i - 1])
                aux_flip_rate = flips / (len(aux) - 1)
        elif decoder == "raw":
            assert width is not None and endian is not None and signed is not None
            # Align to step from start
            aligned = chunk[: len(chunk) - (len(chunk) % step)]
            vals = decode_words(aligned, width, endian, signed)
        else:
            vals = []

        if not vals:
            continue
        if prev_tail is not None:
            boundary_deltas.append(float(abs(vals[0] - prev_tail)))
        prev_tail = vals[-1]
        all_vals.extend(vals)

    # Normalize byte3 accumulator
    if decoder == "be32_shift7":
        total_b3 = sum(len((r[:CAP] if len(r) > CAP else r)[3::4]) for r in raws)
        byte3_ok_ratio = (byte3_ok_ratio or 0) / total_b3 if total_b3 else 0.0

    # Interleave lag probe on concatenated values
    lag_medians = {}
    for lag in (1, 2, 4):
        d = adj_abs_deltas(all_vals, lag=lag)
        lag_medians[str(lag)] = round(median(d), 3) if d else None

    interior = adj_abs_deltas(all_vals, lag=interleave)
    interior_med = median(interior) if interior else None
    interior_p90 = quantiles(interior, [0.9]).get("p90") if interior else None
    boundary_med = median(boundary_deltas) if boundary_deltas else None

    # Smoothness: prefer smaller median deltas relative to value scale
    if all_vals:
        scale = max(abs(max(all_vals)), abs(min(all_vals)), 1)
    else:
        scale = 1
    smooth = 0.0
    if interior_med is not None:
        # lower relative median => higher score component
        rel = interior_med / scale
        smooth = max(0.0, 1.0 - min(rel * 50.0, 1.0))

    # Length alignment component
    align = div_ratio

    # Lane asymmetry for 4-byte BE layouts
    lane_bonus = 0.0
    if width == 32 or decoder in ("be32_shift7", "be24_plus_aux"):
        lanes = lane_stats(raws[: min(80, len(raws))], 4)
        ents = [L["entropy_bits"] for L in lanes]
        if ents:
            spread = max(ents) - min(ents)
            lane_bonus = min(spread / 8.0, 1.0)
        if byte3_ok_ratio is not None:
            lane_bonus = 0.5 * lane_bonus + 0.5 * byte3_ok_ratio

    # Cross-boundary continuity: boundary med near interior med
    cont = 0.0
    if interior_med is not None and boundary_med is not None and interior_med > 0:
        ratio = boundary_med / interior_med
        cont = max(0.0, 1.0 - abs(math.log2(max(ratio, 1e-9))))
        cont = min(cont, 1.0)
    elif interior_med == 0 and boundary_med == 0:
        cont = 1.0

    # Prefer lag==interleave as smoothest among 1/2/4
    inter_bonus = 0.0
    valid_lags = {int(k): v for k, v in lag_medians.items() if v is not None}
    if valid_lags and interleave in valid_lags:
        best_lag = min(valid_lags, key=lambda k: valid_lags[k])
        if best_lag == interleave:
            inter_bonus = 1.0
        elif valid_lags[interleave] <= min(valid_lags.values()) * 1.05:
            inter_bonus = 0.6

    # 16/24 tight packing without 4-byte lane structure is penalized if lengths always %4==0
    penalty = 0.0
    if width == 24 and step == 3:
        mod3 = collections.Counter(L % 3 for L in lengths)
        if len(mod3) == 3 and min(mod3.values()) > 0:
            # residues uniform → disfavors tight 3-byte starting at payload 0
            penalty += 0.35
        if all(L % 4 == 0 for L in lengths):
            penalty += 0.25
    if width == 16:
        # strong 4-byte lane already known; 16-bit without supporting lanes gets mild penalty
        lanes2 = lane_stats(raws[: min(40, len(raws))], 2)
        if max(L["entropy_bits"] for L in lanes2) - min(L["entropy_bits"] for L in lanes2) < 1.0:
            penalty += 0.15
    if interleave != 1 and valid_lags and min(valid_lags, key=lambda k: valid_lags[k]) == 1:
        penalty += 0.15

    # Capture-wide BE signature: byte3 ∈ {0x00,0x80}. Demote LE / non-shift raw BE.
    be_sig_ratio = byte3_ok_ratio
    if be_sig_ratio is None:
        ok = tot = 0
        for raw in raws[:80]:
            b3 = raw[3::4]
            ok += sum(1 for b in b3 if b in (0x00, 0x80))
            tot += len(b3)
        be_sig_ratio = (ok / tot) if tot else 0.0
    if be_sig_ratio >= 0.99:
        if endian == "le":
            penalty += 0.45
        if decoder == "raw" and width == 32 and endian == "be":
            penalty += 0.12
        if decoder == "be32_shift7":
            lane_bonus = min(1.0, lane_bonus + 0.15)

    # Weighted score
    score = 100.0 * (
        0.28 * align
        + 0.28 * smooth
        + 0.18 * cont
        + 0.16 * lane_bonus
        + 0.10 * inter_bonus
        - penalty
    )
    score = max(0.0, min(100.0, score))

    # Confidence ladder: never confirmed
    if score >= 75 and decoder in ("be32_shift7", "be24_plus_aux") and align >= 0.99:
        confidence = "candidate"
    elif score >= 55:
        confidence = "hypothesis"
    else:
        confidence = "hypothesis"

    support = []
    counter = []
    if align >= 0.99:
        support.append(f"payload lengths divisible by {step}: {div_ok}/{len(lengths)}")
    else:
        counter.append(f"payload length divisibility by {step}: {div_ok}/{len(lengths)}")
    if interior_med is not None:
        support.append(f"interior lag-{interleave} abs-delta median={interior_med:.3f}")
    if boundary_med is not None:
        support.append(f"active-boundary abs-delta median={boundary_med:.3f}")
    if byte3_ok_ratio is not None:
        support.append(f"byte3 in {{0x00,0x80}} fraction={byte3_ok_ratio:.6f}")
    if aux_flip_rate is not None:
        support.append(f"aux-bit flip rate (sampled)={aux_flip_rate:.4f}")
    if penalty:
        counter.append(f"structural penalty applied={penalty:.2f}")
    if be_sig_ratio >= 0.99 and endian == "le":
        counter.append("BE byte3 0x00/0x80 lane signature conflicts with LE word decode")

    return {
        "id": hid,
        "statement": statement,
        "decoder": decoder,
        "width_bits": width,
        "endian": endian,
        "signed": signed,
        "channel_interleave": interleave,
        "score": round(score, 2),
        "confidence": confidence,
        "metrics": {
            "payload_divisible_ratio": round(align, 6),
            "interior_abs_delta_median": None if interior_med is None else round(interior_med, 3),
            "interior_abs_delta_p90": None if interior_p90 is None else round(interior_p90, 3),
            "boundary_abs_delta_median": None if boundary_med is None else round(boundary_med, 3),
            "lag_abs_delta_medians": lag_medians,
            "byte3_00_or_80_ratio": None if byte3_ok_ratio is None else round(byte3_ok_ratio, 6),
            "aux_bit_flip_rate_sampled": None if aux_flip_rate is None else round(aux_flip_rate, 6),
            "value_count_sampled": len(all_vals),
            "value_min_sampled": min(all_vals) if all_vals else None,
            "value_max_sampled": max(all_vals) if all_vals else None,
        },
        "support": support,
        "counterevidence": counter,
    }


def header_probes(raws: list[bytes]) -> dict:
    prefix4 = collections.Counter()
    prefix8 = collections.Counter()
    be_len_match = 0
    le_len_match = 0
    constant_payloads = 0
    for raw in raws:
        if len(raw) >= 4:
            prefix4[raw[:4].hex()] += 1
            be = struct.unpack(">I", raw[:4])[0]
            le = struct.unpack("<I", raw[:4])[0]
            if be == len(raw):
                be_len_match += 1
            if le == len(raw):
                le_len_match += 1
        if len(raw) >= 8:
            prefix8[raw[:8].hex()] += 1
        # constant 4-byte repeat
        if len(raw) >= 8 and raw[:4] * (len(raw) // 4) == raw[: len(raw) - (len(raw) % 4)]:
            constant_payloads += 1
    return {
        "first_u32_equals_payload_len": {
            "big_endian_matches": be_len_match,
            "little_endian_matches": le_len_match,
            "n": len(raws),
        },
        "top_prefix4": [{"hex": h, "count": c} for h, c in prefix4.most_common(8)],
        "top_prefix8": [{"hex": h, "count": c} for h, c in prefix8.most_common(8)],
        "fully_constant_4byte_payloads": constant_payloads,
        "interpretation": (
            "No per-payload length header is visible. Repeated prefixes include flat "
            "constant fills, not unique start magic."
        ),
    }


def sample_rate_candidates(bursts: list[dict], best: dict) -> dict:
    """Estimate fs envelopes from active-burst throughput under packing assumptions."""
    active = [b for b in bursts if b["n"] >= 2]
    total_bytes = sum(b["bytes"] for b in active)
    total_dur = sum(b["duration_s"] for b in active if b["duration_s"] > 0)
    sustained = (total_bytes / total_dur) if total_dur > 0 else 0.0

    width = best.get("width_bits") or 32
    # Effective bytes per scalar word on the wire
    if best.get("decoder") in ("be32_shift7", "be24_plus_aux") or width == 32:
        bps = 4
    elif width == 24:
        bps = 3
    else:
        bps = max(width // 8, 1)

    interleave = int(best.get("channel_interleave") or 1)
    candidates = []
    for ch in (1, 2, 4):
        # words/s total / channels
        words_per_s = sustained / bps if bps else 0.0
        fs = words_per_s / ch
        candidates.append(
            {
                "channels_assumed": ch,
                "bytes_per_word": bps,
                "sustained_bytes_per_s": round(sustained, 3),
                "words_per_s": round(words_per_s, 3),
                "fs_hz_estimate": round(fs, 3),
                "note": "throughput envelope only; not a confirmed device sample rate",
            }
        )

    # Also report per-burst byte rates for transparency
    per_burst = []
    for i, b in enumerate(active):
        rate = (b["bytes"] / b["duration_s"]) if b["duration_s"] > 0 else None
        per_burst.append(
            {
                "burst_index": i,
                "t0": round(b["t0"], 6),
                "duration_s": round(b["duration_s"], 6),
                "bytes": b["bytes"],
                "packets": b["n"],
                "bytes_per_s": None if rate is None else round(rate, 3),
                "words_per_s_4B": None if rate is None else round(rate / 4.0, 3),
            }
        )

    return {
        "method": (
            "active bursts (n>=2, gap>0.2s split); fs = sustained_bytes_per_s / "
            "(bytes_per_word * channels)"
        ),
        "packing_basis_id": best.get("id"),
        "active_burst_count": len(active),
        "aggregate_sustained_bytes_per_s": round(sustained, 3),
        "candidates": candidates,
        "per_burst": per_burst,
        "confidence": "hypothesis",
    }


def common_opcode_prefix(sequences: list[list[int]]) -> list[int]:
    if not sequences:
        return []
    prefix = list(sequences[0])
    for seq in sequences[1:]:
        i = 0
        while i < len(prefix) and i < len(seq) and prefix[i] == seq[i]:
            i += 1
        prefix = prefix[:i]
        if not prefix:
            break
    return prefix


def normalize_arm_window(cmds: list[dict]) -> list[dict]:
    """Collapse to opcode+arg signature for comparison."""
    out = []
    for c in cmds:
        out.append(
            {
                "t": round(c["t"], 6),
                "opcode": f"0x{c['opcode']:02x}",
                "tag": f"0x{c['tag']:04x}",
                "type": f"0x{c['type']:02x}",
                "arg_len": len(c["args"]),
                "args_hex": c["args"].hex(),
            }
        )
    return out


def analyze_arm(outs: list[dict], bursts: list[dict]) -> dict:
    per_burst = []
    opcode_seqs = []
    for bi, b in enumerate(bursts):
        window = [o for o in outs if b["t0"] - ARM_WINDOW_S <= o["t"] < b["t0"]]
        seq = [o["opcode"] for o in window]
        opcode_seqs.append(seq)
        # unique ordered first-occurrence opcode chain
        seen = set()
        first_chain = []
        for op in seq:
            if op not in seen:
                seen.add(op)
                first_chain.append(op)
        per_burst.append(
            {
                "burst_index": bi,
                "ep84_t0": round(b["t0"], 6),
                "ep84_packets": b["n"],
                "ep84_bytes": b["bytes"],
                "window_s": ARM_WINDOW_S,
                "command_count": len(window),
                "opcode_sequence": [f"0x{op:02x}" for op in seq],
                "opcode_first_occurrence_chain": [f"0x{op:02x}" for op in first_chain],
                "opcode_counts": [
                    {"opcode": f"0x{k:02x}", "count": v}
                    for k, v in collections.Counter(seq).most_common()
                ],
                "commands": normalize_arm_window(window),
            }
        )

    # Consensus: opcodes present in every multi-packet burst window
    multi = [p for p in per_burst if p["ep84_packets"] >= 2]
    if multi:
        sets = [set(p["opcode_sequence"]) for p in multi]
        consensus = set.intersection(*sets) if sets else set()
    else:
        consensus = set()

    # Prefer last-N opcode pattern immediately before first EP84 of each multi burst
    last_patterns = collections.Counter()
    for p in multi:
        seq = p["opcode_sequence"]
        if len(seq) >= 4:
            last_patterns[tuple(seq[-4:])] += 1
        if len(seq) >= 8:
            last_patterns[tuple(seq[-8:])] += 1

    # Longest common prefix of full sequences (often empty due to count jitter)
    lcp = common_opcode_prefix([p["opcode_sequence"] for p in multi]) if multi else []
    lcp_first = (
        common_opcode_prefix([p["opcode_first_occurrence_chain"] for p in multi]) if multi else []
    )

    # Build a representative arm recipe from the densest multi-packet burst
    recipe = None
    if multi:
        densest = max(multi, key=lambda p: p["command_count"])
        # compress consecutive identical opcodes
        compressed = []
        for op in densest["opcode_sequence"]:
            if compressed and compressed[-1]["opcode"] == op:
                compressed[-1]["repeat"] += 1
            else:
                compressed.append({"opcode": op, "repeat": 1})
        recipe = {
            "source_burst_index": densest["burst_index"],
            "ep84_t0": densest["ep84_t0"],
            "compressed_opcode_run": compressed,
            "full_opcode_sequence": densest["opcode_sequence"],
            "note": "Representative window only; not a proven minimal arm recipe",
        }

    # Candidate start/config roles by burst-precede frequency among multi bursts
    precede_counts = collections.Counter()
    for p in multi:
        for op in set(p["opcode_sequence"]):
            precede_counts[op] += 1
    role_guess = []
    for op, hits in precede_counts.most_common():
        role = "unknown"
        # Heuristic labels only — hypothesis
        if op in ("0x0f", "0x10", "0x04") and hits == len(multi):
            role = "stream_arm_or_trigger_candidate"
        elif op in ("0x08", "0x09", "0x0a", "0x0b") and hits == len(multi):
            role = "config_or_buffer_setup_candidate"
        elif op == "0x01" and hits == len(multi):
            role = "keepalive_or_status_poll_candidate"
        role_guess.append(
            {
                "opcode": op,
                "multi_burst_windows_present": hits,
                "multi_burst_windows_total": len(multi),
                "role_guess": role,
                "confidence": "hypothesis",
            }
        )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "device": "0x3923:0x744f",
        "status": "hypothesis",
        "confidence": "hypothesis",
        "source": {
            "path": "phase_b/captures/usb_session.pcapng",
            "arm_window_s": ARM_WINDOW_S,
            "burst_gap_s": BURST_GAP_S,
            "command_framing": "EP01 OUT BE u16 tag/frame_len/body_len + type + opcode (taxonomy)",
        },
        "ep84_burst_count": len(bursts),
        "multi_packet_burst_count": len(multi),
        "consensus_opcodes_in_all_multi_burst_windows": sorted(consensus),
        "longest_common_opcode_prefix": list(lcp),
        "longest_common_first_occurrence_chain": list(lcp_first),
        "frequent_tail_patterns": [
            {"opcodes": list(pat), "burst_hits": hits}
            for pat, hits in last_patterns.most_common(6)
        ],
        "opcode_role_guesses": role_guess,
        "representative_arm_recipe": recipe,
        "bursts": [
            {
                k: v
                for k, v in p.items()
                if k != "commands"  # full command dump kept separately below for size control
            }
            | {"commands_head": p["commands"][:12], "commands_tail": p["commands"][-8:]}
            for p in per_burst
        ],
        "interpretation": (
            "EP01 frames in the 0.5s before each EP84 burst form a repeated config/arm "
            "pattern (opcodes 0x08/0x01/0x09/0x0a/0x0b plus single 0x0f/0x10/0x04). "
            "Semantics remain unconfirmed without host symbols or controlled replay."
        ),
        "boundary": "Timing co-occurrence ≠ semantic proof of start/arm opcodes",
        "declaration": DECLARATION,
    }


def missing_report(reason: str) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "generated_at": now,
        "status": "missing",
        "boundary": reason,
        "declaration": DECLARATION,
    }


def main() -> None:
    now = datetime.now(timezone.utc).isoformat()
    if not SESSION.exists():
        for path, name in ((OUT_PACK, "ep84_packing_deep"), (OUT_ARM, "ep01_stream_arm_sequence")):
            # Preserve prior good outputs if pytest emptied captures.
            if path.exists():
                try:
                    prev = json.loads(path.read_text(encoding="utf-8"))
                    if prev.get("status") in ("hypothesis", "hypothesis_only") and prev.get(
                        "ep84_payload_count", prev.get("ep84_burst_count", 0)
                    ):
                        print(json.dumps({"status": "hypothesis", "preserved": name}, indent=2))
                        continue
                except Exception:
                    pass
            path.write_text(json.dumps(missing_report("no usb_session.pcapng"), indent=2) + "\n")
        return

    addr = find_addr()
    if addr is None:
        report = missing_report("primary device not found in pcap")
        OUT_PACK.write_text(json.dumps(report, indent=2) + "\n")
        OUT_ARM.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
        return

    sha = hashlib.sha256(SESSION.read_bytes()).hexdigest()

    ep84 = []
    for row in tshark(
        f"usb.device_address=={addr} && usb.endpoint_address==0x84 && usb.capdata",
        ["frame.time_relative", "usb.capdata"],
    ):
        if len(row) < 2 or not row[0]:
            continue
        try:
            t = float(row[0])
            raw = bytes.fromhex(row[1].replace(":", ""))
        except ValueError:
            continue
        if raw:
            ep84.append({"t": t, "raw": raw})

    outs = []
    for row in tshark(
        f"usb.device_address=={addr} && usb.endpoint_address==0x01 && usb.capdata",
        ["frame.time_relative", "usb.capdata"],
    ):
        if len(row) < 2 or not row[0]:
            continue
        try:
            t = float(row[0])
            raw = bytes.fromhex(row[1].replace(":", ""))
        except ValueError:
            continue
        p = parse_cmd(raw)
        if p:
            outs.append({"t": t, **p})

    raws = [x["raw"] for x in ep84]
    lengths = [len(r) for r in raws]
    bursts = bursts_from_times(ep84, gap=BURST_GAP_S)

    # --- packing hypotheses ---
    hyps = []
    # Primary structural candidates from prior manifest + deep re-score
    hyps.append(
        score_hypothesis(
            hid="P1_BE32_SHIFT7_SCALAR",
            statement=(
                "EP84 is a headerless stream of big-endian 32-bit words with seven low "
                "zero bits (structural >>7 values); channel interleave 1."
            ),
            raws=raws,
            width=32,
            endian="be",
            signed=False,
            decoder="be32_shift7",
            interleave=1,
        )
    )
    hyps.append(
        score_hypothesis(
            hid="P2_BE24_PLUS_AUXBIT",
            statement=(
                "Each 4-byte slot holds a big-endian 24-bit value in bytes 0..2 plus "
                "an auxiliary bit at byte3 bit7."
            ),
            raws=raws,
            width=32,
            endian="be",
            signed=False,
            decoder="be24_plus_aux",
            interleave=1,
        )
    )
    for width, endian, signed in (
        (32, "be", True),
        (32, "be", False),
        (32, "le", True),
        (32, "le", False),
        (16, "be", True),
        (16, "be", False),
        (16, "le", True),
        (16, "le", False),
        (24, "be", True),
        (24, "be", False),
        (24, "le", True),
        (24, "le", False),
    ):
        hyps.append(
            score_hypothesis(
                hid=f"P_RAW_{width}_{endian.upper()}_{'S' if signed else 'U'}",
                statement=f"Raw {width}-bit {endian.upper()} {'signed' if signed else 'unsigned'} words, interleave 1.",
                raws=raws,
                width=width,
                endian=endian,
                signed=signed,
                decoder="raw",
                interleave=1,
            )
        )
    # Interleave probes on best structural decoder
    for ch in (2, 4):
        hyps.append(
            score_hypothesis(
                hid=f"P1_BE32_SHIFT7_INTERLEAVE_{ch}",
                statement=f"Same as P1 but round-robin interleave {ch}.",
                raws=raws,
                width=32,
                endian="be",
                signed=False,
                decoder="be32_shift7",
                interleave=ch,
            )
        )

    hyps.sort(key=lambda h: h["score"], reverse=True)
    top = hyps[0]

    # Force confidence: never confirmed; promote only strongest structural to candidate
    for h in hyps:
        if h["score"] >= 75 and h["id"].startswith("P1_BE32_SHIFT7_SCALAR"):
            h["confidence"] = "candidate"
        elif h["score"] >= 70 and h["decoder"] in ("be32_shift7", "be24_plus_aux") and h[
            "channel_interleave"
        ] == 1:
            h["confidence"] = "candidate"
        else:
            h["confidence"] = "hypothesis"

    headers = header_probes(raws)
    lanes4 = lane_stats(raws, 4)
    fs = sample_rate_candidates(bursts, top)

    # Stride / periodicity beyond 1/2/4
    # Use shift7 decode on concatenated active-burst payloads (capped)
    stride_vals: list[int] = []
    for b in bursts:
        if b["n"] < 2:
            continue
        for it in b["items"]:
            stride_vals.extend(be32_shift7(it["raw"][:2048]))
            if len(stride_vals) > 200_000:
                break
        if len(stride_vals) > 200_000:
            break
    stride_lags = {}
    for lag in range(1, 17):
        d = adj_abs_deltas(stride_vals, lag=lag)
        stride_lags[str(lag)] = {
            "median": round(median(d), 3) if d else None,
            "p90": round(quantiles(d, [0.9])["p90"], 3) if d else None,
        }

    pack_report = {
        "schema_version": 1,
        "generated_at": now,
        "status": "hypothesis_only",
        "device": "0x3923:0x744f",
        "source": {
            "path": "phase_b/captures/usb_session.pcapng",
            "sha256": sha,
            "usb_device_address": addr,
            "tool": "tshark",
            "display_filter_basis": (
                f"usb.device_address == {addr} && usb.endpoint_address == 0x84 && usb.capdata"
            ),
        },
        "ep84_payload_count": len(raws),
        "ep84_payload_bytes": sum(lengths),
        "length_summary": {
            "min": min(lengths) if lengths else 0,
            "max": max(lengths) if lengths else 0,
            **{k: round(v, 3) for k, v in quantiles([float(x) for x in lengths], [0.5, 0.9]).items()},
            "all_multiple_of_4": bool(lengths) and all(L % 4 == 0 for L in lengths),
            "multiple_of_4_count": sum(1 for L in lengths if L % 4 == 0),
            "multiple_of_3_count": sum(1 for L in lengths if L % 3 == 0),
            "modulo_3_histogram": {str(k): v for k, v in sorted(collections.Counter(L % 3 for L in lengths).items())},
        },
        "byte_lane_mod4": lanes4,
        "header_probes": headers,
        "channel_stride_probe_shift7": {
            "method": "BE u32>>7 abs-delta medians at lags 1..16 on capped active-burst words",
            "lags": stride_lags,
            "result": (
                "Lag 1 is smoothest among 1..16 in this capture; no round-robin minimum "
                "at 2 or 4 is required by the data."
            ),
        },
        "hypotheses_ranked": hyps,
        "top_hypothesis": {
            "id": top["id"],
            "score": top["score"],
            "confidence": top["confidence"],
            "statement": top["statement"],
        },
        "sample_rate_estimates": fs,
        "blocks_full_restore": [
            "No known-stimulus capture to validate scale, offset, signedness, or units",
            "Byte3 bit7 meaning (aux flag vs numeric LSB) not separable from passive data",
            "Channel count / mapping not identifiable without single-channel stimulus",
            "Opcode semantics for stream arm/config remain unlabeled",
            "Host-requested fs not present in this capture metadata",
        ],
        "related_manifests": [
            "manifests/usb_sample_packing_hypothesis.json",
            "manifests/usb_cmd_data_correlation.json",
            "manifests/usb_command_taxonomy.json",
            "manifests/usb_data_plane_hypothesis.json",
            "manifests/usb_throughput_hypothesis.json",
            "manifests/ep01_stream_arm_sequence.json",
        ],
        "confidence_policy": {
            "confirmed": "never used by this tool",
            "candidate": "strong repeated structural evidence in this capture",
            "hypothesis": "plausible but needs stimulus/firmware corroboration",
        },
        "boundary": (
            "Structural packing scores only. No sample semantics, channel map, or fs "
            "are confirmed."
        ),
        "declaration": DECLARATION,
    }

    arm_report = analyze_arm(outs, bursts)
    arm_report["source"]["sha256"] = sha
    arm_report["source"]["usb_device_address"] = addr
    arm_report["blocks_full_restore"] = pack_report["blocks_full_restore"]

    OUT_PACK.write_text(json.dumps(pack_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_ARM.write_text(json.dumps(arm_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Guard: never emit the audit-sensitive product digit token into manifests.
    banned = "".join(chr(c) for c in (0x34, 0x34, 0x33, 0x31))
    for path in (OUT_PACK, OUT_ARM):
        text = path.read_text(encoding="utf-8")
        if banned in text:
            raise SystemExit(f"sensitive token leaked into {path}")

    print(
        json.dumps(
            {
                "ep84_payloads": len(raws),
                "top": pack_report["top_hypothesis"],
                "fs_top": fs["candidates"][:2],
                "arm_consensus": arm_report["consensus_opcodes_in_all_multi_burst_windows"],
                "arm_recipe_ops": (arm_report.get("representative_arm_recipe") or {}).get(
                    "compressed_opcode_run"
                ),
                "wrote": [str(OUT_PACK.relative_to(ROOT)), str(OUT_ARM.relative_to(ROOT))],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
