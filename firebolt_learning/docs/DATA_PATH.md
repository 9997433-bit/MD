# 数据路径综合（静态，不抓包）

> 目标：在规格 + 固件静态证据下，讲清「多通道同步采集」从模拟输入到主机的路径。  
> **目录完整 ≠ 厂商等价 ≠ 掌握运行行为**

## 端到端路径

```
AI0..31 ──► 16×ADC（共享 sample clock convert）──► Artix-7 FPGA
                                                      │ 组帧 / FIFO(8191) / 触发与 bank
                                                      │ GPIF / 寄存器 (candidate)
                                                      ▼
                                                 FX3 CYUSB3014
                                            ┌─────┴──────┐
                                            │ Fusion@EP0 │  控制面（vendor class）
                                            │ Bulk EPx   │  数据面（Signal Stream 假设）
                                            └─────┬──────┘
                                                  ▼
                                              Host DAQmx
                                           （本包 not_started）
```

## 规格钉死的同步段（confirmed）

| 段 | 结论 | ID |
|----|------|-----|
| 转换 | 最多 16 路真同时；SE 冲突 → bank + AIConv | `SPEC-SIM-*` / `SPEC-BANK` |
| 时基 | sample clock；PFI 可作触发/时钟 | `SPEC-TIMING-RES` / `SPEC-PFI-TRIG` |
| 缓冲 | 共享 FIFO 8191 | `SPEC-FIFO-AI` |
| 上送名 | USB Signal Stream | `SPEC-XFER-STREAM` |

## 固件钉死的 USB 形状（confirmed，本轮静态）

来源：`manifests/fx3_static_re.json`（设备描述符 @ file `0x45328`）

| 项 | 值 |
|----|-----|
| VID:PID | `0x3923:0x7B44` |
| bcdUSB | `0x0210`（镜像内为 USB2 视图） |
| bDeviceClass | 0（接口里出类） |
| Interface | 1 × class **255**（vendor specific） |
| Endpoints | **16**（15×bulk + 1×interrupt IN `0x82`） |
| wMaxPacketSize | 描述符均为 **64**（见下） |
| bMaxPower | 250→500 mA（USB2 总线供电编码） |

**解读（学习口径）：**

1. **控制面**：vendor-specific 接口 + EP0 → 与 `Fusion` / `tFusionVendorDeviceRequest` 符号一致；具体 bRequest 仍 `unknown`（不抓包）。
2. **数据面**：大量 bulk 端点与「多 DMA 流 / Signal Stream」叙事相容（`candidate` 到帧格式为止）。
3. **包长 64**：与 SuperSpeed 典型 1024 不符——可能是镜像中的 **USB2 配置表**、运行时再协商、或另有 SS 描述符未嵌入此 `.cfg`。不得据此否认 USB-C/SS 产品形态；只记录「此固件镜像内可见描述符如此」。

## FX3 vs FPGA 职责（confirmed 综合）

| 职责 | 位置 |
|------|------|
| 同源 convert / bank / FIFO 实时 | FPGA（+ADC） |
| 上电加载 bitstream、寄存器 poke、DMA↔USB | FX3 |
| 采样时基引擎 | **不在** FX3 ARM（无 sample/sync 字符串角色） |

## 本轮仍不能写穿的点

见 `manifests/pending_index.json`：`FX3-FUSION-REQ`、`USB-FRAME-LAYOUT`、`FX3-REGMAP`、`BIT-SYNC-CLOCK-TREE` 等。  
强制 null 桥见 `BRIDGE_REPORT.md`。

## 建议阅读顺序

1. `docs/spec_sync_model.md` / `docs/sync_state_machine.md`  
2. 本文  
3. `docs/fx3_role_map.md` + `docs/LEARN_ANSWERS.md`  
4. `OMISSIONS_AND_REMAINING.md`（下一步手段）
