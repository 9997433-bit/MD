# FX3 PIB/GPIF 与 Cypress 公开头文件交叉对照

> 本轮用公开 `pib_regs.h` / `gpif_regs.h` 校正此前 MMIO 解读，避免把 reserved 空隙误当成具名寄存器块。

## 官方布局（Cypress SDK）

| 区域 | 地址 | 作用 |
|------|------|------|
| PIB core | `0xE0010000` | config / intr / mailbox |
| GPIF | `0xE0014000` | bus/thread/waveform |
| PP mode | `0xE0017E00+` | mailbox、**PP_MMIO_ADDR/DATA**（外设/FPGA 窗） |
| DMA sockets | `0xE0018000 + n×0x80` | 32 个 socket，步长 **128** |

参考：`nickdademo/cypress-fx3-sdk-linux` → `pib_regs.h`。

## 固件字面量命中（confirmed 存在）

| 地址 | 名称 | 固件中 |
|------|------|--------|
| `0xE0010000` | PIB_CONFIG | 有 |
| `0xE0014000` | GPIF_CONFIG | 有 |
| `0xE0014004` | GPIF_BUS_CONFIG | 有 |
| `0xE0018000` | SCK0 | 有 |
| `0xE0018010` | SCK0_INTR | 有 |
| `0xE0017F04` | PIB_POWER | 有 |

详见 `manifests/fx3_pib_crossref.json`。

## 需要纠正/降级的说法

1. **`0xE0011000`**：落在公开头文件 `rsrvd0[]` 空隙内，**无官方字段名**。固件确有读写，但不得再写成“标准 PIB 配置块具名基址”；语义保持 `candidate`。
2. **socket 步长**：官方 DMA socket 为 `×0x80` @ `0xE0018000`。先前 `0xE0010000 + index<<4` 是另一处反汇编模式，**两套并存**，不可强行合并。
3. **PP_MMIO_ADDR/DATA**（`0xE0017E3C/40`）：公开文档里这是进 FPGA/外部空间的窗；**本镜像未出现绝对字面量**。可能经基址+偏移访问，或走 GPIF ingress/egress——仍 `unknown`。

## 对同步采集学习的意义

- 仍然成立：样本路径经 **GPIF/PIB sockets → FX3 DMA → USB**；同步不在 ARM。
- 新增：可用 Cypress 符号名称呼固件里的 GPIF/socket 锚点，便于后续 Ghidra 标注。
- 未解：哪几个 socket 承载 AI 流、Fusion 如何触发 PP_MMIO/GPIF 编程。

## 产物

- `scripts/analyze_fx3_pib_crossref.py`
- `manifests/fx3_pib_crossref.json`
