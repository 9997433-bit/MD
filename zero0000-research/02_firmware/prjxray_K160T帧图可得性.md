# prjxray 帧图可得性（XC7K160T）

> 日期：2026-08-28  
> 目的：关闭 G0/P2.5「不需板、用公开 frame map 定死 blk=1 边界」路径是否仍可行。  
> 范围：仅 `20230825_s2056`（器件 XC7K160T）。

---

## 核查

| 源 | 结果 |
|----|------|
| `f4pga/prjxray-db` → `kintex7/mapping/devices.yaml` | **仅** `"xc7k70t"` |
| 同仓 `kintex7/` 目录 | 有 `xc7k70t/tilegrid.json`；**无** `xc7k160t` |
| UG470 | 公布 K160T 总配置位数 `53,540,576`；**不**公布 type0/type1 帧数拆分 |
| 本仓 FDRI | 16 560 帧（与 UG470 量级一致）；密度塌陷估 BRAM 区见 `位流BRAM帧分析.md` |

复核命令（任意时刻可再跑）：

```bash
curl -sL https://raw.githubusercontent.com/f4pga/prjxray-db/master/kintex7/mapping/devices.yaml
# 期望仅见 xc7k70t
```

---

## 结论

| 项 | 等级 |
|----|------|
| 用公开 prjxray **精确**切本板 blk1 BRAM 内容区 | ❌ **路径关闭**（库无 K160T） |
| 密度塌陷 + ~5.5 KB 非零字节 →「无大规模 BRAM ROM」 | 仍为 **强 🔶**（`analyze_bram_frames.py`） |
| 升到命题 ✅（ILA/总线） | 仍须 G2+/G4；或自备 Vivado frame map |

**不做**：用 K70T tilegrid 外推 K160T 列数（器件不同，禁止冒充本板证据）。
