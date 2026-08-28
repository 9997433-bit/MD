#!/usr/bin/env python3
"""
位流网络常量搜索
在 MCS 展开镜像中搜索可能的网络硬编码常量：
  1. IPv4 地址（私网/特殊段，大端 + 小端）
  2. MAC OUI（厂商前缀，含板载芯片相关厂商）
  3. 常见 UDP/TCP 端口（大端 + 小端）

用法：
  python3 search_net_constants.py [镜像路径] [--json 输出.json]

镜像路径可为：
  - .bin  已展开的线性镜像（默认优先）
  - .mcs  Intel-HEX，脚本内联展开

默认从 zero0000-research/assets/firmware/ 自动定位。
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

# ----------------------------------------------------------------------------
# 镜像加载
# ----------------------------------------------------------------------------

def load_mcs(path: Path) -> bytearray:
    """展开 Intel-HEX(.mcs) 为线性镜像（缺口以 0xFF 填充）。"""
    segments: dict[int, bytes] = {}
    upper = 0
    with path.open("r", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line.startswith(":") or len(line) < 11:
                continue
            count = int(line[1:3], 16)
            addr = int(line[3:7], 16)
            rectype = int(line[7:9], 16)
            payload = bytes.fromhex(line[9 : 9 + count * 2])
            if rectype == 4 and count == 2:
                upper = ((payload[0] << 8) | payload[1]) << 16
            elif rectype == 0:
                segments[upper + addr] = payload
    if not segments:
        return bytearray()
    max_addr = max(base + len(p) for base, p in segments.items())
    data = bytearray(b"\xff" * max_addr)
    for base, payload in segments.items():
        data[base : base + len(payload)] = payload
    return data


def load_image(path: Path) -> bytearray:
    if path.suffix.lower() == ".mcs":
        return load_mcs(path)
    return bytearray(path.read_bytes())


def autolocate() -> Path | None:
    here = Path(__file__).resolve().parent
    fw = here.parent / "assets" / "firmware"
    for name in ("20230825_s2056.bin", "20230825_s2056.mcs"):
        p = fw / name
        if p.exists():
            return p
    for cand in list(fw.glob("*.bin")) + list(fw.glob("*.mcs")):
        return cand
    return None


# ----------------------------------------------------------------------------
# IPv4 搜索
# ----------------------------------------------------------------------------

def classify_ipv4(a: int, b: int, c: int, d: int) -> str | None:
    """返回可读的 IPv4 分类；若非"有意义"地址返回 None。"""
    # 过滤无信息量的地址
    if (a, b, c, d) == (0, 0, 0, 0) or (a, b, c, d) == (255, 255, 255, 255):
        return None
    if a == 0 or a == 255:
        return None
    if a == 10:
        return "私网 10/8"
    if a == 172 and 16 <= b <= 31:
        return "私网 172.16/12"
    if a == 192 and b == 168:
        return "私网 192.168/16"
    if a == 127:
        return "环回 127/8"
    if a == 169 and b == 254:
        return "链路本地 169.254/16"
    if 224 <= a <= 239:
        return "组播 224-239"
    if a == 100 and 64 <= b <= 127:
        return "CGNAT 100.64/10"
    return None


def search_ipv4(data: bytes) -> list[dict]:
    """滑窗扫描 4 字节，big/little 两种字节序解读为 IPv4。"""
    hits: list[dict] = []
    n = len(data)
    for i in range(n - 3):
        w = data[i : i + 4]
        # 全同字节（0x00 0xFF 等）快速跳过
        if w[0] == w[1] == w[2] == w[3]:
            continue
        for order in ("big", "little"):
            if order == "big":
                a, b, c, d = w[0], w[1], w[2], w[3]
            else:
                a, b, c, d = w[3], w[2], w[1], w[0]
            cls = classify_ipv4(a, b, c, d)
            if cls:
                hits.append(
                    {
                        "offset": i,
                        "endian": order,
                        "raw": w.hex(),
                        "ip": f"{a}.{b}.{c}.{d}",
                        "class": cls,
                    }
                )
    return hits


# ----------------------------------------------------------------------------
# MAC OUI 搜索
# ----------------------------------------------------------------------------
# 关注：Xilinx/AMD（软核 TEMAC 常用）、板载芯片厂商、及常见网络设备厂商。
OUI_TABLE: dict[str, str] = {
    "000a35": "Xilinx",
    "002170": "Xilinx (旧)",
    "0050c2": "IEEE Registration Authority(私有块)",
    "001c23": "Dell",
    "0004a3": "Microchip/Atmel",
    "0080e1": "STMicroelectronics",
    "d88039": "Texas Instruments",
    "3c2af4": "Brother",
    "001b21": "Intel",
    "0015c5": "Dell",
    "001dfd": "Nokia",
    "b827eb": "Raspberry Pi",
    "dca632": "Raspberry Pi",
    "000e0c": "Intel",
    "00a0c9": "Intel",
    "005043": "Marvell",
    "0050b6": "Good Way (常见 GigE)",
    "70b3d5": "IEEE RA(小块/OEM 常用)",
}


def search_mac_oui(data: bytes) -> list[dict]:
    hits: list[dict] = []
    n = len(data)
    for oui_hex, vendor in OUI_TABLE.items():
        pat = bytes.fromhex(oui_hex)
        start = 0
        while True:
            i = data.find(pat, start)
            if i < 0:
                break
            start = i + 1
            if i + 6 > n:
                continue
            mac = data[i : i + 6]
            hits.append(
                {
                    "offset": i,
                    "oui": oui_hex,
                    "vendor": vendor,
                    "mac": ":".join(f"{x:02x}" for x in mac),
                }
            )
    return hits


# ----------------------------------------------------------------------------
# UDP/TCP 端口搜索
# ----------------------------------------------------------------------------
COMMON_PORTS: dict[int, str] = {
    53: "DNS",
    67: "DHCP server",
    68: "DHCP client",
    69: "TFTP",
    80: "HTTP",
    123: "NTP",
    161: "SNMP",
    162: "SNMP trap",
    319: "PTP event",
    320: "PTP general",
    443: "HTTPS",
    502: "Modbus/TCP",
    514: "Syslog",
    520: "RIP",
    546: "DHCPv6 client",
    547: "DHCPv6 server",
    1900: "SSDP/UPnP",
    3702: "WS-Discovery",
    4660: "0x1234(常见占位)",
    5000: "常见自定义/UPnP",
    5353: "mDNS",
    5555: "常见调试/自定义",
    8080: "HTTP-alt",
    9000: "常见自定义",
    49152: "动态端口起始",
}


def search_ports(data: bytes) -> dict[str, list[dict]]:
    """统计常见端口值出现次数（big/little）。端口=2 字节，命中极多，故只统计与抽样。"""
    result: dict[str, list[dict]] = {"big": [], "little": []}
    for order in ("big", "little"):
        for port, name in COMMON_PORTS.items():
            pat = port.to_bytes(2, order)
            cnt = data.count(pat)
            if cnt == 0:
                continue
            # 抽样前若干偏移
            offs: list[int] = []
            start = 0
            while len(offs) < 8:
                i = data.find(pat, start)
                if i < 0:
                    break
                offs.append(i)
                start = i + 1
            result[order].append(
                {"port": port, "name": name, "count": cnt, "sample_offsets": offs}
            )
    return result


# ----------------------------------------------------------------------------
# 主流程
# ----------------------------------------------------------------------------

def dedup_context(hits: list[dict], data: bytes) -> None:
    """就地为每条命中补充上下文（前后 4 字节 hex），便于人工研判。"""
    for h in hits:
        o = h["offset"]
        lo = max(0, o - 4)
        hi = min(len(data), o + 8)
        h["context"] = data[lo:hi].hex()


def summarize_entropy(data: bytes) -> float:
    import math

    if not data:
        return 0.0
    c = Counter(data)
    n = len(data)
    return -sum((v / n) * math.log2(v / n) for v in c.values())


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("image", nargs="?", type=Path, default=None)
    ap.add_argument("--json", type=Path, default=None, help="将完整结果写入 JSON")
    ap.add_argument("--max-print", type=int, default=40, help="每类最多打印条数")
    args = ap.parse_args()

    path = args.image or autolocate()
    if not path or not path.exists():
        print("[ERR] 找不到镜像文件，请显式指定路径。", file=sys.stderr)
        sys.exit(1)

    data = load_image(path)
    print(f"镜像: {path}")
    print(f"长度: {len(data)} B ({len(data)/1024/1024:.3f} MiB)")
    print(f"整体熵: {summarize_entropy(data):.4f} bit/byte")
    print(f"0x00 占比: {data.count(0)/len(data)*100:.2f}%  0xFF 占比: {data.count(0xFF)/len(data)*100:.2f}%")
    print("-" * 60)

    ipv4 = search_ipv4(data)
    dedup_context(ipv4, data)
    mac = search_mac_oui(data)
    dedup_context(mac, data)
    ports = search_ports(data)

    # IPv4
    print(f"\n[IPv4] 命中 {len(ipv4)} 处（私网/特殊段, big+little）")
    ip_by_class = Counter(h["class"] for h in ipv4)
    for cls, c in ip_by_class.most_common():
        print(f"   {cls:20s}: {c}")
    for h in ipv4[: args.max_print]:
        print(
            f"   @0x{h['offset']:08X} {h['endian']:6s} {h['raw']} -> {h['ip']:15s} "
            f"[{h['class']}] ctx={h['context']}"
        )
    if len(ipv4) > args.max_print:
        print(f"   ... 其余 {len(ipv4)-args.max_print} 条见 JSON")

    # MAC
    print(f"\n[MAC OUI] 命中 {len(mac)} 处")
    for h in mac[: args.max_print]:
        print(
            f"   @0x{h['offset']:08X} {h['mac']}  [{h['vendor']}] ctx={h['context']}"
        )

    # 端口
    print("\n[端口] 常见端口出现统计（count 高多为巧合，重点看小端/大端一致且计数低者）")
    for order in ("big", "little"):
        rows = sorted(ports[order], key=lambda r: r["count"])
        print(f"  -- {order} --")
        for r in rows:
            print(
                f"   {r['port']:6d} {r['name']:20s} count={r['count']:8d} "
                f"sample={[hex(x) for x in r['sample_offsets'][:4]]}"
            )

    if args.json:
        args.json.write_text(
            json.dumps(
                {
                    "image": str(path),
                    "length": len(data),
                    "entropy": summarize_entropy(data),
                    "ipv4": ipv4,
                    "mac": mac,
                    "ports": ports,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"\n完整结果已写入: {args.json}")


if __name__ == "__main__":
    main()
