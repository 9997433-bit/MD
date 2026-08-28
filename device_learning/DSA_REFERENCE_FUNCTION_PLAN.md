# NI USB DSA 参考规格 ↔ 本机功能映射与采集规划

> **声明：目录完整 ≠ 厂商等价 ≠ 掌握运行行为。**  
> 本文把 **NI 官方 USB 声振 DSA 设备**（产品页/规格书公开能力，订货号示例 `780164-01`：4 路 AI + 1 路 AO）当作 **功能参考清单**，对照本仓库已有 USB/照片/固件证据，给出可执行规划。  
> **不是** 声称本机已证实与某 SKU 电气/固件/驱动完全等价；仓库策略禁止把敏感产品型号数字串写入产物（见 `audit_sensitive_tokens.py`）。

## 1. 官方公开能力（参考源）

| 能力域 | 官网/规格摘要（USB DSA 4AI+1AO 类） | 参考入口 |
|--------|--------------------------------------|----------|
| 总线 | USB 2.0，总线供电（约 2.5 W max） | NI 产品页；规格书 372485 |
| AI | 4 路伪差分；BNC；±10 Vpk；24-bit Δ-Σ；**同步**采样 | 同上 |
| 采样率 | 约 **1 kS/s … 102.4 kS/s**（可强制到步长） | 规格书 Sample rates |
| 耦合 | 每通道软件可选 **AC/DC**；AC 高通约 **0.8 Hz** | 产品页 / Feature Usage |
| IEPE | 每通道 **0 / 2.1 mA**；开路/短路故障检测 | Feature Usage / Specs |
| 滤波 | 抗混叠随采样率自动调整 | Specs |
| AO | 1 路；约 ±3.5 Vpk；最高约 **96 kS/s**；可与 AI 同步（激励–响应） | Feature Usage |
| 触发 | 数字触发；**PFI&lt;0..7&gt;**，5 V TTL，上升/下降沿 | Specs |
| 软件生态 | DAQmx / Sound & Vibration / FlexLogger 等（厂商栈） | 产品页 Accessories |

规格 PDF（公开镜像示例）：`https://docs-be.ni.com/bundle/usb-443x-seri/raw/resource/enus/372485e.pdf`  
产品页：`https://www.ni.com/en/shop/hardware/sound-and-vibration/`（按订货号检索）。

## 2. 功能映射表（参考能力 → 本仓库证据 → 下一动作）

图例：**O** = 已有强证据；**C** = candidate；**H** = hypothesis；**M** = missing / 未开实验。

| # | 参考功能 | 本仓库对应标识 / 观测 | 现状 | 规划动作（证据门禁） |
|---|----------|------------------------|------|----------------------|
| F1 | USB 2.0 设备枚举 | VID `0x3923`；主设备 PID `0x744f`；伴生装载 `0x7317`→RAM `0xA0` | O/C | 保持枚举抓包；对照伴生→主设备时间线 |
| F2 | 4×AI BNC | 照片约 **5×BNC**；`SIG-INPUT-CONNECTOR`；HW 通道叙述 4 ADC | C | 用丝印/示波器确认 AI0–3 与第 5 口（疑似 AO） |
| F3 | 1×AO BNC | 同上第 5 BNC 候选 | H | 直流台阶注入 AO 口 + USB/`EP06` 关联实验 |
| F4 | 同步多通道采样 | `phase_c/templates/sync_multichannel.md`；EXP 多通道项 | M→待做 | **P-SYNC**：共源正弦/脉冲，解包后测通道偏斜 |
| F5 | 采样率可编程至 ~102.4 kS/s | `SIG-ADC-SAMPLE-RATE` unknown；吞吐假设 manifests | M | **P-RATE**：阶梯配置候选 opcode，对照 EP84 字节率 |
| F6 | 24-bit 样本 | `usb_sample_packing_hypothesis.json`；位宽未坐实 | H | **P-PACK**：已知幅度直流/正弦 → 恢复标度与交织 |
| F7 | AC/DC 耦合 | `SIG-COUPLING-MODE` / relay 相关 unknown | M | **P-COUPLE**：低频方波 + 切换命令前后频谱/均值 |
| F8 | IEPE 0/2.1 mA | 前级/激励标识多 unknown | M | **P-IEPE**：IEPE 传感器偏置电压与开路/短路指示对照命令 |
| F9 | 抗混叠 | `SIG-ANTIALIAS-FILTER` unknown | M | **P-AAF**：扫频近 Nyquist，看镜像抑制 vs 采样率 |
| F10 | 过载检测 | 无专用标识 | M | **P-OVLD**：超 ±10 V（安全限内）观察状态回报 opcode |
| F11 | AO 激励同步 AI | EP06 OUT 有大量 bulk；角色未证 | H | **P-STIM**：EP06 波形出 ↔ AO 口示波器 ↔ AI 回采 |
| F12 | PFI 数字触发 | 板边 **D-sub** 候选；PFI 未映射 | H | **P-TRIG**：TTL 边沿 ↔ 流起点对齐统计 |
| F13 | 命令/配置面 | EP `0x01/0x81` 帧；14 opcode；taxonomy | C | M1/M2 重放 + 白名单；固件 `0x1435`/`0x08` 旁证 |
| F14 | 数据流面 | EP `0x84` IN 主数据；`0x08`∩`0x1435` oracle | C | M3–M5；固件 datapath 候选已锚定 |
| F15 | 厂商 DAQmx API | 本仓库 **不复现** SDK；仅自研 API 草案 | — | 维持 `HOST_ACQ_API_SKETCH.md` 观测映射 |

