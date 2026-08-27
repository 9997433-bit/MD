# 实机接入指南

**阶段**：静态分析已完成 → 等待阶段 B 实机证据  
**声明**：目录完整 ≠ 厂商等价 ≠ 掌握运行行为

## 你需要准备

| 物品 | 用途 |
|------|------|
| 实物设备 | EEPROM 读取、USB 抓包 |
| EEPROM 读取器（或 FX2 编程夹具） | 读出 24LC64 完整镜像 |
| USB 抓包主机（Linux 推荐） | Wireshark / usbmon |
| 合法分析授权 | 仅在你有权分析的范围内操作 |

## 三步接入

### 1. 放置采集文件

```text
device_learning/phase_b/captures/
├── eeprom.bin          # 8192 字节（24LC64 全片）
├── usb_enum.pcapng     # 枚举场景
├── usb_session.pcapng  # 工作/配置场景
└── protocol_log.json   # 可选：手工整理的命令记录
```

模板见 `phase_b/templates/`。

### 2. 刷新账本

```bash
cd device_learning
python3 scripts/ingest_phase_b.py
python3 scripts/analyze_pcap_stub.py
python3 scripts/generate_ledger.py
python3 -m pytest tests/ -q
```

### 3. 深化分析（采集后）

| 产物 | 工具 / 动作 |
|------|-------------|
| 8051 固件 | Ghidra（8051 处理器）→ `phase_b/analysis/mcu_disasm.txt` |
| USB 协议 | Wireshark 解析 → 回填 PROTO-* / SIG-* |
| 驱动解包 | 合法授权下解包 → `phase_b/driver/` |

## 验收检查

- `manifests/phase_b_status.json` → `flags.eeprom_present` 或 `usb_capture_present` 为 true
- `manifests/firmware_scan.json` → `status: observed`（非 synthetic）
- `manifests/usb_capture_meta.json` → `status: observed`
- `coverage.json` → `phase` 可升级为 `phase_b_in_progress`

## 诚实边界

- 合成夹具（`phase_b/fixtures/`）仅用于流水线测试，**不代表设备真相**
- 抓包观察 ≠ 协议完全理解
- 未采集项保持 `unknown` / `missing`，见 `OMISSIONS_AND_REMAINING.md`
- 强制 null 桥（`bridge_matrix.json`）在无新证据前不得升级

## 阶段 C

采集完成后按 `phase_c/README.md` 设计实验，将 `hypothesis` / `candidate` 升级为 `confirmed` 或 `refuted`。
