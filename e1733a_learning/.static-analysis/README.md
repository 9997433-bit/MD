# .static-analysis 冻结层（占位）

本目录用于存放 **反汇编冻结** 产物，形态对齐 xd_laser 方法论：

| 字段 | 含义 |
|------|------|
| `body_range.sha256` | 函数体字节范围哈希 |
| `rva` | PE 内相对虚拟地址 |
| `instruction_window` | 指令窗哈希（固定长度反汇编片段） |
| `window_hash` | 与 EvidenceLedger 行关联 |

## 当前状态

**尚未冻结**。以下项在 `placeholders.json` 中登记，status 保持 `unknown`：

- `CMP-UNK-AMBIENT-BODY`（E1736A_ReadEnvironment）
- `CMP-UNK-LASERDIST-BODY`（E1735ACore_ProcessRawData）
- `CMP-UNK-INTERPOLATE-ALG`
- `ANA-UNK-ALG-ISO230-BODY`

## 禁止

- 无新指令窗不得将 unknown 升级为 E1
- 旁证（export 符号、Remote.h 常量）不得写入本目录冒充公式窗

## 未来文件

```
E1735ACore.dll.json
E1736A.dll.json
E1733A.exe.json
```
