# 系统架构图（自动生成）

**生成时间**：2026-08-27 16:24 UTC

> 目录完整 ≠ 厂商等价 ≠ 掌握运行行为

```mermaid
flowchart LR
  NODE-IN -->|"analog (candidate)"| NODE-RELAY
  NODE-RELAY -->|"analog (candidate)"| NODE-ADC
  NODE-ADC -->|"digital (hypothesis)"| NODE-FPGA
  NODE-FPGA -->|"slave_fifo (hypothesis)"| NODE-USB-CTL
  NODE-USB-CTL -->|"[redacted] (not_started)"| NODE-HOST
```

## 节点

| Node | Layer | Status |
|------|-------|--------|
| `NODE-IN` | hw | confirmed |
| `NODE-RELAY` | hw | candidate |
| `NODE-ADC` | hw | candidate |
| `NODE-FPGA` | bit | confirmed |
| `NODE-USB-CTL` | hw | confirmed |
| `NODE-HOST` | usb | not_started |

证据来源：`manifests/system_map.json`

