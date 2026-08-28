# Must 完成审计（当前 · 未达成）

> 对照 `算法与ADCDAC实现_研究计划.md` §5 **最低合格（Must）**。  
> 审计时刻：2026-08-28（SPI auto-map / inbox 加固后复审）；证据以仓库现文件 + `g2_inbox` 根目录无实测为准。  
> 结论：**Must 未达成 → 总目标未完成。禁止标 complete。**

---

## Must-1：P1.1–P1.4 均 ✅ 或强 🔶

| 命题 | 当前 | 权威证据 | 判定 |
|------|------|----------|------|
| P1.1 模拟拓扑 | 🔶 | `G0_命题基线证据表.md` §1.1；BOM/信号链照片 | **未达 ✅**；强 🔶 可辩，但通道一一对应未蜂鸣 |
| P1.2 DDR LVDS | 🔶 | 同 §1.2；datasheet 排除法 | **未达 ✅**（标准要求边沿/ILA） |
| P1.3 样钟/更新钟 | ❓ | 同 §1.3；`g2_inbox` **无**可用 `g2_clocks.json`（非全 null） | **缺口** — 无测频 Hz |
| P1.4 SPI 模式 | ❓ | 同 §1.4；根目录 **无** `spi_capture.csv`（`examples/` 为合成，ingest 忽略） | **缺口** — 无 SPI 帧 |

**Must-1 总判：失败**（P1.3、P1.4 仍 ❓）。

解锁：`05_tests/g2_inbox/` 根目录 + `scripts/ingest_g2_inbox.py`（见 `G2_资源门禁_用户动作.md`）。  
管线自检：`decode_spi_capture.py --self-test`（含 `--auto-map`）✅；**不等于** P1.4 实测。

---

## Must-2：P2 排除表（哪些算法不像）

| 项 | 状态 | 证据 |
|----|------|------|
| 细假说排除（ROM/MIF/大 BRAM 软核/硬编码网常量/明文 IP 标签） | ✅ 已有 | `G3G4_算法判别矩阵.md` §4.1 |
| **算法模块**排除（FFT/DDC/FIR/…） | ❌ 空 | §4.2 仍空；须 G3/G4 |

**Must-2 总判：部分** — 细假说到，模块排除未到。按原文「哪些算法不像」，模块行空则 **未完全满足**。

---

## Must-3：第三人可按记录复现关键实验

| 项 | 状态 |
|----|------|
| Day-1 / G2 / G3 步骤与脚本 | ✅ 文档+脚本在库（含 auto-map / examples 演练） |
| 已完成实验的原始数据+哈希 | ❌ 无钟/SPI/单音落盘 |

**Must-3 总判：失败**（无可复现实测记录，仅有方案）。

---

## 环境核验（本审计执行时）

```text
g2_inbox 根: 仅 template/README（ingest exit 2）
g2_inbox/examples: 合成 CSV（非实测；ingest 忽略）
USB/板卡: 无
Montyzhang/zero0000: 仍仅 mcs+照片（最新 commit 2026-08-28 上传）
分支: cursor/zero0000-research-7055
```

---

## 下一步（唯一能翻转 Must-1 的动作）

1. 用户投放 `g2_clocks.json`（至少 C2 或 C3 非 null）与/或根目录 `spi_capture.csv`  
2. `python3 scripts/ingest_g2_inbox.py`  
3. 人工复核后回填 G0 → 再开本审计为「Must-1 通过」  

在此之前：**保持 goal active，不做空静态扫描。**
