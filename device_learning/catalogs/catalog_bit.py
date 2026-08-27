"""Bitstream / FPGA configuration layer identifier catalog."""
from catalogs import make_entry

LAYER = "bit"


def _e(i, m, d, s, b, ev):
    return make_entry(i, LAYER, m, d, s, b, ev)


ENTRIES = [
    _e("BIT-001-FORMAT", "header", "Xilinx BIT bitstream format", "confirmed", None, "file magic"),
    _e("BIT-002-FILE-SIZE", "header", "131046 bytes total", "confirmed", None, "wc -c"),
    _e("BIT-003-SHA256", "header", "63cd3874297407bceedb524909d919dd35ba8a16639573a1af81721aed4fc3f5", "confirmed", None, "sha256sum"),
    _e("BIT-004-SOURCE-DESIGN", "header", "Source NCD design name in section b", "confirmed", None, "strings section b"),
    _e("BIT-005-TARGET-DEVICE", "header", "Spartan-3 XC3S200", "confirmed", None, "section a"),
    _e("BIT-006-PACKAGE", "header", "FT256 package", "confirmed", None, "device string"),
    _e("BIT-007-BUILD-DATE", "header", "2011/06/10", "confirmed", None, "section b"),
    _e("BIT-008-BUILD-TIME", "header", "12:44:47", "confirmed", None, "section b"),
    _e("BIT-009-USER-ID", "header", "0xFFFFFFFF", "confirmed", None, "section b"),
    _e("BIT-010-DATA-LENGTH", "header", "Config data 0x1FF88 bytes", "confirmed", None, "section d"),
    _e("BIT-011-SECTION-A", "header", "Section a device identifier", "confirmed", None, "BIT parser"),
    _e("BIT-012-SECTION-B", "header", "Section b design metadata", "confirmed", None, "BIT parser"),
    _e("BIT-013-SECTION-C", "header", "Section c part name", "confirmed", None, "BIT parser"),
    _e("BIT-014-SECTION-D", "header", "Section d configuration data", "confirmed", None, "BIT parser"),
    _e("BIT-015-CONFIG-OFFSET", "header", "Configuration data byte offset", "confirmed", None, "parse_bit_header.py"),
    _e("FRM-001-FORMAT", "frame", "Spartan-3 Type-1/Type-2 frame format", "candidate", "帧解析未完全验证", "UG332"),
    _e("FRM-002-COUNT", "frame", "Total configuration frame count", "candidate", "需完整解码器", "frame scan"),
    _e("FRM-003-WORD-WIDTH", "frame", "16-bit frame words", "confirmed", None, "Spartan-3 spec"),
    _e("FRM-004-TYPE1", "frame", "Type-1 write frames", "candidate", "计数未闭合", "frame scan"),
    _e("FRM-005-TYPE2", "frame", "Type-2 noop/pad frames", "candidate", "计数未闭合", "frame scan"),
    _e("FRM-006-STARTUP", "frame", "Startup clock cycles", "unknown", "需帧级解码", None),
    _e("FRM-007-CRC", "frame", "Embedded CRC check value", "candidate", "CRC未重算", "BIT trailer"),
    _e("FRM-008-FAR", "frame", "Frame Address Register targets", "unknown", "需完整解析", None),
    _e("FRM-009-PIPELINE", "frame", "Pipeline register settings", "unknown", None, None),
    _e("FRM-010-PADDING", "frame", "Padding/unused config bits", "candidate", None, "entropy analysis"),
    _e("IOB-001-ACTIVE-COUNT", "iob", "Estimated active IOB count", "candidate", "需IOB解码器", "heuristic"),
    _e("IOB-002-INPUTS", "iob", "Input-configured IOB pins", "unknown", None, None),
    _e("IOB-003-OUTPUTS", "iob", "Output-configured IOB pins", "unknown", None, None),
    _e("IOB-004-BIDIR", "iob", "Bidirectional IOB pins", "unknown", None, None),
    _e("IOB-005-USB-FIFO", "iob", "USB Slave FIFO bus pins", "hypothesis", "需引脚对照", "pin_hypothesis.json"),
    _e("IOB-006-ADC-IF", "iob", "ADC interface pins", "hypothesis", "需引脚对照", "pin_hypothesis.json"),
    _e("IOB-007-RELAY-GPIO", "iob", "Relay control GPIO", "hypothesis", "需切换实验", "pin_hypothesis.json"),
    _e("IOB-008-CLOCK", "iob", "Global clock input pins", "unknown", None, None),
    _e("IOB-009-RESET", "iob", "Reset input pins", "unknown", None, None),
    _e("IOB-010-UNUSED", "iob", "Unconfigured pins", "unknown", None, None),
    _e("IOB-011-BANK-0", "iob", "IO Bank 0 config", "unknown", None, None),
    _e("IOB-012-BANK-1", "iob", "IO Bank 1 config", "unknown", None, None),
    _e("IOB-013-BANK-2", "iob", "IO Bank 2 config", "unknown", None, None),
    _e("IOB-014-BANK-3", "iob", "IO Bank 3 config", "unknown", None, None),
    _e("IOB-015-PULL", "iob", "Pull-up/down settings", "unknown", None, None),
    _e("CLK-001-GCLK", "clock", "Global clock buffer usage", "unknown", None, None),
    _e("CLK-002-DIST", "clock", "Clock tree distribution", "unknown", None, None),
    _e("CLK-003-DLL", "clock", "DLL configuration", "unknown", None, None),
    _e("CLK-004-RESET", "clock", "Global reset network", "unknown", None, None),
    _e("CLK-005-DOMAINS", "clock", "Clock domain count", "unknown", None, None),
    _e("MEM-001-BRAM", "memory", "Block RAM instances", "unknown", None, None),
    _e("MEM-002-BRAM-INIT", "memory", "BRAM init content", "unknown", None, None),
    _e("MEM-003-DIST-RAM", "memory", "Distributed RAM", "unknown", None, None),
    _e("MEM-004-FIFO", "memory", "FIFO blocks", "hypothesis", "需BRAM解码", "architecture expectation"),
    _e("MEM-005-ROM", "memory", "ROM init tables", "unknown", None, None),
]
