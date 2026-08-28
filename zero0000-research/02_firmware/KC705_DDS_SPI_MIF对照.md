# KC705_DDS SPI MIF 对照（s2056 静态否定证据）

> 对照仓库：[samprager/KC705_DDS](https://github.com/samprager/KC705_DDS)  
> 本地位流：`assets/firmware/20230825_s2056.bin`  
> 工具：`scripts/search_fmc150_mif_rom.py`  
> 表源（2026-08-28 从上游拉取核对）：
> - `.../ads62p49_init_mem_synth_1/ads62p49_init_mem.mif`
> - `.../dac3283_init_mem_synth_1/dac3283_init_mem.mif`
> - `.../cdce72010_init_mem_int_synth_1/cdce72010_init_mem_int.mif`
> - `.../cdce72010_init_mem_ext_synth_1/cdce72010_init_mem_ext.mif`

## 1. 参考设计如何写 SPI

KC705_DDS 用 `blk_mem_gen` + `.mif`/`.coe` 把整表 SPI 配置固化进 BRAM，再由 FSM 顺序读出经 SPI 发出。因此：**若 s2056 复用同一套表，位流里应能找到连续的 LE/BE 16/32-bit 字节串**，而不是零散的单字命中。

| ROM | 关键特征字 | 含义（参考设计） |
|-----|----------|------------------|
| ADS62P49 | `0x4180`（表中第 5 字） | CLKOUT = DDR LVDS |
| DAC3283 | `0x0121`（表中第 2 字） | CONFIG1：约 2× 插值 |
| CDCE int | Reg0=`0x683C0350` 等 13 字 | 内部 491.52 方案（近 E2E，非逐字相同） |
| CDCE ext | Reg0=`0x683C0310` 等 13 字 | 外部参考方案 |

GPIO 拨码：README 要求 GPIO1=1、GPIO2–4=0 才能按演示通路运行 —— 支撑本板 **H9(SW5)** 的「拨码改数据通路」先验，但**不能**把 KC705 拨码语义直接映射到 SW5。

## 2. s2056 搜索结果（真实 MIF，可复现）

```
ADS62P49_MIF LE16/BE16: full_hits=0, longest_prefix≤2/18
DAC3283_MIF  LE16/BE16: full_hits=0, longest_prefix=0/32
CDCE_INT_MIF LE32/BE32: full_hits=0, longest_prefix=0/13
CDCE_EXT_MIF LE32/BE32: full_hits=0, longest_prefix=0/13
```

**结论（✅ 否定细假说）**：s2056 **未**以 KC705_DDS 那种「整表 MIF → BRAM INIT」方式嵌入上述四套 SPI 表。  
与 `位流SPI常量搜索.md`（无 FMC150 E2E Reg0/A/B 明文簇）及 `位流BRAM帧分析.md`（BRAM 初值极少）同向。

> 纠错：早期草稿曾用错误路径/错误字序的假想表；本文件与脚本已改为上游 `.mif` 实值。否定结论在纠正后**仍然成立**。

## 3. 对命题①②的含义

| 命题 | 含义 |
|------|------|
| ① ADC/DAC 模式 | 不能从「拷贝 KC705_DDS MIF」推出；`0x4180`/`0x0121` 仍是 **G2 SPI 探针靶标** |
| ① 配置归属 P1.5 | 削弱「照抄 KC705_DDS BRAM ROM 写表」；EEPROM / 运行时拼帧 / 主机下发仍待 G2 |
| ② / H6 | 与「无大规模 BRAM 驻留表」互洽；不证明无 RTL SPI FSM |

## 4. 复现

```bash
cd zero0000-research
python3 scripts/search_fmc150_mif_rom.py assets/firmware/20230825_s2056.bin
```

## 5. 证据分级

| 断言 | 级 |
|------|----|
| 位流中无 KC705_DDS ADS/DAC/CDCE(int+ext) MIF 连续表（LE/BE） | ✅ |
| 因此本板 SPI 表 ≠ 该公开工程的 MIF INIT | ✅ |
| 本板实际 SPI 寄存器值 | ❓（需 G2） |
