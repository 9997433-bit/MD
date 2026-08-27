# 阶段 B：实机证据采集

**前提**：需要实物设备、EEPROM 读取器、USB 抓包环境。  
**声明**：本阶段产物将升级 FW/PROTO 层 status，但不自动升级为厂商等价。

## 检查清单

| # | 任务 | 产出 | 模板 |
|---|------|------|------|
| B1 | 读取板载 EEPROM | `phase_b/captures/eeprom.bin` | [eeprom_read.md](templates/eeprom_read.md) |
| B2 | 8051 固件反汇编 | `phase_b/analysis/mcu_disasm.txt` | — |
| B3 | USB 枚举抓包 | `phase_b/captures/usb_enum.pcapng` | [usb_capture.md](templates/usb_capture.md) |
| B4 | 配置/采集命令抓包 | `phase_b/captures/usb_session.pcapng` | [usb_capture.md](templates/usb_capture.md) |
| B5 | 命令记录 | `phase_b/captures/protocol_log.json` | [protocol_log_template.json](templates/protocol_log_template.json) |
| B6 | 驱动解包 | `phase_b/driver/` | — |

## 操作

1. 按模板读取 EEPROM / 抓包
2. 将文件放入 `phase_b/captures/`
3. 运行 `python3 scripts/ingest_phase_b.py`
4. 运行 `python3 scripts/analyze_pcap_stub.py`
5. 运行 `python3 scripts/generate_ledger.py`

## 诚实边界

- 抓包观察 ≠ 协议完全理解
- 反汇编入口 ≠ 掌握全部固件逻辑
