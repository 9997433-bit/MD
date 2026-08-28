# 执行状态

| 项 | 状态 |
|----|------|
| 骨架 | 已建立 |
| 固件入库 | `firmware/niusbFirebolt.cfg` + `niusbFireboltFPGA.cfg` |
| 并行充实 | Fable 批次已合并（见 `SUBAGENT_RUN.md`） |
| USB 描述符静态 | 已解析（`fx3_static_re.json` / `docs/DATA_PATH.md`） |
| 照片入库 | 未默认提交；见 `manifests/photo_index.json` 远程索引 |
| 静态冻结 | **未冻结**（可继续 Ghidra 深挖；抓包仍延后） |
| 抓包 | 不做（本阶段） |

生成账本：`make verify`
