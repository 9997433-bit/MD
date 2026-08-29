# Cosmic Front VR — Steam 上架检查清单（P6）

> 对应 `SteamManager`（默认离线骨架，测试 AppID `480` Spacewar）与 [GAME_MODES.md](GAME_MODES.md)。正式上架前逐项勾选。

## 1. 合作伙伴与 AppID

- [ ] Steamworks 合作伙伴账户就绪，应用已创建
- [ ] 正式 **AppID** 已申请（替换代码中的 `480`）
- [ ] `steam_appid.txt`（开发用）与正式 depot 配置一致
- [ ] `SteamManager.appId` / 发布构建 Define `COSMIC_STEAMWORKS` 已对齐
- [ ] 导入 [Steamworks.NET](https://github.com/rlabrecque/Steamworks.NET) 并接通 `SteamAPI.Init()`
- [ ] 仓库 **不得** 提交含正式密钥的私密配置

## 2. 构建与 Depot

- [ ] 目标平台：**Windows PCVR**（64-bit）
- [ ] Unity 构建：Standalone Windows，IL2CPP 或 Mono 策略已定
- [ ] VR：OpenXR 启用；SteamVR / 主流头显冒烟通过
- [ ] Dedicated Server 构建（若提供）：单独 depot 或工具页说明
- [ ] SteamPipe / 内容构建工具上传成功，分支 `default` / `beta` 策略明确
- [ ] 版本号与 `Player Settings` bundleVersion 同步
- [ ] 首次启动无缺 DLL（Steam API、Visual C++ 运行库说明）

## 3. 商店页文案与品牌

- [ ] 短描述 / 长描述（中英至少其一完整）
- [ ] 标签：VR、多人、射击、机甲/太空 等（避免侵权词）
- [ ] **IP 合规**：无 GUNDAM / SEED / 万代商标或近似剪影（见 [IP_BIBLE.md](IP_BIBLE.md)）
- [ ] 开发商 / 发行商名称、支持邮箱、官网或 Discord

## 4. 视觉资产规格（商店）

| 资产 | 规格 | 状态 |
|------|------|------|
| 主胶囊图 Header Capsule | 460×215 | [ ] |
| 小胶囊 Small Capsule | 231×87 | [ ] |
| 主胶囊 Main Capsule | 616×353 | [ ] |
| 竖直主胶囊 | 374×448 | [ ] |
| 页面背景 | 1438×810（可选） | [ ] |
| 库概览 Library Capsule | 600×900 | [ ] |
| 库英雄 Library Hero | 3840×1240（或官方当前规格） | [ ] |
| 库 logo | 透明 PNG，官方推荐尺寸 | [ ] |
| 商店截图 | **至少 5 张**，常见 **1920×1080**（16:9） | [ ] |
| 预告片 | 可选；若有则符合 Steam 编码要求 | [ ] |

截图建议覆盖：机库、机甲驾驶舱 HUD、战舰座位、护送/据点模式、多人记分板。

## 5. VR 特性页（Steam VR）

- [ ] 在 Steamworks 勾选 **VR Supported** / OpenXR 相关选项
- [ ] 填写头显兼容说明（SteamVR、Index、Quest Link 等实测列表）
- [ ] 标明输入：手柄（OpenXR action bindings）
- [ ] Comfort：默认 Snap Turn、推进暗角等（见 `VRComfortSettings`）
- [ ] 写明最低 / 推荐 PC 配置与 VR 就绪要求
- [ ] 若仅 PCVR、无 Quest 原生：商店页写清「仅 SteamVR / OpenXR PC」

## 6. 隐私政策与法律

- [ ] 公开发布 **隐私政策 URL**（Steam 必填项）
- [ ] 说明收集内容：Steam ID、多人 IP/会话、崩溃日志（如有）
- [ ] 地区合规提示（GDPR 等按发行范围）
- [ ] EULA / 用户协议（若需要）
- [ ] 年龄分级问卷完成（见下节）

## 7. 年龄分级与内容描述

- [ ] Steam 问卷调查完成（暴力：机甲/舰船战斗击毁）
- [ ] 无血腥肢体分解则如实填写；有夸张爆炸需在描述中体现
- [ ] 无赌博 / 随机箱则明确「无」
- [ ] 目标 ESRB / PEGI 自评与商店页一致（正式评级按地区流程）

## 8. 网络与多人

- [ ] 大厅 / 邀请方案：Steam Overlay 邀请或深链 `cosmicfront://join?ip=&port=`（`SteamManager.GetInviteConnectString`）
- [ ] 防火墙 / 端口说明（默认参考 `NetworkSessionConfig`，常见 7770）
- [ ] NAT / Relay 计划（FishySteamworks 等）写入商店 FAQ
- [ ] Dedicated Server 玩家自建说明文档链接

## 9. 成就、云存档、富媒体（可选 MVP）

- [ ] 成就是否首发上线（可后期）
- [ ] Steam Cloud 是否需要（机库设置 / Comfort）
- [ ] 富存在感（Rich Presence）：模式名、分队

## 10. 发布前验收

- [ ] 干净机器 + 仅 Steam 库安装冒烟
- [ ] 离线启动与 Steam 在线启动均验证
- [ ] 单机 TDM / Escort / Domination 各一局
- [ ] Host + Join 局域网一局
- [ ] VR 与键鼠回退均可用
- [ ] 性能测试：目标头显 ≥ 72 Hz 可接受帧时
- [ ] 卸载干净、无残留强制服务

## 参考

- 内部：`Assets/_Project/Scripts/Steam/SteamManager.cs`
- 文档：[GAME_MODES.md](GAME_MODES.md)、[MULTIPLAYER_SETUP.md](MULTIPLAYER_SETUP.md)、[DEDICATED_SERVER.md](DEDICATED_SERVER.md)
- Valve：Steamworks 文档 → Store Page / VR / Depot builds（以官网当前规格为准）
