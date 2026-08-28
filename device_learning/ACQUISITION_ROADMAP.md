# 实机采集与协议逆向路线图

> **声明：目录完整 ≠ 厂商等价 ≠ 掌握运行行为。** 本路线图只定义证据门禁；任何结论必须由可复现实验和账本记录支撑。里程碑按依赖排序，不承诺天/周工期。

## M0 — 证据盘点（USB 已完成，EEPROM 缺失）

- **目标**：冻结当前证据基线并显式记录缺口。
- **输入**：`phase_b/captures/usb_enum.pcapng`、`usb_session.pcapng`、`protocol_log.json`；[`manifests/phase_b_status.json`](manifests/phase_b_status.json)、[`usb_protocol_decode.json`](manifests/usb_protocol_decode.json)。
- **输出**：带哈希的 USB 证据清单；EEPROM 缺失项；刷新后的采集清单。
- **阻塞项**：`eeprom.bin` 尚未取得；[`capture_manifest.json`](manifests/capture_manifest.json) 与实物采集状态不一致时须先重建。
- **成功标准**：两份实机 USB 抓包及协议日志可校验、可追溯；EEPROM 状态明确为 `missing`，无合成夹具冒充实机证据。

## M1 — 命令重放框架

- **目标**：安全、确定性地重放已观察命令并记录响应。
- **输入**：M0 证据；[`usb_command_taxonomy.json`](manifests/usb_command_taxonomy.json) 中的端点、标签、opcode 与样例。
- **输出**：支持 dry-run、白名单和超时的重放工具；逐事务请求/响应日志。
- **阻塞项**：opcode 语义未知；写操作可能改变设备状态；设备重枚举会使地址失效。
- **成功标准**：选定的只读/低风险事务可从语义字段编码、发送并稳定复现捕获中的响应形态，失败可诊断且默认不发送未知命令。

## M2 — 分帧解码器

- **目标**：把 EP `0x01/0x81` 字节流可靠还原为命令帧，不依赖单个 URB 边界。
- **输入**：M1 日志；[`usb_command_taxonomy.json`](manifests/usb_command_taxonomy.json) 的 `tag + frame_length + body_length` 假设；[`usb_bulk_framing_hypothesis.json`](manifests/usb_bulk_framing_hypothesis.json) 的历史假设。
- **输出**：流式编码/解码库、截断/拼接处理、黄金向量与异常报告。
- **阻塞项**：尚无主动重放覆盖全部长度与标签组合；命令语义仍未知。
- **成功标准**：全部已观察命令面流量可无剩余字节地解析，长度约束全部满足，编码→解码往返与抓包字节一致。

## M3 — 样本打包逆向

- **目标**：确定 EP `0x06/0x84` 的样本位宽、字节序、符号、通道交织和缩放关系。
- **输入**：M2；[`usb_data_plane_hypothesis.json`](manifests/usb_data_plane_hypothesis.json)；Phase C 已知直流/正弦/阶跃输入及同步 USB 抓包。
- **输出**：样本解包器、格式说明、黄金样本和假设置信度记录。
- **阻塞项**：缺少已知激励与设置变化的对照实验；EEPROM/固件缺失使格式旁证不足。
- **成功标准**：同一格式模型可跨多组已知输入和采集设置恢复预期波形、极性、频率及通道顺序，且残余字节有明确解释。

## M4 — 多通道同步验证实验（Phase C）

- **目标**：验证通道映射、帧序、触发对齐、偏斜及丢样行为。
- **输入**：M3 解包器；共源多通道脉冲/正弦；[`phase_roadmap.json`](manifests/phase_roadmap.json)、[`phase_c_readiness.json`](manifests/phase_c_readiness.json) 与 `phase_c/templates/experiment_log_template.json`。
- **输出**：Phase C 实验日志；逐通道偏斜、连续性、重复性和丢样统计。
- **阻塞项**：M3 未通过；通道/触发命令未识别；测试设备无共同时间基准。
- **成功标准**：在预先登记的采样率、通道组合和容差矩阵中，通道映射与对齐可重复验证；任何漂移、重排或丢样均可定位到帧/样本索引。

## M5 — 高速压力验证

- **目标**：测出当前主机与设备组合的可持续采集上限及失效模式。
- **输入**：M1–M4 工具链；最高可配置采样率/通道数；USB 传输、主机负载和样本连续性计数。
- **输出**：吞吐/延迟/丢帧矩阵、资源曲线、失败抓包与可复现压力脚本。
- **阻塞项**：缺少稳定连续性判据；主机控制器、驱动缓存或存储写入可能先成为瓶颈。
- **成功标准**：测试矩阵和通过阈值预先登记；在实测上限下持续运行无未解释数据缺口，超过上限时能检测、记录并复现实效模式。

## M6 — EEPROM + 反汇编解锁

- **目标**：取得实机 EEPROM，提取 8051 固件，并用静态证据约束命令与数据格式假设。
- **输入**：`phase_b/captures/eeprom.bin`；[`eeprom_layout_ref.json`](manifests/eeprom_layout_ref.json)、[`firmware_extract.json`](manifests/firmware_extract.json)；M2–M5 的待验证假设。
- **输出**：带哈希的 EEPROM、可重复提取的固件、`phase_b/analysis/mcu_disasm.txt`、入口/调用/常量交叉引用及账本升级提案。
- **阻塞项**：需授权的物理读取条件与正确接线；代码/XRAM 映射和间接调用可能不完整。
- **成功标准**：C2 记录边界与校验可复现，复位入口和关键调用链可追踪；命令表或样本格式获得固件交叉引用，状态升级仍逐条附证据而非批量推断。

## 功能专题（对照公开 DSA 规格）

声振 DSA 类公开能力（4 AI + 1 AO、同步采样、IEPE、AC/DC、PFI 触发等）与本仓库标识的逐项映射、实验优先级见：

[`DSA_REFERENCE_FUNCTION_PLAN.md`](DSA_REFERENCE_FUNCTION_PLAN.md)

还原进度（启发式，非完全还原）见：

[`RESTORE_PROGRESS.md`](RESTORE_PROGRESS.md)

该文档只做功能规划与证据门禁，不构成厂商 SKU 等价声明。
