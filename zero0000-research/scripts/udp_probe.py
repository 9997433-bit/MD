#!/usr/bin/env python3
"""L4 prep: UDP probe scaffold for ethernet control/data plane."""
from __future__ import annotations

import argparse
import socket
import time


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bind", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=50000)
    ap.add_argument("--seconds", type=float, default=5.0)
    ap.add_argument("--send-to", default="", help="host:port to send probe")
    args = ap.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.bind, args.port))
    sock.settimeout(0.5)
    print(f"listening udp://{args.bind}:{args.port} for {args.seconds}s")

    if args.send_to:
        host, port_s = args.send_to.rsplit(":", 1)
        sock.sendto(b"PROBE\n", (host, int(port_s)))
        print("sent PROBE")

    end = time.time() + args.seconds
    n = 0
    while time.time() < end:
        try:
            data, addr = sock.recvfrom(65535)
            n += 1
            print(f"#{n} from {addr} len={len(data)}")
        except socket.timeout:
            pass
    print(f"done packets={n}")


if __name__ == "__main__":
    main()
