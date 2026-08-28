# 系统架构图（自动生成）

**生成时间**：2026-08-28T14:32:10.900699+00:00

> 目录完整 ≠ 厂商等价 ≠ 掌握运行行为

```mermaid
flowchart LR
  NODE-AI-IN -->|analog| NODE-ADC16
  NODE-ADC16 -->|shared convert clock| NODE-FPGA
  NODE-FPGA -->|GPIF/regs candidate| NODE-FX3
  NODE-FX3 -->|USB3| NODE-USB
  NODE-USB -->|not_started| NODE-HOST
```

## 节点

| Node | Layer | Status |
|------|-------|--------|
| `NODE-AI-IN` | hw | confirmed |
| `NODE-ADC16` | hw | confirmed |
| `NODE-FPGA` | bit | confirmed |
| `NODE-FX3` | fw | confirmed |
| `NODE-USB` | bus | candidate |
| `NODE-HOST` | host | not_started |

证据来源：`manifests/system_map.json`
