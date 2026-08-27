# 8051 固件反汇编指南（阶段 B）

**前提**：已从板载 EEPROM 获得真实 `eeprom.bin`，且 `eeprom_meta.json` 显示 `status: observed`。

## 提取固件切片

```bash
cd device_learning
python3 scripts/analyze_eeprom.py
# 查看 manifests/eeprom_meta.json 中的 firmware_offset / firmware_size_bytes
```

C2 格式下固件位于数据记录 payload；C0 格式无板载固件镜像。

## Ghidra 步骤

1. 安装 Ghidra + 8051 处理器模块（或 ghidra_8051 扩展）
2. File → Import File → 导出固件二进制切片
3. Language：**8051:LE:16:default**
4. 入口：reset vector `0x0000`（C2 首记录加载地址以 meta 为准）
5. 标注 I/O 端口访问（0xE6xx FX2LP 寄存器空间）

## 产出

- 反汇编文本 → `phase_b/analysis/mcu_disasm.txt`
- 关键发现登记到 `phase_b/captures/protocol_log.json` 或账本 FW-* 项

## 诚实边界

- 反汇编入口 ≠ 掌握全部固件逻辑
- 合成夹具（`phase_b/fixtures/`）**不得**用于声称设备行为
- 无实机转储前 FW-MCU-* 保持 `missing`