## 3. 规划阶段（与现有 M0–M6 对齐并加功能专题）

```text
参考规格清单 (本文 §1–2)
        │
        ▼
M0 证据盘点 ──► M1 命令重放 ──► M2 分帧 ──► M3 样本打包
        │                                      │
        │                              ┌───────┴────────┐
        │                              ▼                ▼
        │                         P-RATE/P-PACK    P-SYNC/P-TRIG
        │                              │                │
        │                              ▼                ▼
        │                            M4 多通道同步 ◄──┘
        │                              │
        │                              ▼
        │                            M5 高速压力（逼近参考 102.4 kS/s）
        │                              │
        └──────── EEPROM/L7 ───────────┴──► 固件交叉验证 F5–F14
```

### 阶段 A — 规格锚定（文档/账本，无新硬件动作）

1. 将 §2 映射表挂到 `ACQUISITION_ROADMAP.md` / `INDEX.md`。  
2. 为 F5–F12 各挂一条 Phase C 实验模板条目（可复用现有 `phase_c/templates/`）。  
3. **禁止**把参考 SKU 型号数字串写入 manifests；证据只用 VID/PID、照片、pcap 哈希。

### 阶段 B — 信号链坐实（需要实机 + 已知激励）

| 优先级 | 专题 | 最小成功标准 | 依赖 |
|--------|------|--------------|------|
| P0 | P-PACK + P-RATE | 至少 1 种位宽/交织模型在 ≥2 组已知正弦上复现频率与相对幅度 | M2；session 抓包 |
| P0 | P-SYNC | 4 AI 共源下通道间偏斜有界且可重复 | P-PACK |
| P1 | P-COUPLE / P-IEPE | 切换前后电气行为与至少 1 个候选 opcode 稳定共现 | M1 白名单 |
| P1 | P-STIM（AO） | AO 口电压与 EP06 载荷或命令序列可对拍 | 示波器 |
| P2 | P-TRIG / P-AAF / P-OVLD | 触发对齐、近 Nyquist 抑制、过载指示各至少 1 次可复现 | P0 |

### 阶段 C — 主机采集栈（开源侧）

对齐 `HOST_ACQ_API_SKETCH.md`，按参考功能补齐配置面（**名称自拟，非 DAQmx**）：

- `set_sample_rate(fs)` ↔ F5  
- `set_channel_enable(mask)` / `set_coupling` / `set_iepe` ↔ F4/F7/F8  
- `start_stream` / `read_samples` ↔ F14（EP84）  
- `write_ao` / `load_stimulus` ↔ F11（EP06 候选）  
- `arm_trigger(pfi, edge)` ↔ F12  

每项升 `candidate` 必须附：pcap 片段哈希、激励记录、可选示波器照片。

### 阶段 D — 固件交叉（已有 RAM 镜像）

| 参考功能 | 固件侧已有锚点 | 下一步 |
|----------|----------------|--------|
| 流启动 | opcode `0x08` @ `0x1435` + EP6/FIFO SFR | Ghidra 标 CFG；对照 start_stream |
| 端点配置 | init chain：`EP6FIFOCFG`/`EP*BCL`/`PINFLAGS*` | 与采样率/通道使能命令共现分析 |
| 持久真源 | `eeprom.bin` 仍 missing | 物理 I²C dump（`phase_b/templates/eeprom_read.md`） |

## 4. 明确非目标

- 不宣称已实现或兼容 NI-DAQmx / Sound and Vibration Toolkit。  
- 不把参考规格中的量程、噪声、校准指标直接写成 `confirmed`。  
- 不在仓库提交受版权的完整厂商驱动/手册 PDF 二进制。  
- 不因“照片像 / VID 同厂”自动升级 null 桥。

## 5. 验收清单（规划完成 ≠ 功能证实）

- [x] 公开规格能力表（§1）  
- [x] 与本仓库标识/观测的逐项映射（§2）  
- [x] 与 M0–M6 对齐的专题实验序（§3）  
- [ ] 至少 P0（打包+采样率+同步）实验日志入库并人工审阅  
- [ ] 参考功能中已证实子集写入账本（逐条证据，禁止批量升格）

## 6. 相关文件

- [`ACQUISITION_ROADMAP.md`](ACQUISITION_ROADMAP.md) — 采集里程碑 M0–M6  
- [`BINARY_RE_PLAN.md`](BINARY_RE_PLAN.md) — FX2 RAM 静态逆向  
- [`HOST_ACQ_API_SKETCH.md`](HOST_ACQ_API_SKETCH.md) — 主机 API 草案  
- [`phase_b/analysis/MCU_NOTES.md`](phase_b/analysis/MCU_NOTES.md) — 固件锚点  
- [`phase_c/templates/sync_multichannel.md`](phase_c/templates/sync_multichannel.md)  
- [`phase_c/templates/high_speed_capture.md`](phase_c/templates/high_speed_capture.md)
