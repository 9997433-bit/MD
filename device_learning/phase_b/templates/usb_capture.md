# USB 抓包步骤模板（Wireshark / USBPcap / usbmon）

**用途**：记录设备的 USB 报文采集过程。**本文件为空模板，需在完成实机抓包后填写。**

> 未抓包前，PROTO-* 与依赖抓包的 SIG-* 项保持 `unknown` / `missing`。

## 0. 工具准备

| 平台 | 抓包方案 |
|------|----------|
| Windows | Wireshark + USBPcap 扩展 |
| Linux | Wireshark + usbmon（`modprobe usbmon`） |
| macOS | Wireshark + 系统 USB 抓包接口（按版本支持情况） |

## 1. 安全与前置检查

- [ ] 确认对设备与其通信软件有合法分析授权
- [ ] 关闭无关的 USB 设备，减少干扰报文
- [ ] 记录主机 OS、Wireshark 版本、抓包扩展版本

## 2. 定位目标设备

- [ ] 插入设备，记录其 VID / PID 与总线/端口号
  - Windows：设备管理器 → 详细信息 → 硬件 ID
  - Linux：`lsusb`（记录 `Bus xxx Device yyy: ID vvvv:pppp`）
- [ ] 在 Wireshark 中选择对应的 USBPcap / usbmon 接口

## 3. 抓包场景（每段单独存文件）

按"一个操作 = 一段抓包"的原则采集，便于后续对齐命令：

- [ ] 场景 1：纯枚举（插入设备，不做任何操作）
- [ ] 场景 2：初始化 / 打开会话
- [ ] 场景 3：一次典型工作操作（记录具体动作）
- [ ] 场景 4：空闲 / 关闭

每段抓包：开始前点"开始"，操作完成后点"停止"，另存为独立文件。

## 4. 保存与命名

- [ ] 文件名：`usb_<场景>_<日期>.pcapng`
- [ ] 计算哈希：`sha256sum usb_<场景>_<日期>.pcapng`
- [ ] 为每个文件写一句话说明：这段对应什么物理操作

## 5. 记录表（抓包后填写）

| 字段 | 值 |
|------|----|
| 采集时间 | |
| 主机 OS | |
| Wireshark 版本 | |
| 抓包扩展 / 接口 | |
| 设备 VID:PID | |
| 总线 / 端口 | |
| 抓包文件列表 | |
| 各文件 SHA-256 | |
| 采集者 / 环境 | |
| 备注 | |

## 6. 初步分析（可选，抓包后）

- [ ] 用显示过滤器聚焦目标设备：`usb.idVendor == 0xVVVV`（按实际填写）
- [ ] 识别控制传输（枚举描述符）与批量/中断传输（数据）
- [ ] 将请求-响应对整理进 `protocol_log_template.json`
- [ ] 与 EEPROM 内容交叉比对，标注一致/矛盾之处

## 7. 后续

- [ ] 回填 PROTO-* / SIG-* 的 `status` 与 `evidence`
- [ ] 未观察到的行为保持 `unknown`，登记到 `OMISSIONS_AND_REMAINING.md`
