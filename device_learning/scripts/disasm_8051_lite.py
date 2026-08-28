#!/usr/bin/env python3
"""Minimal MCS-51 disassembler for FX2 RAM region dumps (not a full Ghidra)."""
from __future__ import annotations

# opcode -> (mnemonic_fmt with {0} {1} placeholders, size)
# Based on public Intel MCS-51 instruction set; incomplete but covers common FX2 code.

def _ajmp(op: int, b1: int) -> str:
    page = (op >> 5) & 7
    addr = (page << 8) | b1
    return f"AJMP 0x{addr:04x}"


def _acall(op: int, b1: int) -> str:
    page = (op >> 5) & 7
    addr = (page << 8) | b1
    return f"ACALL 0x{addr:04x}"


def disasm_one(data: bytes, pc: int) -> tuple[str, int]:
    if pc >= len(data):
        return ("??? ", 1)
    op = data[pc]
    n = len(data) - pc

    def b(i: int) -> int:
        return data[pc + i] if n > i else 0

    # 1-byte
    one = {
        0x00: "NOP",
        0x04: "INC A",
        0x06: "INC @R0",
        0x07: "INC @R1",
        0x14: "DEC A",
        0x16: "DEC @R0",
        0x17: "DEC @R1",
        0x22: "RET",
        0x26: "ADD A,@R0",
        0x27: "ADD A,@R1",
        0x32: "RETI",
        0x36: "ADDC A,@R0",
        0x37: "ADDC A,@R1",
        0x84: "DIV AB",
        0xA4: "MUL AB",
        0xA5: "reserved",
        0xC4: "SWAP A",
        0xD4: "DA A",
        0xE4: "CLR A",
        0xF4: "CPL A",
        0xC3: "CLR C",
        0xD3: "SETB C",
        0xB3: "CPL C",
        0x23: "RL A",
        0x03: "RR A",
        0x33: "RLC A",
        0x13: "RRC A",
        0xA3: "INC DPTR",
        0x93: "MOVC A,@A+DPTR",
        0x83: "MOVC A,@A+PC",
        0xE0: "MOVX A,@DPTR",
        0xF0: "MOVX @DPTR,A",
        0xE2: "MOVX A,@R0",
        0xE3: "MOVX A,@R1",
        0xF2: "MOVX @R0,A",
        0xF3: "MOVX @R1,A",
    }
    if op in one:
        return (one[op], 1)
    if 0x08 <= op <= 0x0F:
        return (f"INC R{op - 0x08}", 1)
    if 0x18 <= op <= 0x1F:
        return (f"DEC R{op - 0x18}", 1)
    if 0xE8 <= op <= 0xEF:
        return (f"MOV A,R{op - 0xE8}", 1)
    if 0xF8 <= op <= 0xFF:
        return (f"MOV R{op - 0xF8},A", 1)
    if 0xC8 <= op <= 0xCF:
        return (f"XCH A,R{op - 0xC8}", 1)
    if 0x28 <= op <= 0x2F:
        return (f"ADD A,R{op - 0x28}", 1)
    if 0x38 <= op <= 0x3F:
        return (f"ADDC A,R{op - 0x38}", 1)
    if 0x68 <= op <= 0x6F:
        return (f"XRL A,R{op - 0x68}", 1)
    if 0x58 <= op <= 0x5F:
        return (f"ANL A,R{op - 0x58}", 1)
    if 0x48 <= op <= 0x4F:
        return (f"ORL A,R{op - 0x48}", 1)

    # AJMP / ACALL (a10)
    if (op & 0x1F) == 0x01 and n >= 2:
        return (_ajmp(op, b(1)), 2)
    if (op & 0x1F) == 0x11 and n >= 2:
        return (_acall(op, b(1)), 2)

    # common 2-byte
    if op == 0x02 and n >= 3:  # LJMP
        return (f"LJMP 0x{(b(1) << 8) | b(2):04x}", 3)
    if op == 0x12 and n >= 3:  # LCALL
        return (f"LCALL 0x{(b(1) << 8) | b(2):04x}", 3)
    if op == 0x90 and n >= 3:  # MOV DPTR,#
        return (f"MOV DPTR,#0x{(b(1) << 8) | b(2):04x}", 3)
    if op == 0x74 and n >= 2:
        return (f"MOV A,#0x{b(1):02x}", 2)
    if op == 0x75 and n >= 3:
        return (f"MOV 0x{b(1):02x},#0x{b(2):02x}", 3)
    if op == 0x85 and n >= 3:
        return (f"MOV 0x{b(2):02x},0x{b(1):02x}", 3)
    if op == 0x05 and n >= 2:
        return (f"INC 0x{b(1):02x}", 2)
    if op == 0x15 and n >= 2:
        return (f"DEC 0x{b(1):02x}", 2)
    if op == 0xE5 and n >= 2:
        return (f"MOV A,0x{b(1):02x}", 2)
    if op == 0xF5 and n >= 2:
        return (f"MOV 0x{b(1):02x},A", 2)
    if op == 0x25 and n >= 2:
        return (f"ADD A,0x{b(1):02x}", 2)
    if op == 0x24 and n >= 2:
        return (f"ADD A,#0x{b(1):02x}", 2)
    if op == 0x35 and n >= 2:
        return (f"ADDC A,0x{b(1):02x}", 2)
    if op == 0x34 and n >= 2:
        return (f"ADDC A,#0x{b(1):02x}", 2)
    if op == 0x54 and n >= 2:
        return (f"ANL A,#0x{b(1):02x}", 2)
    if op == 0x55 and n >= 2:
        return (f"ANL A,0x{b(1):02x}", 2)
    if op == 0x44 and n >= 2:
        return (f"ORL A,#0x{b(1):02x}", 2)
    if op == 0x45 and n >= 2:
        return (f"ORL A,0x{b(1):02x}", 2)
    if op == 0x64 and n >= 2:
        return (f"XRL A,#0x{b(1):02x}", 2)
    if op == 0x65 and n >= 2:
        return (f"XRL A,0x{b(1):02x}", 2)
    if op == 0xB4 and n >= 3:
        rel = b(2) - 256 if b(2) > 127 else b(2)
        return (f"CJNE A,#0x{b(1):02x},0x{pc + 3 + rel:04x}", 3)
    if op == 0xB5 and n >= 3:
        rel = b(2) - 256 if b(2) > 127 else b(2)
        return (f"CJNE A,0x{b(1):02x},0x{pc + 3 + rel:04x}", 3)
    if op == 0x60 and n >= 2:
        rel = b(1) - 256 if b(1) > 127 else b(1)
        return (f"JZ 0x{pc + 2 + rel:04x}", 2)
    if op == 0x70 and n >= 2:
        rel = b(1) - 256 if b(1) > 127 else b(1)
        return (f"JNZ 0x{pc + 2 + rel:04x}", 2)
    if op == 0x80 and n >= 2:
        rel = b(1) - 256 if b(1) > 127 else b(1)
        return (f"SJMP 0x{pc + 2 + rel:04x}", 2)
    if op == 0x40 and n >= 2:
        rel = b(1) - 256 if b(1) > 127 else b(1)
        return (f"JC 0x{pc + 2 + rel:04x}", 2)
    if op == 0x50 and n >= 2:
        rel = b(1) - 256 if b(1) > 127 else b(1)
        return (f"JNC 0x{pc + 2 + rel:04x}", 2)
    if op == 0xD5 and n >= 3:
        rel = b(2) - 256 if b(2) > 127 else b(2)
        return (f"DJNZ 0x{b(1):02x},0x{pc + 3 + rel:04x}", 3)
    if 0xD8 <= op <= 0xDF and n >= 2:
        rel = b(1) - 256 if b(1) > 127 else b(1)
        return (f"DJNZ R{op - 0xD8},0x{pc + 2 + rel:04x}", 2)
    if 0x78 <= op <= 0x7F and n >= 2:
        return (f"MOV R{op - 0x78},#0x{b(1):02x}", 2)
    if 0xA8 <= op <= 0xAF and n >= 2:
        return (f"MOV R{op - 0xA8},0x{b(1):02x}", 2)
    if 0x88 <= op <= 0x8F and n >= 2:
        return (f"MOV 0x{b(1):02x},R{op - 0x88}", 2)
    if op == 0x76 and n >= 2:
        return (f"MOV @R0,#0x{b(1):02x}", 2)
    if op == 0x77 and n >= 2:
        return (f"MOV @R1,#0x{b(1):02x}", 2)
    if op == 0x86 and n >= 2:
        return (f"MOV 0x{b(1):02x},@R0", 2)
    if op == 0x87 and n >= 2:
        return (f"MOV 0x{b(1):02x},@R1", 2)
    if op == 0xF6:
        return ("MOV @R0,A", 1)
    if op == 0xF7:
        return ("MOV @R1,A", 1)
    if op == 0xE6:
        return ("MOV A,@R0", 1)
    if op == 0xE7:
        return ("MOV A,@R1", 1)
    if op == 0xC0 and n >= 2:
        return (f"PUSH 0x{b(1):02x}", 2)
    if op == 0xD0 and n >= 2:
        return (f"POP 0x{b(1):02x}", 2)
    if op == 0xC2 and n >= 2:
        return (f"CLR 0x{b(1):02x}", 2)
    if op == 0xD2 and n >= 2:
        return (f"SETB 0x{b(1):02x}", 2)
    if op == 0xB2 and n >= 2:
        return (f"CPL 0x{b(1):02x}", 2)
    if op == 0x20 and n >= 3:
        rel = b(2) - 256 if b(2) > 127 else b(2)
        return (f"JB 0x{b(1):02x},0x{pc + 3 + rel:04x}", 3)
    if op == 0x30 and n >= 3:
        rel = b(2) - 256 if b(2) > 127 else b(2)
        return (f"JNB 0x{b(1):02x},0x{pc + 3 + rel:04x}", 3)
    if op == 0x10 and n >= 3:
        rel = b(2) - 256 if b(2) > 127 else b(2)
        return (f"JBC 0x{b(1):02x},0x{pc + 3 + rel:04x}", 3)

    # fallback
    return (f"DB 0x{op:02x}", 1)


def disasm_region(data: bytes, start: int, length: int, max_insns: int = 200) -> list[dict]:
    pc = start
    end = min(len(data), start + length)
    out = []
    for _ in range(max_insns):
        if pc >= end:
            break
        text, size = disasm_one(data, pc)
        raw = data[pc : pc + size]
        out.append({"addr": f"0x{pc:04x}", "bytes": raw.hex(), "text": text})
        pc += max(1, size)
    return out
