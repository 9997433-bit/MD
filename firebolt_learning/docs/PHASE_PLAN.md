# 阶段计划 A→F（不抓包）

> 与对话中约定的学习计划一致；本文件是仓库内权威阶段说明。

## A — 资产编目

- 输入：`firmware/*.cfg`，源仓库照片清单
- 产出：`manifests/manifest_files.json`、`file_hashes.json`、`photo_index.json`
- 验收：SHA-256 稳定；类型识别正确（FX3 image / Xilinx bin）

## B — 规格书同步模型

- 输入：USB-6453 Specifications（16 ADC、simultaneous、bank、FIFO、Signal Stream）
- 产出：账本 `catalogs.spec`（`SPEC-*`）
- 验收：同步语义状态机可叙述，且不依赖固件

## C — 硬件拓扑

- 输入：拆机照片索引 + SPEC
- 产出：`manifests/system_map.json`、账本 `catalogs.hardware`
- 验收：节点职责与“同步发生在 ADC+FPGA”一致

## D — FX3 控制面角色

- 输入：`niusbFirebolt.cfg` strings / 浅结构
- 产出：`manifests/firmware_meta.json`、账本 `catalogs.fx3`
- 验收：Fusion / FPGA register / DMA 角色写清；**不**声称已还原寄存器表

## E — FPGA bitstream 边界

- 输入：`niusbFireboltFPGA.cfg`
- 产出：`manifests/bitstream_meta.json`、账本 `catalogs.bitstream`
- 验收：IDCODE=XC7A100T confirmed；同步 HDL = `unknown`

## F — 桥接与闭环

- 产出：`bridge_matrix.json`、`OMISSIONS_AND_REMAINING.md`、`coverage.json`
- 验收：强制 null 桥保留；LEARN 检查项可追踪

## 延后（不阻塞静态结案）

- USB 抓包还原 Fusion 字段
- 实机示波器看 convert/bank
- FPGA 网表逆向
- 行为复现 / 自研驱动
