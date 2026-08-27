# 遗漏登记与剩余边界

**生成时间**：2026-08-27  
**声明**：目录完整 ≠ 厂商等价 ≠ 掌握运行行为

## 预期保持 unknown / missing / not_started 的项

### 固件层（需实机）
| ID | 原因 |
|----|------|
| FW-001~FW-005 | 板载 EEPROM 未读取，8051 固件镜像缺失 |
| DRV-001~DRV-005 | 官方驱动安装包未解包 |
| PROTO-001~PROTO-015 | 无 USB 抓包/无实机 |

### 位流深层（需专用解码器）
| ID | 原因 |
|----|------|
| FRM-006, FRM-008, FRM-009 | 完整 Spartan-3 帧解码器未实现 |
| IOB-002~004, IOB-008~015 | IOB 配置字解码未闭合 |
| CLK-001~005 | 时钟网络需帧级分析 |
| MEM-001~003, MEM-005 | BRAM 初始化数据未提取 |

### 信号层（需实验验证）
| ID | 原因 |
|----|------|
| SIG-008, SIG-010, SIG-017, SIG-018 | 需抓包或实测 |
| SIG-002, SIG-006, SIG-012 | 继电器路由仅为假设 |

## 强制 null 桥（禁止升级）
见 `bridge_matrix.json` — 10 条桥接在无新证据前保持 null。

## 后续阶段

- **阶段 B**：EEPROM + USB 抓包 → `phase_b/`
- **阶段 C**：实验验证 → `phase_c/`
- 静态阶段验收：`python3 scripts/verify_completion.py`

## 阶段 B 检查清单（需实物，未采集前保持 unknown / missing）

> 所有项在完成真实采集前不得升级为 `confirmed`；数据只能来自实机采集，禁止静态推断填充。

### 前置
- [ ] 确认对设备与相关软件有合法分析授权
- [ ] 备齐实物设备、EEPROM 读取器/夹具、USB 抓包主机

### EEPROM 读取（模板 `phase_b/templates/eeprom_read.md`）
- [ ] 读出 24LC64 完整镜像至 `phase_b/captures/eeprom.bin`
- [ ] 两次读取一致性校验通过
- [ ] 记录 SHA-256 与采集环境到 `manifests/eeprom_meta.json`
- [ ] 回填对应 FW-* 的 status 与 evidence

### USB 抓包（模板 `phase_b/templates/usb_capture.md`）
- [ ] 采集枚举 / 初始化 / 工作 / 空闲各场景
- [ ] 每段抓包记录哈希与操作说明
- [ ] 请求-响应整理进 `protocol_log_template.json`
- [ ] 回填对应 PROTO-* / SIG-* 的 status 与 evidence

### 驱动解包（步骤见 `phase_b/README.md`）
- [ ] 合法授权下解包官方分发包并校验来源哈希
- [ ] 提取可读字符串 / 资源用于交叉比对
- [ ] 不留存超出学习目的的完整受版权二进制

### 回填闭环
- [ ] 运行 `python3 scripts/ingest_phase_b.py` 登记采集物
- [ ] 运行 `python3 scripts/generate_ledger.py` 刷新账本
- [ ] 未采集项保持 unknown/missing 并在本文件登记
- [ ] 强制 null 桥未被破坏
