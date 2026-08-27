# 阶段 B：实机证据采集

**前提**：需要实物设备、EEPROM 读取器、USB 抓包环境。  
**声明**：本阶段产物将升级 FW/PROTO 层 status，但不自动升级为厂商等价。

## 检查清单

| # | 任务 | 产出 | 模板 |
|---|------|------|------|
| B1 | 读取板载 EEPROM | `phase_b/captures/eeprom.bin` | [eeprom_read.md](templates/eeprom_read.md) |
| B2 | USB 枚举抓包 | `phase_b/captures/usb_enum.pcapng` | [usb_capture.md](templates/usb_capture.md) |
| B3 | 配置/采集命令抓包 | `phase_b/captures/usb_session.pcapng` | [usb_capture.md](templates/usb_capture.md) |
| B4 | 命令记录（可选） | `phase_b/captures/protocol_log.json` | [protocol_log_template.json](templates/protocol_log_template.json) |
| B5 | 账本刷新 | `make phase-b` | — |
| B6 | 8051 反汇编 | `phase_b/analysis/mcu_disasm.txt` | [ghidra_8051.md](templates/ghidra_8051.md) |

可选：[driver_unpack.md](templates/driver_unpack.md) — 合法授权下解包官方驱动，产出放 `phase_b/driver/`。

## 操作

```bash
cd device_learning
make check-captures    # 采集前预检
make phase-b           # 采集后一键刷新
```

或分步：

1. 按模板读取 EEPROM / 抓包，文件放入 `phase_b/captures/`
2. `python3 scripts/extract_firmware_slice.py`（有 eeprom.bin 时）
3. Ghidra 反汇编 → `phase_b/analysis/mcu_disasm.txt`
4. `make phase-b`

## 诚实边界

- 抓包观察 ≠ 协议完全理解
- 反汇编入口 ≠ 掌握全部固件逻辑
- 合成夹具（`phase_b/fixtures/`）仅用于流水线测试
