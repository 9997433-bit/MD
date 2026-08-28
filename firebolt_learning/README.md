# Firebolt / USB-6453 同步采集静态学习包

基于 [Montyzhang/sixfour](https://github.com/Montyzhang/sixfour) 固件转储与 USB-6453 规格书的**静态学习包**。  
目标：弄清多通道同步采集的规格语义与芯片职责划分，**不**声称厂商等价或可复现驱动。

## 声明

> **目录完整 ≠ 厂商等价 ≠ 掌握运行行为**

本阶段**不包含 USB 抓包**。抓包/实机/网表逆向仅登记在 `OMISSIONS_AND_REMAINING.md` 作为升级路径。

## 产品身份

| 项 | 值 | 证据 |
|----|-----|------|
| 正式型号 | NI USB-6453 (mioDAQ) | 规格书 + 社区 PID 对照 |
| 内部代号 | Firebolt | 固件文件名 + NI-MAX 字符串 |
| USB | VID `0x3923` PID `0x7B44` | FX3 固件设备描述符 |
| MCU | Cypress CYUSB3014 (FX3) + ThreadX ARM9 | 照片 + 固件字符串 |
| FPGA | Xilinx Artix-7 XC7A100T | bitstream IDCODE `0x0362C093` |
| 源仓库 | `Montyzhang/sixfour` | 固件与拆机照片 |

## 快速开始

```bash
cd firebolt_learning
make verify    # 扫描固件 → 生成账本 → 验收
make test      # pytest
make status    # 阶段与覆盖摘要
```

## 阶段（A→F，不抓包）

| 阶段 | 内容 | 状态 |
|------|------|------|
| A | 资产编目与哈希冻结 | 骨架已建，`make verify` 可生成 |
| B | 规格书同步功能模型 `SPEC-*` | catalog 已登记 |
| C | 硬件拓扑 / system_map | catalog + manifest 骨架 |
| D | FX3 控制面角色 | strings 锚点 catalog |
| E | FPGA bitstream 载体边界 | IDCODE confirmed，同步 HDL = unknown |
| F | bridge_matrix + OMISSIONS 闭环 | 已建强制 null 桥 |

详见 `LEARNING_GUIDE.md`、`docs/PHASE_PLAN.md`。

## 目录

| 路径 | 用途 |
|------|------|
| `firmware/` | `niusbFirebolt.cfg` / `niusbFireboltFPGA.cfg` |
| `hardware/photos/` | 可选：从 sixfour 拉取的拆机图（默认不入库） |
| `catalogs/` | SPEC / HW / FX3 / BIT / LEARN 标识符 |
| `manifests/` | 哈希、固件元数据、system_map、photo_index |
| `EvidenceLedger.json` | 主账本（由脚本生成） |
| `bridge_matrix.json` | 功能↔证据桥；含强制 null |
| `OMISSIONS_AND_REMAINING.md` | 静态阶段缺口与升级手段 |

## 停止条件（静态骨架）

1. 每条 identifier 有 `status` / `boundary`
2. SPEC 同步模型条目齐全
3. FX3 / FPGA 角色边界写清且不互相越权声称
4. `unknown` 全部进入 OMISSIONS
5. 强制 null 桥未被“猜通”
