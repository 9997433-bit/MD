# 官方驱动解包步骤模板（阶段 B，可选）

**用途**：在合法授权下，从官方分发包提取可读元数据用于交叉比对。**禁止**将完整受版权二进制长期留存于仓库。

> 未解包前，DRV-* 项保持 `unknown` / `not_started`。

## 0. 前置

- [ ] 确认对驱动/软件包有合法分析授权
- [ ] 记录分发包文件名、版本号、来源 URL 或安装介质
- [ ] 计算分发包 SHA-256 并记入 `phase_b/driver/package_meta.json`（采集后创建）

## 1. 解包（按实际格式选择）

| 格式 | 建议工具 | 产出 |
|------|----------|------|
| `.exe` / `.msi` | 7-Zip、`msiextract` | 解压目录 |
| `.inf` + `.sys` | 直接文本/二进制检视 | 字符串、版本资源 |
| 压缩包 | `unzip` / `tar` | 目录树清单 |

## 2. 允许留存的学习产物

- [ ] 文件树清单（路径 + 大小 + SHA-256）→ `phase_b/driver/file_tree.json`
- [ ] 可读字符串摘要（VID/PID、设备名、错误信息）→ `phase_b/driver/strings_summary.txt`
- [ ] INF 中的硬件 ID 行摘录（不含完整二进制）

## 3. 禁止 / 不建议

- 不要将完整 `.sys` / `.dll` 提交到 Git
- 不要用解包结果**单独**升级 PROTO-* 为 confirmed（需与抓包/EEPROM 交叉验证）
- 不要恢复敏感产品型号字眼到 manifest

## 4. 交叉比对

- [ ] VID/PID 与 `eeprom_meta.json` / USB 抓包是否一致
- [ ] 设备字符串与 `usb_capture` 描述符是否一致
- [ ] 矛盾处登记到 `protocol_log.json` 的 `unresolved` 段

## 5. 后续

- [ ] 运行 `make phase-b` 刷新账本
- [ ] 在 `OMISSIONS_AND_REMAINING.md` 记录仍无法从驱动获得的边界
