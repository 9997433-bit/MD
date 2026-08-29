# 静态阶段关闭摘要（骨架）

**状态：未冻结** — 本包为 A→F 骨架，可 `make verify`，但尚未宣称静态学习结案。

## 已可宣称

- 产品身份：USB-6453 / Firebolt / VID:PID 3923:7B44
- 同步语义：16 ADC 同源 convert；32 SE bank + AIConv（规格 confirmed）
- 职责边界：同步在 ADC+FPGA；FX3 = 配置代理 + DMA 桥
- FPGA 载体：XC7A100T bitstream；同步 HDL unknown

## 未关闭（见 OMISSIONS）

- Fusion 请求字典、寄存器表、帧格式、ADC 料号、网表时钟树

冻结条件：LEARN 六问书面答案入库 + OMISSIONS 审阅 + 强制 null 桥审计通过后，再写 `manifests/static_freeze.json`。
