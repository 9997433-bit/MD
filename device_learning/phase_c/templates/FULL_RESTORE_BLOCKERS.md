# 完全还原 — 可复现阻塞实验清单

> **声明：目录完整 ≠ 厂商等价 ≠ 掌握运行行为。**  
> 被动 USB + FX2 RAM 证据已尽量挖尽；下列实验是继续提升还原度的**硬门禁**。每项写清输入、步骤、成功判据与产出路径，便于实机复现。

关联：[`RESTORE_PROGRESS.md`](RESTORE_PROGRESS.md) · [`DSA_REFERENCE_FUNCTION_PLAN.md`](DSA_REFERENCE_FUNCTION_PLAN.md) · [`ACQUISITION_ROADMAP.md`](ACQUISITION_ROADMAP.md)

## 总原则

- 每次实验单独目录：`phase_c/runs/<date>_<id>/`（pcap、笔记、激励照片/设置）。  
- 同步抓 `usb_session`；保留 `protocol_log` 手工补注。  
- 结论升 `candidate` 需：原始哈希 + 本清单条目 ID + 人工审阅。  
- **禁止**无激励推断伏特/通道图；**禁止**写入敏感型号数字串。

---

### B1 — 单通道已知正弦（打包 + 标定）

| 项 | 内容 |
|----|------|
| **目的** | 验证 `P1_BE32_SHIFT7_SCALAR`；求码值→伏特；判符号 |
| **输入** | AI0 注入已知 f、A 正弦；其余通道接地/开路（记录）；主机按既有 arm 链启动 |
| **步骤** | 1) 抓 USB 全程 2) `unpack_ep84_candidate.py` 解包 3) FFT/过零测频 4) 幅度比对数个 A |
| **成功判据** | 解包频谱峰与注入 f 误差有界；幅度近似线性；文档化 scale/offset |
| **产出** | `phase_c/runs/.../notes.md` + 更新 `ep84_packing_deep` 旁证 |
| **解锁** | 样本物理单位、符号 |

### B2 — 四通道共源（交织 / 通道图）

| 项 | 内容 |
|----|------|
| **目的** | 确认 interleave=1 是否错误；映射 AI0..3 ↔ 字流 |
| **输入** | 共源正弦；或三路接地 + 一路正弦轮转 |
| **步骤** | 对照 `ep01_body_semantics` 中 `0c03` 索引 0..3 的配置命令与 EP84 字流 |
| **成功判据** | 单一有源通道时能量只落在预测字位置；四通道偏斜可重复 |
| **产出** | 通道图 JSON |
| **解锁** | `channel_map_and_sync` |

### B3 — 白名单重放 arm 配方

| 项 | 内容 |
|----|------|
| **目的** | 证明 `0x01→0x0f→0x08→…` 为充分启动序列 |
| **输入** | `ep01_stream_arm_sequence.json` representative recipe；只读/低风险子集 |
| **步骤** | dry-run → 实机白名单发送 → 观察是否出现 EP84 burst |
| **成功判据** | 无意外状态；burst 可复现；失败可诊断 |
| **产出** | 最小配方 + 事务日志 |
| **解锁** | opcode 启停语义 |

### B4 — 采样率阶梯

| 项 | 内容 |
|----|------|
| **目的** | 找到主机请求的 fs 字段（疑在 `0c0f`/`0c10` TLV） |
| **输入** | 官方栈或自研配置多档 fs；或暴力关联 body u32 与 EP84 字节率 |
| **成功判据** | 至少 3 档 fs 下，body 字段与 `sustained_bytes_per_s` 单调对应 |
| **解锁** | Host-requested fs |

### B5 — EEPROM 物理 dump（L7）

| 项 | 内容 |
|----|------|
| **目的** | 持久固件真源 |
| **输入** | 授权；按 `phase_b/templates/eeprom_read.md` |
| **成功判据** | `eeprom.bin` 哈希稳定；C2 记录可解析 |
| **解锁** | 符号/表之外的固件对齐 |

### B6 — 耦合 / IEPE / 触发 / AO（功能面）

见 `DSA_REFERENCE_FUNCTION_PLAN.md` 专题 P-COUPLE / P-IEPE / P-TRIG / P-STIM。  
在 B1–B3 完成前优先级低于打包与通道。

---

## 被动证据已穷尽的边界（勿重复空转）

在无新 pcap / 无 B1–B5 之前，下列分析视为**已达被动上限**：

1. EP84 字结构评分与吞吐估 fs  
2. EP01 arm 窗口共识 opcode 链  
3. EP01/81 tag 配对与 `0x0c` TLV / `0c03` 通道索引候选  
4. FX2 `0x1435` FIFO 微操作与 lite CFG  
5. 架构草图（BNC→ADC→FPGA→FX2→USB）

新增工作应优先：**新激励抓包**或 **EEPROM**，而不是再扫同一 `usb_session.pcapng`。
