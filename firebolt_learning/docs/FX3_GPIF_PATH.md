# FX3 → FPGA 桥接路径（PIB/GPIF 静态）

> 本轮目标：在不抓包前提下，把「样本如何离开 FPGA」从口头假设推进到 **片上外设证据**。  
> 寄存器级 FPGA fabric map 仍为 unknown。

## 结论摘要

| 层 | 证据 | 等级 |
|----|------|------|
| USB 引擎 | 大量字面量 `0xE0030000` / `0xE0033000`（UIB） | confirmed |
| 时钟/系统 | `0xE0050000`（GCTL） | confirmed |
| **FPGA 数据/控制桥** | `0xE0010000`（PIB/GPIF）+ **socket×16** 寻址 | confirmed（桥） / fabric map 仍 unknown |
| Fusion 字段 | 仅有符号 | unknown（需抓包） |

## 关键反汇编证据

VA `0x400115F8` 一带（映像基址 addend `0x3FFD6000`）：

```
lsl r3, r0, #4
add r3, r3, #0xe0000000
add r3, r3, #0x10000
; => r3 = 0xE0010000 + socket_index * 16
```

这是 Cypress FX3 **PIB socket 寄存器块**的典型步长，说明固件按 socket 索引访问 GPIF 侧硬件——正是 FPGA 通过 GPIF-II 挂接 FX3 时的片上窗口。

另见 `0x40011400`：`ldr r2, [r3, #0x4000]` 形式访问 PIB 窗口内偏移，属于同一外设族。

## 与同步采集目标的关系

```
ADC 同源 convert ──► FPGA FIFO/组帧 ──► GPIF sockets ──► PIB@0xE0010000
                                                         │
                                                         ▼
                                              FX3 DMA 线程 / UIB
                                                         │
                                                         ▼
                                              USB bulk pipes（见 DATA_PATH）
```

- **同步仍然发生在 ADC+FPGA**，本轮不改变 `SPEC-SYNC-LAYER`。
- 本轮补齐的是：**FX3 侧如何“够到”FPGA**（PIB/GPIF），从而把 `NODE-FPGA → NODE-FX3` 边从纯假设推进到 **candidate/confirmed-bridge**。
- **不能**把 `0xE0010000+n*16` 误当成 AIConv/通道寄存器表（那是 fabric 内地址，仍 `FX3-REGMAP=unknown`）。

## 产物

- `manifests/fx3_mmio_map.json`
- `scripts/analyze_fx3_mmio.py`
- catalog：`FX3-PIB-*` / `FX3-UIB-*` / `FX3-GCTL-*`
