# 学习指南

本包供**静态学习**使用，不声称厂商等价。当前范围：**不抓包**。

## 推荐顺序

1. 读 `README.md`、`docs/PHASE_PLAN.md`、`OMISSIONS_AND_REMAINING.md`
2. 读规格驱动条目：`catalogs/catalog_spec_sync.py`（或账本 `catalogs.spec`）
3. 看 `system_map` + `DATA_PATH` + `FX3_GPIF_PATH` + `FX3_REGACCESS_SHAPE` + `FX3_PIB_CROSSREF`
4. 对照 `fx3_*` manifests（含 `fx3_pib_crossref.json`）与 bitstream meta
5. 读 `bridge_matrix.json` — 哪些桥被强制置空
6. 用 `docs/LEARN_ANSWERS.md` + `catalogs/catalog_learn.py` 自测

## 六问验收（每问需证据等级）

1. 同步在哪一层发生？
2. 16 路同时 vs 32 路单端 bank 的条件？
3. Sample clock / Start trigger / AIConv 各管什么？
4. FX3 与 FPGA 谁负责什么？
5. FIFO→USB 帧如何打包？（本阶段允许多为 hypothesis/unknown）
6. 哪些结论必须抓包/实机才能升级？

## 证据等级

| status | 含义 |
|--------|------|
| `confirmed` | 规格书原文、固件魔数/IDCODE/VIDPID、照片可读丝印 |
| `candidate` | 多源旁证，尚未闭合 |
| `hypothesis` | 合理推断，无直接字节证据 |
| `unknown` | 静态包无法证明；见 OMISSIONS |

## 命令

```bash
make verify
make test
make status
```
