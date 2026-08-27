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

## 后续阶段（不在本轮静态范围）

- **阶段 B（已搭脚手架）**：EEPROM 读取 + USB 抓包 → 见 `phase_b/README.md`
- 阶段 C：实验验证 hypothesis
- 阶段 D：开源行为复现

## 阶段 B 脚手架

```
phase_b/
├── README.md
├── templates/
│   ├── eeprom_read.md
│   ├── usb_capture.md
│   └── protocol_log_template.json
└── captures/          # 待用户填入实机数据
```
