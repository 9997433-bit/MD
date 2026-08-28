# Must 完成审计（当前 · 未达成）

> 对照 `算法与ADCDAC实现_研究计划.md` §5 **最低合格（Must）**。
> 由 `scripts/audit_must.py` 生成：2026-08-28T11:25:25.453541+00:00
> 结论：**Must 未达成 → 总目标未完成。禁止标 complete。**

---

## 机器核验快照

```text
g2_inbox usable: False; clocks_filled=[]; spi=[]
G0: P1.1=强 🔶 P1.2=强 🔶 P1.3=❓ P1.4=❓
§4.2 empty: False
Must-1=False Must-2=True Must-3=False
```

## Must-1

| 命题 | 等级 | 达子条 |
|------|------|--------|
| P1.1 | 强 🔶 | 是 |
| P1.2 | 强 🔶 | 是 |
| P1.3 | ❓ | **否** |
| P1.4 | ❓ | **否** |

**Must-1：失败。**

## Must-2

§4.2 算法模块排除表空：False
**Must-2：通过。**

## Must-3

实测 inbox：{'clocks_file': False, 'clocks_filled': [], 'spi_csvs': [], 'usable': False}
含 sha256 的 G2 文档：（无）
**Must-3：失败。**

## 解锁

`G2_投放三步.md` → 根目录实测 → `ingest_g2_inbox.py` → 人工回填 G0 → 再跑本脚本。
