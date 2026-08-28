# 采集链路还原进度

> **声明：目录完整 ≠ 厂商等价 ≠ 掌握运行行为。**
> 自动刷新于 `2026-08-28T14:40:30.950273+00:00`。整体还原估计 **42%**（启发式，非厂商等价）。

## 分层状态

| 层 | 已还原 | 置信 | 仍缺 |
|----|--------|------|------|
| `USB_command_plane` | framing + opcode inventory + arm-window consensus + 0x0c TLV/body pairing | candidate | opcode semantics proof via replay; stimulus-linked field meanings |
| `USB_data_plane_bytes` | EP84 as primary sample bulk IN; length%4==0; headerless BE32>>7 top model | candidate | volts scale, signedness, channel interleave proof |
| `FX2_firmware_path` | 0x1435 hub FIFO/EP micro-ops; init→0x1435; opcode imm sites | candidate | full CFG, indirect calls, eeprom.bin |
| `joint_oracle` | 0x08 owner ∩ 0x1435 ∩ EP84-precede | candidate | proof 0x08 is start vs FIFO constant |
| `analog_frontend_FPGA` | architecture sketch only (BNC→relay→ADC→FPGA→FX2) | hypothesis | bitstream behavior, coupling/IEPE/trigger experiments |
| `host_output_API` | API sketch mapped to EP01/81 + EP84 | hypothesis | working open-source stack validated on live device |

## 当前最强候选

- 打包：`P1_BE32_SHIFT7_SCALAR` — EP84 is a headerless stream of big-endian 32-bit words with seven low zero bits (structural >>7 values); channel interleave 1.
- 启动链（首现）：`0x01 → 0x0f → 0x08 → 0x09 → 0x0a → 0x0b → 0x10 → 0x04`
- 固件枢纽：`0x1435`（FIFO/EP micro-ops + oracle 与 `0x08` 关联）
- 命令体：`0x0c` TLV；`0c03` 索引 0..3 为通道候选；EP81 状态前缀多为 `u32be==2`

## 完全还原阻塞

可复现实验清单：[`phase_c/templates/FULL_RESTORE_BLOCKERS.md`](phase_c/templates/FULL_RESTORE_BLOCKERS.md)

**被动证据已穷尽**（无新激励 pcap / EEPROM 前勿重复空扫同一 session）。

- No known-stimulus capture to validate scale, offset, signedness, or units
- Byte3 bit7 meaning (aux flag vs numeric LSB) not separable from passive data
- Channel count / mapping not identifiable without single-channel stimulus
- Opcode semantics for stream arm/config remain unlabeled
- Host-requested fs not present in this capture metadata
- No controlled stimulus capture in phase_b/captures/
- eeprom.bin still missing (L7)
- Cannot auto-upgrade to confirmed under catalog policy

## 下一步

1. Lab B1: known sine/DC on AI0 alone → validate packing + scale
1. Lab B2: 4ch common-source / single-hot → channel map vs 0c03 index
1. Lab B3: Replay white-list arm recipe from ep01_stream_arm_sequence.json
1. Lab B5: Physical eeprom.bin dump for L7 firmware truth

## 相关 manifests

- `manifests/restore_crosscheck.json`
- `manifests/ep84_packing_deep.json`
- `manifests/ep01_stream_arm_sequence.json`
- `manifests/ep01_body_semantics.json`
- `manifests/fx2_stream_path.json`
- `manifests/ep84_unpack_preview.json`
