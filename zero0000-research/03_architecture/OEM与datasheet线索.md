# Datasheet 索引与 OEM 线索

> 来源：[datasheet索引与OEM线索](bc-4087b0e8-b679-59b3-a314-015d99a95406)

## 关键结论

模拟前端 **ADS62P49 + DAC3283 + CDCE72010** 与 **4DSP/Abaco FMC150** BOM **逐芯片一致**（✅ 公开产品证据）。  
**未发现** Kintex-7 + FT600 + 上述三件套的公开一体成品 → 本板更像 **FMC150 参考设计 + FT600 USB3 载板** 的定制整合（🔶）。

## 相近平台

| 平台 | K7 | FT60x | ADS62P49 | DAC3283 |
|------|----|-------|----------|---------|
| Abaco FMC150 | — | ✗ | ✓ | ✓ |
| Avnet K7 DSP Kit | ✓ | ✗ | ✓ | ✓ |
| HuMANDATA EDX-009 | ✓ | FT600 | ✗ | ✗ |
| Numato Proteus | ✓ | FT601 | ✗ | ✗ |
| **本板** | ✓ | FT600 | ✓ | ✓ |

## Datasheet（速查）

- XC7K160T：AMD DS180 / DS182  
- FT600Q：FTDI DS_FT600Q-FT601Q  
- ADS62P49：TI SLAS635  
- DAC3283：TI SLAS693  
- CDCE72010：TI SCAS858  
- S25FL128S：Infineon FL-S datasheet  
- IS43TR16128D / RTL8211FI：见子代理完整链接表  

## 待证

国内淘宝/立创是否有同 BOM 成品；固件信号命名是否含 `flp_adc_*` 等 FMC150 血统痕迹。
